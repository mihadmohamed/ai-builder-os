from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class PublicationFinding:
    kind: str
    severity: str
    detail: str


@dataclass(frozen=True)
class PublicationReview:
    allowed: bool
    findings: tuple[PublicationFinding, ...]
    sanitized_title: str
    sanitized_body: str


@dataclass(frozen=True)
class GitHubPublicationDraft:
    target: str
    title: str
    body: str
    metadata: dict[str, str] = field(default_factory=dict)
    review: PublicationReview | None = None


@dataclass(frozen=True)
class GitHubPublishResult:
    kind: str
    url: str
    reference_id: str
    detail: str


class GitHubPublishError(RuntimeError):
    pass


EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d ()-]{7,}\d)(?!\d)")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"\b(?:OPENAI_API_KEY|OIDC_CLIENT_SECRET|OIDC_COOKIE_SECRET|CLIENT_SECRET|API_KEY|SECRET|TOKEN)\s*=\s*\S+",
    re.I,
)
OPENAI_KEY_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b")
PRIVATE_PATH_PATTERNS = (
    re.compile(r"(^|[\s`'\"(])/?private/", re.I),
    re.compile(r"(^|[\s`'\"(])projects/[^/\s`'\"]+/private/", re.I),
)
RUNTIME_PATH_PATTERNS = (
    re.compile(r"projects/[^/\s`'\"]+/data/(?:agent_traces|agent_threads|approvals|pm_clarifications|experience_findings|implementation_runs)\.jsonl?", re.I),
    re.compile(r"projects/os-control-panel/data/(?:agent_uploads|implementation_logs)(?:/|\b)", re.I),
    re.compile(r"/private/tmp/[^\s`'\"]+", re.I),
    re.compile(r"\bAI_BUILDER_OS_RUNTIME_ROOT\s*=\s*\S+", re.I),
)
PRIVATE_LANGUAGE_PATTERNS = (
    re.compile(r"\bcandid (?:strategy|planning|reflection|notes?)\b", re.I),
    re.compile(r"\bprivate (?:planning|reflection|notes?|strategy|roadmap)\b", re.I),
    re.compile(r"\braw (?:agent )?traces?\b", re.I),
    re.compile(r"\binternal thinking\b", re.I),
)
PUBLIC_POLICY_LANGUAGE_REPLACEMENTS = (
    (re.compile(r"\bcandid strategy\b", re.I), "non-public strategy detail"),
    (re.compile(r"\bcandid planning\b", re.I), "non-public planning detail"),
    (re.compile(r"\bcandid reflection\b", re.I), "non-public reflection detail"),
    (re.compile(r"\bcandid notes?\b", re.I), "non-public notes"),
    (re.compile(r"\bprivate planning\b", re.I), "local-only planning detail"),
    (re.compile(r"\bprivate reflection\b", re.I), "local-only reflection detail"),
    (re.compile(r"\bprivate notes?\b", re.I), "local-only notes"),
    (re.compile(r"\bprivate strategy\b", re.I), "local-only strategy detail"),
    (re.compile(r"\bprivate roadmap\b", re.I), "local-only roadmap detail"),
    (re.compile(r"\braw agent traces?\b", re.I), "agent trace internals"),
    (re.compile(r"\braw traces?\b", re.I), "trace internals"),
    (re.compile(r"\binternal thinking\b", re.I), "local reasoning notes"),
)


def _redact_low_risk_contact_info(text: str) -> str:
    text = EMAIL_PATTERN.sub("<redacted-email>", text)
    return PHONE_PATTERN.sub("<redacted-phone>", text)


def _publicize_policy_language(text: str) -> str:
    for pattern, replacement in PUBLIC_POLICY_LANGUAGE_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


def _hard_block_findings(text: str, source_paths: tuple[str, ...]) -> list[PublicationFinding]:
    findings: list[PublicationFinding] = []
    for pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(text) or any(pattern.search(path) for path in source_paths):
            findings.append(
                PublicationFinding(
                    kind="private_path",
                    severity="blocked",
                    detail="Payload references ignored private planning paths that must stay local.",
                )
            )
            break
    for pattern in RUNTIME_PATH_PATTERNS:
        if pattern.search(text) or any(pattern.search(path) for path in source_paths):
            findings.append(
                PublicationFinding(
                    kind="runtime_state",
                    severity="blocked",
                    detail="Payload references local runtime state, traces, uploads, logs, or temp storage.",
                )
            )
            break
    if SECRET_ASSIGNMENT_PATTERN.search(text) or OPENAI_KEY_PATTERN.search(text):
        findings.append(
            PublicationFinding(
                kind="secret",
                severity="blocked",
                detail="Payload appears to include a secret, token, or API key.",
            )
        )
    for pattern in PRIVATE_LANGUAGE_PATTERNS:
        if pattern.search(text):
            findings.append(
                PublicationFinding(
                    kind="private_planning",
                    severity="blocked",
                    detail="Payload includes private planning, raw trace, or internal-thinking language.",
                )
            )
            break
    return findings


def review_publication_payload(
    *,
    title: str,
    body: str,
    source_paths: tuple[str, ...] = (),
) -> PublicationReview:
    sanitized_title = _publicize_policy_language(_redact_low_risk_contact_info(title.strip()))
    sanitized_body = _publicize_policy_language(_redact_low_risk_contact_info(body.strip()))
    reviewed_text = f"{sanitized_title}\n\n{sanitized_body}"
    findings = tuple(_hard_block_findings(reviewed_text, source_paths))
    return PublicationReview(
        allowed=not any(finding.severity == "blocked" for finding in findings),
        findings=findings,
        sanitized_title=sanitized_title,
        sanitized_body=sanitized_body,
    )


def finalize_draft(draft: GitHubPublicationDraft) -> GitHubPublicationDraft:
    source_paths = tuple(
        path.strip()
        for path in draft.metadata.get("source_paths", "").split(",")
        if path.strip()
    )
    review = review_publication_payload(
        title=draft.title,
        body=draft.body,
        source_paths=source_paths,
    )
    return GitHubPublicationDraft(
        target=draft.target,
        title=review.sanitized_title,
        body=review.sanitized_body,
        metadata=dict(draft.metadata),
        review=review,
    )


def draft_issue_from_requirement(
    *,
    project_name: str,
    requirement_id: str,
    title: str,
    status: str,
    priority: str,
    effort: str,
    description: str,
) -> GitHubPublicationDraft:
    body = "\n".join(
        [
            "## Requirement",
            "",
            f"- Project: `{project_name}`",
            f"- Requirement: `{requirement_id}`",
            f"- Status: `{status}`",
            f"- Priority: `{priority or 'UNPRIORITISED'}`",
            f"- Effort: `{effort or 'UNSIZED'}`",
            "",
            "## Product Scope",
            "",
            description.strip() or "No public description is available yet.",
            "",
            "## Publication Boundary",
            "",
            "Generated from canonical product truth only. Local-only notes, runtime details, trace internals, and secrets are excluded.",
        ]
    )
    return finalize_draft(
        GitHubPublicationDraft(
            target="issue",
            title=f"{requirement_id}: {title}",
            body=body,
            metadata={
                "project_name": project_name,
                "requirement_id": requirement_id,
                "source_paths": f"projects/{project_name}/product/requirements.md",
            },
        )
    )


def draft_pr_description(
    *,
    project_name: str,
    requirement_id: str,
    requirement_title: str,
    run_id: str,
    run_status: str,
    summary: str,
) -> GitHubPublicationDraft:
    body = "\n".join(
        [
            "## Summary",
            "",
            summary.strip() or "Implementation summary was not captured.",
            "",
            "## OS Context",
            "",
            f"- Project: `{project_name}`",
            f"- Requirement: `{requirement_id}`",
            f"- Requirement title: {requirement_title}",
            f"- Implementation run: `{run_id}`",
            f"- Run status: `{run_status}`",
            "",
            "## Validation",
            "",
            "- Review the OS Quality panel and CI checks before merge.",
            "",
            "## Publication Boundary",
            "",
            "This PR description is a sanitized delivery summary. Runtime logs, trace internals, unpublished planning, and local-only paths are excluded.",
        ]
    )
    return finalize_draft(
        GitHubPublicationDraft(
            target="pull_request_description",
            title=f"{requirement_id}: {requirement_title}",
            body=body,
            metadata={
                "project_name": project_name,
                "requirement_id": requirement_id,
                "run_id": run_id,
                "source_paths": f"projects/{project_name}/product/requirements.md",
                "derived_from": "sanitized_implementation_run_summary",
            },
        )
    )


def draft_eval_summary(
    *,
    project_name: str,
    status: str,
    summary: str,
    failures: tuple[str, ...],
    runner_path: str,
) -> GitHubPublicationDraft:
    failure_lines = "\n".join(f"- {failure}" for failure in failures) if failures else "- No failing cases reported."
    body = "\n".join(
        [
            "## Evaluation Summary",
            "",
            f"- Project: `{project_name}`",
            f"- Status: `{status}`",
            f"- Runner: `{runner_path or 'not recorded'}`",
            "",
            summary.strip() or "No summary was recorded.",
            "",
            "## Failures",
            "",
            failure_lines,
            "",
            "## Publication Boundary",
            "",
            "This is a concise validation summary. Full validation output, local-only notes, runtime paths, and secrets are excluded.",
        ]
    )
    return finalize_draft(
        GitHubPublicationDraft(
            target="pr_eval_summary",
            title=f"{project_name}: {status} evaluation summary",
            body=body,
            metadata={
                "project_name": project_name,
                "source_paths": f"projects/{project_name}/product/tasks.md",
            },
        )
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _configured_repo() -> str:
    explicit = os.environ.get("AI_BUILDER_OS_GITHUB_REPO") or os.environ.get("GITHUB_REPOSITORY")
    if explicit:
        return explicit.strip().removeprefix("https://github.com/").removesuffix(".git")
    try:
        remote = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=_repo_root(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise GitHubPublishError(
            "GitHub repo is not configured. Set AI_BUILDER_OS_GITHUB_REPO to owner/repo."
        ) from exc
    if remote.startswith("git@github.com:"):
        remote = remote.removeprefix("git@github.com:")
    elif remote.startswith("https://github.com/"):
        remote = remote.removeprefix("https://github.com/")
    repo = remote.removesuffix(".git").strip("/")
    if "/" not in repo:
        raise GitHubPublishError("GitHub repo must be configured as owner/repo.")
    return repo


def _configured_token() -> str:
    token = os.environ.get("AI_BUILDER_OS_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise GitHubPublishError(
            "GitHub publishing is not configured. Set AI_BUILDER_OS_GITHUB_TOKEN, GITHUB_TOKEN, or GH_TOKEN."
        )
    return token


def _current_branch() -> str:
    explicit = os.environ.get("AI_BUILDER_OS_GITHUB_BRANCH") or os.environ.get("GITHUB_HEAD_REF")
    if explicit:
        return explicit.strip()
    try:
        return subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=_repo_root(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def _github_request(
    *,
    method: str,
    path: str,
    token: str,
    payload: dict[str, object] | None = None,
) -> dict[str, object] | list[object]:
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "ai-builder-os",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(f"https://api.github.com{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GitHubPublishError(f"GitHub API returned {exc.code}: {detail}") from exc
    except URLError as exc:
        raise GitHubPublishError(f"GitHub API request failed: {exc.reason}") from exc
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, (dict, list)):
        raise GitHubPublishError("GitHub API returned an unexpected response.")
    return parsed


def _require_policy_pass(payload: dict[str, str]) -> None:
    if payload.get("policy_status") != "PASS":
        raise GitHubPublishError("GitHub publication is blocked because the policy review did not pass.")
    review = review_publication_payload(
        title=payload.get("github_title", ""),
        body=payload.get("github_body", ""),
    )
    if not review.allowed:
        details = "; ".join(finding.detail for finding in review.findings)
        raise GitHubPublishError(details or "GitHub publication policy blocked this payload.")


def _publish_issue(*, repo: str, token: str, title: str, body: str, detail: str) -> GitHubPublishResult:
    created = _github_request(
        method="POST",
        path=f"/repos/{repo}/issues",
        token=token,
        payload={"title": title, "body": body},
    )
    if not isinstance(created, dict):
        raise GitHubPublishError("GitHub issue creation returned an unexpected response.")
    url = str(created.get("html_url", ""))
    number = str(created.get("number", ""))
    if not url or not number:
        raise GitHubPublishError("GitHub issue creation did not return an issue URL.")
    return GitHubPublishResult(kind="issue", url=url, reference_id=number, detail=detail)


def _open_pull_request_for_branch(*, repo: str, token: str, branch: str) -> dict[str, object] | None:
    if not branch:
        return None
    owner = repo.split("/", 1)[0]
    query = urlencode({"state": "open", "head": f"{owner}:{branch}"})
    response = _github_request(method="GET", path=f"/repos/{repo}/pulls?{query}", token=token)
    if not isinstance(response, list) or not response:
        return None
    first = response[0]
    return first if isinstance(first, dict) else None


def publish_github_publication(payload: dict[str, str]) -> GitHubPublishResult:
    _require_policy_pass(payload)
    repo = _configured_repo()
    token = _configured_token()
    target = payload.get("github_target", "")
    title = payload.get("github_title", "").strip()
    body = payload.get("github_body", "").strip()
    if not title or not body:
        raise GitHubPublishError("GitHub publication requires a title and body.")

    if target == "issue":
        return _publish_issue(
            repo=repo,
            token=token,
            title=title,
            body=body,
            detail="Created GitHub issue from approved OS requirement draft.",
        )

    if target == "pr_eval_summary":
        return _publish_issue(
            repo=repo,
            token=token,
            title=title,
            body=body,
            detail="Created GitHub issue from approved OS evaluation summary.",
        )

    if target == "pull_request_description":
        branch = payload.get("metadata_branch", "").strip() or _current_branch()
        pull_request = _open_pull_request_for_branch(repo=repo, token=token, branch=branch)
        if pull_request is None:
            raise GitHubPublishError(
                "No open pull request was found for the current branch. Open a PR first, or set "
                "AI_BUILDER_OS_GITHUB_BRANCH to the branch whose PR should be updated."
            )
        number = str(pull_request.get("number", ""))
        updated = _github_request(
            method="PATCH",
            path=f"/repos/{repo}/pulls/{number}",
            token=token,
            payload={"title": title, "body": body},
        )
        if not isinstance(updated, dict):
            raise GitHubPublishError("GitHub pull request update returned an unexpected response.")
        url = str(updated.get("html_url", ""))
        if not url:
            raise GitHubPublishError("GitHub pull request update did not return a PR URL.")
        return GitHubPublishResult(
            kind="pull_request",
            url=url,
            reference_id=number,
            detail="Updated GitHub pull request title and description from approved OS draft.",
        )

    raise GitHubPublishError(f"Unsupported GitHub publication target: {target or 'unknown'}")
