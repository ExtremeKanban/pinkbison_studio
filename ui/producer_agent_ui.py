import streamlit as st

from agents.producer import ProducerAgent
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session


def render_producer_agent_panel(project_name: str):
    """
    Producer Agent UI — single entry point for autonomous workflows:
    - Story Bible
    - Single Chapter
    - Full Story
    - Director Mode
    """

    st.header("Producer Agent (Autonomous Director)")

    # ---------------------------------------------------------
    # Instructions Section
    # ---------------------------------------------------------
    with st.expander("Instructions: How to Use the Producer Agent"):
        st.markdown("""
### Recommended Workflow

**1. Start in Draft Mode**
- Uses the fast model for everything.
- Generate a full story quickly.
- Great for exploration and rapid iteration.

**2. Review the Draft**
- Read outline, world, characters, and chapters.
- Decide what needs more depth or polish.

**3. Switch to High‑Quality Mode**
- Uses the big model for planning, continuity, and editing.
- Regenerate chapters or run Director Mode for a prestige pass.

**4. Final Polish**
- Run Director Mode again in High‑Quality Mode.
- Produces the most coherent, polished version of your story.
        """)

    # ---------------------------------------------------------
    # Seed idea
    # ---------------------------------------------------------
    st.text_area(
        "Seed idea for the Producer Agent",
        key="producer_seed_idea",
        height=120,
        help="High-level story concept. The Producer will use this to build outline, world, characters, and chapters.",
    )

    # ---------------------------------------------------------
    # Model Mode Toggle
    # ---------------------------------------------------------
    model_mode = st.radio(
        "Model Mode",
        options=["draft", "high_quality"],
        format_func=lambda x: {
            "draft": "Draft Mode — Fast model for everything",
            "high_quality": "High‑Quality Mode — Big model for planning, continuity, editing",
        }[x],
        key="producer_model_mode",
    )

    # ---------------------------------------------------------
    # Goal mode
    # ---------------------------------------------------------
    goal_mode = st.selectbox(
        "Goal",
        options=["story_bible", "chapter", "full_story", "director"],
        format_func=lambda x: {
            "story_bible": "Generate Story Bible",
            "chapter": "Generate Single Chapter",
            "full_story": "Generate Full Story",
            "director": "Director Mode (Autonomous)",
        }[x],
        key="producer_goal_mode",
    )

    # ---------------------------------------------------------
    # Project settings
    # ---------------------------------------------------------
    genre = st.session_state.get("project_genre", "")
    tone = st.session_state.get("project_tone", "")
    themes = st.session_state.get("project_themes", "")
    setting = st.session_state.get("project_setting", "")

    st.subheader("Project Context")
    st.write(f"**Genre:** {genre}")
    st.write(f"**Tone:** {tone}")
    st.write(f"**Themes:** {themes}")
    st.write(f"**Setting:** {setting}")

    # ---------------------------------------------------------
    # Automation Options
    # ---------------------------------------------------------
    st.subheader("Automation Options")

    auto_memory = st.checkbox(
        "Auto-store facts in memory",
        value=True,
        key="producer_auto_memory",
    )
    run_continuity = st.checkbox(
        "Run Continuity checks",
        value=True,
        key="producer_run_continuity",
    )
    run_editor = st.checkbox(
        "Run Editor polish",
        value=True,
        key="producer_run_editor",
    )
    max_chapters = st.number_input(
        "Max chapters (for full story / director)",
        min_value=1,
        max_value=100,
        value=20,
        key="producer_max_chapters",
    )

    if goal_mode == "chapter":
        chapter_index = st.number_input(
            "Chapter index (0 = first chapter)",
            min_value=0,
            max_value=99,
            value=0,
            key="producer_chapter_index",
        )
    else:
        chapter_index = 0

    # ---------------------------------------------------------
    # Run button
    # ---------------------------------------------------------
    run_button = st.button("Run Producer Pipeline")

    # Output placeholders
    progress_placeholder = st.empty()
    output_placeholder = st.empty()

    if run_button:
        seed = st.session_state["producer_seed_idea"].strip()
        if not seed:
            st.info("Provide a seed idea for the Producer Agent.")
            return

        agent = ProducerAgent(
            project_name=project_name,
            model_mode=model_mode,   # <-- NEW
        )

        with st.spinner("Running Producer Agent pipeline..."):
            if goal_mode == "story_bible":
                result = agent.run_story_bible_pipeline(
                    idea=seed,
                    genre=genre,
                    tone=tone,
                    themes=themes,
                    setting=setting,
                    auto_memory=auto_memory,
                )
            elif goal_mode == "chapter":
                result = agent.run_chapter_pipeline(
                    idea=seed,
                    genre=genre,
                    tone=tone,
                    themes=themes,
                    setting=setting,
                    auto_memory=auto_memory,
                    run_continuity=run_continuity,
                    run_editor=run_editor,
                    chapter_index=int(chapter_index),
                    max_chapters=int(max_chapters),
                )
            elif goal_mode == "full_story":
                result = agent.run_full_story_pipeline(
                    idea=seed,
                    genre=genre,
                    tone=tone,
                    themes=themes,
                    setting=setting,
                    auto_memory=auto_memory,
                    run_continuity=run_continuity,
                    run_editor=run_editor,
                    max_chapters=int(max_chapters),
                )
            else:  # director
                result = agent.run_director_mode(
                    idea=seed,
                    genre=genre,
                    tone=tone,
                    themes=themes,
                    setting=setting,
                    auto_memory=auto_memory,
                    run_continuity=run_continuity,
                    run_editor=run_editor,
                    max_chapters=int(max_chapters),
                    max_revision_passes=2,
                )

        # Save into session & project
        st.session_state["producer_last_result"] = result
        save_project_state(project_name, extract_state_from_session())

        # ---------------------------------------------------------
        # Output Rendering
        # ---------------------------------------------------------
        with output_placeholder.container():
            st.subheader("Producer Outputs")

            # Story bible parts
            if "outline" in result:
                with st.expander("Outline", expanded=(goal_mode == "story_bible")):
                    st.write(result["outline"])
                    st.session_state["pipeline_outline"] = result["outline"]
            if "world" in result:
                with st.expander("World Bible", expanded=(goal_mode == "story_bible")):
                    st.write(result["world"])
                    st.session_state["pipeline_world"] = result["world"]
            if "characters" in result:
                with st.expander("Character Bible", expanded=(goal_mode == "story_bible")):
                    st.write(result["characters"])
                    st.session_state["pipeline_characters"] = result["characters"]

            # Chapter / story outputs
            if goal_mode == "chapter" and "chapter" in result:
                ch = result["chapter"]
                with st.expander(f"Chapter {result.get('chapter_index', 0) + 1}", expanded=True):
                    st.subheader("Raw")
                    st.write(ch["raw"])
                    st.subheader("After Continuity")
                    st.write(ch["after_continuity"])
                    st.subheader("Final")
                    st.write(ch["final"])

            if goal_mode in ("full_story", "director"):
                chapters = result.get("chapters", [])
                if chapters:
                    with st.expander("Chapters (final)", expanded=True):
                        for idx, ch in enumerate(chapters):
                            st.markdown(f"### Chapter {idx + 1}: {ch.get('title', 'Untitled')}")
                            st.write(ch["final"])

                full_story = result.get("full_story")
                if full_story:
                    with st.expander("Full Story (combined)", expanded=False):
                        st.text_area(
                            "Full Story",
                            value=full_story,
                            height=400,
                        )

            st.success("Producer Agent pipeline complete.")
