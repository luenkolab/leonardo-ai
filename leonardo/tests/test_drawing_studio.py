import copy
from contextlib import nullcontext
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
    monkeypatch.setattr(drawing_studio_page.st, "container", lambda **kwargs: nullcontext())
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
        "load_concept_for_viewer",
        lambda concept_id, language: (valid_concept, "en"),
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
    assert spaces == [40, 40]
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
        (91, valid_concept, "robotics_automation", "en")
    ]
    package_results = {
        title: content
        for title, content, _kwargs in result_boxes
        if title
        in {
            "General Arrangement",
            "Orthographic Views",
            "Assembly Drawings",
            "Component / Detail Drawings",
            "Connections & Fasteners",
            "Bill of Materials",
        }
    }
    assert package_results["General Arrangement"] == (
        "Additional geometry data required"
    )
    assert package_results["Orthographic Views"] == (
        "Front View · Top View · Side View"
    )
    assert package_results["Assembly Drawings"] == (
        "Front View · Top View · Side View"
    )
    assert package_results["Component / Detail Drawings"] == "System Components"
    assert package_results["Connections & Fasteners"] == "Component A ↔ Component B"
    assert package_results["Bill of Materials"] == "System Components"
    assert set(package_results.values()) == {
        "Additional geometry data required",
        "Front View · Top View · Side View",
        "System Components",
        "Component A ↔ Component B",
    }
    assert "Not generated" not in package_results.values()
    assert len(envelope_input_renders) == 1
    assert envelope_input_renders[0][0] == 91
    assert envelope_input_renders[0][2] == "en"
    assert len(component_input_renders) == 1
    assert component_input_renders[0][0] == 91
    assert component_input_renders[0][2] == "en"
    assert len(arrangement_view_renders) == 1
    assert arrangement_view_renders[0][1] == "en"
    assert len(orthographic_view_renders) == 1
    assert orthographic_view_renders[0][0] is arrangement_view_renders[0][0]
    assert orthographic_view_renders[0][1] == "en"
    assert len(assembly_drawing_renders) == 1
    assert assembly_drawing_renders[0][0] is arrangement_view_renders[0][0]
    assert assembly_drawing_renders[0][1] == "en"
    assert len(component_detail_renders) == 1
    assert component_detail_renders[0][0] is arrangement_view_renders[0][0]
    assert component_detail_renders[0][1] == "en"
    assert len(connection_renders) == 1
    assert connection_renders[0][0] == 91
    assert connection_renders[0][1] is arrangement_view_renders[0][0]
    assert connection_renders[0][2] == []
    assert connection_renders[0][3] == "en"
    assert len(bom_renders) == 1
    assert bom_renders[0][0] is arrangement_view_renders[0][0]
    assert bom_renders[0][1] is valid_concept
    assert bom_renders[0][2] == []
    assert bom_renders[0][3] == "en"


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


def test_orthographic_svg_omits_incomplete_and_out_of_envelope_components():
    arrangement = _orthographic_arrangement(
        {
            "visible": _component_geometry(),
            "incomplete": _component_geometry(
                length="100", width=None, height=None, x="0", y=None, z=None
            ),
            "outside": _component_geometry(length="100", x="950", y="0", z="0"),
        }
    )
    top, projections = drawing_studio_page._orthographic_view_data(arrangement)[1]

    markup = drawing_studio_page._general_arrangement_view_markup(
        top,
        "Top View",
        "Missing geometry",
        projections,
    )

    assert 'data-component-key="visible"' in markup
    assert 'data-component-key="incomplete"' not in markup
    assert 'data-component-key="outside"' not in markup
    assert next(
        item for item in projections if item.component_key == "outside"
    ).out_of_envelope is True


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
    legend = drawing_studio_page._assembly_legend_markup(
        numbered_components,
        "System Components",
    )

    assert 'data-assembly-item="1"' in markup
    assert 'data-component-key="incomplete"' not in markup
    assert 'data-component-key="outside"' not in markup
    assert "1 — Main Frame" in legend
    assert "2 — Incomplete" in legend
    assert "3 — Outside" in legend


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
