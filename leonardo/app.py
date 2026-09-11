# ----------------------------
# import
 # ----------------------------

import streamlit as st

from i18n import translate
from ui.concept_page import generate_or_load_concept, render_concept_result
from ui.home import render_banner, render_empty_concept_area
from ui.images import render_saved_images
from ui.sidebar import render_controls
from ui.state import get_current_language, get_current_page, initialize_session_state
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
# App flow
# ----------------------------

category, creativity_mode, audience, user_prompt, generate, regenerate = render_controls()

render_banner()

if get_current_page() == "gallery":
    st.markdown(f"## {translate('gallery.page_title', get_current_language())}")
    render_saved_images()
    st.stop()

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
