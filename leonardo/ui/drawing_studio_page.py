import streamlit as st

from application.concepts import (
    ConceptLoadError,
    list_recent_concepts,
    load_concept_for_viewer,
)
from application.images import MODERN_CONCEPT_IMAGE_TYPES, get_concept_image_slots
from database import (
    get_concept_prompt,
    get_engineering_parameter_set,
    save_engineering_parameter_set,
)
from i18n import category_display_name, translate
from services.engineering_parameters_service import (
    build_empty_parameter_set,
    calculate_readiness,
    merge_project_suggestions,
    suggest_project_parameters,
    update_parameter,
    validate_parameter_set,
)
from ui.components import render_generated_section_heading, render_result_box
from ui.concept_page import _render_concept_image_slot
from ui.state import get_current_concept_id, get_current_language, set_current_page


_STUDIO_SECTION_ICON = """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="5" r="2"/><path d="m11 7-5 13M13 7l5 13M8.2 14h7.6M5 20h4M15 20h4"/></svg>"""


def _parameter_label(parameter, language):
    if parameter["key"] in {item["key"] for item in build_empty_parameter_set()["universal"]}:
        return translate(
            f"engineering_parameters.universal.{parameter['key']}",
            language,
        )
    return parameter["label"]


def _render_parameter_rows(concept_id, parameter_set, group_name, language):
    parameters = parameter_set[group_name]
    if not parameters:
        st.caption(translate("engineering_parameters.none_suggested", language))
        return

    headings = st.columns((1.7, 2.0, 1.0, 0.9, 4.7))
    for column, key in zip(
        headings,
        ("parameter", "value", "unit", "status", "actions"),
    ):
        column.markdown(f"**{translate(f'engineering_parameters.{key}', language)}**")

    for parameter in parameters:
        row = st.columns(
            (1.7, 2.0, 1.0, 0.9, 4.7),
            vertical_alignment="center",
        )
        row[0].markdown(f"**{_parameter_label(parameter, language)}**")
        value = row[1].text_input(
            translate("engineering_parameters.value", language),
            value=parameter["value"] or "",
            key=f"engineering_parameter_value_{concept_id}_{parameter['key']}",
            label_visibility="collapsed",
        )
        unit = row[2].text_input(
            translate("engineering_parameters.unit", language),
            value=parameter["unit"] or "",
            key=f"engineering_parameter_unit_{concept_id}_{parameter['key']}",
            label_visibility="collapsed",
        )
        row[3].markdown(
            translate(
                f"engineering_parameters.status.{parameter['status']}",
                language,
            )
        )
        if parameter["rationale"]:
            st.caption(
                f"{translate('engineering_parameters.ai_suggestion', language)}: "
                f"{parameter['rationale']}"
            )

        confirm_key = (
            "accept"
            if group_name == "project_specific" and parameter["status"] == "suggested"
            else "confirm"
        )
        with row[4]:
            with st.container(
                horizontal=True,
                horizontal_alignment="right",
                vertical_alignment="center",
                gap="small",
            ):
                edit_clicked = st.button(
                    translate("engineering_parameters.edit", language),
                    key=f"engineering_parameter_edit_{concept_id}_{parameter['key']}",
                )
                confirm_clicked = False
                if parameter["status"] != "confirmed":
                    confirm_clicked = st.button(
                        translate(f"engineering_parameters.{confirm_key}", language),
                        key=f"engineering_parameter_confirm_{concept_id}_{parameter['key']}",
                    )
                not_applicable_clicked = st.button(
                    translate("engineering_parameters.not_applicable", language),
                    key=f"engineering_parameter_na_{concept_id}_{parameter['key']}",
                )
        if not (edit_clicked or confirm_clicked or not_applicable_clicked):
            continue

        action = (
            "not_applicable"
            if not_applicable_clicked
            else "confirm" if confirm_clicked else "edit"
        )
        updated = update_parameter(
            parameter_set,
            group_name,
            parameter["key"],
            value,
            unit,
            action,
        )
        save_engineering_parameter_set(concept_id, updated)
        st.rerun()


def _render_engineering_parameters(
    concept_id,
    concept_data,
    category,
    language,
):
    stored = get_engineering_parameter_set(concept_id)
    parameter_set = validate_parameter_set(stored or build_empty_parameter_set())
    readiness = calculate_readiness(parameter_set)
    render_result_box(
        translate("engineering_parameters.inputs", language),
        [
            translate(f"engineering_parameters.readiness.{readiness}", language),
            translate("engineering_parameters.note", language),
        ],
        visual_variant="blue",
    )

    if st.button(
        translate("engineering_parameters.suggest", language),
        key=f"engineering_parameters_suggest_{concept_id}",
    ):
        try:
            suggestions = suggest_project_parameters(
                concept_data,
                category,
                get_concept_prompt(concept_id),
                language,
            )
            parameter_set = merge_project_suggestions(parameter_set, suggestions)
            save_engineering_parameter_set(concept_id, parameter_set)
            st.rerun()
        except (RuntimeError, ValueError):
            st.error(translate("engineering_parameters.suggestion_error", language))

    st.subheader(translate("engineering_parameters.universal", language))
    _render_parameter_rows(concept_id, parameter_set, "universal", language)
    st.subheader(translate("engineering_parameters.project_specific", language))
    _render_parameter_rows(concept_id, parameter_set, "project_specific", language)


def _get_current_category(concept_id):
    for stored_id, _title, category, _created_at, _favorite in list_recent_concepts(
        limit=-1
    ):
        if stored_id == concept_id:
            return category
    return ""


def _render_reference_visuals(concept_id, language):
    concept_images = get_concept_image_slots(
        concept_id,
        MODERN_CONCEPT_IMAGE_TYPES,
    )
    modern_images = {
        image_type: concept_images[image_type]
        for image_type in MODERN_CONCEPT_IMAGE_TYPES
        if image_type in concept_images
    }

    columns = st.columns(3)
    for index, (column, image_type) in enumerate(
        zip(columns, MODERN_CONCEPT_IMAGE_TYPES),
        start=1,
    ):
        with column:
            _render_concept_image_slot(
                image_type,
                translate("common.image", language, index=index),
                modern_images,
                False,
                {},
            )


def render_drawing_studio():
    language = get_current_language()
    concept_id = get_current_concept_id()

    if st.button(
        translate("drawing_studio.back_to_concept", language),
        key="drawing_studio_back",
    ):
        set_current_page("app")
        st.rerun()
        return

    render_generated_section_heading(
        translate("concept.engineering_drawing_studio", language),
        _STUDIO_SECTION_ICON,
    )
    st.caption(translate("drawing_studio.subtitle", language))

    if concept_id is None:
        st.info(translate("images.no_concept", language))
        return

    try:
        concept_data, _source_language = load_concept_for_viewer(
            concept_id,
            language,
        )
    except ConceptLoadError:
        concept_data = None

    if concept_data is None:
        st.error(translate("sidebar.open_error", language))
        return

    category = _get_current_category(concept_id)

    render_generated_section_heading(
        translate("drawing_studio.project_context", language),
        "",
    )
    render_result_box(
        translate("drawing_studio.project", language),
        concept_data["title"],
    )
    render_result_box(
        translate("common.category", language),
        category_display_name(category, language),
    )
    render_result_box(
        translate("drawing_studio.short_summary", language),
        concept_data["executive_summary"],
    )

    render_generated_section_heading(
        translate("drawing_studio.reference_visuals", language),
        "",
    )
    st.caption(translate("drawing_studio.reference_notice", language))
    _render_reference_visuals(concept_id, language)

    st.space(40)
    render_generated_section_heading(
        translate("drawing_studio.engineering_data", language),
        "",
    )
    for label_key, field_name in (
        ("concept.technical_requirements", "technical_requirements"),
        ("concept.materials", "materials"),
        ("concept.system_components", "system_components"),
        ("concept.constraints", "constraints"),
        ("concept.risks", "risks"),
    ):
        render_result_box(
            translate(label_key, language),
            concept_data[field_name],
            visual_variant="blue",
        )

    render_generated_section_heading(
        translate("drawing_studio.engineering_parameters", language),
        "",
    )
    _render_engineering_parameters(
        concept_id,
        concept_data,
        category,
        language,
    )

    render_generated_section_heading(
        translate("drawing_studio.drawing_package", language),
        "",
    )
    package_items = (
        "general_arrangement",
        "orthographic_views",
        "assembly_drawings",
        "component_detail_drawings",
        "connections_fasteners",
        "bill_of_materials",
    )
    package_columns = st.columns(2)
    for index, item in enumerate(package_items):
        with package_columns[index % 2]:
            render_result_box(
                translate(f"drawing_studio.{item}", language),
                translate("drawing_studio.not_generated", language),
                visual_variant="blue",
            )
