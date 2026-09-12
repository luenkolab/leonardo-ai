import streamlit as st

from i18n import translate
from ui.assets import image_to_base64
from ui.components import render_section_heading
from ui.state import get_current_language


_FEATURE_ICONS = {
    "title_summary": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 3h8l4 4v14H6Z"/><path d="M14 3v5h4M9 13h6M9 17h6"/></svg>""",
    "core": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06a1.7 1.7 0 0 0-1.88-.34A1.7 1.7 0 0 0 14 20.92V21h-4v-.08A1.7 1.7 0 0 0 9 19.37a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.63 15 1.7 1.7 0 0 0 3.08 14H3v-4h.08A1.7 1.7 0 0 0 4.63 9a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.63 1.7 1.7 0 0 0 10 3.08V3h4v.08a1.7 1.7 0 0 0 1.03 1.55 1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.37 9a1.7 1.7 0 0 0 1.55 1H21v4h-.08A1.7 1.7 0 0 0 19.4 15Z"/></svg>""",
    "sketch": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20h16M6 16 16 6l3 3L9 19H6Z"/><path d="m14.5 7.5 3 3M9 19l-3 1 1-3"/></svg>""",
    "blueprint": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="5" r="2"/><path d="m11 7-5 13M13 7l5 13M8.2 14h7.6M5 20h4M15 20h4"/></svg>""",
    "materials": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/></svg>""",
    "use_cases": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/><path d="m15 9 5-5M17 4h3v3"/></svg>""",
    "investor": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20V5M4 20h17"/><path d="m7 16 4-4 3 2 6-7M16 7h4v4"/></svg>""",
    "commercial_metrics": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20V5M4 20h17"/><path d="m7 16 4-4 3 2 6-7M16 7h4v4"/><path d="M8 9v2M12 6v2"/></svg>""",
    "implementation_metrics": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 16a8 8 0 1 1 14 0"/><path d="m12 12 4-4M4 19h16"/><circle cx="12" cy="12" r="1"/></svg>""",
}


def render_banner():
    with st.container(key="main_banner"):
        st.image("banner.png", use_container_width=True)


def render_empty_concept_area():
    language = get_current_language()
    render_section_heading(translate("home.generated_concept", language))

    with st.container(key="generated_concept_panel"):
        concept_panel_base64 = image_to_base64("concept_panel_engineering.png")

        if concept_panel_base64:
            st.markdown(
                f"""
<div class="concept-empty-image-box">
    <img src="data:image/png;base64,{concept_panel_base64}" class="concept-empty-image">
    <div class="concept-empty-text">
        <div class="concept-panel-line">{translate("home.empty_description.line1", language)}</div>
        <div class="concept-panel-line">{translate("home.empty_description.line2", language)}</div>
        <div class="concept-panel-line">{translate("home.empty_description.line3", language)}</div>
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
        (_FEATURE_ICONS["title_summary"], translate("home.feature.title_summary.title", language), translate("home.feature.title_summary.text", language)),
        (_FEATURE_ICONS["core"], translate("home.feature.core.title", language), translate("home.feature.core.text", language)),
        (_FEATURE_ICONS["sketch"], translate("home.feature.sketch.title", language), translate("home.feature.sketch.text", language)),
        (_FEATURE_ICONS["blueprint"], translate("home.feature.blueprint.title", language), translate("home.feature.blueprint.text", language)),
        (_FEATURE_ICONS["materials"], translate("home.feature.materials.title", language), translate("home.feature.materials.text", language)),
        (_FEATURE_ICONS["use_cases"], translate("home.feature.use_cases.title", language), translate("home.feature.use_cases.text", language)),
        (_FEATURE_ICONS["investor"], translate("home.feature.investor.title", language), translate("home.feature.investor.text", language)),
        (_FEATURE_ICONS["commercial_metrics"], translate("home.feature.commercial_metrics.title", language), translate("home.feature.commercial_metrics.text", language)),
        (_FEATURE_ICONS["implementation_metrics"], translate("home.feature.implementation_metrics.title", language), translate("home.feature.implementation_metrics.text", language)),
    ]

    feature_card_markup = []
    for icon, title, text in feature_cards:
        feature_card_markup.append(
            f"""
<div class="feature-card">
    <div class="feature-title">
        <span class="feature-icon">{icon}</span>{title}
    </div>
    <div class="feature-text">{text}</div>
</div>
""",
        )

    st.markdown(
        f'<div class="feature-grid">{"".join(feature_card_markup)}</div>',
        unsafe_allow_html=True,
    )
