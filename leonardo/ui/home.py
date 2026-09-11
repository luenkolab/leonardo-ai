import streamlit as st

from i18n import translate
from ui.assets import image_to_base64
from ui.components import render_section_heading
from ui.state import get_current_language


def render_banner():
    st.image("banner.png", use_container_width=True)


def render_empty_concept_area():
    language = get_current_language()
    render_section_heading(translate("home.generated_concept", language))

    concept_panel_base64 = image_to_base64("concept_panel.png")

    if concept_panel_base64:
        st.markdown(
            f"""
<div class="concept-empty-image-box">
    <img src="data:image/png;base64,{concept_panel_base64}" class="concept-empty-image">
    <div class="concept-empty-text">
        <p>{translate("home.empty_title", language)}</p>
        <p>{translate("home.empty_description", language)}</p>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
<div class="concept-empty">
    <p>{translate("home.empty_fallback_title", language)}</p>
    <p>{translate("home.empty_fallback_description", language)}</p>
</div>
""",
            unsafe_allow_html=True,
        )

    feature_cards = [
        ("🪶", translate("home.feature.title_summary.title", language), translate("home.feature.title_summary.text", language)),
        ("⚙️", translate("home.feature.core.title", language), translate("home.feature.core.text", language)),
        ("🖼️", translate("home.feature.sketch.title", language), translate("home.feature.sketch.text", language)),
        ("📦", translate("home.feature.blueprint.title", language), translate("home.feature.blueprint.text", language)),
        ("⚗️", translate("home.feature.materials.title", language), translate("home.feature.materials.text", language)),
        ("🎯", translate("home.feature.use_cases.title", language), translate("home.feature.use_cases.text", language)),
    ]

    for row_start in range(0, len(feature_cards), 3):
        cols = st.columns(3)

        for col, card in zip(cols, feature_cards[row_start:row_start + 3]):
            icon, title, text = card

            with col:
                st.markdown(
                    f"""
<div class="feature-card">
    <div class="feature-title">
        <span class="feature-icon">{icon}</span>{title}
    </div>
    <div class="feature-text">{text}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

    st.markdown(
        f"""
<div class="feature-card">
    <div class="feature-title">
        <span class="feature-icon">📊</span>{translate("home.feature.investor.title", language)}
    </div>
    <div class="feature-text">{translate("home.feature.investor.text", language)}</div>
</div>
""",
        unsafe_allow_html=True,
    )
