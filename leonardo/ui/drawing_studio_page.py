import streamlit as st

from application.concepts import (
    ConceptLoadError,
    list_recent_concepts,
    load_concept_for_viewer,
)
from application.engineering_parameters import (
    load_engineering_parameters_for_viewer,
    save_engineering_parameter_values,
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


def _render_parameter_rows(
    concept_id,
    parameter_set,
    group_name,
    language,
    edit_mode,
):
    parameters = parameter_set[group_name]
    if not parameters:
        st.caption(translate("engineering_parameters.none_suggested", language))
        return {}

    headings = st.columns((2.3, 1.5, 2.3, 1.2))
    for column, key in zip(
        (headings[2], headings[3]),
        ("value", "unit"),
    ):
        column.markdown(f"**{translate(f'engineering_parameters.{key}', language)}**")

    rendered_values = {}
    for parameter in parameters:
        row = st.columns(
            (2.3, 1.5, 2.3, 1.2),
            vertical_alignment="center",
        )
        row[0].markdown(f"**{_parameter_label(parameter, language)}**")
        value = row[2].text_input(
            translate("engineering_parameters.value", language),
            value=parameter["value"] or "",
            key=f"engineering_parameter_value_{concept_id}_{parameter['key']}",
            label_visibility="collapsed",
            disabled=not edit_mode,
            width=360,
        ).strip() or None
        unit = row[3].text_input(
            translate("engineering_parameters.unit", language),
            value=parameter["unit"] or "",
            key=(
                f"engineering_parameter_unit_{concept_id}_"
                f"{parameter['key']}_{language}"
            ),
            label_visibility="collapsed",
            disabled=not edit_mode,
        ).strip() or None
        rendered_values[parameter["key"]] = (value, unit)
        if group_name == "project_specific" and parameter["rationale"]:
            st.caption(
                f"{translate('engineering_parameters.ai_suggestion', language)}: "
                f"{parameter['rationale']}"
            )
        st.space("small" if parameter is parameters[-1] else "xxsmall")

    return rendered_values


def _render_engineering_parameters(
    concept_id,
    concept_data,
    category,
    language,
):
    parameter_set = load_engineering_parameters_for_viewer(concept_id, language)
    readiness = calculate_readiness(parameter_set)

    for group_name, heading_key in (
        ("universal", "universal"),
        ("project_specific", "project_specific"),
    ):
        edit_mode_key = f"engineering_parameters_edit_mode_{concept_id}_{group_name}"
        edit_mode = bool(st.session_state.get(edit_mode_key, False))
        if group_name == "project_specific":
            with st.container(
                horizontal=True,
                horizontal_alignment="left",
                vertical_alignment="center",
                gap="small",
            ):
                st.subheader(
                    translate(f"engineering_parameters.{heading_key}", language),
                    width="content",
                )
                suggest_clicked = st.button(
                    translate("engineering_parameters.suggest", language),
                    key=f"engineering_parameters_suggest_{concept_id}",
                    help=translate("engineering_parameters.suggest", language),
                    type="secondary",
                    width=32,
                )
        else:
            st.subheader(translate(f"engineering_parameters.{heading_key}", language))

        if group_name == "project_specific" and suggest_clicked:
            try:
                stored = get_engineering_parameter_set(concept_id)
                source_parameter_set = validate_parameter_set(
                    stored or build_empty_parameter_set()
                )
                suggestions = suggest_project_parameters(
                    concept_data,
                    category,
                    get_concept_prompt(concept_id),
                    language,
                )
                source_parameter_set = merge_project_suggestions(
                    source_parameter_set,
                    suggestions,
                )
                save_engineering_parameter_set(
                    concept_id,
                    source_parameter_set,
                    source_language=language,
                )
                st.rerun()
            except (RuntimeError, ValueError):
                st.error(translate("engineering_parameters.suggestion_error", language))

        rendered_values = _render_parameter_rows(
            concept_id,
            parameter_set,
            group_name,
            language,
            edit_mode,
        )

        with st.container(
            horizontal=True,
            horizontal_alignment="right",
            vertical_alignment="center",
            gap="small",
        ):
            edit_clicked = st.button(
                translate("engineering_parameters.edit", language),
                key=f"engineering_parameters_edit_{concept_id}_{group_name}",
                disabled=edit_mode,
                type="secondary",
                width="content",
            )
            save_clicked = st.button(
                translate("engineering_parameters.save", language),
                key=f"engineering_parameters_save_{concept_id}_{group_name}",
                disabled=not edit_mode,
                type="secondary",
                width="content",
            )
        if group_name == "universal":
            st.space("xxsmall")

        if edit_clicked:
            st.session_state[edit_mode_key] = True
            st.rerun()

        if save_clicked:
            save_engineering_parameter_values(
                concept_id,
                parameter_set,
                group_name,
                rendered_values,
            )
            st.session_state[edit_mode_key] = False
            st.rerun()


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

    st.space(40)
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
