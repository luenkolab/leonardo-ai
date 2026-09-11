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
    list_concept_images,
    map_automatic_concept_images,
)
from application.project_export import export_project_package
from ui.components import render_complete_guide, render_result_box
from ui.images import render_generated_visuals, render_saved_images
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
        image_base64 = base64.b64encode(image[3]).decode("ascii")
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
    concept_images,
    is_pending,
    image_errors,
):
    language = get_current_language()
    with st.container(border=False, key="leonardo_section"):
        st.markdown(f"## 🪶 {translate('concept.leonardo_vision', language)}")
        st.caption(translate("concept.leonardo_subtitle", language))

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

        render_result_box(translate("concept.concept", language), concept_data["leonardo_concept"])
        render_result_box(translate("concept.sketch_description", language), concept_data["leonardo_sketch_description"])

    st.markdown('</div>', unsafe_allow_html=True)


def _render_modern_implementation(
    concept_data,
    title,
    concept_images,
    is_pending,
    image_errors,
):
    language = get_current_language()
    with st.container(border=False, key="modern_section"):
        st.markdown(f"## ⚡ {translate('concept.modern_implementation', language)}")
        st.caption(translate("concept.modern_subtitle", language))

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

        render_result_box(translate("concept.title", language), title)
        render_result_box(translate("concept.product_name", language), concept_data["modern_product_name"])
        render_result_box(translate("common.category", language), concept_data["modern_category"])
        render_result_box(translate("concept.executive_summary", language), concept_data["executive_summary"])

        st.markdown(f"## {translate('concept.business_need', language)}")
        render_result_box(translate("concept.problem_statement", language), concept_data["problem_statement"])
        render_result_box(translate("concept.target_users", language), concept_data["target_users"])
        render_result_box(translate("concept.industries", language), concept_data["industries"])
        render_result_box(translate("concept.use_cases", language), concept_data["use_cases"])

        st.markdown(f"## {translate('concept.engineering', language)}")
        render_result_box(translate("concept.modern_principle", language), concept_data["modern_principle"])
        render_result_box(translate("concept.system_components", language), concept_data["system_components"])
        render_result_box(translate("concept.materials", language), concept_data["materials"])
        render_result_box(translate("concept.technical_requirements", language), concept_data["technical_requirements"])
        render_result_box(translate("concept.modern_sketch_description", language), concept_data["modern_sketch_description"])

    st.markdown('</div>', unsafe_allow_html=True)


def _render_visual_generation(concept_data):
    language = get_current_language()
    st.markdown(f"## {translate('concept.visual_generation', language)}")
    render_result_box(translate("concept.leonardo_prompt", language), concept_data["leonardo_sketch_description"])
    render_result_box(
        translate("concept.blueprint_prompt", language),
        concept_data["modern_sketch_description"],
        extra_bottom_spacing=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        generate_leonardo_image = st.button(f"🖼 {translate('concept.generate_leonardo', language)}", use_container_width=True)
    with col2:
        generate_blueprint_image = st.button(f"📐 {translate('concept.generate_blueprint', language)}", use_container_width=True)

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
    st.markdown(f"## {translate('concept.roadmap', language)}")
    guides = concept_data["implementation_guides"]
    render_complete_guide(translate("concept.prototype", language), guides["prototype"])
    render_complete_guide(translate("concept.mvp", language), guides["mvp"])
    render_complete_guide(translate("concept.pilot", language), guides["pilot"])
    render_complete_guide(translate("concept.production", language), guides["production"])

    render_result_box(translate("concept.deployment_strategy", language), concept_data["deployment_strategy"])


def _render_risks_and_constraints(concept_data):
    language = get_current_language()
    st.markdown(f"## {translate('concept.risks_constraints', language)}")
    render_result_box(translate("concept.risks", language), concept_data["risks"])
    render_result_box(translate("concept.constraints", language), concept_data["constraints"])


def _render_commercial_outlook(concept_data):
    language = get_current_language()
    st.markdown(f"## {translate('concept.commercial_outlook', language)}")
    render_result_box(translate("concept.market_demand", language), concept_data["market_demand"])
    render_result_box(translate("concept.startup_cost", language), concept_data["startup_cost"])
    render_result_box(translate("concept.roi", language), concept_data["roi"])
    render_result_box(translate("concept.investor_summary", language), concept_data["investor_summary"])


def _render_delivery_metrics(concept_data):
    language = get_current_language()
    st.markdown(f"## {translate('concept.delivery_metrics', language)}")
    render_result_box(translate("concept.concept_difficulty", language), concept_data["difficulty"])
    render_result_box(translate("concept.modern_difficulty", language), concept_data["modern_difficulty"])
    render_result_box(
        translate("concept.development_time", language),
        concept_data["dev_time"],
        extra_bottom_spacing=True,
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

    if st.button(f"📦 {translate('concept.export_pdf', language)}", key="export_pdf_main"):
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
        map_automatic_concept_images(list_concept_images(current_concept_id))
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
        concept_images,
        is_pending,
        image_errors,
    )
    _render_modern_implementation(
        concept_data,
        title,
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
    render_saved_images()
    if current_concept_id is not None:
        _run_pending_automatic_image_generation(concept_data, current_concept_id)
