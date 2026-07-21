import base64
import html
import unicodedata

import streamlit as st

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
from ui.formatting import pretty_label
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
            else f"Create an idea in {pretty_label(category)}"
        )

        with st.spinner("Generating concept..."):

            concept_data, concept_id = generate_and_save_concept(
                category=category,
                creativity_mode=creativity_mode,
                audience=audience,
                user_prompt=prompt_text,
            )

        set_current_concept(concept_data, concept_id)
        start_automatic_image_generation(concept_id)
        st.rerun()

    return concept_data


def _render_concept_image_slot(
    image_type,
    placeholder_text,
    concept_images,
    is_pending,
    image_errors,
):
    image = concept_images.get(image_type)
    escaped_label = html.escape(placeholder_text, quote=True)

    if image:
        image_base64 = base64.b64encode(image[3]).decode("ascii")
        slot_content = (
            f'<img src="data:image/png;base64,{image_base64}" alt="{escaped_label}">'
        )
        extra_attributes = ""
    elif is_pending:
        slot_content = "Generating image…"
        extra_attributes = ' aria-busy="true"'
    elif image_type in image_errors:
        slot_content = "Image generation failed"
        extra_attributes = ""
    else:
        slot_content = html.escape(placeholder_text)
        extra_attributes = ""

    st.markdown(
        f'<div class="concept-image-slot" role="img" aria-label="{escaped_label}"{extra_attributes}>{slot_content}</div>',
        unsafe_allow_html=True,
    )


def _render_leonardo_vision(
    concept_data,
    concept_images,
    is_pending,
    image_errors,
):
    with st.container(border=False, key="leonardo_section"):
        st.markdown("## 🪶 Leonardo Vision")
        st.caption("Renaissance-inspired interpretation of the idea")

        img_cols = st.columns(3)
        with img_cols[0]:
            _render_concept_image_slot(
                LEONARDO_CONCEPT_IMAGE_TYPES[0],
                "Leonardo scene image 1",
                concept_images,
                is_pending,
                image_errors,
            )
        with img_cols[1]:
            _render_concept_image_slot(
                LEONARDO_CONCEPT_IMAGE_TYPES[1],
                "Leonardo scene image 2",
                concept_images,
                is_pending,
                image_errors,
            )
        with img_cols[2]:
            _render_concept_image_slot(
                LEONARDO_CONCEPT_IMAGE_TYPES[2],
                "Leonardo scene image 3",
                concept_images,
                is_pending,
                image_errors,
            )

        render_result_box("Concept", concept_data["leonardo_concept"])
        render_result_box("Sketch Description", concept_data["leonardo_sketch_description"])

    st.markdown('</div>', unsafe_allow_html=True)


def _render_modern_implementation(
    concept_data,
    title,
    concept_images,
    is_pending,
    image_errors,
):
    with st.container(border=False, key="modern_section"):
        st.markdown("## ⚡ Modern Implementation")
        st.caption("Modern product, business and engineering interpretation")

        img_cols = st.columns(3)
        with img_cols[0]:
            _render_concept_image_slot(
                MODERN_CONCEPT_IMAGE_TYPES[0],
                "Modern use-case image 1",
                concept_images,
                is_pending,
                image_errors,
            )
        with img_cols[1]:
            _render_concept_image_slot(
                MODERN_CONCEPT_IMAGE_TYPES[1],
                "Modern use-case image 2",
                concept_images,
                is_pending,
                image_errors,
            )
        with img_cols[2]:
            _render_concept_image_slot(
                MODERN_CONCEPT_IMAGE_TYPES[2],
                "Modern use-case image 3",
                concept_images,
                is_pending,
                image_errors,
            )

        render_result_box("Title", title)
        render_result_box("Product Name", concept_data["modern_product_name"])
        render_result_box("Category", concept_data["modern_category"])
        render_result_box("Executive Summary", concept_data["executive_summary"])

        st.markdown("## Business Need")
        render_result_box("Problem Statement", concept_data["problem_statement"])
        render_result_box("Target Users", concept_data["target_users"])
        render_result_box("Industries", concept_data["industries"])
        render_result_box("Use Cases", concept_data["use_cases"])

        st.markdown("## Engineering")
        render_result_box("Modern Principle", concept_data["modern_principle"])
        render_result_box("System Components", concept_data["system_components"])
        render_result_box("Materials", concept_data["materials"])
        render_result_box("Technical Requirements", concept_data["technical_requirements"])
        render_result_box("Modern Sketch Description", concept_data["modern_sketch_description"])

    st.markdown('</div>', unsafe_allow_html=True)


def _render_visual_generation(concept_data):
    st.markdown("## Visual Generation")
    render_result_box("Leonardo Sketch Prompt", concept_data["leonardo_sketch_description"])
    render_result_box(
        "Modern Blueprint Prompt",
        concept_data["modern_sketch_description"],
        extra_bottom_spacing=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        generate_leonardo_image = st.button("🖼 Generate Leonardo Sketch", use_container_width=True)
    with col2:
        generate_blueprint_image = st.button("📐 Generate Modern Blueprint", use_container_width=True)

    if generate_leonardo_image:
        with st.spinner("Generating Leonardo sketch..."):
            try:
                st.session_state[LEONARDO_ASSET] = generate_leonardo_visual(
                    concept_data["leonardo_sketch_description"]
                )
            except Exception as e:
                st.error(f"Leonardo sketch generation failed: {e}")

    if generate_blueprint_image:
        with st.spinner("Generating modern blueprint..."):
            try:
                st.session_state[BLUEPRINT_ASSET] = generate_blueprint_visual(
                    concept_data["modern_sketch_description"]
                )
            except Exception as e:
                st.error(f"Blueprint generation failed: {e}")

    render_generated_visuals()


def _render_implementation_roadmap(concept_data):
    st.markdown("## Implementation Roadmap")
    guides = concept_data["implementation_guides"]
    render_complete_guide("Prototype", guides["prototype"])
    render_complete_guide("MVP", guides["mvp"])
    render_complete_guide("Pilot", guides["pilot"])
    render_complete_guide("Production", guides["production"])

    render_result_box("Deployment Strategy", concept_data["deployment_strategy"])


def _render_risks_and_constraints(concept_data):
    st.markdown("## Risks and Constraints")
    render_result_box("Risks", concept_data["risks"])
    render_result_box("Constraints", concept_data["constraints"])


def _render_commercial_outlook(concept_data):
    st.markdown("## Commercial Outlook")
    render_result_box("Market Demand", concept_data["market_demand"])
    render_result_box("Startup Cost", concept_data["startup_cost"])
    render_result_box("ROI", concept_data["roi"])
    render_result_box("Investor Summary", concept_data["investor_summary"])


def _render_delivery_metrics(concept_data):
    st.markdown("## Delivery Metrics")
    render_result_box("Concept Difficulty", concept_data["difficulty"])
    render_result_box("Modern Difficulty", concept_data["modern_difficulty"])
    render_result_box(
        "Development Time",
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
    pdf_filename = _safe_pdf_filename(title)

    if st.button("📦 Export Full Project Package (PDF)", key="export_pdf_main"):
        try:
            current_concept_id = get_current_concept_id()
            pdf_data = export_project_package(concept_data, current_concept_id)
        except Exception:
            st.error("PDF export failed. Please try again.")
        else:
            st.download_button(
                label="Download PDF",
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

    st.success("Concept generated successfully.")

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
