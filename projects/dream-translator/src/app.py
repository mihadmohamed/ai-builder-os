from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from dream_analyzer import STYLE_DESCRIPTIONS, analyze_dream, format_insight_count


def render_result(result: dict) -> None:
    for warning in result.get("warnings", []):
        st.warning(warning)

    if not result.get("ready"):
        st.info(result["summary"])
        return

    visual = result["visual"]
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.image(visual["svg"], caption=visual["alt_text"], use_container_width=True)
        st.caption(f"Style: {visual['style']}")

    with right:
        st.success("Dream translation complete.")
        st.markdown("### Interpretation")
        st.write(result["summary"])
        st.metric("Insight depth", format_insight_count(result))

        for insight in result["insights"]:
            st.markdown(f"**{insight['label']}**")
            st.write(insight["text"])

    with st.expander("Image prompt"):
        st.write(visual["image_prompt"])

    with st.expander("Structured output"):
        st.json(result, expanded=False)


def main() -> None:
    st.set_page_config(
        page_title="Dream Translator",
        page_icon="🌙",
        layout="wide",
    )

    st.title("Dream Translator")
    st.write("Describe a dream to receive a respectful interpretation and an artistic visual representation.")

    with st.form("dream_translation_form"):
        dream_text = st.text_area(
            "Dream description",
            height=220,
            placeholder=(
                "Example: I was walking through a flooded house at night, "
                "following a glowing door while hearing waves outside."
            ),
        )
        style = st.selectbox("Visual style", options=sorted(STYLE_DESCRIPTIONS))
        submitted = st.form_submit_button("Translate dream", use_container_width=True)

    if submitted:
        st.session_state["dream_translation_result"] = analyze_dream(dream_text, style)

    result = st.session_state.get("dream_translation_result")
    if result:
        render_result(result)
    else:
        st.info("Your interpretation and visual representation will appear here after submission.")


if __name__ == "__main__":
    main()
