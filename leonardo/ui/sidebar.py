import streamlit as st

from application.concepts import (
    ConceptLoadError,
    list_recent_concepts,
    load_concept,
    remove_concept,
    toggle_concept_favorite,
)
from config import CATEGORIES
from i18n import LANGUAGES, language_display_name, translate
from ui.formatting import safe_text
from ui.state import (
    LANGUAGE,
    clear_automatic_image_generation_state,
    clear_current_concept,
    clear_transient_visuals,
    get_current_concept_id,
    get_current_language,
    set_current_concept,
    set_current_page,
)
from ui.voice import render_voice_prompt


def render_language_selector():
    language = get_current_language()
    st.selectbox(
        translate("language", language),
        list(LANGUAGES),
        key=LANGUAGE,
        format_func=language_display_name,
    )


def render_previous_concepts_sidebar():
    language = get_current_language()
    with st.expander(f"📦 {translate('sidebar.previous_concepts', language)}", expanded=False, key="previous_concepts"):
        concepts = list_recent_concepts()

        if not concepts:
            st.info(translate("sidebar.no_saved_concepts", language))
            return

        for concept_id, title, category, created_at, is_favorite in concepts:
            star = "⭐" if is_favorite else ""

            st.markdown(
                f"""
<div class="mini-card">
    <h4>{star} {safe_text(title)}</h4>
    <div class="small-note">
        {safe_text(translate('common.category', language))}: {safe_text(translate(f'option.category.{category}', language))}<br>
        {safe_text(translate('common.created', language))}: {safe_text(created_at)}
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("📂", key=f"open_concept_{concept_id}", use_container_width=True, help=translate("sidebar.previous_concepts", language)):
                    try:
                        selected_concept = load_concept(concept_id)
                    except ConceptLoadError:
                        st.error(
                            translate("sidebar.open_error", language)
                        )
                    else:
                        if selected_concept:
                            set_current_concept(selected_concept, concept_id)
                            clear_transient_visuals()
                            clear_automatic_image_generation_state()
                            st.rerun()

            with c2:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_concept_{concept_id}", use_container_width=True, help=translate("common.favorite", language)):
                    toggle_concept_favorite(concept_id)
                    st.rerun()

            with c3:
                if st.button("🗑", key=f"delete_concept_{concept_id}", use_container_width=True, help=translate("common.delete", language)):
                    remove_concept(concept_id)
                    if get_current_concept_id() == concept_id:
                        clear_current_concept()
                    st.rerun()


def render_controls():
    with st.sidebar:
        render_language_selector()
        language = get_current_language()

        nav1 = st.button(f"⌂  {translate('nav.app', language)}", key="nav_app", use_container_width=True)
        nav2 = st.button(f"▧  {translate('nav.gallery', language)}", key="nav_gallery", use_container_width=True)

        if nav1:
            set_current_page("app")
            st.rerun()

        if nav2:
            st.switch_page("pages/Gallery.py")

        render_previous_concepts_sidebar()

        st.markdown('<div class="ornament-line"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-title">{translate("sidebar.control", language)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-group-title">⚙️ {translate("sidebar.concept_settings", language)}</div>', unsafe_allow_html=True)

        category = st.selectbox(
            translate("sidebar.idea_category", language),
            CATEGORIES,
            format_func=lambda value: translate(f"option.category.{value}", language),
        )

        creativity_mode = st.selectbox(
            translate("sidebar.creativity_mode", language),
            ["Classic", "Bold", "Experimental"],
            format_func=lambda value: translate(f"option.creativity.{value.lower()}", language),
        )

        audience = st.selectbox(
            translate("sidebar.target_audience", language),
            ["Engineers", "Investors", "Students", "General Public"],
            format_func=lambda value: translate(f"option.audience.{value.lower().replace(' ', '_')}", language),
        )

        user_prompt = st.text_area(
            translate("sidebar.prompt", language),
            placeholder=translate("sidebar.prompt_placeholder", language),
            height=120,
        )

        generate = st.button(f"✨ {translate('sidebar.generate', language)}", use_container_width=True, type="primary")
        regenerate = st.button(f"🔄 {translate('sidebar.regenerate', language)}", use_container_width=True)

        render_voice_prompt()

    return category, creativity_mode, audience, user_prompt, generate, regenerate
