"""
Producer Agent UI with Phase 1 real-time controls.
"""

import streamlit as st

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agents.producer import ProducerAgent

from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session


def render_producer_agent_panel(producer):
    """
    Producer Agent UI — single entry point for autonomous workflows:
    - Story Bible
    - Single Chapter
    - Full Story
    - Director Mode
    
    Args:
        producer: ProducerAgent instance
    """
    # Get project name from producer
    project_name = producer.project_name
    
    # Clean up bad session state values (from old code)
    for key in ["producer_auto_memory", "producer_run_continuity", "producer_run_editor"]:
        if key in st.session_state and not isinstance(st.session_state[key], bool):
            del st.session_state[key]
    
    for key in ["producer_max_chapters", "producer_chapter_index"]:
        if key in st.session_state and not isinstance(st.session_state[key], int):
            del st.session_state[key]
            
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
    # Real-Time Pipeline Controls (PHASE 1)
    # ---------------------------------------------------------
    st.subheader("⏱️ Real-Time Controls")
    
    try:
        from ui.pipeline_controls_ui import render_pipeline_controls
        render_pipeline_controls(project_name)
    except Exception as e:
        st.info(f"Real-time controls unavailable: {str(e)}")
    
    st.markdown("---")
    
    # PHASE 1 info
    st.info("""
    **Phase 1: Real-Time Mode Available**
    - Non-blocking execution
    - Pause/Resume/Stop controls
    - Live feedback injection
    - Progress tracking
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
    if "producer_model_mode" not in st.session_state or st.session_state["producer_model_mode"] not in ["draft", "high_quality"]:
        st.session_state["producer_model_mode"] = "draft"
    
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
    # Ensure default value is valid
    if "producer_goal_mode" not in st.session_state or st.session_state["producer_goal_mode"] not in ["story_bible", "chapter", "full_story", "director"]:
        st.session_state["producer_goal_mode"] = "story_bible"
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
        value=10,
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
    run_button = st.button("Run Producer Pipeline (Legacy Blocking Mode)")

    # Output placeholders
    progress_placeholder = st.empty()
    output_placeholder = st.empty()

    if run_button:
        st.warning("Running in blocking mode - UI will freeze until complete!")
        
        seed = st.session_state["producer_seed_idea"].strip()
        if not seed:
            st.info("Provide a seed idea for the Producer Agent.")
            return

        producer.model_mode = model_mode
        agent = producer

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

        # Save into session only (Producer already saved pipeline results to ProjectState)
        st.session_state["producer_last_result"] = result
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


# Alternative function that takes project_name instead of producer
def render_producer_agent_panel_by_name(project_name: str):
    """Alternative version that takes project_name instead of producer."""
    try:
        from ui.common import get_producer
        producer = get_producer(project_name)
        render_producer_agent_panel(producer)
    except Exception as e:
        st.error(f"Could not load producer for {project_name}: {str(e)}")
        st.info("Running in basic mode")
        
        # Basic fallback
        st.header("🎬 Producer Agent (Basic Fallback)")
        seed = st.text_area("Seed Idea", key="basic_seed")
        if st.button("Test Producer"):
            st.info(f"Would run producer for {project_name} with seed: {seed}")