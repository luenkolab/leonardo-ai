from decimal import Decimal

import database
from application.engineering_parameters import save_overall_envelope_values
from services.general_arrangement_service import (
    build_general_arrangement,
    build_envelope_views,
    calculate_display_rectangle,
    has_prepared_geometry,
    normalize_known_value,
)


def _parameter_set(*parameters):
    return {"universal": list(parameters), "project_specific": []}


def _parameter(key, value, unit="mm", source="user"):
    return {
        "key": key,
        "value": value,
        "unit": unit,
        "source": source,
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


def test_ai_suggested_or_arbitrary_parameters_do_not_become_geometry():
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

    assert arrangement.overall_envelope.length is None
    assert len(arrangement.raw_inputs) == 2
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
