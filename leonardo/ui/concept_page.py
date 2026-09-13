import base64
import html
import unicodedata

import streamlit as st

from i18n import translate
from application.concepts import generate_and_save_concept
from application.images import (
    CONCEPT_IMAGE_TYPES,
    LEONARDO_CONCEPT_IMAGE_TYPES,
    MODERN_CONCEPT_IMAGE_TYPES,
    generate_and_save_concept_images,
    generate_blueprint_visual,
    generate_leonardo_visual,
    get_concept_image_slots,
)
from application.project_export import export_project_package
from ui.components import (
    render_complete_guide,
    render_generated_section_heading,
    render_result_box,
)
from ui.images import render_generated_visuals
from ui.state import (
    BLUEPRINT_ASSET,
    LEONARDO_ASSET,
    clear_transient_visuals,
    finish_automatic_image_generation,
    get_automatic_image_errors,
    get_automatic_image_pending_concept_id,
    get_current_concept,
    get_current_concept_id,
    get_current_language,
    set_current_concept,
    start_automatic_image_generation,
)
from ui.voice import render_voice_assistant


_LEONARDO_VISION_ICON = """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M20.5 2.8c-4.8.6-9.9 3.4-12.9 7.5-2.3 3.1-3.4 6.4-3.2 9.2 2.8-.1 6-1.3 8.9-3.8 3.9-3.4 6.3-8.3 7.2-12.9Z"/><path d="M3.8 21.2 14.7 9.2M7.2 17.5l-.7-4.2M10.1 14.3l-1-5M12.8 11.3l4.6-.8M15.4 8.2l3.2-.7"/></svg>"""
_CONCEPT_ICON = """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9 18h6M10 22h4M8.5 15.5A7 7 0 1 1 15.5 15.5c-.9.7-1.5 1.5-1.5 2.5h-4c0-1-.6-1.8-1.5-2.5Z"/></svg>"""
_SKETCH_DESCRIPTION_ICON = """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20h16M6 16 16 6l3 3L9 19H6Z"/><path d="m14.5 7.5 3 3M9 19l-3 1 1-3M5 4l5 5M5 4v4M5 4h4"/></svg>"""
_MODERN_SECTION_ICON = """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17h18M5 17l2-7h10l2 7M8 10V7h8v3M12 3v4"/><circle cx="5" cy="17" r="1.5"/><circle cx="19" cy="17" r="1.5"/><path d="M9 21h6M12 17v4"/></svg>"""
_MODERN_RESULT_ICONS = {
    "title": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 3h8l4 4v14H6Z"/><path d="M14 3v5h4M9 13h6M9 17h6"/></svg>""",
    "product_name": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m20 13-7 7L4 11V4h7l9 9Z"/><circle cx="8.5" cy="8.5" r="1.5"/></svg>""",
    "category": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/></svg>""",
    "executive_summary": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20V5M4 20h17"/><path d="m7 16 4-4 3 2 6-7M16 7h4v4"/></svg>""",
    "problem_statement": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 17h.01"/></svg>""",
    "target_users": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c.4-4 2.4-6 6-6s5.6 2 6 6M14 15c3.7-.7 6.3 1 7 5"/></svg>""",
    "industries": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 21V5h10v16M14 10h6v11M8 9h2M8 13h2M8 17h2M17 14h1M17 17h1M2 21h20"/></svg>""",
    "use_cases": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/><path d="m15 9 5-5M17 4h3v3"/></svg>""",
    "modern_principle": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/></svg>""",
    "system_components": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3" y="4" width="7" height="7" rx="1"/><rect x="14" y="4" width="7" height="7" rx="1"/><rect x="8.5" y="15" width="7" height="6" rx="1"/><path d="M6.5 11v2h11v-2M12 13v2"/></svg>""",
    "materials": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m12 3 8 4-8 4-8-4 8-4Z"/><path d="m4 11 8 4 8-4M4 15l8 4 8-4"/></svg>""",
    "technical_requirements": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 16a8 8 0 1 1 14 0M4 19h16"/><path d="m12 12 4-4"/><circle cx="12" cy="12" r="1"/></svg>""",
    "modern_sketch_description": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="5" r="2"/><path d="m11 7-5 13M13 7l5 13M8.2 14h7.6M5 20h4M15 20h4"/></svg>""",
}

_GENERATED_SECTION_ICONS = {
    "visual": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9" r="1.5"/><path d="m3 17 5-5 4 4 3-3 6 6"/></svg>""",
    "roadmap": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="5" cy="18" r="2"/><circle cx="19" cy="6" r="2"/><path d="M7 18h3a4 4 0 0 0 4-4v-4a4 4 0 0 1 4-4h-1M10 14l4 4M14 14l-4 4"/></svg>""",
    "risks": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v5M12 17.5h.01"/></svg>""",
    "commercial": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20V5M4 20h17"/><path d="m7 16 4-4 3 2 6-7M16 7h4v4"/></svg>""",
    "metrics": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 16a8 8 0 1 1 14 0M4 19h16"/><path d="m12 12 4-4"/><circle cx="12" cy="12" r="1"/></svg>""",
}

_GENERATED_RESULT_ICONS = {
    "leonardo_prompt": _SKETCH_DESCRIPTION_ICON,
    "blueprint_prompt": _MODERN_RESULT_ICONS["modern_sketch_description"],
    "deployment": _GENERATED_SECTION_ICONS["roadmap"],
    "risk": _GENERATED_SECTION_ICONS["risks"],
    "constraint": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3 20 6v6c0 4.8-3.1 7.7-8 9-4.9-1.3-8-4.2-8-9V6l8-3Z"/><path d="M9 12h6"/></svg>""",
    "market": _GENERATED_SECTION_ICONS["commercial"],
    "cost": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><ellipse cx="9" cy="7" rx="5" ry="2.5"/><path d="M4 7v4c0 1.4 2.2 2.5 5 2.5s5-1.1 5-2.5V7M4 11v4c0 1.4 2.2 2.5 5 2.5 1.1 0 2.1-.2 3-.5"/><ellipse cx="16" cy="16" rx="4" ry="2"/><path d="M12 16v3c0 1.1 1.8 2 4 2s4-.9 4-2v-3"/></svg>""",
    "roi": _MODERN_RESULT_ICONS["executive_summary"],
    "investor": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V4h6v3M3 12h18M10 12v2h4v-2"/></svg>""",
    "concept_complexity": _GENERATED_SECTION_ICONS["metrics"],
    "modern_complexity": _MODERN_RESULT_ICONS["category"],
    "development_time": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>""",
}


def generate_or_load_concept(
    category,
    creativity_mode,
    audience,
    user_prompt,
    generate,
    regenerate,
):

    concept_data = get_current_concept()

    if generate or regenerate:

        clear_transient_visuals()

        prompt_text = (
            user_prompt.strip()
            if user_prompt.strip()
            else translate(
                "concept.default_prompt",
                get_current_language(),
                category=translate(f"option.category.{category}", get_current_language()),
            )
        )

        with st.spinner(translate("concept.generating", get_current_language())):

            concept_data, concept_id = generate_and_save_concept(
                category=category,
                creativity_mode=creativity_mode,
                audience=audience,
                user_prompt=prompt_text,
                language=get_current_language(),
            )

        set_current_concept(concept_data, concept_id)
        start_automatic_image_generation(concept_id)
        st.rerun()

    return concept_data


def _render_concept_image_slot(
    image_type,
    accessible_label,
    concept_images,
    is_pending,
    image_errors,
):
    image = concept_images.get(image_type)
    escaped_label = html.escape(accessible_label, quote=True)
    state_class = ""
    extra_attributes = ""

    if image:
        image_base64 = base64.b64encode(image[4]).decode("ascii")
        slot_content = (
            f'<img src="data:image/png;base64,{image_base64}" alt="{escaped_label}">'
        )
    else:
        slot_content = ""
        if is_pending:
            state_class = " concept-image-slot--loading"
            extra_attributes = ' aria-busy="true"'
        elif image_type in image_errors:
            state_class = " concept-image-slot--error"

    st.markdown(
        f'<div class="concept-image-slot{state_class}" role="img" aria-label="{escaped_label}"{extra_attributes}>{slot_content}</div>',
        unsafe_allow_html=True,
    )


def _render_leonardo_vision(
    concept_data,
    concept_id,
    concept_images,
    is_pending,
    image_errors,
):
    language = get_current_language()
    with st.container(border=False, key="leonardo_section"):
        st.markdown(
            f"""
<h2 class="leonardo-section-heading">
    <span class="leonardo-section-heading__icon">{_LEONARDO_VISION_ICON}</span>
    {html.escape(translate('concept.leonardo_vision', language))}
</h2>
""",
            unsafe_allow_html=True,
        )
        st.caption(translate("concept.leonardo_subtitle", language))

        with st.container(key=f"leonardo_image_slots_{concept_id}"):
            img_cols = st.columns(3)
            section_label = translate("concept.leonardo_vision", language)
            for index, (column, image_type) in enumerate(
                zip(img_cols, LEONARDO_CONCEPT_IMAGE_TYPES),
                start=1,
            ):
                with column:
                    _render_concept_image_slot(
                        image_type,
                        f"{section_label} {index}",
                        concept_images,
                        is_pending,
                        image_errors,
                    )

        render_result_box(
            translate("concept.concept", language),
            concept_data["leonardo_concept"],
            icon_svg=_CONCEPT_ICON,
        )
        render_result_box(
            translate("concept.sketch_description", language),
            concept_data["leonardo_sketch_description"],
            icon_svg=_SKETCH_DESCRIPTION_ICON,
        )

    st.markdown('</div>', unsafe_allow_html=True)


def _render_modern_implementation(
    concept_data,
    title,
    concept_id,
    concept_images,
    is_pending,
    image_errors,
):
    language = get_current_language()
    with st.container(border=False, key="modern_section"):
        st.markdown(
            f"""
<h2 class="modern-section-heading">
    <span class="modern-section-heading__icon">{_MODERN_SECTION_ICON}</span>
    {html.escape(translate('concept.modern_implementation', language))}
</h2>
""",
            unsafe_allow_html=True,
        )
        st.caption(translate("concept.modern_subtitle", language))

        with st.container(key=f"modern_image_slots_{concept_id}"):
            img_cols = st.columns(3)
            section_label = translate("concept.modern_implementation", language)
            for index, (column, image_type) in enumerate(
                zip(img_cols, MODERN_CONCEPT_IMAGE_TYPES),
                start=1,
            ):
                with column:
                    _render_concept_image_slot(
                        image_type,
                        f"{section_label} {index}",
                        concept_images,
                        is_pending,
                        image_errors,
                    )

        render_result_box(translate("concept.title", language), title, icon_svg=_MODERN_RESULT_ICONS["title"])
        render_result_box(translate("concept.product_name", language), concept_data["modern_product_name"], icon_svg=_MODERN_RESULT_ICONS["product_name"])
        render_result_box(translate("common.category", language), concept_data["modern_category"], icon_svg=_MODERN_RESULT_ICONS["category"])
        render_result_box(translate("concept.executive_summary", language), concept_data["executive_summary"], icon_svg=_MODERN_RESULT_ICONS["executive_summary"])

        st.markdown(f"## {translate('concept.business_need', language)}")
        render_result_box(translate("concept.problem_statement", language), concept_data["problem_statement"], icon_svg=_MODERN_RESULT_ICONS["problem_statement"])
        render_result_box(translate("concept.target_users", language), concept_data["target_users"], icon_svg=_MODERN_RESULT_ICONS["target_users"])
        render_result_box(translate("concept.industries", language), concept_data["industries"], icon_svg=_MODERN_RESULT_ICONS["industries"])
        render_result_box(translate("concept.use_cases", language), concept_data["use_cases"], icon_svg=_MODERN_RESULT_ICONS["use_cases"])

        st.markdown(f"## {translate('concept.engineering', language)}")
        render_result_box(translate("concept.modern_principle", language), concept_data["modern_principle"], icon_svg=_MODERN_RESULT_ICONS["modern_principle"])
        render_result_box(translate("concept.system_components", language), concept_data["system_components"], icon_svg=_MODERN_RESULT_ICONS["system_components"])
        render_result_box(translate("concept.materials", language), concept_data["materials"], icon_svg=_MODERN_RESULT_ICONS["materials"])
        render_result_box(translate("concept.technical_requirements", language), concept_data["technical_requirements"], icon_svg=_MODERN_RESULT_ICONS["technical_requirements"])
        render_result_box(translate("concept.modern_sketch_description", language), concept_data["modern_sketch_description"], icon_svg=_MODERN_RESULT_ICONS["modern_sketch_description"])

    st.markdown('</div>', unsafe_allow_html=True)


def _render_visual_generation(concept_data):
    language = get_current_language()
    render_generated_section_heading(
        translate("concept.visual_generation", language),
        _GENERATED_SECTION_ICONS["visual"],
    )
    render_result_box(
        translate("concept.leonardo_prompt", language),
        concept_data["leonardo_sketch_description"],
        icon_svg=_GENERATED_RESULT_ICONS["leonardo_prompt"],
        visual_variant="blue",
    )
    render_result_box(
        translate("concept.blueprint_prompt", language),
        concept_data["modern_sketch_description"],
        extra_bottom_spacing=True,
        icon_svg=_GENERATED_RESULT_ICONS["blueprint_prompt"],
        visual_variant="blue",
    )

    col1, col2 = st.columns(2)
    with col1:
        generate_leonardo_image = st.button(
            translate("concept.generate_leonardo", language),
            key="generate_leonardo_manual",
            use_container_width=True,
        )
    with col2:
        generate_blueprint_image = st.button(
            translate("concept.generate_blueprint", language),
            key="generate_blueprint_manual",
            use_container_width=True,
        )

    if generate_leonardo_image:
        with st.spinner(translate("concept.generating_leonardo", language)):
            try:
                st.session_state[LEONARDO_ASSET] = generate_leonardo_visual(
                    concept_data["leonardo_sketch_description"]
                )
            except Exception as e:
                st.error(translate("concept.leonardo_error", language, error=e))

    if generate_blueprint_image:
        with st.spinner(translate("concept.generating_blueprint", language)):
            try:
                st.session_state[BLUEPRINT_ASSET] = generate_blueprint_visual(
                    concept_data["modern_sketch_description"]
                )
            except Exception as e:
                st.error(translate("concept.blueprint_error", language, error=e))

    render_generated_visuals()


def _render_implementation_roadmap(concept_data):
    language = get_current_language()
    render_generated_section_heading(
        translate("concept.roadmap", language),
        _GENERATED_SECTION_ICONS["roadmap"],
    )
    guides = concept_data["implementation_guides"]
    render_complete_guide(translate("concept.prototype", language), guides["prototype"], key="roadmap_prototype")
    render_complete_guide(translate("concept.mvp", language), guides["mvp"], key="roadmap_mvp")
    render_complete_guide(translate("concept.pilot", language), guides["pilot"], key="roadmap_pilot")
    render_complete_guide(translate("concept.production", language), guides["production"], key="roadmap_production")

    render_result_box(
        translate("concept.deployment_strategy", language),
        concept_data["deployment_strategy"],
        icon_svg=_GENERATED_RESULT_ICONS["deployment"],
        visual_variant="blue",
    )


def _render_risks_and_constraints(concept_data):
    language = get_current_language()
    render_generated_section_heading(
        translate("concept.risks_constraints", language),
        _GENERATED_SECTION_ICONS["risks"],
    )
    render_result_box(translate("concept.risks", language), concept_data["risks"], icon_svg=_GENERATED_RESULT_ICONS["risk"], visual_variant="risk")
    render_result_box(translate("concept.constraints", language), concept_data["constraints"], icon_svg=_GENERATED_RESULT_ICONS["constraint"], visual_variant="constraint")


def _render_commercial_outlook(concept_data):
    language = get_current_language()
    render_generated_section_heading(translate("concept.commercial_outlook", language), _GENERATED_SECTION_ICONS["commercial"])
    render_result_box(translate("concept.market_demand", language), concept_data["market_demand"], icon_svg=_GENERATED_RESULT_ICONS["market"])
    render_result_box(translate("concept.startup_cost", language), concept_data["startup_cost"], icon_svg=_GENERATED_RESULT_ICONS["cost"])
    render_result_box(translate("concept.roi", language), concept_data["roi"], icon_svg=_GENERATED_RESULT_ICONS["roi"])
    render_result_box(translate("concept.investor_summary", language), concept_data["investor_summary"], icon_svg=_GENERATED_RESULT_ICONS["investor"])


def _render_delivery_metrics(concept_data):
    language = get_current_language()
    render_generated_section_heading(translate("concept.delivery_metrics", language), _GENERATED_SECTION_ICONS["metrics"])
    render_result_box(translate("concept.concept_difficulty", language), concept_data["difficulty"], icon_svg=_GENERATED_RESULT_ICONS["concept_complexity"], visual_variant="blue")
    render_result_box(translate("concept.modern_difficulty", language), concept_data["modern_difficulty"], icon_svg=_GENERATED_RESULT_ICONS["modern_complexity"], visual_variant="blue")
    render_result_box(
        translate("concept.development_time", language),
        concept_data["dev_time"],
        extra_bottom_spacing=True,
        icon_svg=_GENERATED_RESULT_ICONS["development_time"],
        visual_variant="blue",
    )


def _safe_pdf_filename(title):
    raw_title = "" if title is None else str(title)
    cleaned_title = "".join(
        character
        for character in raw_title
        if not unicodedata.category(character).startswith("C")
    )
    cleaned_title = cleaned_title.replace("/", "_").replace("\\", "_")
    cleaned_title = "".join(
        character if character.isalnum() or character in " ._-" else "_"
        for character in cleaned_title
    )
    cleaned_title = "_".join(cleaned_title.split())
    while "__" in cleaned_title:
        cleaned_title = cleaned_title.replace("__", "_")
    cleaned_title = cleaned_title.strip(" ._")[:100].rstrip(" ._")

    if not cleaned_title or cleaned_title in {".", ".."}:
        cleaned_title = "leonardo_project"

    return f"{cleaned_title}.pdf"


def _render_pdf_export(concept_data, title):
    language = get_current_language()
    pdf_filename = _safe_pdf_filename(title)

    if st.button(translate("concept.export_pdf", language), key="export_pdf_main"):
        try:
            current_concept_id = get_current_concept_id()
            pdf_data = export_project_package(concept_data, current_concept_id, language=language)
        except Exception:
            st.error(translate("concept.pdf_error", language))
        else:
            st.download_button(
                label=translate("concept.download_pdf", language),
                data=pdf_data,
                file_name=pdf_filename,
                mime="application/pdf",
                key="download_pdf_main",
            )


def _run_pending_automatic_image_generation(concept_data, concept_id):
    if get_automatic_image_pending_concept_id() != concept_id:
        return

    try:
        results = generate_and_save_concept_images(concept_data, concept_id)
        errors = {
            image_type: result["error"]
            for image_type, result in results.items()
            if result["status"] == "failed"
        }
    except Exception:
        errors = {
            image_type: "Image generation failed. Please try again later."
            for image_type in CONCEPT_IMAGE_TYPES
        }

    finish_automatic_image_generation(concept_id, errors)
    st.rerun()


def render_concept_result(concept_data):
    title = concept_data["title"]
    current_concept_id = get_current_concept_id()
    concept_images = (
        get_concept_image_slots(current_concept_id)
        if current_concept_id is not None
        else {}
    )
    is_pending = (
        current_concept_id is not None
        and get_automatic_image_pending_concept_id() == current_concept_id
    )
    image_errors = (
        get_automatic_image_errors(current_concept_id)
        if current_concept_id is not None
        else {}
    )

    st.success(translate("concept.generated", get_current_language()))

    _render_leonardo_vision(
        concept_data,
        current_concept_id,
        concept_images,
        is_pending,
        image_errors,
    )
    _render_modern_implementation(
        concept_data,
        title,
        current_concept_id,
        concept_images,
        is_pending,
        image_errors,
    )
    _render_visual_generation(concept_data)
    _render_implementation_roadmap(concept_data)
    _render_risks_and_constraints(concept_data)
    _render_commercial_outlook(concept_data)
    render_voice_assistant(concept_data)
    _render_delivery_metrics(concept_data)
    _render_pdf_export(concept_data, title)
    if current_concept_id is not None:
        _run_pending_automatic_image_generation(concept_data, current_concept_id)
