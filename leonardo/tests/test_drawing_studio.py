import copy
import re
from contextlib import nullcontext
from datetime import datetime
from decimal import Decimal

from application.images import MODERN_CONCEPT_IMAGE_TYPES
from services import concept_service, image_service
from ui import concept_page, drawing_studio_page, state


def test_open_drawing_studio_uses_existing_page_route(monkeypatch):
    page_updates = []
    reruns = []
    monkeypatch.setattr(
        concept_page,
        "render_generated_section_heading",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(concept_page.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(concept_page.st, "button", lambda *args, **kwargs: True)
    monkeypatch.setattr(concept_page.st, "rerun", lambda: reruns.append(True))
    monkeypatch.setattr(concept_page, "set_current_page", page_updates.append)

    concept_page._render_engineering_drawing_studio("en")

    assert page_updates == ["drawing_studio"]
    assert reruns == [True]


def test_back_to_concept_preserves_current_concept_state(monkeypatch, valid_concept):
    session_state = {
        state.CURRENT_PAGE: "drawing_studio",
        state.CURRENT_CONCEPT: valid_concept,
        state.CURRENT_CONCEPT_ID: 73,
        state.CURRENT_CONCEPT_LANGUAGE: "ru",
        state.LANGUAGE: "en",
        state.GENERATE_IMAGES: True,
    }
    monkeypatch.setattr(state.st, "session_state", session_state)
    monkeypatch.setattr(drawing_studio_page.st, "container", lambda **kwargs: nullcontext())
    monkeypatch.setattr(
        drawing_studio_page.st,
        "button",
        lambda *args, key=None, **kwargs: key == "drawing_studio_back",
    )
    monkeypatch.setattr(drawing_studio_page.st, "rerun", lambda: None)

    drawing_studio_page.render_drawing_studio()

    assert state.get_current_page() == "app"
    assert state.get_current_concept() is valid_concept
    assert state.get_current_concept_id() == 73
    assert state.get_current_concept_language() == "ru"
    assert state.get_generate_images_enabled() is True


def test_studio_uses_current_concept_and_only_modern_references(
    monkeypatch,
    valid_concept,
):
    image_lookups = []
    rendered_slots = []
    result_boxes = []
    headings = []
    spaces = []
    engineering_parameter_renders = []
    envelope_input_renders = []
    component_input_renders = []
    arrangement_view_renders = []
    orthographic_view_renders = []
    assembly_drawing_renders = []
    component_detail_renders = []
    connection_renders = []
    bom_renders = []
    expanders = []
    containers = []
    drawing_package_order = []
    concept_images = {
        "leonardo_concept_1": (1, 91, "leonardo_concept_1", "prompt", b"old", "date", 0),
        "modern_concept_1": (2, 91, "modern_concept_1", "prompt", b"one", "date", 0),
        "modern_concept_3": (3, 91, "modern_concept_3", "prompt", b"three", "date", 0),
    }
    session_state = {
        state.CURRENT_PAGE: "drawing_studio",
        state.CURRENT_CONCEPT: valid_concept,
        state.CURRENT_CONCEPT_ID: 91,
        state.CURRENT_CONCEPT_LANGUAGE: "en",
        state.LANGUAGE: "en",
    }
    monkeypatch.setattr(state.st, "session_state", session_state)
    def container(**kwargs):
        containers.append(kwargs)
        return nullcontext()

    monkeypatch.setattr(drawing_studio_page.st, "container", container)

    def expander(label, **kwargs):
        expanders.append((label, kwargs))
        drawing_package_order.append(label)
        return nullcontext()

    monkeypatch.setattr(drawing_studio_page.st, "expander", expander)
    monkeypatch.setattr(drawing_studio_page.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(drawing_studio_page.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(drawing_studio_page.st, "space", spaces.append)
    monkeypatch.setattr(
        drawing_studio_page.st,
        "columns",
        lambda count: [nullcontext() for _ in range(count)],
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "render_generated_section_heading",
        lambda title, icon_svg=None, **kwargs: headings.append(
            (title, icon_svg, kwargs)
        ),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "render_result_box",
        lambda title, content, **kwargs: result_boxes.append((title, content, kwargs)),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_engineering_parameters",
        lambda *args: engineering_parameter_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "get_engineering_parameter_set",
        lambda _concept_id: None,
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "load_engineering_parameters_for_viewer",
        lambda _concept_id, _language: drawing_studio_page.build_empty_parameter_set(),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_overall_envelope_inputs",
        lambda *args: envelope_input_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_component_geometry_inputs",
        lambda *args: component_input_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_general_arrangement_views",
        lambda *args: arrangement_view_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_orthographic_views",
        lambda *args: orthographic_view_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_assembly_drawings",
        lambda *args: assembly_drawing_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_component_detail_drawings",
        lambda *args: component_detail_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_connections_fasteners",
        lambda *args: connection_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_bill_of_materials",
        lambda *args: bom_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_drawing_package_export",
        lambda *args: drawing_package_order.append("export"),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "load_concept_for_viewer",
        lambda concept_id, language: (valid_concept, "en"),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "load_concept",
        lambda concept_id: valid_concept,
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "list_recent_concepts",
        lambda limit=-1: [(91, valid_concept["title"], "robotics_automation", "date", 0)],
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "get_concept_image_slots",
        lambda concept_id, image_types: image_lookups.append(
            (concept_id, image_types)
        )
        or concept_images,
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_concept_image_slot",
        lambda image_type, _label, images, *_args: rendered_slots.append(
            (image_type, set(images))
        ),
    )
    monkeypatch.setattr(
        image_service,
        "generate_concept_image",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Studio must not call the image API")
        ),
    )
    monkeypatch.setattr(
        concept_service,
        "generate_concept",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Studio must not generate concept text")
        ),
    )

    drawing_studio_page.render_drawing_studio()

    assert image_lookups == [(91, MODERN_CONCEPT_IMAGE_TYPES)]
    assert headings[0][1] == drawing_studio_page._STUDIO_SECTION_ICON
    assert all(icon_svg == "" for _title, icon_svg, _kwargs in headings[1:])
    engineering_heading = next(
        heading for heading in headings if heading[0] == "Engineering Data"
    )
    assert engineering_heading[2] == {}
    assert spaces == [40, 40, "small"]
    assert tuple(image_type for image_type, _images in rendered_slots) == (
        MODERN_CONCEPT_IMAGE_TYPES
    )
    assert all(
        images <= set(MODERN_CONCEPT_IMAGE_TYPES)
        for _image_type, images in rendered_slots
    )
    rendered_contents = [content for _title, content, _kwargs in result_boxes]
    for field_name in (
        "technical_requirements",
        "materials",
        "system_components",
        "constraints",
        "risks",
    ):
        assert valid_concept[field_name] in rendered_contents
    assert engineering_parameter_renders == [
        (91, valid_concept, valid_concept, "robotics_automation", "en")
    ]
    package_titles = {
        "General Arrangement",
        "Orthographic Views",
        "Assembly Drawings",
        "Component / Detail Drawings",
        "Connections & Fasteners",
        "Bill of Materials",
    }
    assert not any(title in package_titles for title, _content, _kwargs in result_boxes)
    assert [label for label, _kwargs in expanders] == [
        "General Arrangement",
        "Orthographic Views",
        "Assembly Drawings",
        "Component / Detail Drawings",
        "Connections & Fasteners",
        "Bill of Materials",
    ]
    assert all(kwargs["expanded"] is False for _label, kwargs in expanders)
    assert [kwargs["key"] for _label, kwargs in expanders] == [
        f"drawing_package_{item}" for item in drawing_studio_page._DRAWING_PACKAGE_ITEMS
    ]
    assert drawing_package_order[-1] == "export"
    assert containers[-1] == {
        "horizontal": True,
        "horizontal_alignment": "right",
        "vertical_alignment": "center",
    }
    assert envelope_input_renders == []
    assert component_input_renders == []
    assert arrangement_view_renders == []
    assert orthographic_view_renders == []
    assert assembly_drawing_renders == []
    assert component_detail_renders == []
    assert connection_renders == []
    assert len(bom_renders) == 1
    assert bom_renders[0][1] is valid_concept
    assert bom_renders[0][2] == []
    assert bom_renders[0][3] == "en"


def test_viewer_language_preserves_list_component_identity_and_geometry(monkeypatch):
    canonical = {
        "title": "Mobile Robot",
        "executive_summary": "A mobile robot",
        "system_components": ["Wheeled Platform", "Sensor Mast"],
        "technical_requirements": [],
        "materials": [],
        "constraints": [],
        "risks": [],
    }
    translated = {
        "en": canonical,
        "ru": {
            **canonical,
            "title": "Мобильный робот",
            "system_components": ["Колёсная платформа", "Сенсорная мачта"],
        },
        "sv": {
            **canonical,
            "title": "Mobil robot",
            "system_components": ["Hjulplattform", "Sensormast"],
        },
    }
    parameters = drawing_studio_page.build_empty_parameter_set()
    envelope = next(
        item for item in parameters["universal"]
        if item["key"] == "overall_dimensions_envelope"
    )
    envelope.update(value="length=1000; width=600; height=500", unit="mm")
    parameters["component_geometry"] = {
        "wheeled_platform": {
            "length": "400", "width": "300", "height": "100",
            "x": "10", "y": "20", "z": "0", "unit": "mm",
            "subgeometry": [{
                "key": "left_wheel", "primitive": "box",
                "length": "40", "width": "40", "height": "40",
                "position": {"x": "20", "y": "0", "z": "0"},
                "unit": "mm",
            }],
        },
        "sensor_mast": {
            "length": "50", "width": "50", "height": "300",
            "x": "200", "y": "100", "z": "100", "unit": "mm",
        },
    }
    parameters["connections"] = [{
        "component_a": "wheeled_platform",
        "component_b": "sensor_mast",
        "connection_type": "Bolted",
        "fastener_type": "M8 bolts",
        "quantity": 4,
        "note": "Attach mast to platform",
    }]
    connection_text = {
        "en": ("Bolted", "M8 bolts", "Attach mast to platform"),
        "ru": ("Болтовое", "Болты M8", "Закрепить мачту на платформе"),
        "sv": ("Skruvförband", "M8-bultar", "Fäst masten på plattformen"),
    }
    current_language = ["en"]
    rendered = {}
    ai_inputs = []

    monkeypatch.setattr(drawing_studio_page, "get_current_language", lambda: current_language[0])
    monkeypatch.setattr(drawing_studio_page, "get_current_concept_id", lambda: 91)
    monkeypatch.setattr(drawing_studio_page, "load_concept", lambda _id: canonical)
    monkeypatch.setattr(
        drawing_studio_page, "load_concept_for_viewer",
        lambda _id, language: (translated[language], "en"),
    )
    monkeypatch.setattr(drawing_studio_page, "_get_current_category", lambda _id: "robotics_automation")
    monkeypatch.setattr(drawing_studio_page, "get_engineering_parameter_set", lambda _id: parameters)
    monkeypatch.setattr(
        drawing_studio_page, "load_engineering_parameters_for_viewer",
        lambda _id, language: {
            **parameters,
            "connections": [{
                **parameters["connections"][0],
                "connection_type": connection_text[language][0],
                "fastener_type": connection_text[language][1],
                "note": connection_text[language][2],
            }],
        },
    )
    monkeypatch.setattr(drawing_studio_page, "_render_reference_visuals", lambda *_args: None)
    monkeypatch.setattr(
        drawing_studio_page, "_render_engineering_parameters",
        lambda *args: ai_inputs.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page, "_render_drawing_package_sections",
        lambda _id, _concept, arrangement, connections, _language:
        rendered.update({current_language[0]: (arrangement, connections)}),
    )
    exports = {}
    monkeypatch.setattr(
        drawing_studio_page, "_render_drawing_package_export",
        lambda _concept, _category, _arrangement, connections, language:
        exports.update({language: connections}),
    )
    monkeypatch.setattr(drawing_studio_page, "render_generated_section_heading", lambda *args: None)
    monkeypatch.setattr(drawing_studio_page, "render_result_box", lambda *args, **kwargs: None)
    monkeypatch.setattr(drawing_studio_page.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(drawing_studio_page.st, "caption", lambda *args: None)
    monkeypatch.setattr(drawing_studio_page.st, "space", lambda *args: None)
    monkeypatch.setattr(drawing_studio_page.st, "container", lambda **kwargs: nullcontext())

    for language in ("en", "ru", "sv"):
        current_language[0] = language
        drawing_studio_page.render_drawing_studio()

    fingerprints = []
    for language in ("en", "ru", "sv"):
        arrangement, connections = rendered[language]
        assert [component.key for component in arrangement.components] == [
            "wheeled_platform", "sensor_mast"
        ]
        assert [component.name for component in arrangement.components] == translated[
            language
        ]["system_components"]
        assert arrangement.components[0].dimensions.length.value == Decimal("400")
        assert arrangement.components[1].position.z.value == Decimal("100")
        assert arrangement.components[0].subgeometry[0].key == (
            "wheeled_platform.left_wheel"
        )
        assert (connections[0]["component_a"], connections[0]["component_b"]) == (
            "wheeled_platform", "sensor_mast"
        )
        assert connections is exports[language]
        assert (
            connections[0]["connection_type"],
            connections[0]["fastener_type"],
            connections[0]["note"],
        ) == connection_text[language]
        assert connections[0]["quantity"] == 4
        connection_fields = dict(drawing_studio_page._connection_display_data(
            connections[0], drawing_studio_page._component_names(arrangement)
        )["fields"])
        assert connection_fields["connection_type"] == connection_text[language][0]
        assert connection_fields["fastener_type"] == connection_text[language][1]
        assert connection_fields["note"] == connection_text[language][2]
        assert drawing_studio_page._connection_display_data(
            connections[0], drawing_studio_page._component_names(arrangement)
        )["components"] == (
            f"{translated[language]['system_components'][0]} ↔ "
            f"{translated[language]['system_components'][1]}"
        )
        top = drawing_studio_page.build_envelope_views(arrangement)[0]
        fingerprints.append(tuple(
            (
                projection.component_key,
                projection.horizontal_size.value,
                projection.vertical_size.value,
                projection.horizontal_position.value,
                projection.vertical_position.value,
            )
            for projection in drawing_studio_page.build_component_projections(
                arrangement, top
            )
        ))
        bom_rows = drawing_studio_page._build_bom_rows(
            arrangement, translated[language], connections
        )
        assert [row["component"] for row in bom_rows] == translated[language][
            "system_components"
        ]
        assert all(connection_text[language][0] in row["connections"][0] for row in bom_rows)
        assert all(connection_text[language][1] in row["connections"][0] for row in bom_rows)
        assert all(connection_text[language][2] in row["notes"] for row in bom_rows)
        package = drawing_studio_page._drawing_package_export_data(
            translated[language], "robotics_automation", arrangement,
            exports[language], language,
        )
        sections = {section["key"]: section for section in package["sections"]}
        export_fields = dict(sections["connections_fasteners"]["connections"][0]["fields"])
        assert tuple(export_fields.values()) == (
            *connection_text[language][:2], "4", connection_text[language][2],
        )
        assert sections["bill_of_materials"]["rows"] == bom_rows
    assert fingerprints[0] == fingerprints[1] == fingerprints[2]
    assert {item[0] for item in fingerprints[0]} == {
        "wheeled_platform", "wheeled_platform.left_wheel", "sensor_mast"
    }
    assert all(args[1] is canonical for args in ai_inputs)
    assert parameters["connections"][0]["connection_type"] == "Bolted"


def test_general_arrangement_svg_uses_real_labels_and_omits_partial_geometry():
    complete = drawing_studio_page.build_general_arrangement(
        {"system_components": []},
        {
            "universal": [
                {
                    "key": "overall_dimensions_envelope",
                    "value": "length=1200; width=800",
                    "unit": "mm",
                    "source": "user",
                }
            ],
            "project_specific": [],
        },
    )
    top, front, _side = drawing_studio_page.build_envelope_views(complete)

    top_markup = drawing_studio_page._general_arrangement_view_markup(
        top,
        "Top View",
        "Missing geometry",
    )
    front_markup = drawing_studio_page._general_arrangement_view_markup(
        front,
        "Front View",
        "Missing geometry",
    )

    assert "<rect" in top_markup
    assert ">1200 mm<" in top_markup
    assert ">800 mm<" in top_markup
    assert top_markup.count("<svg ") == top_markup.count("</svg>") == 1
    svg_start = top_markup.index("<svg ")
    svg_end = top_markup.index("</svg>")
    assert svg_start < top_markup.index("<line ") < svg_end
    assert svg_start < top_markup.index("<text ", svg_start) < svg_end
    assert "\n" not in top_markup
    assert "<rect" not in front_markup
    assert "Missing geometry" in front_markup


def test_general_arrangement_svg_uses_envelope_scale_for_complete_components():
    arrangement = drawing_studio_page.build_general_arrangement(
        {"system_components": ["Frame"]},
        {
            "universal": [
                {
                    "key": "overall_dimensions_envelope",
                    "value": "length=1000; width=500; height=400",
                    "unit": "mm",
                    "source": "user",
                }
            ],
            "project_specific": [],
            "component_geometry": {
                "frame": {
                    "length": "200",
                    "width": "100",
                    "height": "50",
                    "x": "100",
                    "y": "50",
                    "z": "0",
                    "unit": "mm",
                }
            },
        },
    )
    top = drawing_studio_page.build_envelope_views(arrangement)[0]
    projections = drawing_studio_page.build_component_projections(arrangement, top)

    markup = drawing_studio_page._general_arrangement_view_markup(
        top,
        "Top View",
        "Missing geometry",
        projections,
    )

    assert 'data-component-key="frame"' in markup
    assert 'width="44.00" height="22.00"' in markup


def _orthographic_arrangement(component_geometry, component_names=None):
    return drawing_studio_page.build_general_arrangement(
        {"system_components": component_names or list(component_geometry)},
        {
            "universal": [
                {
                    "key": "overall_dimensions_envelope",
                    "value": "length=1000; width=500; height=400",
                    "unit": "mm",
                    "source": "user",
                }
            ],
            "project_specific": [],
            "component_geometry": component_geometry,
        },
    )


def _component_geometry(**overrides):
    geometry = {
        "length": "200",
        "width": "100",
        "height": "50",
        "x": "20",
        "y": "30",
        "z": "40",
        "unit": "mm",
    }
    geometry.update(overrides)
    return geometry


def _primitive_markup(primitive, view_axes, longitudinal_axis="length"):
    return drawing_studio_page._primitive_shape_markup(
        primitive,
        "part",
        10,
        20,
        80,
        40,
        "top",
        5,
        view_axes,
        longitudinal_axis,
    )


def test_axial_primitives_render_end_and_longitudinal_views_differently():
    end_view = ("width", "height", "length")
    side_view = ("length", "height", "width")

    for primitive in ("cylinder", "shaft"):
        end_markup = _primitive_markup(primitive, end_view)
        side_markup = _primitive_markup(primitive, side_view)
        assert "<ellipse " in end_markup
        assert "<ellipse " not in side_markup
        assert "stroke-dasharray" in side_markup

        height_axis_end = _primitive_markup(
            primitive, ("length", "width", "height"), "height"
        )
        height_axis_side = _primitive_markup(
            primitive, ("height", "width", "length"), "height"
        )
        assert "<ellipse " in height_axis_end
        assert "<ellipse " not in height_axis_side

    tube_end = _primitive_markup("tube", end_view)
    tube_side = _primitive_markup("tube", side_view)
    assert tube_end.count("<rect ") == 2
    assert "<line " not in tube_end
    assert tube_side.count("<rect ") == 1
    assert tube_side.count("<line ") == 2

    beam_end = _primitive_markup("beam", end_view)
    beam_side = _primitive_markup("beam", side_view)
    assert "<line " not in beam_end
    assert beam_side.count("<line ") == 2


def test_planar_primitives_render_face_and_edge_views_differently():
    face_view = ("length", "width", "height")
    edge_view = ("length", "height", "width")

    assert _primitive_markup("plate", face_view).count("<line ") == 1
    assert "<line " not in _primitive_markup("plate", edge_view)
    assert _primitive_markup("panel", face_view).count("<line ") == 2
    assert "<line " not in _primitive_markup("panel", edge_view)
    assert _primitive_markup("frame", face_view).count("<rect ") == 2
    assert _primitive_markup("frame", edge_view).count("<rect ") == 1

    truss_face = _primitive_markup("truss", edge_view)
    truss_edge = _primitive_markup("truss", face_view)
    assert truss_face.count("<line ") == 2
    assert "<line " not in truss_edge

    shell_profile = _primitive_markup("shell", edge_view)
    shell_edge = _primitive_markup("shell", face_view)
    assert "<path " in shell_profile
    assert "<path " not in shell_edge


def test_view_invariant_primitive_fallbacks_remain_unchanged():
    top_view = ("length", "width", "height")
    front_view = ("width", "height", "length")

    assert _primitive_markup("box", top_view) == _primitive_markup("box", front_view)
    custom_top = _primitive_markup("custom", top_view)
    assert custom_top == _primitive_markup("custom", front_view)
    assert 'stroke-dasharray="5 3"' in custom_top


def test_svg_renderer_uses_legacy_box_fallback_and_distinct_primitives():
    legacy = _orthographic_arrangement({"part": _component_geometry()})
    beam = _orthographic_arrangement(
        {"part": _component_geometry(primitive="beam")}
    )
    tube = _orthographic_arrangement(
        {
            "part": _component_geometry(
                primitive="tube",
                wall_thickness="5",
            )
        }
    )
    cylinder = _orthographic_arrangement(
        {
            "part": _component_geometry(
                primitive="cylinder", width="50", height="50"
            )
        }
    )

    def markup(arrangement, view_index):
        view = drawing_studio_page.build_envelope_views(arrangement)[view_index]
        projections = drawing_studio_page.build_component_projections(
            arrangement,
            view,
        )
        return drawing_studio_page._general_arrangement_view_markup(
            view,
            "View",
            "Missing geometry",
            projections,
        )

    legacy_top = markup(legacy, 0)
    beam_top = markup(beam, 0)
    tube_top = markup(tube, 0)
    cylinder_front = markup(cylinder, 1)

    assert 'data-primitive="box"' in legacy_top
    assert 'data-primitive="beam"' in beam_top
    assert beam_top.count("<line ") > legacy_top.count("<line ")
    assert 'data-primitive="tube"' in tube_top
    assert tube_top.count("<line ") > legacy_top.count("<line ")
    assert 'data-primitive="cylinder"' in cylinder_front
    assert "<ellipse " in cylinder_front


def test_svg_renderer_reuses_primitive_renderer_for_parent_relative_subgeometry():
    arrangement = _orthographic_arrangement(
        {
            "part": _component_geometry(
                primitive="box",
                subgeometry=[
                    {
                        "key": "left_wheel",
                        "role": "wheel",
                        "primitive": "cylinder",
                        "length": "80",
                        "diameter": "40",
                        "unit": "mm",
                        "position": {"x": "100", "y": "0", "z": "0"},
                        "orientation": {"roll": "90", "pitch": "0", "yaw": "0"},
                    }
                ],
            )
        }
    )
    top = drawing_studio_page.build_envelope_views(arrangement)[0]
    projections = drawing_studio_page.build_component_projections(arrangement, top)

    markup = drawing_studio_page._general_arrangement_view_markup(
        top,
        "Top View",
        "Missing geometry",
        projections,
    )

    assert 'data-component-key="part"' in markup
    assert 'data-component-key="part.left_wheel"' in markup
    assert 'data-primitive="cylinder"' in markup

    component, detail_views = drawing_studio_page._component_detail_view_data(
        arrangement
    )[0]
    detail_top = next(view for view in detail_views if view.key == "top")
    detail_markup = drawing_studio_page._general_arrangement_view_markup(
        detail_top,
        "Top View",
        "Missing geometry",
        component_projections=drawing_studio_page.build_component_projections(
            (component,),
            detail_top,
            zero_origin=True,
        ),
    )
    assert 'data-component-key="part.left_wheel"' in detail_markup


def test_rotated_subgeometry_renderer_uses_composed_view_orientation():
    arrangement = _orthographic_arrangement(
        {
            "part": _component_geometry(
                orientation={"roll": "90", "pitch": "0", "yaw": "0"},
                subgeometry=[
                    {
                        "key": "pin",
                        "primitive": "shaft",
                        "length": "80",
                        "width": "40",
                        "height": "40",
                        "unit": "mm",
                        "position": {"x": "100", "y": "0", "z": "0"},
                        "orientation": {"roll": "0", "pitch": "0", "yaw": "90"},
                    }
                ],
            )
        }
    )
    top = drawing_studio_page.build_envelope_views(arrangement)[0]
    projections = drawing_studio_page.build_component_projections(arrangement, top)

    assert projections[1].view_axes[2] == "length"
    assert projections[1].longitudinal_axis == "length"
    markup = drawing_studio_page._general_arrangement_view_markup(
        top,
        "Top View",
        "Missing geometry",
        projections,
    )
    assert 'data-component-key="part.pin"' in markup
    assert '<ellipse data-component-key="part.pin"' in markup


def test_diameter_height_wheel_geometry_uses_height_as_cylinder_axis():
    arrangement = _orthographic_arrangement(
        {
            "part": _component_geometry(
                subgeometry=[
                    {
                        "key": "wheel",
                        "primitive": "cylinder",
                        "height": "180",
                        "diameter": "400",
                        "unit": "mm",
                        "position": {"x": "100", "y": "0", "z": "0"},
                        "orientation": {"roll": "90", "pitch": "0", "yaw": "0"},
                    }
                ]
            )
        }
    )
    front = drawing_studio_page.build_envelope_views(arrangement)[1]
    projections = drawing_studio_page.build_component_projections(arrangement, front)

    assert projections[1].view_axes == ("height", "width", "length")
    assert projections[1].longitudinal_axis == "height"
    markup = drawing_studio_page._general_arrangement_view_markup(
        front,
        "Front View",
        "Missing geometry",
        projections,
    )
    assert '<ellipse data-component-key="part.wheel"' not in markup
    assert '<rect data-component-key="part.wheel"' in markup


def test_legacy_geometry_without_subgeometry_keeps_existing_markup():
    arrangement = _orthographic_arrangement({"part": _component_geometry()})
    top = drawing_studio_page.build_envelope_views(arrangement)[0]
    projections = drawing_studio_page.build_component_projections(arrangement, top)

    markup = drawing_studio_page._general_arrangement_view_markup(
        top,
        "Top View",
        "Missing geometry",
        projections,
    )

    assert markup.count('data-component-key="part"') == 1
    assert "part." not in markup


def test_component_detail_renderer_uses_component_primitive():
    arrangement = _orthographic_arrangement(
        {"frame": _component_geometry(primitive="frame", wall_thickness="5")}
    )
    component, views = drawing_studio_page._component_detail_view_data(arrangement)[0]

    markup = drawing_studio_page._general_arrangement_view_markup(
        views[0],
        "Top View",
        "Missing geometry",
        component_projections=drawing_studio_page.build_component_projections(
            (component,), views[0], zero_origin=True
        ),
    )

    assert 'data-primitive="frame"' in markup
    assert markup.count("<rect ") >= 2


def test_detail_without_global_position_matches_pdf_and_keeps_child(monkeypatch):
    arrangement = _orthographic_arrangement({
        "part": _component_geometry(
            x=None, y=None, z=None,
            subgeometry=[{
                "key": "mount", "primitive": "box",
                "length": "40", "width": "30", "height": "20",
                "position": {"x": "50", "y": "20", "z": "0"},
                "unit": "mm",
            }],
        )
    })
    original_geometry = arrangement.model_dump()
    component, views = drawing_studio_page._component_detail_view_data(arrangement)[0]
    top = views[0]
    assert component.position is None
    assert drawing_studio_page.build_component_projections((component,), top) == ()
    projections = drawing_studio_page.build_component_projections(
        (component,), top, zero_origin=True
    )
    assert [item.component_key for item in projections] == ["part", "part.mount"]
    assert [item.horizontal_position.value for item in projections] == [
        Decimal("0"), Decimal("50")
    ]
    assert projections[1].vertical_position.value == Decimal("20")

    ui_markup = []
    monkeypatch.setattr(drawing_studio_page.st, "container", lambda **kwargs: nullcontext())
    monkeypatch.setattr(
        drawing_studio_page.st, "columns", lambda _count: [nullcontext()] * 3
    )
    monkeypatch.setattr(
        drawing_studio_page.st, "markdown",
        lambda value, **kwargs: ui_markup.append(value),
    )
    drawing_studio_page._render_component_detail_drawings(arrangement, "en")
    package = drawing_studio_page._drawing_package_export_data(
        {"title": "Part", "system_components": ["part"]},
        "Mechanical", arrangement, [], "en",
        exported_at=datetime(2026, 9, 19, 12, 30),
    )
    pdf_top = package["sections"][3]["groups"][0]["views"][0]["markup"]
    assert pdf_top in ui_markup
    assert 'data-component-key="part"' in pdf_top
    assert 'data-component-key="part.mount"' in pdf_top
    assert arrangement.model_dump() == original_geometry


def test_drawing_package_expanders_keep_existing_renderers_and_bom(monkeypatch):
    arrangement = _orthographic_arrangement(
        {
            "frame": _component_geometry(),
            "cover": _component_geometry(x="300"),
        },
        [
            {"key": "frame", "name": "Main Frame"},
            {"key": "cover", "name": "Safety Cover"},
        ],
    )
    concept_data = {"system_components": ["Main Frame", "Safety Cover"]}
    connections = [
        {
            "component_a": "frame",
            "component_b": "cover",
            "connection_type": "Bolted",
            "fastener_type": None,
            "quantity": None,
            "note": None,
        }
    ]
    expanders = []
    calls = []

    def expander(label, **kwargs):
        expanders.append((label, kwargs))
        return nullcontext()

    monkeypatch.setattr(drawing_studio_page.st, "expander", expander)
    monkeypatch.setattr(
        drawing_studio_page,
        "render_result_box",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Drawing Package summary cards must not render")
        ),
    )
    for name in (
        "_render_general_arrangement_views",
        "_render_orthographic_views",
        "_render_assembly_drawings",
        "_render_component_detail_drawings",
        "_render_connections_fasteners",
        "_render_bill_of_materials",
    ):
        monkeypatch.setattr(
            drawing_studio_page,
            name,
            lambda *args, _name=name: calls.append((_name, args)),
        )

    drawing_studio_page._render_drawing_package_sections(
        12,
        concept_data,
        arrangement,
        connections,
        "en",
    )

    assert [kwargs["key"] for _label, kwargs in expanders] == [
        f"drawing_package_{item}" for item in drawing_studio_page._DRAWING_PACKAGE_ITEMS
    ]
    assert all(kwargs["expanded"] is False for _label, kwargs in expanders)
    assert [name for name, _args in calls] == [
        "_render_general_arrangement_views",
        "_render_orthographic_views",
        "_render_assembly_drawings",
        "_render_component_detail_drawings",
        "_render_connections_fasteners",
        "_render_bill_of_materials",
    ]
    assert calls[-1][1] == (arrangement, concept_data, connections, "en")


def test_orthographic_views_reuse_ga_axes_positions_and_real_dimensions():
    arrangement = _orthographic_arrangement({"frame": _component_geometry()})
    original_values = arrangement.model_dump()

    orthographic = drawing_studio_page._orthographic_view_data(arrangement)

    assert [view.key for view, _projections in orthographic] == [
        "front",
        "top",
        "side",
    ]
    assert [
        (view.horizontal_axis, view.vertical_axis)
        for view, _projections in orthographic
    ] == [("width", "height"), ("length", "width"), ("length", "height")]
    assert [
        (
            projections[0].horizontal_position.value,
            projections[0].vertical_position.value,
        )
        for _view, projections in orthographic
    ] == [
        (Decimal("30"), Decimal("40")),
        (Decimal("20"), Decimal("30")),
        (Decimal("20"), Decimal("40")),
    ]
    assert all(
        projections
        == drawing_studio_page.build_component_projections(arrangement, view)
        for view, projections in orthographic
    )
    assert arrangement.model_dump() == original_values


def test_orthographic_svg_keeps_outside_geometry_and_omits_incomplete(monkeypatch):
    arrangement = _orthographic_arrangement(
        {
            "visible": _component_geometry(subgeometry=[{
                "key": "extension", "primitive": "box",
                "length": "40", "width": "30", "height": "20",
                "position": {"x": "1000", "y": "0", "z": "0"},
                "unit": "mm",
            }]),
            "incomplete": _component_geometry(
                length="100", width=None, height=None, x="0", y=None, z=None
            ),
            "outside": _component_geometry(length="100", x="950", y="0", z="0"),
        }
    )
    top, projections = drawing_studio_page._orthographic_view_data(arrangement)[1]
    original_geometry = arrangement.model_dump()

    markup = drawing_studio_page._general_arrangement_view_markup(
        top,
        "Top View",
        "Missing geometry",
        projections,
    )

    assert 'data-component-key="visible"' in markup
    assert 'data-component-key="visible.extension"' in markup
    assert 'data-component-key="incomplete"' not in markup
    assert 'data-component-key="outside"' in markup
    assert next(
        item for item in projections if item.component_key == "outside"
    ).out_of_envelope is True
    outside = re.search(
        r'<rect data-component-key="outside"[^>]* x="([\d.]+)" '
        r'y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',
        markup,
    )
    assert outside is not None
    x, y, width, height = map(float, outside.groups())
    assert 65 <= x < x + width <= 285
    assert 30 <= y < y + height <= 160
    extension = re.search(
        r'<rect data-component-key="visible.extension"[^>]* x="([\d.]+)" '
        r'y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',
        markup,
    )
    assert extension is not None
    child_x, child_y, child_width, child_height = map(float, extension.groups())
    assert 65 <= child_x < child_x + child_width <= 285
    assert 30 <= child_y < child_y + child_height <= 160
    assert '>1000 mm<' in markup
    assert arrangement.model_dump() == original_geometry

    warnings = []
    monkeypatch.setattr(
        drawing_studio_page.st, "columns", lambda _count: [nullcontext()] * 3
    )
    monkeypatch.setattr(drawing_studio_page.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(drawing_studio_page.st, "warning", warnings.append)
    drawing_studio_page._render_projected_views(((top, projections),), "en")
    assert len(warnings) == 1 and "outside" in warnings[0]

    assembly = drawing_studio_page._general_arrangement_view_markup(
        top, "Top View", "Missing geometry", projections,
        {"visible": 1, "outside": 3},
    )
    assert 'data-assembly-item="1"' in assembly
    assert 'data-assembly-item="3"' in assembly


def test_orthographic_views_do_not_mix_concepts():
    first = _orthographic_arrangement({"first": _component_geometry()})
    second = _orthographic_arrangement(
        {"second": _component_geometry(x="10", y="10", z="10")}
    )

    first_keys = {
        projection.component_key
        for _view, projections in drawing_studio_page._orthographic_view_data(first)
        for projection in projections
    }
    second_keys = {
        projection.component_key
        for _view, projections in drawing_studio_page._orthographic_view_data(second)
        for projection in projections
    }

    assert first_keys == {"first"}
    assert second_keys == {"second"}


def test_assembly_views_reuse_orthographic_projections_and_stable_numbering():
    arrangement = _orthographic_arrangement(
        {
            "main_frame": _component_geometry(),
            "incomplete": _component_geometry(
                width=None, height=None, y=None, z=None
            ),
            "drive_unit": _component_geometry(x="300"),
        },
        ["Main Frame", "Incomplete", "Drive Unit"],
    )
    original_values = arrangement.model_dump()

    assembly_views, numbered_components = drawing_studio_page._assembly_view_data(
        arrangement
    )

    assert assembly_views == drawing_studio_page._orthographic_view_data(arrangement)
    assert [view.key for view, _projections in assembly_views] == [
        "front",
        "top",
        "side",
    ]
    assert [
        (number, component.key) for number, component in numbered_components
    ] == [(1, "main_frame"), (2, "incomplete"), (3, "drive_unit")]
    assert numbered_components == drawing_studio_page._assembly_view_data(
        arrangement
    )[1]
    assert arrangement.model_dump() == original_values


def test_assembly_markers_omit_unrenderable_components_without_losing_identity():
    arrangement = _orthographic_arrangement(
        {
            "main_frame": _component_geometry(),
            "incomplete": _component_geometry(
                width=None, height=None, y=None, z=None
            ),
            "outside": _component_geometry(
                length="100", x="950", y="450", z="360"
            ),
        },
        ["Main Frame", "Incomplete", "Outside"],
    )
    view_data, numbered_components = drawing_studio_page._assembly_view_data(
        arrangement
    )
    item_numbers = {
        component.key: number for number, component in numbered_components
    }
    top, projections = view_data[1]

    markup = drawing_studio_page._general_arrangement_view_markup(
        top,
        "Top View",
        "Missing geometry",
        projections,
        item_numbers,
    )
    assert 'data-assembly-item="1"' in markup
    assert 'data-component-key="incomplete"' not in markup
    assert 'data-component-key="outside"' in markup
    assert 'data-assembly-item="3"' in markup


def test_assembly_main_ui_renders_numbered_views_without_component_legend(monkeypatch):
    arrangement = _orthographic_arrangement({"frame": _component_geometry()})
    projected = []
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_projected_views",
        lambda *args: projected.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page.st,
        "markdown",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Assembly legend must not render in the main UI")
        ),
    )

    drawing_studio_page._render_assembly_drawings(arrangement, "en")

    assert len(projected) == 1
    assert projected[0][2] == {"frame": 1}


def test_drawing_package_keeps_component_and_connection_identity_across_sections():
    arrangement = _orthographic_arrangement(
        {
            "frame": _component_geometry(),
            "partial": _component_geometry(
                width=None, height=None, y=None, z=None
            ),
            "outside": _component_geometry(
                length="100", x="950", y="450", z="360"
            ),
        },
        [
            {"key": "frame", "name": "Main Frame"},
            {"key": "partial", "name": "Partial Bracket"},
            {"key": "outside", "name": "Outside Guard"},
        ],
    )
    connection = {
        "component_a": "partial",
        "component_b": "outside",
        "connection_type": "Bolted",
        "fastener_type": "M8 bolt",
        "quantity": 4,
        "note": "Service removable",
    }

    orthographic, assembly_components = drawing_studio_page._assembly_view_data(
        arrangement
    )
    bom_rows = drawing_studio_page._build_bom_rows(
        arrangement,
        {},
        [connection],
    )
    component_names = drawing_studio_page._component_names(arrangement)

    expected_identity = [
        (1, "frame", "Main Frame"),
        (2, "partial", "Partial Bracket"),
        (3, "outside", "Outside Guard"),
    ]
    assert [
        (number, component.key, component.name)
        for number, component in assembly_components
    ] == expected_identity
    assert [
        (row["item"], row["component_key"], row["component"])
        for row in bom_rows
    ] == expected_identity
    assert component_names == {
        "frame": "Main Frame",
        "partial": "Partial Bracket",
        "outside": "Outside Guard",
    }
    assert {
        (projection.component_key, projection.component_name)
        for _view, projections in orthographic
        for projection in projections
    } == {
        ("frame", "Main Frame"),
        ("outside", "Outside Guard"),
    }
    assert [
        (component.key, component.name)
        for component, _views in drawing_studio_page._component_detail_view_data(
            arrangement
        )
    ] == [
        ("frame", "Main Frame"),
        ("partial", "Partial Bracket"),
        ("outside", "Outside Guard"),
    ]

    connection_markup = drawing_studio_page._connection_markup(
        connection,
        component_names,
        "en",
    )
    partial_row = bom_rows[1]
    outside_row = bom_rows[2]
    assert "Partial Bracket ↔ Outside Guard" in connection_markup
    assert "Bolted" in connection_markup
    assert "M8 bolt" in connection_markup
    assert "Quantity:</strong> 4" in connection_markup
    assert "Service removable" in connection_markup
    assert partial_row["connections"] == (
        "Bolted · M8 bolt · ×4 · ↔ Outside Guard",
    )
    assert partial_row["notes"] == ("Service removable",)
    assert outside_row["connections"] == (
        "Bolted · M8 bolt · ×4 · ↔ Partial Bracket",
    )
    assert outside_row["notes"] == ("Service removable",)
    assert all(
        projection.out_of_envelope
        for _view, projections in orthographic
        for projection in projections
        if projection.component_key == "outside"
    )


def test_drawing_package_export_reuses_ui_data_without_inventing_geometry():
    concept = {
        "title": "First Concept",
        "system_components": [
            {"key": "frame", "name": "Main Frame", "material": "Steel"},
            {"key": "partial", "name": "Partial Bracket"},
        ],
    }
    arrangement = _orthographic_arrangement(
        {
            "frame": _component_geometry(),
            "partial": _component_geometry(
                width=None, height=None, y=None, z=None
            ),
        },
        concept["system_components"],
    )
    connections = [
        {
            "component_a": "frame",
            "component_b": "partial",
            "connection_type": "Bolted",
            "fastener_type": "M8 bolt",
            "quantity": 4,
            "note": "Removable",
        },
        {
            "component_a": "partial",
            "component_b": "frame",
            "connection_type": "Located",
            "fastener_type": None,
            "quantity": None,
            "note": None,
        },
    ]
    original_arrangement = arrangement.model_dump()
    original_concept = copy.deepcopy(concept)
    original_connections = copy.deepcopy(connections)

    package = drawing_studio_page._drawing_package_export_data(
        concept,
        "Mechanical",
        arrangement,
        connections,
        "en",
        exported_at=datetime(2026, 9, 19, 12, 30),
    )

    assert [section["key"] for section in package["sections"]] == list(
        drawing_studio_page._DRAWING_PACKAGE_ITEMS
    )
    assembly = package["sections"][2]
    bom = package["sections"][5]
    assert assembly["legend"] == ("1 - Main Frame", "2 - Partial Bracket")
    assert [
        (row["item"], row["component_key"], row["component"])
        for row in bom["rows"]
    ] == [
        (1, "frame", "Main Frame"),
        (2, "partial", "Partial Bracket"),
    ]
    partial_detail = package["sections"][3]["groups"][1]
    assert all("<svg" not in view["markup"] for view in partial_detail["views"])
    exported_connections = package["sections"][4]["connections"]
    assert [field[0] for field in exported_connections[0]["fields"]] == [
        "Connection Type",
        "Fastener Type",
        "Quantity",
        "Note",
    ]
    assert exported_connections[1]["fields"] == (("Connection Type", "Located"),)
    assert arrangement.model_dump() == original_arrangement
    assert concept == original_concept
    assert connections == original_connections


def test_drawing_package_export_does_not_mix_concepts():
    first = _orthographic_arrangement({"first": _component_geometry()})
    second = _orthographic_arrangement({"second": _component_geometry()})

    first_package = drawing_studio_page._drawing_package_export_data(
        {"title": "First", "system_components": ["first"]},
        "Mechanical",
        first,
        [],
        "en",
    )
    second_package = drawing_studio_page._drawing_package_export_data(
        {"title": "Second", "system_components": ["second"]},
        "Mechanical",
        second,
        [],
        "en",
    )

    assert [row["component_key"] for row in first_package["sections"][5]["rows"]] == [
        "first"
    ]
    assert [row["component_key"] for row in second_package["sections"][5]["rows"]] == [
        "second"
    ]


def test_drawing_package_export_uses_single_download_button(monkeypatch):
    arrangement = _orthographic_arrangement({"frame": _component_geometry()})
    buttons = []
    monkeypatch.setattr(
        drawing_studio_page,
        "export_drawing_package",
        lambda package, language: b"%PDF-package",
    )
    monkeypatch.setattr(
        drawing_studio_page.st,
        "download_button",
        lambda **kwargs: buttons.append(kwargs),
    )

    drawing_studio_page._render_drawing_package_export(
        {"title": "Test Project", "system_components": ["frame"]},
        "mechanical",
        arrangement,
        [],
        "en",
    )

    assert len(buttons) == 1
    assert buttons[0]["label"] == "Export Drawing Package"
    assert buttons[0]["data"] == b"%PDF-package"
    assert buttons[0]["mime"] == "application/pdf"
    assert buttons[0]["width"] == "content"


def test_assembly_numbering_does_not_mix_concepts():
    first = _orthographic_arrangement({"first": _component_geometry()})
    second = _orthographic_arrangement({"second": _component_geometry()})

    _first_views, first_components = drawing_studio_page._assembly_view_data(first)
    _second_views, second_components = drawing_studio_page._assembly_view_data(second)

    assert [(number, component.key) for number, component in first_components] == [
        (1, "first")
    ]
    assert [(number, component.key) for number, component in second_components] == [
        (1, "second")
    ]


def test_component_details_use_component_dimensions_and_existing_view_axes():
    arrangement = _orthographic_arrangement({"frame": _component_geometry()})
    original_values = arrangement.model_dump()

    component, views = drawing_studio_page._component_detail_view_data(arrangement)[0]
    top, front, side = views

    assert component.key == "frame"
    assert (top.horizontal_axis, top.vertical_axis) == ("length", "width")
    assert (front.horizontal_axis, front.vertical_axis) == ("width", "height")
    assert (side.horizontal_axis, side.vertical_axis) == ("length", "height")
    assert (top.horizontal.value, top.vertical.value) == (
        Decimal("200"),
        Decimal("100"),
    )
    assert (front.horizontal.value, front.vertical.value) == (
        Decimal("100"),
        Decimal("50"),
    )
    assert (side.horizontal.value, side.vertical.value) == (
        Decimal("200"),
        Decimal("50"),
    )
    top_markup = drawing_studio_page._general_arrangement_view_markup(
        top, "Top View", "Missing geometry"
    )
    assert ">200 mm<" in top_markup
    assert ">100 mm<" in top_markup
    assert ">1000 mm<" not in top_markup
    assert arrangement.model_dump() == original_values


def test_component_detail_partial_dimensions_do_not_create_invented_views():
    arrangement = _orthographic_arrangement(
        {
            "top_only": _component_geometry(height=None),
            "no_complete_view": _component_geometry(
                width=None, height=None, x=None, y=None, z=None
            ),
        }
    )
    details = drawing_studio_page._component_detail_view_data(arrangement)
    top_only_views = details[0][1]
    incomplete_views = details[1][1]

    assert drawing_studio_page.calculate_display_rectangle(top_only_views[0]) is not None
    assert drawing_studio_page.calculate_display_rectangle(top_only_views[1]) is None
    assert drawing_studio_page.calculate_display_rectangle(top_only_views[2]) is None
    assert all(
        drawing_studio_page.calculate_display_rectangle(view) is None
        for view in incomplete_views
    )
    assert all(
        "<rect" not in drawing_studio_page._general_arrangement_view_markup(
            view, "Detail View", "Missing geometry"
        )
        for view in incomplete_views
    )


def test_component_details_ignore_positions_and_do_not_mix_data():
    first = _orthographic_arrangement(
        {
            "first": _component_geometry(x="0", y="0", z="0"),
            "second": _component_geometry(
                length="300",
                width="150",
                height="75",
                x="900",
                y="400",
                z="300",
            ),
        }
    )
    moved_first = _orthographic_arrangement(
        {"first": _component_geometry(x="700", y="300", z="200")}
    )

    first_details = drawing_studio_page._component_detail_view_data(first)
    moved_details = drawing_studio_page._component_detail_view_data(moved_first)

    assert [component.key for component, _views in first_details] == ["first", "second"]
    assert [component.key for component, _views in moved_details] == ["first"]
    assert first_details[0][1] == moved_details[0][1]
    assert first_details[0][1][0].horizontal.value == Decimal("200")
    assert first_details[1][1][0].horizontal.value == Decimal("300")


def test_connection_presentation_shows_only_saved_optional_fields():
    component_names = {"frame": "Main Frame", "cover": "Safety Cover"}
    complete = {
        "component_a": "frame",
        "component_b": "cover",
        "connection_type": "Bolted flange",
        "fastener_type": "M8 bolt",
        "quantity": 4,
        "note": "Service removable",
    }
    minimal = {
        "component_a": "cover",
        "component_b": "frame",
        "connection_type": "Welded",
        "fastener_type": None,
        "quantity": None,
        "note": None,
    }

    complete_markup = drawing_studio_page._connection_markup(
        complete, component_names, "en"
    )
    minimal_markup = drawing_studio_page._connection_markup(
        minimal, component_names, "en"
    )

    assert "Main Frame ↔ Safety Cover" in complete_markup
    assert "Bolted flange" in complete_markup
    assert "M8 bolt" in complete_markup
    assert "Quantity:</strong> 4" in complete_markup
    assert "Service removable" in complete_markup
    assert "Safety Cover ↔ Main Frame" in minimal_markup
    assert "Welded" in minimal_markup
    assert "Fastener Type" not in minimal_markup
    assert "Quantity" not in minimal_markup
    assert "Note" not in minimal_markup


def test_connections_section_is_read_only_in_main_drawing_package(monkeypatch):
    arrangement = _orthographic_arrangement(
        {
            "frame": _component_geometry(),
            "cover": _component_geometry(x="300"),
        },
        [
            {"key": "frame", "name": "Main Frame"},
            {"key": "cover", "name": "Safety Cover"},
        ],
    )
    connections = [
        {
            "component_a": "frame",
            "component_b": "cover",
            "connection_type": "Bolted",
            "fastener_type": None,
            "quantity": None,
            "note": None,
        }
    ]
    rendered = []
    monkeypatch.setattr(
        drawing_studio_page.st,
        "columns",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Read-only connections must not render input columns")
        ),
    )
    monkeypatch.setattr(
        drawing_studio_page.st,
        "markdown",
        lambda markup, **kwargs: rendered.append(markup),
    )

    drawing_studio_page._render_connections_fasteners(
        12,
        arrangement,
        connections,
        "en",
    )

    assert len(rendered) == 1
    assert "Main Frame ↔ Safety Cover" in rendered[0]
    assert "Bolted" in rendered[0]


def _bom_arrangement(concept_data):
    return drawing_studio_page.build_general_arrangement(
        concept_data,
        {"universal": [], "project_specific": [], "component_geometry": {}},
    )


def test_bom_uses_component_order_explicit_materials_and_related_connections():
    concept_data = {
        "system_components": [
            {
                "key": "main_frame",
                "name": "Main Frame",
                "material": "Structural steel",
                "note": "Prefabricated",
            },
            {"key": "safety_cover", "name": "Safety Cover"},
            {
                "key": "sensor",
                "name": "Sensor",
                "material": "Polymer housing",
            },
        ],
        "materials": ["Unassigned project material"],
    }
    connections = [
        {
            "component_a": "main_frame",
            "component_b": "safety_cover",
            "connection_type": "Bolted",
            "fastener_type": "M8 bolt",
            "quantity": 4,
            "note": "Removable guard",
        },
        {
            "component_a": "safety_cover",
            "component_b": "sensor",
            "connection_type": "Clipped",
            "fastener_type": None,
            "quantity": None,
            "note": None,
        },
    ]
    arrangement = _bom_arrangement(concept_data)
    original_arrangement = arrangement.model_dump()
    original_concept = copy.deepcopy(concept_data)
    original_connections = copy.deepcopy(connections)

    rows = drawing_studio_page._build_bom_rows(
        arrangement,
        concept_data,
        connections,
    )

    assert [(row["item"], row["component"], row["quantity"]) for row in rows] == [
        (1, "Main Frame", 1),
        (2, "Safety Cover", 1),
        (3, "Sensor", 1),
    ]
    assert rows[0]["material"] == "Structural steel"
    assert rows[1]["material"] is None
    assert rows[2]["material"] == "Polymer housing"
    assert rows[0]["connections"] == ("Bolted · M8 bolt · ×4 · ↔ Safety Cover",)
    assert all("Clipped" not in value for value in rows[0]["connections"])
    assert rows[2]["connections"] == ("Clipped · ↔ Safety Cover",)
    assert rows[0]["notes"] == ("Prefabricated", "Removable guard")
    assert arrangement.model_dump() == original_arrangement
    assert concept_data == original_concept
    assert connections == original_connections


def test_bom_keeps_duplicate_components_separate_and_concepts_isolated():
    first = _bom_arrangement({"system_components": ["Bracket", "Bracket"]})
    second = _bom_arrangement({"system_components": ["Motor"]})

    first_rows = drawing_studio_page._build_bom_rows(first, {}, [])
    second_rows = drawing_studio_page._build_bom_rows(second, {}, [])

    assert [(row["item"], row["component_key"]) for row in first_rows] == [
        (1, "bracket"),
        (2, "bracket_2"),
    ]
    assert [(row["item"], row["component_key"]) for row in second_rows] == [
        (1, "motor")
    ]


def test_bom_markup_uses_saved_rows_without_inventing_missing_material():
    arrangement = _bom_arrangement({"system_components": ["Frame"]})
    rows = drawing_studio_page._build_bom_rows(arrangement, {}, [])

    markup = drawing_studio_page._bom_markup(rows, "en")

    assert "<th>Item</th>" in markup
    assert "<th>Fasteners / Connections</th>" in markup
    assert "<td>Frame</td>" in markup
    assert "Unassigned" not in markup
