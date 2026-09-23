from decimal import Decimal

import database
from application.engineering_parameters import (
    save_component_geometry_values,
    save_overall_envelope_values,
)
from services.engineering_parameters_service import build_empty_parameter_set
from services.general_arrangement_service import (
    build_component_projections,
    build_general_arrangement,
    build_envelope_views,
    calculate_display_rectangle,
    has_prepared_geometry,
    normalize_known_value,
    oriented_component_dimensions,
)


def _parameter_set(*parameters):
    return {
        "universal": list(parameters),
        "project_specific": [],
        "component_geometry": {},
    }


def _parameter(key, value, unit="mm", source="user"):
    return {
        "key": key,
        "value": value,
        "unit": unit,
        "source": source,
    }


def _structured_component(dimensions=None, position=None):
    return {
        "key": "frame",
        "name": "Frame",
        "dimensions": {
            field: {"value": str(value), "unit": "mm"}
            for field, value in (dimensions or {}).items()
        },
        "position": {
            field: {"value": str(value), "unit": "mm"}
            for field, value in (position or {}).items()
        },
    }


def test_empty_engineering_parameters_are_ignored():
    arrangement = build_general_arrangement(
        {"system_components": ["Frame"]},
        _parameter_set(
            _parameter("overall_dimensions_envelope", None),
            _parameter("mass_weight", "   ", "kg"),
        ),
    )

    assert arrangement.raw_inputs == ()
    assert arrangement.overall_envelope.length is None
    assert not has_prepared_geometry(arrangement)


def test_known_numeric_values_are_normalized_to_canonical_units():
    millimetres = normalize_known_value(
        "1200",
        "mm",
        source_type="engineering_parameter",
        source_key="universal.overall_dimensions_envelope",
    )
    metres = normalize_known_value(
        "1.2",
        "m",
        source_type="concept_data",
        source_key="system_components.frame.dimensions.length",
    )
    kilograms = normalize_known_value(
        "25",
        "kg",
        source_type="engineering_parameter",
        source_key="universal.mass_weight",
    )

    assert (millimetres.value, millimetres.unit) == (Decimal("1200"), "mm")
    assert (metres.value, metres.unit) == (Decimal("1200.0"), "mm")
    assert (kilograms.value, kilograms.unit) == (Decimal("25"), "kg")


def test_ambiguous_or_unknown_values_are_not_normalized():
    for raw_value, unit in (
        ("1000-1200", "mm"),
        ("about 1200", "mm"),
        ("1,200", "mm"),
        ("1200 x 800", "mm"),
        ("1200", "furlong"),
    ):
        assert normalize_known_value(
            raw_value,
            unit,
            source_type="engineering_parameter",
            source_key="universal.overall_dimensions_envelope",
        ) is None


def test_unlabelled_envelope_and_concept_text_do_not_invent_dimensions():
    arrangement = build_general_arrangement(
        {
            "system_components": ["Frame 1200 mm long"],
            "technical_requirements": ["Fit within 1200 x 800 x 600 mm"],
        },
        _parameter_set(
            _parameter("overall_dimensions_envelope", "1200 x 800 x 600")
        ),
    )

    envelope = arrangement.overall_envelope
    assert (envelope.length, envelope.width, envelope.height) == (None, None, None)
    assert arrangement.components[0].dimensions.length is None
    assert arrangement.raw_inputs[0].raw_value == "1200 x 800 x 600"
    assert not has_prepared_geometry(arrangement)


def test_labelled_ai_envelope_uses_core_contract_but_arbitrary_parameters_do_not():
    arrangement = build_general_arrangement(
        {"system_components": ["Frame"]},
        {
            "universal": [
                _parameter(
                    "overall_dimensions_envelope",
                    "length=1200; width=800; height=600",
                    source="ai",
                )
            ],
            "project_specific": [_parameter("length", "1200")],
        },
    )

    assert arrangement.overall_envelope.length.value == Decimal("1200")
    assert arrangement.overall_envelope.width.value == Decimal("800")
    assert arrangement.overall_envelope.height.value == Decimal("600")
    assert len(arrangement.raw_inputs) == 1
    assert arrangement.raw_inputs[0].raw_value == "1200"
    assert not has_prepared_geometry(arrangement)


def test_explicit_geometry_preserves_engineering_and_concept_provenance():
    arrangement = build_general_arrangement(
        {
            "system_components": [
                {
                    "key": "main_frame",
                    "name": "Main frame",
                    "dimensions": {
                        "length": {"value": "1.2", "unit": "m"},
                        "width": {"value": "800", "unit": "mm"},
                        "height": {"value": "600", "unit": "mm"},
                    },
                    "position": {
                        "x": {"value": "0", "unit": "mm"},
                        "y": {"value": "250", "unit": "mm"},
                        "z": {"value": "0", "unit": "mm"},
                    },
                }
            ]
        },
        _parameter_set(
            _parameter(
                "overall_dimensions_envelope",
                "length=1200; width=800; height=600",
            )
        ),
    )

    assert has_prepared_geometry(arrangement)
    assert arrangement.overall_envelope.length.provenance.source_type == (
        "engineering_parameter"
    )
    component = arrangement.components[0]
    assert component.dimensions.length.value == Decimal("1200.0")
    assert component.dimensions.length.provenance.source_type == "concept_data"
    assert component.position.x.value == Decimal("0")
    assert component.position.y.provenance.source_key == (
        "system_components.main_frame.position.y"
    )


def test_general_arrangement_builds_do_not_mix_concept_data():
    first = build_general_arrangement(
        {"system_components": ["First frame"]},
        _parameter_set(
            _parameter(
                "overall_dimensions_envelope",
                "length=100; width=200; height=300",
            )
        ),
    )
    second = build_general_arrangement(
        {"system_components": ["Second housing"]},
        _parameter_set(
            _parameter(
                "overall_dimensions_envelope",
                "length=400; width=500; height=600",
            )
        ),
    )

    assert [item.name for item in first.components] == ["First frame"]
    assert [item.name for item in second.components] == ["Second housing"]
    assert first.overall_envelope.length.value == Decimal("100")
    assert second.overall_envelope.length.value == Decimal("400")


def test_overall_envelope_saves_in_existing_parameter_set_and_normalizes(
    temporary_database,
    valid_concept,
):
    concept_id = database.save_concept(
        "Envelope project",
        "robotics_automation",
        "Envelope prompt",
        valid_concept,
        "en",
    )
    save_overall_envelope_values(concept_id, "1.2", "0.8", "0.6", "m")
    stored = database.get_engineering_parameter_set(concept_id)
    parameter = next(
        item
        for item in stored["universal"]
        if item["key"] == "overall_dimensions_envelope"
    )
    arrangement = build_general_arrangement(valid_concept, stored)

    assert parameter["value"] == "length=1.2; width=0.8; height=0.6"
    assert parameter["unit"] == "m"
    assert arrangement.overall_envelope.length.value == Decimal("1200.0")
    assert arrangement.overall_envelope.width.value == Decimal("800.0")
    assert arrangement.overall_envelope.height.value == Decimal("600.0")


def test_partial_and_empty_saved_envelopes_do_not_invent_values(
    temporary_database,
    valid_concept,
):
    concept_id = database.save_concept(
        "Partial envelope",
        "robotics_automation",
        "Partial prompt",
        valid_concept,
        "en",
    )

    save_overall_envelope_values(concept_id, "1200", "", None, "mm")
    partial = build_general_arrangement(
        valid_concept,
        database.get_engineering_parameter_set(concept_id),
    ).overall_envelope
    assert partial.length.value == Decimal("1200")
    assert partial.width is None
    assert partial.height is None

    save_overall_envelope_values(concept_id, "", " ", None, "mm")
    empty = build_general_arrangement(
        valid_concept,
        database.get_engineering_parameter_set(concept_id),
    ).overall_envelope
    assert (empty.length, empty.width, empty.height) == (None, None, None)


def test_saved_envelopes_remain_scoped_to_their_concepts(
    temporary_database,
    valid_concept,
):
    first_id = database.save_concept(
        "First envelope",
        "robotics_automation",
        "First prompt",
        valid_concept,
        "en",
    )
    second_id = database.save_concept(
        "Second envelope",
        "robotics_automation",
        "Second prompt",
        valid_concept,
        "en",
    )
    save_overall_envelope_values(first_id, "100", "200", "300", "mm")
    save_overall_envelope_values(second_id, "2", "3", "4", "m")

    first = build_general_arrangement(
        valid_concept,
        database.get_engineering_parameter_set(first_id),
    )
    second = build_general_arrangement(
        valid_concept,
        database.get_engineering_parameter_set(second_id),
    )

    assert first.overall_envelope.length.value == Decimal("100")
    assert second.overall_envelope.length.value == Decimal("2000")


def test_top_view_uses_length_and_width():
    arrangement = build_general_arrangement(
        {"system_components": []},
        _parameter_set(
            _parameter(
                "overall_dimensions_envelope",
                "length=1200; width=800; height=600",
            )
        ),
    )
    top = build_envelope_views(arrangement)[0]

    assert (top.horizontal_axis, top.vertical_axis) == ("length", "width")
    assert (top.horizontal.value, top.vertical.value) == (
        Decimal("1200"),
        Decimal("800"),
    )


def test_front_view_uses_width_and_height():
    arrangement = build_general_arrangement(
        {"system_components": []},
        _parameter_set(
            _parameter(
                "overall_dimensions_envelope",
                "length=1200; width=800; height=600",
            )
        ),
    )
    front = build_envelope_views(arrangement)[1]

    assert (front.horizontal_axis, front.vertical_axis) == ("width", "height")
    assert (front.horizontal.value, front.vertical.value) == (
        Decimal("800"),
        Decimal("600"),
    )


def test_side_view_uses_length_and_height():
    arrangement = build_general_arrangement(
        {"system_components": []},
        _parameter_set(
            _parameter(
                "overall_dimensions_envelope",
                "length=1200; width=800; height=600",
            )
        ),
    )
    side = build_envelope_views(arrangement)[2]

    assert (side.horizontal_axis, side.vertical_axis) == ("length", "height")
    assert (side.horizontal.value, side.vertical.value) == (
        Decimal("1200"),
        Decimal("600"),
    )


def test_display_scale_preserves_view_proportions_and_partial_views_are_absent():
    complete = build_general_arrangement(
        {"system_components": []},
        _parameter_set(
            _parameter(
                "overall_dimensions_envelope",
                "length=1200; width=600",
            )
        ),
    )
    top, front, side = build_envelope_views(complete)
    display = calculate_display_rectangle(top)

    assert (display.width, display.height) == (Decimal("220"), Decimal("110.0"))
    assert calculate_display_rectangle(front) is None
    assert calculate_display_rectangle(side) is None


def test_envelope_views_from_different_concepts_do_not_mix():
    first = build_general_arrangement(
        {"system_components": []},
        _parameter_set(
            _parameter("overall_dimensions_envelope", "length=100; width=50")
        ),
    )
    second = build_general_arrangement(
        {"system_components": []},
        _parameter_set(
            _parameter("overall_dimensions_envelope", "length=900; width=300")
        ),
    )

    first_top = build_envelope_views(first)[0]
    second_top = build_envelope_views(second)[0]
    assert first_top.horizontal.value == Decimal("100")
    assert second_top.horizontal.value == Decimal("900")


def test_component_geometry_saves_by_stable_key_without_replacing_other_data(
    temporary_database,
    valid_concept,
):
    concept_id = database.save_concept(
        "Component geometry",
        "robotics_automation",
        "Geometry prompt",
        valid_concept,
        "en",
    )
    existing = build_empty_parameter_set()
    mass = next(
        item for item in existing["universal"] if item["key"] == "mass_weight"
    )
    mass["value"] = "25"
    mass["unit"] = "kg"
    existing["project_specific"] = [
        {
            "key": "payload",
            "label": "Payload",
            "value": "25",
            "unit": "kg",
            "status": "confirmed",
            "source": "user",
            "rationale": None,
        }
    ]
    database.save_engineering_parameter_set(concept_id, existing)
    save_component_geometry_values(
        concept_id, "structural_frame", "1.2", "0.4", "0.3", "0", "10", "20", "m"
    )
    save_component_geometry_values(
        concept_id, "control_unit", "50", "40", "30", "5", "6", "7", "cm"
    )
    stored = database.get_engineering_parameter_set(concept_id)

    assert set(stored["component_geometry"]) == {"structural_frame", "control_unit"}
    assert stored["component_geometry"]["structural_frame"]["length"] == "1.2"
    assert stored["component_geometry"]["structural_frame"]["source"] == "user"
    assert len(stored["universal"]) == 11
    assert next(
        item["value"]
        for item in stored["universal"]
        if item["key"] == "mass_weight"
    ) == "25"
    assert stored["project_specific"][0]["value"] == "25"


def test_component_geometry_normalizes_partial_values_and_keeps_concepts_isolated(
    temporary_database,
    valid_concept,
):
    first_id = database.save_concept(
        "First component", "robotics_automation", "First", valid_concept, "en"
    )
    second_id = database.save_concept(
        "Second component", "robotics_automation", "Second", valid_concept, "en"
    )
    component_key = "structural_frame"
    save_component_geometry_values(
        first_id, component_key, "1.2", "", "30", "0", "", "2", "m"
    )
    save_component_geometry_values(
        second_id, component_key, "25", "", "", "0", "", "", "cm"
    )

    first = build_general_arrangement(
        {"system_components": ["Structural Frame"]},
        database.get_engineering_parameter_set(first_id),
    ).components[0]
    second = build_general_arrangement(
        {"system_components": ["Structural Frame"]},
        database.get_engineering_parameter_set(second_id),
    ).components[0]

    assert first.dimensions.length.value == Decimal("1200.0")
    assert first.dimensions.width is None
    assert first.dimensions.height.value == Decimal("30000")
    assert first.position.x.value == Decimal("0")
    assert first.position.y is None
    assert first.position.z.value == Decimal("2000")
    assert first.dimensions.length.provenance.source_key == (
        "component_geometry.structural_frame.length"
    )
    assert second.dimensions.length.value == Decimal("250")
    assert second.dimensions.height is None


def test_partial_stored_geometry_preserves_known_concept_dimensions():
    parameter_set = _parameter_set()
    parameter_set["component_geometry"] = {"frame": {"x": "100", "unit": "mm"}}

    component = build_general_arrangement(
        {
            "system_components": [
                _structured_component(
                    dimensions={"length": 1000, "width": 500, "height": 300}
                )
            ]
        },
        parameter_set,
    ).components[0]

    assert component.dimensions.length.value == Decimal("1000")
    assert component.dimensions.width.value == Decimal("500")
    assert component.dimensions.height.value == Decimal("300")
    assert component.position.x.value == Decimal("100")


def test_structured_component_primitive_geometry_is_loaded_without_inference():
    parameter_set = _parameter_set()
    parameter_set["component_geometry"] = {
        "frame": {
            "primitive": "tube",
            "length": "1000",
            "width": "100",
            "height": "100",
            "wall_thickness": "5",
            "unit": "mm",
            "position": {"x": "10", "y": "20", "z": "30"},
            "orientation": {"roll": "0", "pitch": "0", "yaw": "90"},
            "features": ["hollow", "open ends"],
        }
    }

    component = build_general_arrangement(
        {"system_components": [{"key": "frame", "name": "Frame"}]},
        parameter_set,
    ).components[0]

    assert component.primitive == "tube"
    assert component.wall_thickness.value == Decimal("5")
    assert component.position.x.value == Decimal("10")
    assert component.orientation.yaw == Decimal("90")
    assert component.features == ("hollow", "open ends")


def test_partial_stored_dimensions_preserve_known_concept_position():
    parameter_set = _parameter_set()
    parameter_set["component_geometry"] = {
        "frame": {"length": "800", "unit": "mm"}
    }

    component = build_general_arrangement(
        {
            "system_components": [
                _structured_component(position={"x": 10, "y": 20, "z": 30})
            ]
        },
        parameter_set,
    ).components[0]

    assert component.dimensions.length.value == Decimal("800")
    assert component.position.x.value == Decimal("10")
    assert component.position.y.value == Decimal("20")
    assert component.position.z.value == Decimal("30")


def test_stored_component_field_takes_priority_over_concept_data():
    parameter_set = _parameter_set()
    parameter_set["component_geometry"] = {
        "frame": {"width": "650", "unit": "mm"}
    }

    component = build_general_arrangement(
        {
            "system_components": [
                _structured_component(dimensions={"length": 1000, "width": 500})
            ]
        },
        parameter_set,
    ).components[0]

    assert component.dimensions.length.value == Decimal("1000")
    assert component.dimensions.width.value == Decimal("650")
    assert component.dimensions.width.provenance.source_type == "engineering_parameter"


def test_component_fields_absent_from_both_sources_remain_none():
    parameter_set = _parameter_set()
    parameter_set["component_geometry"] = {"frame": {"x": "0", "unit": "mm"}}

    component = build_general_arrangement(
        {"system_components": [_structured_component(dimensions={"length": 1000})]},
        parameter_set,
    ).components[0]

    assert component.dimensions.width is None
    assert component.dimensions.height is None
    assert component.position.y is None
    assert component.position.z is None


def test_component_projections_use_view_axes_and_skip_incomplete_geometry():
    parameter_set = _parameter_set(
        _parameter(
            "overall_dimensions_envelope",
            "length=1200; width=800; height=600",
        )
    )
    parameter_set["component_geometry"] = {
        "frame": {
            "length": "400",
            "width": "300",
            "height": "200",
            "x": "100",
            "y": "50",
            "z": "25",
            "unit": "mm",
        },
        "incomplete": {
            "length": "100",
            "width": None,
            "height": None,
            "x": "0",
            "y": None,
            "z": None,
            "unit": "mm",
        },
    }
    arrangement = build_general_arrangement(
        {"system_components": ["Frame", "Incomplete"]}, parameter_set
    )
    top, front, side = build_envelope_views(arrangement)
    top_projection = build_component_projections(arrangement, top)
    front_projection = build_component_projections(arrangement, front)
    side_projection = build_component_projections(arrangement, side)

    assert len(top_projection) == len(front_projection) == len(side_projection) == 1
    assert (
        top_projection[0].horizontal_size.value,
        top_projection[0].vertical_size.value,
        top_projection[0].horizontal_position.value,
        top_projection[0].vertical_position.value,
    ) == (Decimal("400"), Decimal("300"), Decimal("100"), Decimal("50"))
    assert (
        front_projection[0].horizontal_size.value,
        front_projection[0].vertical_size.value,
        front_projection[0].horizontal_position.value,
        front_projection[0].vertical_position.value,
    ) == (Decimal("300"), Decimal("200"), Decimal("50"), Decimal("25"))
    assert (
        side_projection[0].horizontal_size.value,
        side_projection[0].vertical_size.value,
        side_projection[0].horizontal_position.value,
        side_projection[0].vertical_position.value,
    ) == (Decimal("400"), Decimal("200"), Decimal("100"), Decimal("25"))


def test_out_of_envelope_projection_is_flagged_without_changing_geometry():
    parameter_set = _parameter_set(
        _parameter(
            "overall_dimensions_envelope",
            "length=500; width=400; height=300",
        )
    )
    parameter_set["component_geometry"] = {
        "frame": {
            "length": "200",
            "width": "100",
            "height": "50",
            "x": "400",
            "y": "0",
            "z": "0",
            "unit": "mm",
        }
    }
    arrangement = build_general_arrangement(
        {"system_components": ["Frame"]}, parameter_set
    )
    projection = build_component_projections(
        arrangement, build_envelope_views(arrangement)[0]
    )[0]

    assert projection.out_of_envelope is True
    assert arrangement.components[0].position.x.value == Decimal("400")
    assert arrangement.components[0].dimensions.length.value == Decimal("200")


def test_orthogonal_orientation_swaps_display_axes_without_mutating_source():
    parameter_set = _parameter_set(
        _parameter(
            "overall_dimensions_envelope",
            "length=500; width=400; height=300",
        )
    )
    parameter_set["component_geometry"] = {
        "frame": {
            "length": "200",
            "width": "100",
            "height": "50",
            "position": {"x": "0", "y": "0", "z": "0"},
            "orientation": {"roll": "0", "pitch": "0", "yaw": "90"},
            "unit": "mm",
        }
    }
    arrangement = build_general_arrangement(
        {"system_components": ["Frame"]}, parameter_set
    )
    component = arrangement.components[0]

    oriented = oriented_component_dimensions(component)

    assert (oriented.length.value, oriented.width.value, oriented.height.value) == (
        Decimal("100"),
        Decimal("200"),
        Decimal("50"),
    )
    assert component.dimensions.length.value == Decimal("200")
