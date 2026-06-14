from __future__ import annotations

import json
import importlib.util
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

import streamlit as st


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_os_control_panel_app() -> ModuleType:
    src_root = _repo_root() / "projects" / "os-control-panel" / "src"
    app_path = src_root / "app.py"
    src_root_str = str(src_root)
    if src_root_str not in sys.path:
        sys.path.insert(0, src_root_str)
    spec = importlib.util.spec_from_file_location("os_control_panel_learning_app", app_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load canonical learning app from {app_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CANONICAL_APP = _load_os_control_panel_app()
SECTION_STYLE = getattr(_CANONICAL_APP, "SECTION_STYLE", "")
render_learning_tab = getattr(_CANONICAL_APP, "render_learning_tab")


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


def _pilot_badge() -> None:
    st.caption("Invite-only pilot")


def _pilot_shell_header() -> None:
    _pilot_badge()
    st.title("AI Builder Learning Agent")
    st.write(
        "Start with your profile, then let the learning agent guide you through a personalized concept plan."
    )


def _render_signed_out_shell() -> None:
    _pilot_shell_header()
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
    _pilot_shell_header()
    st.info(f"Signed in as `{identity.get('email', '')}`")

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

    with access_col:
        st.markdown("### Access status")
        st.markdown(
            "You can preview the pilot now. Full live-agent access is still being opened in deliberate small cohorts."
        )
        st.markdown("### Request access")
        st.markdown("Send a short request from this page and we’ll review it in the next pilot wave.")

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

    st.caption(
        "This preview page is intentional. It lets us show the product before approval without opening unrestricted live-agent usage."
    )
    with st.form("learning-agent-access-request"):
        st.text_input("Google account", value=identity.get("email", ""), disabled=True)
        note = st.text_area(
            "How do you want to use the Learning Agent?",
            placeholder="A sentence or two is enough.",
            key="learning-agent-access-note",
        )
        submitted = st.form_submit_button("Request access", use_container_width=True)
    if submitted:
        clean_note = note.strip()
        if not clean_note:
            st.warning("Please add a short note so we know how you want to use the Learning Agent.")
        else:
            _append_access_request(identity.get("email", ""), identity.get("name", ""), clean_note)
            st.success("Request received. We’ll review it in a small pilot wave and admit your account if it fits the current cohort.")
            if privacy_contact:
                st.caption(f"If needed, you can also reach us at {privacy_contact}.")
    _sign_out("learning-agent-signout-preview")


def _authenticated_identity() -> dict[str, str] | None:
    if _auth_mode() != "oidc":
        local_email = _env("LEARNING_AGENT_LOCAL_USER", "local@learning-agent")
        return {"email": local_email, "name": "Local User"}

    if not _is_logged_in():
        _render_signed_out_shell()
        st.stop()

    identity = {
        "email": str(_user_attr("email", "") or ""),
        "name": str(_user_attr("name", "") or ""),
    }
    allowed_emails = _allowed_emails()
    privacy_contact = _privacy_contact()
    if allowed_emails and identity["email"].lower() not in allowed_emails:
        _render_pending_access_preview(identity, privacy_contact)
        st.stop()
    return identity


def _render_authenticated_shell(identity: dict[str, str]) -> None:
    _pilot_badge()
    header_col, action_col = st.columns((1.25, 1))
    with header_col:
        st.title("AI Builder Learning Agent")
        st.write("Profile first, then follow the guided learning plan and continue learning step by step.")
    with action_col:
        st.caption(identity.get("email", ""))
        _sign_out("learning-agent-signout-active")

    st.markdown("### How it works")
    st.markdown(
        "\n".join(
            [
                "- Set your profile so the tutor can adapt depth and framing.",
                "- Follow the learning plan rather than browsing concepts freely.",
                "- Use Learn next for explanation, clarification, and implementation grounding.",
            ]
        )
    )

    st.markdown("### Pilot boundary")
    st.markdown(
        "This hosted pilot is a focused external surface around the canonical learning engine in AI Builder OS."
    )
    if identity.get("email", "").lower() in _operator_emails():
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

    _render_authenticated_shell(identity)
    render_learning_tab()


if __name__ == "__main__":
    main()
