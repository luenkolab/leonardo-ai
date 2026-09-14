import streamlit as st

from categories import CATEGORY_KEYS
from application.concepts import (
    ConceptLoadError,
    list_recent_concepts,
    load_concept_for_viewer,
    remove_concept,
    toggle_concept_favorite,
)
from i18n import LANGUAGES, category_display_name, translate
from ui.formatting import safe_text
from ui.state import (
    GENERATE_IMAGES,
    GENERATE_IMAGES_WIDGET,
    IDEA_CATEGORY,
    LANGUAGE,
    USER_PROMPT,
    USER_PROMPT_WIDGET,
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
        format_func=lambda value: LANGUAGES[value]["name"],
        label_visibility="collapsed",
    )


def _render_primary_navigation(language):
    navigation = (
        ("app", "nav.app"),
        ("gallery", "nav.gallery"),
        ("marketplace", "nav.marketplace"),
    )
    for page, translation_key in navigation:
        if st.button(
            translate(translation_key, language),
            key=f"nav_{page}",
            use_container_width=True,
        ):
            set_current_page(page)
            st.rerun()


def render_navigation_sidebar():
    with st.sidebar:
        render_language_selector()
        _render_primary_navigation(get_current_language())


def _sync_generate_images_setting():
    st.session_state[GENERATE_IMAGES] = bool(
        st.session_state.get(GENERATE_IMAGES_WIDGET, False)
    )


def _sync_user_prompt():
    st.session_state[USER_PROMPT] = st.session_state.get(USER_PROMPT_WIDGET, "")


def render_previous_concepts_sidebar():
    language = get_current_language()
    with st.expander(translate('sidebar.previous_concepts', language), expanded=False, key="previous_concepts"):
        concepts = list_recent_concepts()

        if not concepts:
            st.info(translate("sidebar.no_saved_concepts", language))
            return

        for concept_id, title, category, created_at, is_favorite in concepts:
            favorite_marker = '<span class="mini-card-favorite" aria-hidden="true"></span>' if is_favorite else ""

            st.markdown(
                f"""
<div class="mini-card">
    <h4>{favorite_marker}{safe_text(title)}</h4>
    <div class="small-note">
        {safe_text(translate('common.category', language))}: {safe_text(category_display_name(category, language))}<br>
        {safe_text(translate('common.created', language))}: {safe_text(created_at)}
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button(" ", key=f"open_concept_{concept_id}", use_container_width=True, help=translate("sidebar.previous_concepts", language)):
                    try:
                        selected_concept, concept_language = (
                            load_concept_for_viewer(concept_id, language)
                        )
                    except ConceptLoadError:
                        st.error(
                            translate("sidebar.open_error", language)
                        )
                    else:
                        if selected_concept:
                            set_current_concept(
                                selected_concept,
                                concept_id,
                                concept_language or language,
                            )
                            clear_transient_visuals()
                            clear_automatic_image_generation_state()
                            st.rerun()

            with c2:
                if st.button(" ", key=f"favorite_concept_{concept_id}", use_container_width=True, help=translate("common.favorite", language)):
                    toggle_concept_favorite(concept_id)
                    st.rerun()

            with c3:
                if st.button(" ", key=f"delete_concept_{concept_id}", use_container_width=True, help=translate("common.delete", language)):
                    remove_concept(concept_id)
                    if get_current_concept_id() == concept_id:
                        clear_current_concept()
                    st.rerun()


def render_controls():
    with st.sidebar:
        render_language_selector()
        language = get_current_language()
        _render_primary_navigation(language)

        render_previous_concepts_sidebar()

        st.markdown('<div class="ornament-line"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-title">{translate("sidebar.control", language)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-group-title sidebar-group-title--settings">{translate("sidebar.concept_settings", language)}</div>', unsafe_allow_html=True)

        category = st.selectbox(
            translate("sidebar.idea_category", language),
            CATEGORY_KEYS,
            format_func=lambda value: category_display_name(value, language),
            key=IDEA_CATEGORY,
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

        st.session_state[GENERATE_IMAGES_WIDGET] = st.session_state[GENERATE_IMAGES]
        st.toggle(
            translate("sidebar.generate_images", language),
            key=GENERATE_IMAGES_WIDGET,
            on_change=_sync_generate_images_setting,
        )

        st.session_state[USER_PROMPT_WIDGET] = st.session_state[USER_PROMPT]
        user_prompt = st.text_area(
            translate("sidebar.prompt", language),
            placeholder=translate("sidebar.prompt_placeholder", language),
            height=120,
            key=USER_PROMPT_WIDGET,
            on_change=_sync_user_prompt,
        )

        generate = st.button(translate('sidebar.generate', language), key="generate_idea", use_container_width=True, type="primary")
        regenerate = st.button(translate('sidebar.regenerate', language), key="regenerate_idea", use_container_width=True)

        render_voice_prompt()

    return category, creativity_mode, audience, user_prompt, generate, regenerate
