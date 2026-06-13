from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[3]
OS_CONTROL_SRC = REPO_ROOT / "projects" / "os-control-panel" / "src"
if str(OS_CONTROL_SRC) not in sys.path:
    sys.path.insert(0, str(OS_CONTROL_SRC))

os.environ.setdefault("AI_BUILDER_OS_LEARNING_RELEASE_PROFILE", "external_v2")

from tenancy import reset_active_user, set_active_user  # noqa: E402


def _load_os_control_panel_app() -> object:
    module_name = "os_control_panel_streamlit_app"
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = OS_CONTROL_SRC / "app.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load os-control-panel app module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_OS_CONTROL_APP = _load_os_control_panel_app()
SECTION_STYLE = _OS_CONTROL_APP.SECTION_STYLE
render_learning_tab = _OS_CONTROL_APP.render_learning_tab


AUTH_MODE_ENV = "LEARNING_AGENT_AUTH_MODE"
LOCAL_USER_ENV = "LEARNING_AGENT_LOCAL_USER"
ALLOWED_EMAILS_ENV = "LEARNING_AGENT_ALLOWED_EMAILS"
PRIVACY_CONTACT_ENV = "LEARNING_AGENT_PRIVACY_CONTACT"


def _privacy_contact() -> str:
    return os.getenv(PRIVACY_CONTACT_ENV, "").strip()


def _authenticated_identity() -> tuple[str, str]:
    auth_mode = os.getenv(AUTH_MODE_ENV, "local").strip().lower()
    if auth_mode != "oidc":
        local_user = os.getenv(LOCAL_USER_ENV, "local-pilot-user").strip() or "local-pilot-user"
        return local_user, "Local pilot"

    if not getattr(st.user, "is_logged_in", False):
        st.title("AI Builder Learning Agent")
        st.caption("Invite-only pilot")
        st.write("Sign in to continue your private concept-learning workspace.")
        with st.container(border=True):
            st.markdown("**How this works**")
            st.write("Set your profile, follow the guided learning plan, and stay with one concept at a time until it feels durable.")
            st.write("This pilot stores your learning progress under your own account and does not expose the wider AI Builder OS.")
            contact = _privacy_contact()
            if contact:
                st.caption(f"Questions about access or privacy: {contact}")
        if st.button("Sign in", type="primary"):
            st.login()
        st.stop()

    identity = str(st.user.get("sub") or st.user.get("email") or "").strip()
    if not identity:
        st.error("Your identity provider did not return a stable user identifier.")
        st.stop()
    display_name = str(st.user.get("name") or st.user.get("email") or "Signed-in learner")
    allowed_emails = {
        item.strip().lower()
        for item in os.getenv(ALLOWED_EMAILS_ENV, "").split(",")
        if item.strip()
    }
    email = str(st.user.get("email") or "").strip().lower()
    if allowed_emails and email not in allowed_emails:
        st.error("This private pilot is currently invite-only.")
        contact = _privacy_contact()
        if contact:
            st.caption(f"If you expected access, contact: {contact}")
        if st.button("Sign out"):
            st.logout()
        st.stop()
    return identity, display_name


def main() -> None:
    st.set_page_config(page_title="AI Builder Learning Agent", layout="wide")
    st.markdown(SECTION_STYLE, unsafe_allow_html=True)
    identity, display_name = _authenticated_identity()
    user_token = set_active_user(identity)
    try:
        header_left, header_right = st.columns([0.75, 0.25])
        with header_left:
            st.title("AI Builder Learning Agent")
            st.caption("Build practical AI product fluency through focused teaching, clarification, and concept progression.")
            st.caption("Invite-only pilot")
        with header_right:
            st.caption(display_name)
            if os.getenv(AUTH_MODE_ENV, "local").strip().lower() == "oidc":
                if st.button("Sign out"):
                    st.logout()
        with st.container(border=True):
            intro_left, intro_right = st.columns([0.65, 0.35])
            with intro_left:
                st.markdown("**How it works**")
                st.write("1. Set your profile so the tutor knows how to teach you.")
                st.write("2. Follow the learning plan so the agent can take you through the right concepts in order.")
                st.write("3. Use `Learn next` to stay with one concept, clarify it, inspect it in the OS, and mark it learned.")
            with intro_right:
                st.markdown("**Pilot boundary**")
                st.write("Your progress is private to your account. This pilot is focused only on the Learning Agent experience.")
        with st.expander("Privacy and data", expanded=False):
            st.write(
                "Your learning profile, concept progress, active session, and agent traces are stored "
                "under your authenticated user identity. They are not shared with other learners."
            )
            st.write(
                "Learning prompts and responses are processed through the configured OpenAI API account. "
                "Do not enter secrets, regulated data, or information you are not authorized to share."
            )
            privacy_contact = _privacy_contact()
            if privacy_contact:
                st.caption(f"Data access or deletion requests: {privacy_contact}")
        render_learning_tab()
    finally:
        reset_active_user(user_token)


if __name__ == "__main__":
    main()
