from __future__ import annotations

import base64
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
from workspace import learning_operator_dashboard_snapshot, record_learning_login  # noqa: E402


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
.learning-agent-preview-card-anchor {
    display: none;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.learning-agent-preview-card-anchor) {
    overflow: hidden;
    position: relative;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.learning-agent-preview-card-anchor) div[data-testid="stButton"] {
    inset: 0;
    margin: 0;
    position: absolute;
    z-index: 3;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.learning-agent-preview-card-anchor) div[data-testid="stButton"] > button {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    color: transparent !important;
    cursor: pointer;
    height: 100%;
    margin: 0;
    min-height: 100%;
    padding: 0;
    width: 100%;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.learning-agent-preview-card-anchor):hover {
    border-color: rgba(47, 111, 237, 0.22);
    box-shadow: 0 14px 30px rgba(24, 34, 48, 0.08);
}
.learning-agent-preview-caption {
    color: #536174;
    font-size: 0.95rem;
    line-height: 1.35;
    margin-top: 0.55rem;
    text-align: center;
}
.learning-agent-preview-frame {
    align-items: center;
    display: flex;
    height: 9.75rem;
    justify-content: center;
    overflow: hidden;
}
.learning-agent-preview-image {
    display: block;
    height: auto;
    max-height: 100%;
    max-width: 100%;
    object-fit: contain;
    width: 100%;
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


def _daily_turn_limit(env_name: str, default: int) -> int:
    raw = _env(env_name)
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(1, value)


def _standard_daily_turn_limit() -> int:
    return _daily_turn_limit("LEARNING_AGENT_STANDARD_DAILY_TURNS", 10)


def _trusted_daily_turn_limit() -> int:
    return _daily_turn_limit("LEARNING_AGENT_TRUSTED_DAILY_TURNS", 30)


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
ACCESS_REQUEST_FEEDBACK_KEY = "learning-agent-access-request-feedback"
ACCESS_REQUEST_EMAIL_KEY = "learning-agent-access-request-email"
LOGIN_RECORDED_STATE_KEY = "learning-agent-login-recorded-email"


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


def _latest_pending_request_for_email(email: str) -> dict[str, str] | None:
    normalized = email.strip().lower()
    if not normalized:
        return None
    allowed = _allowed_emails()
    if normalized in allowed:
        return None
    for item in _latest_access_requests_by_email():
        if item.get("email", "").strip().lower() == normalized:
            return item
    return None


def _looks_like_email(value: str) -> bool:
    email = value.strip()
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        return False
    local, _, domain = email.partition("@")
    return bool(local.strip() and domain.strip())


def _render_pending_request_state(request: dict[str, str], privacy_contact: str | None) -> None:
    st.markdown("### Request sent")
    st.success("Your access request has been sent and is awaiting approval.")
    requested_at = request.get("requested_at", "").strip()
    if requested_at:
        st.caption(f"Requested at {requested_at}")
    note = request.get("note", "").strip()
    if note:
        st.markdown("**Your note**")
        st.write(note)
    if privacy_contact:
        st.caption(f"Questions? You can also reach us at {privacy_contact}.")


def _render_preview_intro() -> None:
    st.markdown("### What this pilot does")
    st.markdown(
        "\n".join(
            [
                "- builds a personalized learning plan from your profile",
                "- teaches core AI Builder OS concepts step by step",
                "- offers live clarification and implementation walkthroughs inside a bounded daily usage limit",
            ]
        )
    )
    st.markdown("### What the learning experience includes")
    st.markdown(
        "\n".join(
            [
                "- private saved progress and session history",
                "- agent-owned learning progression",
                '- live tutoring, clarification, and "See it in the OS" grounding',
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
                f"2. Start learning immediately with {_standard_daily_turn_limit()} live turns per day",
                f"3. Earlier admitted pilot users keep a higher trusted limit of {_trusted_daily_turn_limit()} turns per day",
            ]
        )
    )


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


def _image_data_uri(path: Path) -> str:
    suffix = path.suffix.lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _preview_screenshot_paths() -> tuple[tuple[Path, str], ...]:
    assets_root = _repo_root() / "projects" / "learning-agent" / "assets"
    return (
        (assets_root / "learning-profile-preview.png", "Learning profile"),
        (assets_root / "learning-plan-preview-2.png", "Learning plan"),
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

    _dialog()


def _render_learning_preview(image_items: tuple[tuple[Path, str], ...]) -> None:
    st.markdown("### See the learning experience")
    preview_columns = st.columns(len(image_items))
    for index, (image_path, title) in enumerate(image_items):
        with preview_columns[index]:
            with st.container(border=True):
                st.markdown('<span class="learning-agent-preview-card-anchor"></span>', unsafe_allow_html=True)
                st.markdown(
                    (
                        '<div class="learning-agent-preview-frame">'
                        '<img class="learning-agent-preview-image" src="'
                        + _image_data_uri(image_path)
                        + '" alt="'
                        + html.escape(title)
                        + '" />'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="learning-agent-preview-caption">{html.escape(title)}</div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    f"Open {title}",
                    key=f"learning-agent-enlarge-preview-{index}",
                    use_container_width=True,
                ):
                    _open_learning_preview_dialog(image_path, title)


def _render_signed_out_access_card() -> None:
    with st.container(border=True):
        st.markdown('<span class="learning-agent-card-marker"></span>', unsafe_allow_html=True)
        contact = _privacy_contact()
        st.markdown("### Explore first")
        st.markdown(
            "You can review the product framing and preview the learning experience without signing in first."
        )
        st.caption(
            f"When you are ready to start, Google sign-in unlocks open access with **{_standard_daily_turn_limit()} live turns per day**. "
            f"Earlier admitted pilot users keep a **trusted limit of {_trusted_daily_turn_limit()} turns per day**."
        )
        if contact:
            st.caption(f"Questions or pilot notes: {contact}")


def _render_signed_out_start_card() -> None:
    with st.container(border=True):
        st.markdown('<span class="learning-agent-card-marker"></span>', unsafe_allow_html=True)
        st.markdown("### Ready to start learning?")
        st.markdown(
            f"Sign in with Google to save your profile and use up to **{_standard_daily_turn_limit()} live turns per day**."
        )
        st.caption(
            "If you opened this from LinkedIn or another in-app browser, open the page in Safari or Chrome before signing in. Google blocks sign-in from some embedded browsers."
        )
        if hasattr(st, "login"):
            if st.button("Start learning with Google", key="learning-agent-login", use_container_width=True, type="primary"):
                st.login()
        else:
            st.warning("This deployment does not expose Streamlit OIDC login yet.")


def _render_signed_out_shell() -> None:
    _render_landing_hero()
    _render_signed_out_access_card()
    left_col, right_col = st.columns((1.15, 1))
    with left_col:
        _render_preview_intro()
    with right_col:
        screenshots = [
            (path, title)
            for path, title in _preview_screenshot_paths()
            if path.exists()
        ]
        if screenshots:
            with st.container(border=True):
                st.markdown('<span class="learning-agent-card-marker"></span>', unsafe_allow_html=True)
                _render_learning_preview(tuple(screenshots))
    _render_signed_out_start_card()


def _render_pending_access_preview(identity: dict[str, str], privacy_contact: str | None) -> None:
    _render_landing_hero(identity)
    _render_local_preview_toggle(identity)
    existing_request = _latest_pending_request_for_email(identity.get("email", ""))

    intro_col, access_col = st.columns((1.15, 1))
    with intro_col:
        _render_preview_intro()

    with access_col:
        with st.container(border=True):
            st.markdown('<span class="learning-agent-card-marker"></span>', unsafe_allow_html=True)
            if existing_request:
                _render_pending_request_state(existing_request, privacy_contact)
                submitted = False
            else:
                st.markdown("### Request access")
                st.markdown(
                    "You can preview the pilot now. Tell us how you want to use it and we’ll review your request for an upcoming cohort."
                )
                feedback = st.session_state.pop(ACCESS_REQUEST_FEEDBACK_KEY, None)
                if feedback:
                    st.success(feedback)
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
            st.session_state[ACCESS_REQUEST_FEEDBACK_KEY] = (
                "Request sent. We’ll review it in a small pilot wave and admit your account if it fits the current cohort."
            )
            st.rerun()


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
    return identity


def _render_authenticated_shell(identity: dict[str, str]) -> None:
    _render_admitted_hero(identity)
    _render_local_preview_toggle(identity)
    login_key = f"{LOGIN_RECORDED_STATE_KEY}::{identity.get('email', '').strip().lower()}"
    if not st.session_state.get(login_key):
        record_learning_login()
        st.session_state[login_key] = True

    if _is_operator_view(identity):
        snapshot = learning_operator_dashboard_snapshot()
        with st.expander("Operator dashboard", expanded=False):
            metric_cols = st.columns(5)
            metric_cols[0].metric("Users seen", snapshot.total_users)
            metric_cols[1].metric("Active today", snapshot.active_today)
            metric_cols[2].metric("Active 7d", snapshot.active_last_7d)
            metric_cols[3].metric("Live turns today", snapshot.live_turns_today)
            metric_cols[4].metric("Limit hits today", snapshot.rate_limit_hits_today)
            if snapshot.users:
                st.dataframe(
                    [
                        {
                            "Email": item.user_email,
                            "Tier": item.tier,
                            "Last active": item.last_active_at,
                            "Used today": item.live_turns_today,
                            "Left today": item.turns_remaining_today,
                            "Learned": item.concepts_learned,
                            "Current concept": item.current_concept or "—",
                        }
                        for item in snapshot.users
                    ],
                    use_container_width=True,
                )
            pending_requests = _pending_access_requests()
            if pending_requests:
                st.markdown("**Legacy access requests**")
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
