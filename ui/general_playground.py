import streamlit as st
from models.fast_model_client import chat_fast
from models.heavy_model import generate_with_heavy_model


def render_general_playground(project_name):
    st.header("General Prompt Playground")

    st.text_area(
        "Enter a general prompt for ad-hoc model calls",
        key="general_prompt",
    )

    col_fast, col_heavy = st.columns(2)

    with col_fast:
        if st.button("Run Fast Model (3B)"):
            prompt = st.session_state["general_prompt"].strip()
            if prompt:
                result = chat_fast([{"role": "user", "content": prompt}])
                st.subheader("Fast Model Output")
                st.write(result)
            else:
                st.info("Enter a prompt above to use the fast model.")

    with col_heavy:
        if st.button("Run Creative Model (7B)"):
            prompt = st.session_state["general_prompt"].strip()
            if prompt:
                result = generate_with_heavy_model(prompt, max_new_tokens=300)
                st.subheader("Creative Model Output")
                st.write(result)
            else:
                st.info("Enter a prompt above to use the creative model.")

    st.markdown("---")
