from __future__ import annotations

import html
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_SRC_ROOT = REPO_ROOT / "projects" / "os-control-panel" / "src"
if str(CANONICAL_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(CANONICAL_SRC_ROOT))

os.environ.setdefault("AI_BUILDER_OS_LEARNING_RELEASE_PROFILE", "external_v2")

from app import SECTION_STYLE, render_learning_tab  # noqa: E402
from tenancy import reset_active_user, set_active_user  # noqa: E402


def _repo_root() -> Path:
    return REPO_ROOT

LANDING_PAGE_STYLE = """
<style>
.learning-agent-landing-hero {
    background:
        radial-gradient(circle at 12% 15%, rgba(47, 111, 237, 0.14), transparent 34%),
        radial-gradient(circle at 86% 18%, rgba(219, 68, 55, 0.10), transparent 30%),
        linear-gradient(135deg, #f7faff 0%, #fffafa 50%, #f5fcf8 100%);
    border: 1px solid rgba(47, 111, 237, 0.14);
    border-radius: 1rem;
    padding: clamp(1.25rem, 3vw, 2.25rem);
    margin-bottom: 0.75rem;
}
.learning-agent-hero-top {
    align-items: flex-start;
    display: flex;
    gap: 1rem;
    justify-content: space-between;
}
.learning-agent-hero-account-block {
    align-items: flex-end;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
}
.learning-agent-hero-account {
    color: #536174;
    font-size: 0.9rem;
    line-height: 1.3;
    text-align: right;
}
.learning-agent-signout-link {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(80, 95, 120, 0.18);
    border-radius: 0.5rem;
    color: #253246;
    display: inline-block;
    font-size: 0.84rem;
    font-weight: 600;
    line-height: 1;
    padding: 0.52rem 0.8rem;
    text-decoration: none;
}
.learning-agent-signout-link:hover {
    border-color: rgba(80, 95, 120, 0.28);
    color: #182230;
}
.learning-agent-landing-hero h1 {
    margin: 0.45rem 0 0.55rem;
    font-size: clamp(2rem, 5vw, 3.4rem);
    line-height: 1.05;
}
.learning-agent-landing-hero p {
    color: #3f4a5a;
    font-size: 1.05rem;
    margin: 0;
    max-width: 46rem;
}
.learning-agent-pilot-label {
    color: #2457b8;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.learning-agent-admitted-hero {
    background:
        radial-gradient(circle at 8% 12%, rgba(47, 111, 237, 0.13), transparent 32%),
        radial-gradient(circle at 94% 16%, rgba(15, 157, 88, 0.10), transparent 28%),
        linear-gradient(135deg, #f7faff 0%, #fffdfb 58%, #f5fcf8 100%);
    border: 1px solid rgba(47, 111, 237, 0.16);
    border-radius: 1rem;
    padding: clamp(1rem, 2.6vw, 1.75rem);
    margin-bottom: 0.5rem;
}
.learning-agent-admitted-hero h1 {
    color: #182230;
    font-size: clamp(1.8rem, 4vw, 2.75rem);
    line-height: 1.08;
    margin: 0.35rem 0 0.45rem;
}
.learning-agent-admitted-hero > p {
    color: #3f4a5a;
    margin: 0;
    max-width: 48rem;
}
.learning-agent-admitted-steps {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.65rem;
    align-items: stretch;
    margin-top: 1rem;
}
.learning-agent-card {
    background: rgba(255, 255, 255, 0.80);
    border: 1px solid rgba(80, 95, 120, 0.14);
    border-radius: 0.75rem;
    box-shadow: 0 10px 26px rgba(24, 34, 48, 0.06);
    transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
}
.learning-agent-card:hover {
    border-color: rgba(47, 111, 237, 0.24);
    box-shadow: 0 12px 28px rgba(24, 34, 48, 0.09);
    transform: translateY(-1px);
}
.learning-agent-admitted-step {
    color: #3f4a5a;
    min-height: 7rem;
    padding: 0.7rem 0.8rem;
}
.learning-agent-admitted-step strong {
    color: #2457b8;
    display: block;
    margin-bottom: 0.15rem;
}
.learning-agent-card-marker {
    display: none;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.learning-agent-card-marker) {
    background: rgba(255, 255, 255, 0.80);
    border: 1px solid rgba(80, 95, 120, 0.14);
    border-radius: 0.75rem;
    box-shadow: 0 10px 26px rgba(24, 34, 48, 0.06);
    padding: 1rem 1rem 0.9rem;
    transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.learning-agent-card-marker):hover {
    border-color: rgba(47, 111, 237, 0.24);
    box-shadow: 0 12px 28px rgba(24, 34, 48, 0.09);
    transform: translateY(-1px);
}
@media (max-width: 700px) {
    .learning-agent-hero-top {
        flex-direction: column;
    }
    .learning-agent-hero-account-block {
        align-items: flex-start;
    }
    .learning-agent-hero-account {
        text-align: left;
    }
    .learning-agent-admitted-steps {
        grid-template-columns: 1fr;
    }
}
</style>
"""


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _allowed_emails() -> set[str]:
    raw = _env("LEARNING_AGENT_ALLOWED_EMAILS")
    if not raw:
        return set()
    return {value.strip().lower() for value in raw.split(",") if value.strip()}


def _privacy_contact() -> str | None:
    value = _env("LEARNING_AGENT_PRIVACY_CONTACT")
    return value or None


def _operator_emails() -> set[str]:
    raw = _env("LEARNING_AGENT_OPERATOR_EMAILS")
    if not raw:
        return set()
    return {value.strip().lower() for value in raw.split(",") if value.strip()}


def _auth_mode() -> str:
    return _env("LEARNING_AGENT_AUTH_MODE", "oidc").lower()


def _runtime_root() -> Path:
    return Path(_env("AI_BUILDER_OS_RUNTIME_ROOT", "/data"))


LOCAL_PREVIEW_EMAIL = "preview@learning-agent.local"
LOCAL_PREVIEW_MODE_KEY = "learning-agent-local-preview-mode"
LOCAL_PREVIEW_REQUEST = "request"
LOCAL_PREVIEW_ADMITTED = "admitted"
LOCAL_PREVIEW_OPERATOR = "operator"


def _access_request_log_path() -> Path:
    return _runtime_root() / "learning-agent-access-requests.jsonl"


def _ensure_runtime_root() -> None:
    _runtime_root().mkdir(parents=True, exist_ok=True)


def _load_access_requests() -> list[dict[str, str]]:
    path = _access_request_log_path()
    if not path.exists():
        return []
    records: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(raw, dict):
            records.append({str(key): str(value) for key, value in raw.items()})
    return records


def _append_access_request(email: str, name: str, note: str) -> None:
    _ensure_runtime_root()
    payload = {
        "email": email.strip().lower(),
        "name": name.strip(),
        "note": note.strip(),
        "requested_at": datetime.now(UTC).isoformat(),
        "status": "pending",
    }
    with _access_request_log_path().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def _latest_access_requests_by_email() -> list[dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for record in _load_access_requests():
        email = record.get("email", "").strip().lower()
        if not email:
            continue
        latest[email] = record
    return sorted(
        latest.values(),
        key=lambda item: item.get("requested_at", ""),
        reverse=True,
    )


def _pending_access_requests() -> list[dict[str, str]]:
    allowed = _allowed_emails()
    return [
        item
        for item in _latest_access_requests_by_email()
        if item.get("email", "").strip().lower() not in allowed
    ]


def _clear_login_query_params() -> None:
    try:
        st.query_params.clear()
    except Exception:
        pass


def _user_attr(name: str, default: Any = None) -> Any:
    user = getattr(st, "user", None)
    if user is None:
        return default
    if isinstance(user, dict):
        return user.get(name, default)
    return getattr(user, name, default)


def _is_logged_in() -> bool:
    return bool(_user_attr("is_logged_in", False))


def _sign_out(key: str) -> None:
    if st.button("Sign out", key=key, use_container_width=True):
        _clear_login_query_params()
        if hasattr(st, "logout"):
            st.logout()
        st.rerun()


def _sign_out_href() -> str:
    return "?learning_agent_action=signout"


def _sign_out_link_html() -> str:
    return (
        f'<a class="learning-agent-signout-link" href="{html.escape(_sign_out_href())}">'
        "Sign out</a>"
    )


def _github_repo_url() -> str:
    return "https://github.com/mihadmohamed/ai-builder-os"


def _preview_screenshot_paths() -> tuple[tuple[Path, str], ...]:
    assets_root = _repo_root() / "projects" / "learning-agent" / "assets"
    return (
        (assets_root / "learning-plan-preview.png", "Learning plan overview"),
        (assets_root / "learning-plan-preview-2.png", "Concept family progression"),
        (assets_root / "learning-profile-preview.png", "Learning profile"),
        (assets_root / "current-session-preview.png", "Current learning session"),
    )


def _maybe_handle_signout_request() -> None:
    action = str(st.query_params.get("learning_agent_action", "")).strip().lower()
    if action != "signout":
        return
    _clear_login_query_params()
    if hasattr(st, "logout") and _auth_mode() == "oidc":
        st.logout()
        st.stop()
    st.rerun()


def _render_landing_hero(identity: dict[str, str] | None = None) -> None:
    account_markup = ""
    if identity:
        account_markup = (
            '<div class="learning-agent-hero-account-block">'
            f'<div class="learning-agent-hero-account">{html.escape(identity.get("email", ""))}</div>'
            f"{_sign_out_link_html()}"
            "</div>"
        )
    st.markdown(LANDING_PAGE_STYLE, unsafe_allow_html=True)
    hero_markup = (
        '<div class="learning-agent-landing-hero">'
        '<div class="learning-agent-hero-top">'
        '<div class="learning-agent-pilot-label">Invite-only pilot</div>'
        f"{account_markup}"
        "</div>"
        "<h1>Learn how AI Builder OS works, step by step.</h1>"
        "<p>Build a profile-shaped learning plan, then move through grounded explanations, "
        "clarification, and implementation walkthroughs at your own pace.</p>"
        "</div>"
    )
    st.markdown(hero_markup, unsafe_allow_html=True)


def _render_admitted_hero(identity: dict[str, str]) -> None:
    name = identity.get("name", "").strip()
    heading = f"Welcome back, {name}." if name else "Welcome to your learning workspace."
    st.markdown(LANDING_PAGE_STYLE, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="learning-agent-admitted-hero">
            <div class="learning-agent-hero-top">
                <div class="learning-agent-pilot-label">Admitted learner</div>
                <div class="learning-agent-hero-account-block">
                    <div class="learning-agent-hero-account">{html.escape(identity.get("email", ""))}</div>
                    {_sign_out_link_html()}
                </div>
            </div>
            <h1>{html.escape(heading)}</h1>
            <div class="learning-agent-admitted-steps">
                <div class="learning-agent-card learning-agent-admitted-step">
                    <strong>1 · Profile</strong>
                    Set the context and depth that fit you.
                </div>
                <div class="learning-agent-card learning-agent-admitted-step">
                    <strong>2 · Learning plan</strong>
                    Follow the agent-owned concept sequence.
                </div>
                <div class="learning-agent-card learning-agent-admitted-step">
                    <strong>3 · Learn next</strong>
                    Explain, clarify, and connect ideas to the OS.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _is_local_preview_identity(identity: dict[str, str]) -> bool:
    return _auth_mode() != "oidc" and identity.get("email", "").strip().lower() == LOCAL_PREVIEW_EMAIL


def _local_preview_mode(identity: dict[str, str]) -> str | None:
    if not _is_local_preview_identity(identity):
        return None
    current = st.session_state.get(LOCAL_PREVIEW_MODE_KEY)
    if current not in {LOCAL_PREVIEW_REQUEST, LOCAL_PREVIEW_ADMITTED, LOCAL_PREVIEW_OPERATOR}:
        current = LOCAL_PREVIEW_REQUEST
        st.session_state[LOCAL_PREVIEW_MODE_KEY] = current
    return str(current)


def _render_local_preview_toggle(identity: dict[str, str]) -> None:
    mode = _local_preview_mode(identity)
    if mode is None:
        return
    st.caption("Local review mode")
    selected = st.segmented_control(
        "Review stage",
        options=["Request page", "Admitted app", "Admitted operator"],
        selection_mode="single",
        default=(
            "Request page"
            if mode == LOCAL_PREVIEW_REQUEST
            else "Admitted operator"
            if mode == LOCAL_PREVIEW_OPERATOR
            else "Admitted app"
        ),
        key="learning-agent-local-preview-toggle",
        label_visibility="collapsed",
    )
    next_mode = (
        LOCAL_PREVIEW_REQUEST
        if selected == "Request page"
        else LOCAL_PREVIEW_OPERATOR
        if selected == "Admitted operator"
        else LOCAL_PREVIEW_ADMITTED
    )
    if st.session_state.get(LOCAL_PREVIEW_MODE_KEY) != next_mode:
        st.session_state[LOCAL_PREVIEW_MODE_KEY] = next_mode
        st.rerun()


def _is_operator_view(identity: dict[str, str]) -> bool:
    local_mode = _local_preview_mode(identity)
    if local_mode == LOCAL_PREVIEW_OPERATOR:
        return True
    if local_mode == LOCAL_PREVIEW_ADMITTED:
        return False
    return identity.get("email", "").lower() in _operator_emails()


def _open_learning_preview_dialog(image_path: Path, title: str) -> None:
    @st.dialog(title, width="large")
    def _dialog() -> None:
        st.image(
            str(image_path),
            caption=title,
        )
        st.caption("Preview only. Live tutoring unlocks after admission to the pilot.")

    _dialog()


def _render_learning_preview(image_items: tuple[tuple[Path, str], ...]) -> None:
    st.markdown("### See the learning experience")
    preview_columns = st.columns(2)
    for index, (image_path, title) in enumerate(image_items):
        with preview_columns[index % 2]:
            st.image(
                str(image_path),
                caption=title,
                width=320,
            )
            if st.button(
                f"Enlarge {title}",
                key=f"learning-agent-enlarge-preview-{index}",
                use_container_width=True,
            ):
                _open_learning_preview_dialog(image_path, title)
    st.caption("Preview only. Full live-agent access requires admission.")


def _render_signed_out_shell() -> None:
    _render_landing_hero()
    left_col, right_col = st.columns((1.2, 1))
    with left_col:
        st.markdown("### How it works")
        st.markdown(
            "\n".join(
                [
                    "1. Tell the agent a little about your background and goals.",
                    "2. Get a personalized learning plan through core AI Builder OS concepts.",
                    "3. Use live explanation, clarification, and implementation walkthroughs as you learn.",
                ]
            )
        )
        st.markdown("### Pilot boundary")
        st.markdown(
            "This is an early-access pilot. We keep the live tutoring experience admitted in small cohorts so quality, support, and privacy stay strong."
        )
    with right_col:
        st.markdown("### Sign in")
        st.markdown("Use Google to preview the pilot and access the full experience if your account is admitted.")
        if hasattr(st, "login"):
            if st.button("Continue with Google", key="learning-agent-login", use_container_width=True):
                st.login()
        else:
            st.warning("This deployment does not expose Streamlit OIDC login yet.")
        contact = _privacy_contact()
        if contact:
            st.caption(f"Questions or access requests: {contact}")


def _render_pending_access_preview(identity: dict[str, str], privacy_contact: str | None) -> None:
    _render_landing_hero(identity)
    _render_local_preview_toggle(identity)

    intro_col, access_col = st.columns((1.15, 1))
    with intro_col:
        st.markdown("### What this pilot does")
        st.markdown(
            "\n".join(
                [
                    "- builds a personalized learning plan from your profile",
                    "- teaches core AI Builder OS concepts step by step",
                    "- offers live clarification and implementation walkthroughs for admitted pilot users",
                ]
            )
        )
        st.markdown("### What approved users get")
        st.markdown(
            "\n".join(
                [
                    "- private saved progress and session history",
                    "- agent-owned learning progression",
                    "- live tutoring, clarification, and \"See it in the OS\" grounding",
                ]
            )
        )
        st.markdown("### What is AI Builder OS?")
        st.markdown(
            "AI Builder OS is the working system behind this tutor: a grounded operating environment for learning, building, and understanding agent workflows in practice."
        )
        st.markdown(f"[View the AI Builder OS repository]({_github_repo_url()})")
        st.markdown("### How access works")
        st.markdown(
            "\n".join(
                [
                    "1. Sign in with Google",
                    "2. Get admitted to the current pilot cohort",
                    "3. Return to unlock the full hosted Learning Agent",
                ]
            )
        )

    with access_col:
        with st.container(border=True):
            st.markdown('<span class="learning-agent-card-marker"></span>', unsafe_allow_html=True)
            st.markdown("### Request access")
            st.markdown(
                "You can preview the pilot now. Tell us how you want to use it and we’ll review your request for an upcoming cohort."
            )
            with st.form("learning-agent-access-request"):
                st.text_input("Google account", value=identity.get("email", ""), disabled=True)
                note = st.text_area(
                    "How do you want to use the Learning Agent?",
                    placeholder="A sentence or two is enough.",
                    key="learning-agent-access-note",
                    height=120,
                )
                submitted = st.form_submit_button("Request access", use_container_width=True, type="primary")

        screenshots = [
            (path, title)
            for path, title in _preview_screenshot_paths()
            if path.exists()
        ]
        if screenshots:
            with st.container(border=True):
                st.markdown('<span class="learning-agent-card-marker"></span>', unsafe_allow_html=True)
                _render_learning_preview(tuple(screenshots))

    if submitted:
        clean_note = note.strip()
        if not clean_note:
            st.warning("Please add a short note so we know how you want to use the Learning Agent.")
        else:
            _append_access_request(identity.get("email", ""), identity.get("name", ""), clean_note)
            st.success("Request received. We’ll review it in a small pilot wave and admit your account if it fits the current cohort.")
            if privacy_contact:
                st.caption(f"If needed, you can also reach us at {privacy_contact}.")


def _authenticated_identity() -> dict[str, str] | None:
    _maybe_handle_signout_request()
    if _auth_mode() != "oidc":
        local_email = _env("LEARNING_AGENT_LOCAL_USER", "local@learning-agent")
        identity = {"email": local_email, "name": "Local User"}
    else:
        if not _is_logged_in():
            _render_signed_out_shell()
            st.stop()

        identity = {
            "email": str(_user_attr("email", "") or ""),
            "name": str(_user_attr("name", "") or ""),
        }
    privacy_contact = _privacy_contact()
    local_preview_mode = _local_preview_mode(identity)
    if local_preview_mode == LOCAL_PREVIEW_REQUEST:
        _render_pending_access_preview(identity, privacy_contact)
        st.stop()
    if local_preview_mode in {LOCAL_PREVIEW_ADMITTED, LOCAL_PREVIEW_OPERATOR}:
        return identity

    allowed_emails = _allowed_emails()
    if allowed_emails and identity["email"].lower() not in allowed_emails:
        _render_pending_access_preview(identity, privacy_contact)
        st.stop()
    return identity


def _render_authenticated_shell(identity: dict[str, str]) -> None:
    _render_admitted_hero(identity)
    _render_local_preview_toggle(identity)

    if _is_operator_view(identity):
        pending_requests = _pending_access_requests()
        with st.expander(f"Pilot access requests ({len(pending_requests)})", expanded=False):
            st.caption(
                "Thin operator review loop: add an approved email to `LEARNING_AGENT_ALLOWED_EMAILS` in Railway, then redeploy. Requests disappear from this list automatically once the email is admitted."
            )
            if not pending_requests:
                st.success("No pending access requests right now.")
            else:
                for request in pending_requests:
                    st.markdown(f"**{request.get('email', '')}**")
                    requested_at = request.get("requested_at", "")
                    if requested_at:
                        st.caption(f"Requested at {requested_at}")
                    note = request.get("note", "").strip()
                    if note:
                        st.write(note)
                    st.divider()


def main() -> None:
    st.set_page_config(
        page_title="AI Builder Learning Agent",
        page_icon=":material/school:",
        layout="wide",
    )
    if SECTION_STYLE:
        st.markdown(SECTION_STYLE, unsafe_allow_html=True)

    identity = _authenticated_identity()
    if identity is None:
        return

    token = set_active_user(identity.get("email", ""))
    try:
        _render_authenticated_shell(identity)
        render_learning_tab()
    finally:
        reset_active_user(token)


if __name__ == "__main__":
    main()
