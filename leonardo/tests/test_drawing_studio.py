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
    assert set(package_results.values()) == {
        "Additional geometry data required",
        "Front View · Top View · Side View",
        "Not generated",
    }
    assert list(package_results.values()).count("Not generated") == 4
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


def _orthographic_arrangement(component_geometry):
    return drawing_studio_page.build_general_arrangement(
        {"system_components": list(component_geometry)},
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
