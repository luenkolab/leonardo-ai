import html

import streamlit as st

from application.concepts import (
    ConceptLoadError,
    list_recent_concepts,
    load_concept_for_viewer,
)
from application.engineering_parameters import (
    load_engineering_parameters_for_viewer,
    save_component_geometry_values,
    save_engineering_parameter_values,
    save_overall_envelope_values,
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
    merge_project_suggestions,
    suggest_project_parameters,
    validate_parameter_set,
)
from services.general_arrangement_service import (
    SUPPORTED_LENGTH_UNITS,
    build_component_projections,
    build_general_arrangement,
    build_envelope_views,
    calculate_display_rectangle,
    has_prepared_geometry,
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


def _render_overall_envelope_inputs(
    concept_id,
    general_arrangement,
    language,
):
    envelope = general_arrangement.overall_envelope
    measurements = (envelope.length, envelope.width, envelope.height)
    current_unit = next(
        (
            measurement.raw_unit.casefold()
            for measurement in measurements
            if measurement is not None
            and measurement.raw_unit.casefold() in SUPPORTED_LENGTH_UNITS
        ),
        SUPPORTED_LENGTH_UNITS[0],
    )
    columns = st.columns(4)
    rendered_values = {}
    for column, axis, measurement in zip(
        columns[:3],
        ("length", "width", "height"),
        measurements,
    ):
        rendered_values[axis] = column.text_input(
            translate(f"drawing_studio.envelope.{axis}", language),
            value=measurement.raw_value if measurement is not None else "",
            key=f"general_arrangement_{axis}_{concept_id}",
        ).strip()
    selected_unit = columns[3].selectbox(
        translate("engineering_parameters.unit", language),
        SUPPORTED_LENGTH_UNITS,
        index=SUPPORTED_LENGTH_UNITS.index(current_unit),
        key=f"general_arrangement_unit_{concept_id}",
    )

    with st.container(
        horizontal=True,
        horizontal_alignment="right",
        vertical_alignment="center",
    ):
        save_clicked = st.button(
            translate("engineering_parameters.save", language),
            key=f"general_arrangement_save_{concept_id}",
            type="secondary",
        )
    if not save_clicked:
        return

    try:
        save_overall_envelope_values(
            concept_id,
            rendered_values["length"],
            rendered_values["width"],
            rendered_values["height"],
            selected_unit,
        )
    except ValueError:
        st.error(translate("drawing_studio.envelope.invalid_value", language))
        return
    st.rerun()


def _measurement_label(measurement):
    value = format(measurement.value, "f")
    if "." in value:
        value = value.rstrip("0").rstrip(".")
    return f"{value} {measurement.unit}"


def _render_component_geometry_inputs(concept_id, general_arrangement, language):
    if not general_arrangement.components:
        return
    st.subheader(translate("drawing_studio.ga.component_geometry", language))
    for component in general_arrangement.components:
        st.markdown(f"**{html.escape(component.name)}**")
        measurements = (
            component.dimensions.length,
            component.dimensions.width,
            component.dimensions.height,
            component.position.x if component.position else None,
            component.position.y if component.position else None,
            component.position.z if component.position else None,
        )
        current_unit = next(
            (
                measurement.raw_unit.casefold()
                for measurement in measurements
                if measurement is not None
                and measurement.raw_unit.casefold() in SUPPORTED_LENGTH_UNITS
            ),
            SUPPORTED_LENGTH_UNITS[0],
        )
        dimension_columns = st.columns(4)
        coordinate_columns = st.columns(3)
        rendered = {}
        for column, field, measurement in zip(
            dimension_columns[:3],
            ("length", "width", "height"),
            measurements[:3],
        ):
            rendered[field] = column.text_input(
                translate(f"drawing_studio.envelope.{field}", language),
                value=measurement.raw_value if measurement else "",
                key=f"ga_component_{concept_id}_{component.key}_{field}",
            ).strip()
        selected_unit = dimension_columns[3].selectbox(
            translate("engineering_parameters.unit", language),
            SUPPORTED_LENGTH_UNITS,
            index=SUPPORTED_LENGTH_UNITS.index(current_unit),
            key=f"ga_component_{concept_id}_{component.key}_unit",
        )
        for column, field, measurement in zip(
            coordinate_columns,
            ("x", "y", "z"),
            measurements[3:],
        ):
            rendered[field] = column.text_input(
                translate(f"drawing_studio.ga.position_{field}", language),
                value=measurement.raw_value if measurement else "",
                key=f"ga_component_{concept_id}_{component.key}_{field}",
            ).strip()
        if st.button(
            translate("engineering_parameters.save", language),
            key=f"ga_component_{concept_id}_{component.key}_save",
            type="secondary",
        ):
            try:
                save_component_geometry_values(
                    concept_id,
                    component.key,
                    rendered["length"],
                    rendered["width"],
                    rendered["height"],
                    rendered["x"],
                    rendered["y"],
                    rendered["z"],
                    selected_unit,
                )
            except ValueError:
                st.error(
                    translate("drawing_studio.ga.invalid_component_geometry", language)
                )
            else:
                st.rerun()


def _general_arrangement_view_markup(
    view,
    title,
    missing_message,
    component_projections=(),
    assembly_item_numbers=None,
):
    display = calculate_display_rectangle(view)
    safe_title = html.escape(title)
    if display is None:
        return f"""
<div style="border:1px solid rgba(73, 112, 140, 0.32); border-radius:10px; padding:14px; margin-top:10px; background:rgba(229, 242, 250, 0.28);">
  <div style="font-weight:650; margin-bottom:8px;">{safe_title}</div>
  <div style="font-size:0.9rem; opacity:0.72;">{html.escape(missing_message)}</div>
</div>
"""

    area_x, area_y = 65.0, 30.0
    area_width, area_height = 220.0, 130.0
    rectangle_width = float(display.width)
    rectangle_height = float(display.height)
    rectangle_x = area_x + (area_width - rectangle_width) / 2
    rectangle_y = area_y + (area_height - rectangle_height) / 2
    horizontal_y = rectangle_y + rectangle_height + 28
    vertical_x = rectangle_x - 28
    horizontal_label = html.escape(_measurement_label(view.horizontal))
    vertical_label = html.escape(_measurement_label(view.vertical))
    arrow_id = f"ga-arrow-{view.key}"
    assembly_item_numbers = assembly_item_numbers or {}
    component_rectangles = []
    for projection in component_projections:
        if projection.out_of_envelope:
            continue
        component_width = float(projection.horizontal_size.value * display.scale)
        component_height = float(projection.vertical_size.value * display.scale)
        component_x = rectangle_x + float(
            projection.horizontal_position.value * display.scale
        )
        component_y = rectangle_y + rectangle_height - float(
            (
                projection.vertical_position.value
                + projection.vertical_size.value
            )
            * display.scale
        )
        component_rectangles.append(
            f'<rect data-component-key="{html.escape(projection.component_key)}" '
            f'x="{component_x:.2f}" y="{component_y:.2f}" '
            f'width="{component_width:.2f}" height="{component_height:.2f}" '
            'fill="rgba(39, 125, 161, 0.24)" stroke="#277da1" '
            'stroke-width="1.2"/>'
        )
        item_number = assembly_item_numbers.get(projection.component_key)
        if item_number is not None:
            component_rectangles.append(
                f'<text data-assembly-item="{item_number}" '
                f'x="{component_x + component_width / 2:.2f}" '
                f'y="{component_y + component_height / 2:.2f}" '
                'text-anchor="middle" dominant-baseline="central" '
                'font-size="11" font-weight="700" fill="#173f55">'
                f'{item_number}</text>'
            )
    components_markup = "\n    ".join(component_rectangles)

    return f"""
<div style="border:1px solid rgba(73, 112, 140, 0.32); border-radius:10px; padding:10px; margin-top:10px; background:rgba(229, 242, 250, 0.18);">
  <div style="font-weight:650; margin:2px 4px 4px;">{safe_title}</div>
  <svg viewBox="0 0 320 220" role="img" aria-label="{safe_title}" style="display:block; width:100%; height:auto;">
    <defs>
      <marker id="{arrow_id}" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse">
        <path d="M0,0 L7,3.5 L0,7 Z" fill="#315f78"/>
      </marker>
    </defs>
    <rect x="{rectangle_x:.2f}" y="{rectangle_y:.2f}" width="{rectangle_width:.2f}" height="{rectangle_height:.2f}" fill="rgba(102, 177, 214, 0.10)" stroke="#315f78" stroke-width="1.8"/>
    {components_markup}
    <line x1="{rectangle_x:.2f}" y1="{horizontal_y:.2f}" x2="{rectangle_x + rectangle_width:.2f}" y2="{horizontal_y:.2f}" stroke="#315f78" stroke-width="1" marker-start="url(#{arrow_id})" marker-end="url(#{arrow_id})"/>
    <line x1="{rectangle_x:.2f}" y1="{rectangle_y + rectangle_height:.2f}" x2="{rectangle_x:.2f}" y2="{horizontal_y + 5:.2f}" stroke="#6b8798" stroke-width="0.8"/>
    <line x1="{rectangle_x + rectangle_width:.2f}" y1="{rectangle_y + rectangle_height:.2f}" x2="{rectangle_x + rectangle_width:.2f}" y2="{horizontal_y + 5:.2f}" stroke="#6b8798" stroke-width="0.8"/>
    <text x="{rectangle_x + rectangle_width / 2:.2f}" y="{horizontal_y + 17:.2f}" text-anchor="middle" font-size="11" fill="#254b61">{horizontal_label}</text>
    <line x1="{vertical_x:.2f}" y1="{rectangle_y:.2f}" x2="{vertical_x:.2f}" y2="{rectangle_y + rectangle_height:.2f}" stroke="#315f78" stroke-width="1" marker-start="url(#{arrow_id})" marker-end="url(#{arrow_id})"/>
    <line x1="{vertical_x - 5:.2f}" y1="{rectangle_y:.2f}" x2="{rectangle_x:.2f}" y2="{rectangle_y:.2f}" stroke="#6b8798" stroke-width="0.8"/>
    <line x1="{vertical_x - 5:.2f}" y1="{rectangle_y + rectangle_height:.2f}" x2="{rectangle_x:.2f}" y2="{rectangle_y + rectangle_height:.2f}" stroke="#6b8798" stroke-width="0.8"/>
    <text x="{vertical_x - 9:.2f}" y="{rectangle_y + rectangle_height / 2:.2f}" text-anchor="middle" font-size="11" fill="#254b61" transform="rotate(-90 {vertical_x - 9:.2f} {rectangle_y + rectangle_height / 2:.2f})">{vertical_label}</text>
  </svg>
</div>
"""


def _render_general_arrangement_views(general_arrangement, language):
    missing_message = translate("drawing_studio.ga.insufficient_view_data", language)
    outside_components = set()
    for view in build_envelope_views(general_arrangement):
        projections = build_component_projections(general_arrangement, view)
        outside_components.update(
            projection.component_name
            for projection in projections
            if projection.out_of_envelope
        )
        st.markdown(
            _general_arrangement_view_markup(
                view,
                translate(f"drawing_studio.ga.{view.key}_view", language),
                missing_message,
                projections,
            ),
            unsafe_allow_html=True,
        )
    if outside_components:
        st.warning(
            f"{translate('drawing_studio.ga.outside_envelope', language)} "
            f"{', '.join(sorted(outside_components))}"
        )


def _orthographic_view_data(general_arrangement):
    views = {view.key: view for view in build_envelope_views(general_arrangement)}
    return tuple(
        (views[key], build_component_projections(general_arrangement, views[key]))
        for key in ("front", "top", "side")
    )


def _render_projected_views(view_data, language, assembly_item_numbers=None):
    missing_message = translate("drawing_studio.ga.insufficient_view_data", language)
    outside_components = set()
    columns = st.columns(3)
    for column, (view, projections) in zip(
        columns,
        view_data,
    ):
        outside_components.update(
            projection.component_name
            for projection in projections
            if projection.out_of_envelope
        )
        with column:
            st.markdown(
                _general_arrangement_view_markup(
                    view,
                    translate(f"drawing_studio.ga.{view.key}_view", language),
                    missing_message,
                    projections,
                    assembly_item_numbers,
                ),
                unsafe_allow_html=True,
            )
    if outside_components:
        st.warning(
            f"{translate('drawing_studio.ga.outside_envelope', language)} "
            f"{', '.join(sorted(outside_components))}"
        )


def _render_orthographic_views(general_arrangement, language):
    _render_projected_views(
        _orthographic_view_data(general_arrangement),
        language,
    )


def _assembly_view_data(general_arrangement):
    view_data = _orthographic_view_data(general_arrangement)
    visible_keys = {
        projection.component_key
        for _view, projections in view_data
        for projection in projections
        if not projection.out_of_envelope
    }
    numbered_components = tuple(
        (number, component)
        for number, component in enumerate(
            (
                component
                for component in general_arrangement.components
                if component.key in visible_keys
            ),
            start=1,
        )
    )
    return view_data, numbered_components


def _assembly_legend_markup(numbered_components, title):
    items = "".join(
        f"<div>{number} — {html.escape(component.name)}</div>"
        for number, component in numbered_components
    )
    return (
        '<div style="border:1px solid rgba(73, 112, 140, 0.32); '
        'border-radius:10px; padding:12px; margin-top:10px;">'
        f'<div style="font-weight:650; margin-bottom:6px;">{html.escape(title)}</div>'
        f"{items}</div>"
    )


def _render_assembly_drawings(general_arrangement, language):
    view_data, numbered_components = _assembly_view_data(general_arrangement)
    item_numbers = {
        component.key: number for number, component in numbered_components
    }
    _render_projected_views(view_data, language, item_numbers)
    if numbered_components:
        st.markdown(
            _assembly_legend_markup(
                numbered_components,
                translate("concept.system_components", language),
            ),
            unsafe_allow_html=True,
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
    general_arrangement = build_general_arrangement(
        concept_data,
        validate_parameter_set(
            get_engineering_parameter_set(concept_id) or build_empty_parameter_set()
        ),
    )
    general_arrangement_status = translate(
        (
            "drawing_studio.geometry_data_prepared"
            if has_prepared_geometry(general_arrangement)
            else "drawing_studio.additional_geometry_data_required"
        ),
        language,
    )
    package_columns = st.columns(2)
    for index, item in enumerate(package_items):
        with package_columns[index % 2]:
            if item == "general_arrangement":
                package_content = general_arrangement_status
            elif item in {"orthographic_views", "assembly_drawings"}:
                package_content = " · ".join(
                    translate(f"drawing_studio.ga.{key}_view", language)
                    for key in ("front", "top", "side")
                )
            else:
                package_content = translate("drawing_studio.not_generated", language)
            render_result_box(
                translate(f"drawing_studio.{item}", language),
                package_content,
                visual_variant="blue",
            )
            if item == "general_arrangement":
                _render_overall_envelope_inputs(
                    concept_id,
                    general_arrangement,
                    language,
                )
                _render_component_geometry_inputs(
                    concept_id,
                    general_arrangement,
                    language,
                )
                _render_general_arrangement_views(
                    general_arrangement,
                    language,
                )
            elif item == "orthographic_views":
                _render_orthographic_views(
                    general_arrangement,
                    language,
                )
            elif item == "assembly_drawings":
                _render_assembly_drawings(
                    general_arrangement,
                    language,
                )
