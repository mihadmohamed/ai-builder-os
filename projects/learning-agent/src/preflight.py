from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]

REQUIRED_FILES = (
    REPO_ROOT / "projects" / "learning-agent" / "README.md",
    REPO_ROOT / "projects" / "learning-agent" / "pilot-launch-checklist.md",
    REPO_ROOT / "projects" / "learning-agent" / "deployment-phases.md",
    REPO_ROOT / "projects" / "learning-agent" / "Dockerfile",
    REPO_ROOT / "projects" / "learning-agent" / "start.sh",
    REPO_ROOT / "projects" / "learning-agent" / "render.yaml",
    REPO_ROOT / "projects" / "learning-agent" / "railway.toml",
)

REQUIRED_HOSTED_ENV = (
    "OPENAI_API_KEY",
    "AI_BUILDER_OS_RUNTIME_ROOT",
    "AI_BUILDER_OS_LEARNING_RELEASE_PROFILE",
    "LEARNING_AGENT_AUTH_MODE",
    "LEARNING_AGENT_ALLOWED_EMAILS",
    "LEARNING_AGENT_PRIVACY_CONTACT",
    "OIDC_REDIRECT_URI",
    "OIDC_COOKIE_SECRET",
    "OIDC_CLIENT_ID",
    "OIDC_CLIENT_SECRET",
    "OIDC_SERVER_METADATA_URL",
)


@dataclass(frozen=True)
class CheckResult:
    level: str
    message: str


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _has_placeholder(value: str) -> bool:
    lower = value.strip().lower()
    return lower in {
        "",
        "replace-me",
        "replace-with-a-long-random-secret",
        "replace-with-your-oidc-client-id",
        "replace-with-your-oidc-client-secret",
        "privacy@example.com",
        "user@example.com,second@example.com",
    }


def validate_hosted_pilot_environment() -> list[CheckResult]:
    results: list[CheckResult] = []

    for path in REQUIRED_FILES:
        if path.exists():
            results.append(CheckResult("pass", f"Required file present: {path.relative_to(REPO_ROOT)}"))
        else:
            results.append(CheckResult("fail", f"Missing required file: {path.relative_to(REPO_ROOT)}"))

    for name in REQUIRED_HOSTED_ENV:
        if _env(name):
            results.append(CheckResult("pass", f"{name} is set"))
        else:
            results.append(CheckResult("fail", f"{name} is missing"))

    runtime_root = _env("AI_BUILDER_OS_RUNTIME_ROOT")
    if runtime_root and runtime_root != "/data":
        results.append(CheckResult("fail", "AI_BUILDER_OS_RUNTIME_ROOT must be /data for the hosted pilot"))

    release_profile = _env("AI_BUILDER_OS_LEARNING_RELEASE_PROFILE")
    if release_profile and release_profile != "external_v2":
        results.append(CheckResult("fail", "AI_BUILDER_OS_LEARNING_RELEASE_PROFILE must be external_v2"))

    auth_mode = _env("LEARNING_AGENT_AUTH_MODE")
    if auth_mode and auth_mode != "oidc":
        results.append(CheckResult("fail", "LEARNING_AGENT_AUTH_MODE must be oidc for the invite-only hosted pilot"))

    allowed_emails = _env("LEARNING_AGENT_ALLOWED_EMAILS")
    if allowed_emails:
        invited = [item.strip() for item in allowed_emails.split(",") if item.strip()]
        if not invited:
            results.append(CheckResult("fail", "LEARNING_AGENT_ALLOWED_EMAILS must contain at least one invited email"))
        elif len(invited) > 20:
            results.append(CheckResult("warn", "LEARNING_AGENT_ALLOWED_EMAILS has more than 20 entries; confirm the first pilot wave is intentionally that large"))
        if any("@" not in item for item in invited):
            results.append(CheckResult("fail", "LEARNING_AGENT_ALLOWED_EMAILS contains an invalid email entry"))

    privacy_contact = _env("LEARNING_AGENT_PRIVACY_CONTACT")
    if privacy_contact:
        if _has_placeholder(privacy_contact) or "@" not in privacy_contact:
            results.append(CheckResult("warn", "LEARNING_AGENT_PRIVACY_CONTACT looks like placeholder text or is not a real contact route"))

    redirect_uri = _env("OIDC_REDIRECT_URI")
    if redirect_uri and not redirect_uri.startswith("https://"):
        results.append(CheckResult("warn", "OIDC_REDIRECT_URI should use https in the real hosted environment"))

    metadata_url = _env("OIDC_SERVER_METADATA_URL")
    if metadata_url and not metadata_url.startswith("https://"):
        results.append(CheckResult("fail", "OIDC_SERVER_METADATA_URL must use https"))

    cookie_secret = _env("OIDC_COOKIE_SECRET")
    if cookie_secret and len(cookie_secret) < 24:
        results.append(CheckResult("warn", "OIDC_COOKIE_SECRET looks short; use a long random secret before launch"))

    api_key = _env("OPENAI_API_KEY")
    if api_key and not api_key.startswith(("sk-", "sess-")):
        results.append(CheckResult("warn", "OPENAI_API_KEY does not look like a typical API key; double-check the configured secret"))

    return results


def summarize_results(results: Iterable[CheckResult]) -> tuple[int, int]:
    failures = sum(1 for item in results if item.level == "fail")
    warnings = sum(1 for item in results if item.level == "warn")
    return failures, warnings


def _format_prefix(level: str) -> str:
    if level == "pass":
        return "[PASS]"
    if level == "warn":
        return "[WARN]"
    return "[FAIL]"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the invite-only hosted Learning Agent pilot configuration."
    )
    parser.parse_args()

    results = validate_hosted_pilot_environment()
    for item in results:
        print(f"{_format_prefix(item.level)} {item.message}")

    failures, warnings = summarize_results(results)
    if failures:
        print(f"\nHosted pilot preflight failed with {failures} blocking issue(s) and {warnings} warning(s).")
        return 1

    if warnings:
        print(f"\nHosted pilot preflight passed with {warnings} warning(s) to review.")
    else:
        print("\nHosted pilot preflight passed with no warnings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
