import streamlit as st

from categories import CATEGORY_KEYS, normalize_category
from i18n import DEFAULT_LANGUAGE, LANGUAGE_SESSION_KEY, normalize_language
from ui.router import VALID_PAGES


CURRENT_CONCEPT = "current_concept"
CURRENT_CONCEPT_ID = "current_concept_id"
CURRENT_CONCEPT_LANGUAGE = "current_concept_language"
LEONARDO_ASSET = "leonardo_visual_asset"
BLUEPRINT_ASSET = "blueprint_visual_asset"
CURRENT_PAGE = "page"
AUTO_IMAGE_PENDING_CONCEPT_ID = "auto_image_pending_concept_id"
AUTO_IMAGE_ERRORS = "auto_image_errors"
GENERATE_IMAGES = "generate_images_setting"
GENERATE_IMAGES_WIDGET = "generate_images"
USER_PROMPT = "user_prompt"
USER_PROMPT_WIDGET = "user_prompt_widget"
IDEA_CATEGORY = "idea_category"
LANGUAGE = LANGUAGE_SESSION_KEY

_LEGACY_LOADED_CONCEPT = "loaded_concept"
_LEGACY_GENERATED_CONCEPT = "generated_concept"
_DEFAULT_PAGE = "app"


def initialize_session_state() -> None:
    if CURRENT_CONCEPT not in st.session_state:
        legacy_concept = st.session_state.get(_LEGACY_LOADED_CONCEPT)
        if legacy_concept is None:
            legacy_concept = st.session_state.get(_LEGACY_GENERATED_CONCEPT)
        st.session_state[CURRENT_CONCEPT] = legacy_concept

    if CURRENT_CONCEPT_ID not in st.session_state:
        st.session_state[CURRENT_CONCEPT_ID] = None

    if CURRENT_CONCEPT_LANGUAGE not in st.session_state:
        st.session_state[CURRENT_CONCEPT_LANGUAGE] = DEFAULT_LANGUAGE
    else:
        st.session_state[CURRENT_CONCEPT_LANGUAGE] = normalize_language(
            st.session_state[CURRENT_CONCEPT_LANGUAGE]
        )

    if LEONARDO_ASSET not in st.session_state:
        st.session_state[LEONARDO_ASSET] = None

    if BLUEPRINT_ASSET not in st.session_state:
        st.session_state[BLUEPRINT_ASSET] = None

    if CURRENT_PAGE not in st.session_state:
        st.session_state[CURRENT_PAGE] = _DEFAULT_PAGE

    if AUTO_IMAGE_PENDING_CONCEPT_ID not in st.session_state:
        st.session_state[AUTO_IMAGE_PENDING_CONCEPT_ID] = None

    if AUTO_IMAGE_ERRORS not in st.session_state:
        st.session_state[AUTO_IMAGE_ERRORS] = {}

    if GENERATE_IMAGES not in st.session_state:
        st.session_state[GENERATE_IMAGES] = bool(
            st.session_state.get(GENERATE_IMAGES_WIDGET, False)
        )

    if USER_PROMPT not in st.session_state:
        st.session_state[USER_PROMPT] = ""

    stored_category = normalize_category(st.session_state.get(IDEA_CATEGORY))
    st.session_state[IDEA_CATEGORY] = stored_category or CATEGORY_KEYS[0]

    if LANGUAGE not in st.session_state:
        st.session_state[LANGUAGE] = DEFAULT_LANGUAGE
    else:
        st.session_state[LANGUAGE] = normalize_language(st.session_state[LANGUAGE])


def set_current_concept(
    concept_data,
    concept_id,
    concept_language=DEFAULT_LANGUAGE,
) -> None:
    st.session_state[CURRENT_CONCEPT] = concept_data
    st.session_state[CURRENT_CONCEPT_ID] = concept_id
    st.session_state[CURRENT_CONCEPT_LANGUAGE] = normalize_language(concept_language)


def clear_current_concept() -> None:
    st.session_state[CURRENT_CONCEPT] = None
    st.session_state[CURRENT_CONCEPT_ID] = None
    st.session_state[CURRENT_CONCEPT_LANGUAGE] = DEFAULT_LANGUAGE
    st.session_state[LEONARDO_ASSET] = None
    st.session_state[BLUEPRINT_ASSET] = None
    clear_automatic_image_generation_state()


def clear_transient_visuals() -> None:
    st.session_state[LEONARDO_ASSET] = None
    st.session_state[BLUEPRINT_ASSET] = None


def get_current_concept() -> dict | None:
    return st.session_state.get(CURRENT_CONCEPT)


def get_current_concept_id() -> int | None:
    return st.session_state.get(CURRENT_CONCEPT_ID)


def get_current_concept_language() -> str:
    return normalize_language(
        st.session_state.get(CURRENT_CONCEPT_LANGUAGE, DEFAULT_LANGUAGE)
    )


def get_current_page() -> str:
    current_page = st.session_state.get(CURRENT_PAGE, _DEFAULT_PAGE)
    return current_page if current_page in VALID_PAGES else _DEFAULT_PAGE


def set_current_page(page: str) -> None:
    if page not in VALID_PAGES:
        raise ValueError(f"Unsupported page: {page}")
    st.session_state[CURRENT_PAGE] = page


def get_current_language() -> str:
    return normalize_language(st.session_state.get(LANGUAGE, DEFAULT_LANGUAGE))


def get_generate_images_enabled() -> bool:
    return bool(st.session_state.get(GENERATE_IMAGES, False))


def start_automatic_image_generation(concept_id: int) -> None:
    st.session_state[AUTO_IMAGE_PENDING_CONCEPT_ID] = concept_id
    st.session_state[AUTO_IMAGE_ERRORS] = {}


def get_automatic_image_pending_concept_id() -> int | None:
    return st.session_state.get(AUTO_IMAGE_PENDING_CONCEPT_ID)


def finish_automatic_image_generation(concept_id: int, errors=None) -> None:
    if st.session_state.get(AUTO_IMAGE_PENDING_CONCEPT_ID) == concept_id:
        st.session_state[AUTO_IMAGE_PENDING_CONCEPT_ID] = None
    st.session_state[AUTO_IMAGE_ERRORS] = {
        "concept_id": concept_id,
        "errors": dict(errors or {}),
    }


def get_automatic_image_errors(concept_id: int) -> dict:
    error_state = st.session_state.get(AUTO_IMAGE_ERRORS, {})
    if error_state.get("concept_id") != concept_id:
        return {}
    return dict(error_state.get("errors", {}))


def clear_automatic_image_generation_state() -> None:
    st.session_state[AUTO_IMAGE_PENDING_CONCEPT_ID] = None
    st.session_state[AUTO_IMAGE_ERRORS] = {}
