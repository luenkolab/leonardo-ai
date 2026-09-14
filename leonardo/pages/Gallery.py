import streamlit as st

from ui.state import initialize_session_state, set_current_page


initialize_session_state()
set_current_page("gallery")
st.switch_page("app.py")
