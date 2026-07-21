import streamlit as st

from application.concepts import (
    ConceptLoadError,
    list_recent_concepts,
    load_concept,
    remove_concept,
    toggle_concept_favorite,
)
from config import CATEGORIES
from ui.formatting import pretty_label, safe_text
from ui.state import (
    clear_automatic_image_generation_state,
    clear_current_concept,
    clear_transient_visuals,
    get_current_concept_id,
    set_current_concept,
    set_current_page,
)
from ui.voice import render_voice_prompt


def render_previous_concepts_sidebar():
    with st.expander("📦 Previous Concepts", expanded=False, key="previous_concepts"):
        concepts = list_recent_concepts()

        if not concepts:
            st.info("No saved concepts yet.")
            return

        for concept_id, title, category, created_at, is_favorite in concepts:
            star = "⭐" if is_favorite else ""

            st.markdown(
                f"""
<div class="mini-card">
    <h4>{star} {safe_text(title)}</h4>
    <div class="small-note">
        Category: {safe_text(pretty_label(category))}<br>
        Created: {safe_text(created_at)}
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("📂", key=f"open_concept_{concept_id}", use_container_width=True, help="Open concept"):
                    try:
                        selected_concept = load_concept(concept_id)
                    except ConceptLoadError:
                        st.error(
                            "Unable to open the saved concept: its data is corrupted or uses an outdated format."
                        )
                    else:
                        if selected_concept:
                            set_current_concept(selected_concept, concept_id)
                            clear_transient_visuals()
                            clear_automatic_image_generation_state()
                            st.rerun()

            with c2:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_concept_{concept_id}", use_container_width=True, help="Favorite"):
                    toggle_concept_favorite(concept_id)
                    st.rerun()

            with c3:
                if st.button("🗑", key=f"delete_concept_{concept_id}", use_container_width=True, help="Delete concept"):
                    remove_concept(concept_id)
                    if get_current_concept_id() == concept_id:
                        clear_current_concept()
                    st.rerun()


def render_controls():
    with st.sidebar:
        st.markdown(
            """
<div class="language-row">
    <span title="English">🇬🇧</span>
    <span title="Svenska">🇸🇪</span>
    <span title="Русский">🇷🇺</span>
</div>

<div class="profile-row">
    <div class="profile-avatar">🧠</div>
    <div>
        <div class="profile-name">Developer</div>
        <div class="profile-email">Contact unavailable</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        nav1 = st.button("⌂  APP", key="nav_app", use_container_width=True)
        nav2 = st.button("▧  GALLERY", key="nav_gallery", use_container_width=True)

        if nav1:
            set_current_page("app")
            st.rerun()

        if nav2:
            st.switch_page("pages/Gallery.py")

        render_previous_concepts_sidebar()

        st.markdown('<div class="ornament-line"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">Leonardo<br>Control</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-group-title">⚙️ Concept Settings</div>', unsafe_allow_html=True)

        category = st.selectbox(
            "Idea Category",
            CATEGORIES,
            format_func=pretty_label,
        )

        creativity_mode = st.selectbox(
            "Creativity Mode",
            ["Classic", "Bold", "Experimental"],
        )

        audience = st.selectbox(
            "Target Audience",
            ["Engineers", "Investors", "Students", "General Public"],
        )

        user_prompt = st.text_area(
            "Prompt / Idea",
            placeholder="Create a Renaissance-inspired rescue glider for dangerous mountain missions...",
            height=120,
        )

        generate = st.button("✨ Generate Idea", use_container_width=True, type="primary")
        regenerate = st.button("🔄 Regenerate", use_container_width=True)

        render_voice_prompt()

        with st.expander("📦 Included in Output", expanded=False):
            st.markdown(
                """
                - ✅ Leonardo-style idea concept
                - ✅ Principle of operation
                - ✅ Leonardo sketch description
                - ✅ Modern implementation
                - ✅ Modern blueprint prompt
                - ✅ Market demand estimate
                - ✅ ROI analysis
                - ✅ Difficulty level
                - ✅ Development timeline
                - ✅ Materials / technologies
                - ✅ Use cases
                - ✅ Investor summary
                """
            )

    return category, creativity_mode, audience, user_prompt, generate, regenerate
