# ----------------------------
# import
 # ----------------------------

import streamlit as st

from ui.concept_page import generate_or_load_concept, render_concept_result
from ui.drawing_studio_page import render_drawing_studio
from ui.gallery_page import render_gallery
from ui.home import render_banner, render_empty_concept_area
from ui.marketplace_page import render_marketplace
from ui.router import render_current_page
from ui.sidebar import render_controls, render_navigation_sidebar
from ui.state import (
    get_current_page,
    initialize_session_state,
)
from ui.styles import apply_global_styles
from database import init_db

# ----------------------------
# Page setup
# ----------------------------

st.set_page_config(
    page_title="Leonardo AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
initialize_session_state()


# ----------------------------
# CSS
# ----------------------------

apply_global_styles()


# ----------------------------
# Screen renderers
# ----------------------------

def render_app():
    category, creativity_mode, audience, user_prompt, generate, regenerate = (
        render_controls()
    )
    render_banner()

    concept_data = generate_or_load_concept(
        category=category,
        creativity_mode=creativity_mode,
        audience=audience,
        user_prompt=user_prompt,
        generate=generate,
        regenerate=regenerate,
    )

    if concept_data:
        render_concept_result(concept_data)
    else:
        render_empty_concept_area()


current_page = get_current_page()
if current_page != "app":
    render_navigation_sidebar()

concept_page_root = None
drawing_studio_root = None
if current_page in {"app", "drawing_studio"}:
    concept_page_root = st.container(key="concept_page_root")
    drawing_studio_root = st.container(key="drawing_studio_root")


def render_app_route():
    drawing_studio_root.empty()
    with concept_page_root.container():
        render_app()


def render_drawing_studio_route():
    concept_page_root.empty()
    with drawing_studio_root.container():
        render_drawing_studio()

render_current_page(
    current_page,
    app_renderer=render_app_route,
    gallery_renderer=render_gallery,
    marketplace_renderer=render_marketplace,
    drawing_studio_renderer=render_drawing_studio_route,
)
