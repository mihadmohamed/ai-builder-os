from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from advisor import analyze_career_fit, format_gap_summary


def render_gap(gap: dict, index: int) -> None:
    with st.container(border=True):
        st.subheader(f"{index}. {gap['skill']}")
        st.caption(f"Importance: {gap['importance']}")
        st.write(gap["cv_evidence"])
        st.write(gap["target_job_evidence"])
        st.markdown("**Recommended action**")
        st.write(gap["recommended_action"])
        st.markdown("**Resource**")
        st.write(gap["recommended_resource"])


def render_result(result: dict) -> None:
    for warning in result.get("warnings", []):
        st.warning(warning)

    if not result.get("ready"):
        st.info(result["summary"])
        return

    st.success("Analysis complete.")
    st.markdown("### Summary")
    st.write(result["summary"])
    st.metric("Gap analysis", format_gap_summary(result))

    gaps = result.get("gaps", [])
    if gaps:
        st.markdown("### Priority gaps")
        for index, gap in enumerate(gaps, start=1):
            render_gap(gap, index)
    else:
        st.info("No skill gaps were identified from the current inputs.")

    if result.get("development_plan"):
        st.markdown("### Development plan")
        for item in result["development_plan"]:
            st.markdown(f"**{item['focus_area']}**")
            st.write(item["next_step"])
            st.caption(item["resource"])

    with st.expander("Structured output"):
        st.json(result, expanded=True)


def main() -> None:
    st.set_page_config(
        page_title="Career Guidance Advisor",
        page_icon="🎯",
        layout="wide",
    )

    st.title("Career Guidance Advisor")
    st.write("Paste your CV and target job descriptions to find role-specific gaps and next steps.")

    with st.form("career_guidance_form"):
        cv_text = st.text_area("CV text", height=260, placeholder="Paste your CV text here.")
        target_jobs = st.text_area(
            "Target job descriptions",
            height=260,
            help=(
                "Paste one job posting or several postings into this same field. "
                "Separate each posting with a blank line or a line containing ---."
            ),
            placeholder=(
                "Posting 1: Paste the first target job description here.\n\n"
                "---\n\n"
                "Posting 2: Paste another target job description here."
            ),
        )
        submitted = st.form_submit_button("Analyze career fit", use_container_width=True)

    if submitted:
        st.session_state["career_guidance_result"] = analyze_career_fit(cv_text, target_jobs)

    result = st.session_state.get("career_guidance_result")
    if result:
        render_result(result)
    else:
        st.info("Your analysis will appear here after submission.")


if __name__ == "__main__":
    main()
