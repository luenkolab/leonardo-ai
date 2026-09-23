import copy
import json
from contextlib import nullcontext
from types import SimpleNamespace

import database
import pytest
from application import engineering_parameters as parameter_application
from i18n import LANGUAGES, TRANSLATIONS
from services import concept_translation_service
from services import engineering_parameters_service as service
from services.general_arrangement_service import build_general_arrangement
from ui import drawing_studio_page


def _project_parameter(
    key,
    value=None,
    status="missing",
    source="ai",
    label=None,
):
    return {
        "key": key,
        "label": label or key.replace("_", " ").title(),
        "value": value,
        "unit": None,
        "status": status,
        "source": source,
        "rationale": "Needed for project preparation",
    }


def _universal(parameter_set, key):
    return next(
        parameter for parameter in parameter_set["universal"] if parameter["key"] == key
    )


def _save_test_concept(valid_concept, title):
    return database.save_concept(
        title,
        "robotics_automation",
        f"Prompt for {title}",
        valid_concept,
        "en",
    )


def test_parameter_table_is_idempotent_and_new_concept_has_no_set(
    temporary_database,
    valid_concept,
):
    database.init_db()
    concept_id = _save_test_concept(valid_concept, "New engineering project")

    assert database.get_engineering_parameter_set(concept_id) is None
    connection = database.get_connection()
    try:
        sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE name = 'engineering_parameter_sets'"
        ).fetchone()[0]
    finally:
        connection.close()
    assert "parameters_json" in sql
    assert "json_valid" in sql


def test_parameter_sets_persist_by_concept_without_changing_original(
    temporary_database,
    valid_concept,
):
    first_id = _save_test_concept(valid_concept, "Bridge concept")
    second_id = _save_test_concept(valid_concept, "Water concept")
    original = database.get_concept_by_id(first_id)
    first = service.build_empty_parameter_set()
    first["project_specific"] = [_project_parameter("span_length")]
    second = service.build_empty_parameter_set()
    second["project_specific"] = [_project_parameter("flow_rate")]

    database.save_engineering_parameter_set(first_id, first)
    database.save_engineering_parameter_set(second_id, second)
    database.init_db()

    assert database.get_engineering_parameter_set(first_id)["project_specific"][0]["key"] == "span_length"
    assert database.get_engineering_parameter_set(second_id)["project_specific"][0]["key"] == "flow_rate"
    assert database.get_concept_by_id(first_id) == original


def test_universal_core_is_generic_and_starts_missing():
    parameter_set = service.build_empty_parameter_set()
    keys = {item["key"] for item in parameter_set["universal"]}

    assert len(keys) == 11
    assert "unit_system" not in keys
    assert not any("bridge" in key or "river" in key for key in keys)
    assert all(item["status"] == "missing" for item in parameter_set["universal"])


def test_component_geometry_survives_validation_save_and_load(
    temporary_database,
    valid_concept,
):
    concept_id = _save_test_concept(valid_concept, "Geometry contract")
    parameter_set = service.build_empty_parameter_set()
    _universal(parameter_set, "mass_weight")["value"] = "25"
    parameter_set["project_specific"] = [_project_parameter("payload", "25")]
    parameter_set["component_geometry"] = {
        "main-frame": {
            "source": "user",
            "length": "1.2",
            "width": None,
            "height": "0.6",
            "x": "0",
            "y": None,
            "z": "25",
            "unit": "M",
        }
    }
    parameter_set["unknown_top_level"] = "discarded"

    validated = service.validate_parameter_set(parameter_set)
    database.save_engineering_parameter_set(concept_id, validated)
    loaded = database.get_engineering_parameter_set(concept_id)

    assert loaded["component_geometry"]["main_frame"] == {
        "source": "user",
        "length": "1.2",
        "width": None,
        "height": "0.6",
        "x": "0",
        "y": None,
        "z": "25",
        "unit": "m",
    }
    assert _universal(loaded, "mass_weight")["value"] == "25"
    assert loaded["project_specific"][0]["value"] == "25"
    assert "unknown_top_level" not in loaded


def test_component_geometry_parses_universal_primitive_fields():
    parameter_set = service.build_empty_parameter_set()
    parameter_set["component_geometry"] = {
        "support": {
            "primitive": "Tube",
            "length": "1200",
            "width": "80",
            "height": "80",
            "wall_thickness": "4",
            "unit": "mm",
            "position": {"x": "10", "y": "20", "z": "0"},
            "orientation": {"roll": "0", "pitch": "0", "yaw": "90"},
            "features": ["hollow", "hollow", "open ends"],
        }
    }

    geometry = service.validate_parameter_set(parameter_set)["component_geometry"][
        "support"
    ]

    assert geometry == {
        "length": "1200",
        "width": "80",
        "height": "80",
        "wall_thickness": "4",
        "primitive": "tube",
        "orientation": {"roll": "0", "pitch": "0", "yaw": "90"},
        "features": ["hollow", "open ends"],
        "position": {"x": "10", "y": "20", "z": "0"},
        "unit": "mm",
    }

    parameter_set["component_geometry"]["support"]["primitive"] = "unsupported"
    with pytest.raises(ValueError, match="Unsupported component primitive"):
        service.validate_parameter_set(parameter_set)


def test_component_geometry_validates_structured_subgeometry():
    parameter_set = service.build_empty_parameter_set()
    parameter_set["component_geometry"] = {
        "platform": {
            "source": "ai",
            "primitive": "box",
            "length": "1000",
            "width": "600",
            "height": "300",
            "unit": "mm",
            "subgeometry": [
                {
                    "key": "left-wheel",
                    "role": "wheel",
                    "primitive": "cylinder",
                    "length": "80",
                    "diameter": "240",
                    "unit": "mm",
                    "position": {"x": "100", "y": "0", "z": "0"},
                    "orientation": {"roll": "90", "pitch": "0", "yaw": "0"},
                }
            ],
        }
    }

    geometry = service.validate_parameter_set(parameter_set)["component_geometry"][
        "platform"
    ]

    assert geometry["subgeometry"] == [
        {
            "key": "left_wheel",
            "role": "wheel",
            "primitive": "cylinder",
            "length": "80",
            "width": None,
            "height": None,
            "diameter": "240",
            "wall_thickness": None,
            "position": {"x": "100", "y": "0", "z": "0"},
            "orientation": {"roll": "90", "pitch": "0", "yaw": "0"},
            "unit": "mm",
        }
    ]


def _component_keys(concept_data, parameter_set=None):
    arrangement = build_general_arrangement(
        concept_data,
        parameter_set or service.build_empty_parameter_set(),
    )
    return [component.key for component in arrangement.components]


def test_connections_survive_validation_save_load_without_losing_parameters(
    temporary_database,
    valid_concept,
):
    concept_id = _save_test_concept(valid_concept, "Connected project")
    parameter_set = service.build_empty_parameter_set()
    component_a, component_b = _component_keys(valid_concept)[:2]
    _universal(parameter_set, "mass_weight")["value"] = "25"
    parameter_set["project_specific"] = [_project_parameter("payload", "25")]
    parameter_set["component_geometry"] = {
        component_a: {
            "length": "100",
            "width": None,
            "height": None,
            "x": None,
            "y": None,
            "z": None,
            "unit": "mm",
        }
    }
    database.save_engineering_parameter_set(concept_id, parameter_set)

    parameter_application.save_connection_values(
        concept_id,
        component_a,
        component_b,
        "Bolted flange",
        "M8 bolt",
        "4",
        "User supplied connection",
    )
    loaded = service.validate_parameter_set(
        database.get_engineering_parameter_set(concept_id)
    )

    assert loaded["connections"] == [
        {
            "component_a": component_a,
            "component_b": component_b,
            "connection_type": "Bolted flange",
            "fastener_type": "M8 bolt",
            "quantity": 4,
            "note": "User supplied connection",
        }
    ]
    assert _universal(loaded, "mass_weight")["value"] == "25"
    assert loaded["project_specific"][0]["value"] == "25"
    assert loaded["component_geometry"][component_a]["length"] == "100"


def test_connection_rejects_invalid_or_identical_component_keys(
    temporary_database,
    valid_concept,
):
    concept_id = _save_test_concept(valid_concept, "Connection references")
    component_a, component_b = _component_keys(valid_concept)[:2]

    with pytest.raises(ValueError):
        parameter_application.save_connection_values(
            concept_id, "missing_component", component_b, "Welded"
        )
    with pytest.raises(ValueError):
        parameter_application.save_connection_values(
            concept_id, component_a, component_a, "Welded"
        )


def test_connection_quantity_accepts_only_positive_integer_or_none(
    temporary_database,
    valid_concept,
):
    concept_id = _save_test_concept(valid_concept, "Connection quantity")
    component_a, component_b = _component_keys(valid_concept)[:2]

    parameter_application.save_connection_values(
        concept_id, component_a, component_b, "Welded", quantity=None
    )
    parameter_application.save_connection_values(
        concept_id, component_a, component_b, "Bolted", quantity="3"
    )
    for invalid_quantity in (0, "0", -1, "1.5", True):
        with pytest.raises(ValueError):
            parameter_application.save_connection_values(
                concept_id,
                component_a,
                component_b,
                "Invalid quantity",
                quantity=invalid_quantity,
            )

    stored = database.get_engineering_parameter_set(concept_id)
    assert [connection["quantity"] for connection in stored["connections"]] == [
        None,
        3,
    ]


def test_connections_remain_scoped_to_their_concepts(
    temporary_database,
    valid_concept,
):
    first_concept = copy.deepcopy(valid_concept)
    first_concept["system_components"] = ["First frame", "First cover"]
    second_concept = copy.deepcopy(valid_concept)
    second_concept["system_components"] = ["Second frame", "Second cover"]
    first_id = _save_test_concept(first_concept, "First connections")
    second_id = _save_test_concept(second_concept, "Second connections")
    first_keys = _component_keys(first_concept)
    second_keys = _component_keys(second_concept)

    parameter_application.save_connection_values(
        first_id, first_keys[0], first_keys[1], "First connection"
    )
    parameter_application.save_connection_values(
        second_id, second_keys[0], second_keys[1], "Second connection"
    )

    first = database.get_engineering_parameter_set(first_id)["connections"]
    second = database.get_engineering_parameter_set(second_id)["connections"]
    assert first[0]["component_a"] == "first_frame"
    assert second[0]["component_a"] == "second_frame"


def test_ai_engineer_uses_shared_client_for_full_engineering_context(
    monkeypatch,
    valid_concept,
):
    parameter_set = service.build_empty_parameter_set()
    _universal(parameter_set, "mass_weight")["value"] = "25"
    components = [SimpleNamespace(key="main_frame", name="Main Frame")]
    payload = {
        "universal": [
            {
                **_universal(parameter_set, "overall_dimensions_envelope"),
                "value": "length=2; width=1; height=1.5",
                "unit": "m",
                "source": "model",
                "status": "completed",
                "rationale": "Preliminary purpose-based scale",
            }
        ],
        "project_specific": [_project_parameter("payload", "25", "ai", "model")],
        "component_geometry": {
            "main_frame": {
                "source": "model",
                "primitive": "frame",
                "length": "2",
                "width": "1",
                "height": "1.5",
                "wall_thickness": "0.05",
                "position": {"x": "0", "y": "0", "z": "0"},
                "orientation": {"roll": "0", "pitch": "0", "yaw": "90"},
                "features": ["open perimeter", "cross members"],
                "unit": "m",
            }
        },
        "connections": [],
    }
    calls = []
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
    )
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: calls.append(kwargs) or response
            )
        )
    )
    monkeypatch.setattr(service, "get_text_client", lambda: client)

    result = service.suggest_engineering_data(
        valid_concept,
        "robotics_automation",
        "Original startup prompt",
        "en",
        parameter_set,
        components,
    )

    assert len(calls) == 1
    assert result["universal"][0]["key"] == "overall_dimensions_envelope"
    assert result["universal"][0]["source"] == "ai"
    assert result["universal"][0]["status"] == "suggested"
    assert result["project_specific"][0]["key"] == "payload"
    assert result["project_specific"][0]["source"] == "ai"
    assert result["project_specific"][0]["status"] == "suggested"
    assert result["component_geometry"]["main_frame"]["length"] == "2"
    assert result["component_geometry"]["main_frame"]["source"] == "ai"
    assert result["component_geometry"]["main_frame"]["primitive"] == "frame"
    assert result["component_geometry"]["main_frame"]["position"]["x"] == "0"
    assert result["component_geometry"]["main_frame"]["features"] == [
        "open perimeter",
        "cross members",
    ]
    prompt = "\n".join(message["content"] for message in calls[0]["messages"])
    assert "Original startup prompt" in prompt
    assert "technical_requirements" in prompt
    assert "engineering_parameters" in prompt
    assert "realistic physical scale" in prompt
    assert "Never derive or claim verified engineering dimensions" in prompt
    assert "primitive" in prompt
    assert "structural" in prompt
    assert "topology" in prompt
    assert "minimum corner" in prompt
    assert "envelope origin (0, 0, 0)" in prompt
    assert "x + length <=" in prompt
    assert "Position and dimensions for a component must use the same unit" in prompt
    assert "do not silently" in prompt
    assert "user-sourced component geometry" in prompt
    assert "AI-sourced component geometry may be regenerated or refined" in prompt
    assert isinstance(calls[0]["messages"][1]["content"], str)


def test_ai_engineer_includes_available_modern_images_in_one_request(
    monkeypatch,
    valid_concept,
):
    payload = {
        "universal": [],
        "project_specific": [],
        "component_geometry": {},
        "connections": [],
    }
    calls = []
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
    )
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: calls.append(kwargs) or response
            )
        )
    )
    monkeypatch.setattr(service, "get_text_client", lambda: client)

    service.suggest_engineering_data(
        valid_concept,
        "robotics_automation",
        "Prompt",
        "en",
        service.build_empty_parameter_set(),
        [],
        (("modern_concept_1", b"first"), ("modern_concept_3", b"third")),
    )

    assert len(calls) == 1
    content = calls[0]["messages"][1]["content"]
    assert content[0]["type"] == "text"
    assert [item["type"] for item in content[1:]] == ["image_url", "image_url"]
    assert content[1]["image_url"]["url"] == "data:image/png;base64,Zmlyc3Q="
    assert content[2]["image_url"]["url"] == "data:image/png;base64,dGhpcmQ="


def test_ai_engineer_merge_fills_only_missing_fields_and_preserves_user_data():
    current = service.build_empty_parameter_set()
    _universal(current, "overall_dimensions_envelope").update(
        {
            "value": "length=1; width=0.5; height=0.5",
            "unit": "m",
            "status": "confirmed",
            "source": "user",
        }
    )
    current["project_specific"] = [
        _project_parameter("payload", "User payload", "confirmed", "user"),
        _project_parameter(
            "concept_limit", "Concept value", "confirmed", "concept"
        ),
        _project_parameter("duty_cycle", "Old AI cycle", "suggested", "ai"),
        _project_parameter("obsolete", "Old AI value", "suggested", "ai"),
    ]
    current["component_geometry"] = {
        "frame": {
            "source": "user",
            "primitive": "beam",
            "length": "1000",
            "width": None,
            "height": None,
            "x": "0",
            "y": None,
            "z": None,
            "features": ["user-defined flange"],
            "unit": "mm",
        }
    }
    current["connections"] = [
        {
            "component_a": "frame",
            "component_b": "cover",
            "connection_type": "User bolted",
            "fastener_type": "User M8",
            "quantity": 4,
            "note": "User connection",
        }
    ]
    suggestions = service.build_empty_parameter_set()
    suggestions["universal"] = [
        {
            **_universal(current, "overall_dimensions_envelope"),
            "value": "length=2; width=1; height=1.5",
            "status": "suggested",
            "source": "ai",
        },
        {
            **_universal(current, "mass_weight"),
            "value": "25",
            "unit": "kg",
            "status": "suggested",
            "source": "ai",
            "rationale": "Purpose-based estimate",
        },
    ]
    suggestions["project_specific"] = [
        _project_parameter("payload", "AI payload", "suggested"),
        _project_parameter("concept_limit", "AI replacement", "suggested"),
        _project_parameter("duty_cycle", "8 h", "suggested"),
    ]
    suggestions["component_geometry"] = {
        "frame": {
            "primitive": "truss",
            "length": "2",
            "width": "50",
            "height": "25",
            "x": "5",
            "y": "10",
            "z": "0",
            "features": ["ai diagonal"],
            "unit": "cm",
        },
        "unknown": {
            "length": "10",
            "width": None,
            "height": None,
            "x": None,
            "y": None,
            "z": None,
            "unit": "mm",
        },
    }
    suggestions["connections"] = [
        {
            "component_a": "frame",
            "component_b": "cover",
            "connection_type": "AI welded",
            "fastener_type": None,
            "quantity": None,
            "note": None,
        },
        {
            "component_a": "frame",
            "component_b": "sensor",
            "connection_type": "Clipped",
            "fastener_type": None,
            "quantity": None,
            "note": "AI preliminary",
        },
    ]

    merged = service.merge_ai_engineering_data(
        current,
        suggestions,
        {"frame", "cover", "sensor"},
    )

    assert (
        _universal(merged, "overall_dimensions_envelope")["value"]
        == "length=1; width=0.5; height=0.5"
    )
    assert _universal(merged, "mass_weight")["value"] == "25"
    assert _universal(merged, "mass_weight")["source"] == "ai"
    project_by_key = {
        parameter["key"]: parameter for parameter in merged["project_specific"]
    }
    assert project_by_key["payload"]["value"] == "User payload"
    assert project_by_key["concept_limit"]["value"] == "Concept value"
    assert project_by_key["duty_cycle"]["value"] == "8 h"
    assert "obsolete" not in project_by_key
    assert merged["component_geometry"]["frame"] == {
        "source": "user",
        "primitive": "beam",
        "length": "1000",
        "width": None,
        "height": None,
        "x": "0",
        "y": None,
        "z": None,
        "features": ["user-defined flange"],
        "unit": "mm",
    }
    assert "unknown" not in merged["component_geometry"]
    assert merged["connections"][0]["connection_type"] == "User bolted"
    assert len(merged["connections"]) == 2
    assert merged["connections"][1]["component_b"] == "sensor"


@pytest.mark.parametrize(
    ("source", "expected_length", "expected_z", "expected_source"),
    (
        ("ai", "2", "5", "ai"),
        ("user", "100", "10", "user"),
        (None, "100", "10", None),
    ),
    ids=("ai-refreshes", "user-protected", "legacy-protected"),
)
def test_component_geometry_refresh_respects_entry_source(
    source,
    expected_length,
    expected_z,
    expected_source,
):
    current = service.build_empty_parameter_set()
    geometry = {
        "length": "100",
        "width": "50",
        "height": "25",
        "position": {"x": "0", "y": "0", "z": "10"},
        "unit": "mm",
    }
    if source is not None:
        geometry["source"] = source
    current["component_geometry"] = {"frame": geometry}
    suggestions = service.build_empty_parameter_set()
    suggestions["component_geometry"] = {
        "frame": {
            "source": "ai",
            "length": "2",
            "width": "1",
            "height": "0.5",
            "position": {"x": "0", "y": "0", "z": "5"},
            "unit": "cm",
        }
    }

    merged = service.merge_ai_engineering_data(current, suggestions, {"frame"})
    merged_geometry = merged["component_geometry"]["frame"]

    assert merged_geometry["length"] == expected_length
    assert merged_geometry["position"]["z"] == expected_z
    assert merged_geometry.get("source") == expected_source


def test_ai_engineer_application_saves_only_current_concept(
    monkeypatch,
    temporary_database,
    valid_concept,
):
    first = copy.deepcopy(valid_concept)
    first["system_components"] = ["First frame"]
    second = copy.deepcopy(valid_concept)
    second["system_components"] = ["Second frame"]
    first_id = _save_test_concept(first, "First AI Engineer")
    second_id = _save_test_concept(second, "Second AI Engineer")
    suggestions = service.build_empty_parameter_set()
    suggestions["universal"] = [
        {
            **_universal(suggestions, "mass_weight"),
            "value": "25",
            "unit": "kg",
            "status": "suggested",
            "source": "ai",
            "rationale": "Project context",
        }
    ]
    suggestion_calls = []
    monkeypatch.setattr(
        parameter_application,
        "get_concept_image_slots",
        lambda concept_id, image_types: {
            "modern_concept_1": (1, concept_id, "modern_concept_1", "prompt", b"png")
        },
    )
    monkeypatch.setattr(
        parameter_application,
        "suggest_engineering_data",
        lambda *args: suggestion_calls.append(args) or suggestions,
    )

    parameter_application.run_ai_engineer(
        first_id,
        first,
        "robotics_automation",
        "First prompt",
        "en",
    )

    assert (
        _universal(
            database.get_engineering_parameter_set(first_id),
            "mass_weight",
        )["value"]
        == "25"
    )
    assert database.get_engineering_parameter_set(second_id) is None
    assert suggestion_calls[0][-1] == (("modern_concept_1", b"png"),)


def test_studio_parameter_render_does_not_call_ai_without_explicit_click(
    monkeypatch,
):
    calls = []
    rendered_groups = []
    monkeypatch.setattr(
        drawing_studio_page,
        "get_engineering_parameter_set",
        lambda _concept_id: None,
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "load_engineering_parameters_for_viewer",
        lambda *_args: service.build_empty_parameter_set(),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "run_ai_engineer",
        lambda *args: calls.append(args),
    )
    monkeypatch.setattr(drawing_studio_page.st, "session_state", {})
    monkeypatch.setattr(drawing_studio_page.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        drawing_studio_page.st,
        "container",
        lambda **kwargs: nullcontext(),
    )
    monkeypatch.setattr(drawing_studio_page.st, "subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr(drawing_studio_page, "render_result_box", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_parameter_rows",
        lambda _concept_id, _parameter_set, group, _language, edit_mode: rendered_groups.append(
            (group, edit_mode)
        ),
    )

    drawing_studio_page._render_engineering_parameters(
        11,
        {"title": "Project"},
        "robotics_automation",
        "en",
    )

    assert calls == []
    assert rendered_groups == [
        ("universal", False),
        ("project_specific", False),
    ]


def test_edit_enables_only_core_parameter_fields(monkeypatch):
    field_states = []
    column_specs = []

    class Column:
        def markdown(self, *args, **kwargs):
            return None

        def text_input(self, _label, value, **kwargs):
            field_states.append(kwargs["disabled"])
            return value

    parameter_set = service.build_empty_parameter_set()
    parameter_set["universal"].append(
        {
            "key": "unit_system",
            "label": "Unit System",
            "value": "SI",
            "unit": None,
            "status": "confirmed",
            "source": "user",
            "rationale": None,
        }
    )
    parameter_set["project_specific"] = [
        _project_parameter("payload", "25", "suggested")
    ]
    captions = []
    monkeypatch.setattr(
        drawing_studio_page.st,
        "columns",
        lambda spec, **kwargs: (
            column_specs.append(spec) or [Column(), Column(), Column(), Column()]
        ),
    )
    monkeypatch.setattr(
        drawing_studio_page.st,
        "caption",
        lambda text: captions.append(text),
    )

    drawing_studio_page._render_parameter_rows(
        5,
        parameter_set,
        "universal",
        "en",
        False,
    )
    assert field_states == [True] * 22
    assert column_specs == [(2.3, 1.5, 2.3, 1.2)] * 12
    assert captions == []

    field_states.clear()
    column_specs.clear()
    drawing_studio_page._render_parameter_rows(
        5,
        parameter_set,
        "universal",
        "en",
        True,
    )
    assert field_states == [False] * 22
    assert column_specs == [(2.3, 1.5, 2.3, 1.2)] * 12

    field_states.clear()
    column_specs.clear()
    drawing_studio_page._render_parameter_rows(
        5,
        parameter_set,
        "project_specific",
        "en",
        True,
    )
    assert field_states == [True, True]
    assert len(column_specs) == 2
    assert column_specs == [(2.3, 1.5, 2.3, 1.2)] * 2


def test_project_specific_display_omits_empty_rows(monkeypatch):
    rendered_markdown = []
    rendered_inputs = []
    captions = []
    column_specs = []

    class Column:
        def markdown(self, value, **kwargs):
            rendered_markdown.append(value)

        def text_input(self, _label, value, **kwargs):
            rendered_inputs.append((value, kwargs))
            return value

    parameter_set = service.build_empty_parameter_set()
    parameter_set["project_specific"] = [
        _project_parameter("missing", None),
        _project_parameter("known", "25 kg", "suggested"),
    ]

    def columns(spec, **kwargs):
        column_specs.append(spec)
        return [Column(), Column(), Column(), Column()]

    monkeypatch.setattr(drawing_studio_page.st, "columns", columns)
    monkeypatch.setattr(
        drawing_studio_page.st,
        "caption",
        lambda *args: captions.append(args),
    )
    monkeypatch.setattr(drawing_studio_page.st, "space", lambda *args: None)

    drawing_studio_page._render_parameter_rows(
        7,
        parameter_set,
        "project_specific",
        "en",
        False,
    )

    assert [value for value, _kwargs in rendered_inputs] == ["25 kg", ""]
    assert all(kwargs["disabled"] for _value, kwargs in rendered_inputs)
    assert "**Known**" in rendered_markdown
    assert "**Missing**" not in rendered_markdown
    assert captions == []
    assert column_specs == [
        (2.3, 1.5, 2.3, 1.2),
        (2.3, 1.5, 2.3, 1.2),
    ]
    assert parameter_set["project_specific"][1]["rationale"] == (
        "Needed for project preparation"
    )


def test_parameter_value_and_unit_widget_keys_include_viewer_language(monkeypatch):
    widget_keys = []

    class Column:
        def markdown(self, *_args, **_kwargs):
            return None

        def text_input(self, _label, value, **kwargs):
            widget_keys.append(kwargs["key"])
            return value

    parameter_set = service.build_empty_parameter_set()
    parameter_set["universal"] = [
        _universal(parameter_set, "overall_dimensions_envelope")
    ]
    parameter_set["project_specific"] = [
        _project_parameter("payload", "25", "suggested")
    ]
    monkeypatch.setattr(
        drawing_studio_page.st,
        "columns",
        lambda *args, **kwargs: [Column(), Column(), Column(), Column()],
    )
    monkeypatch.setattr(drawing_studio_page.st, "space", lambda *args: None)

    for language in ("en", "ru"):
        for group_name in ("universal", "project_specific"):
            drawing_studio_page._render_parameter_rows(
                7,
                parameter_set,
                group_name,
                language,
                False,
            )

    assert widget_keys == [
        "engineering_parameter_value_7_overall_dimensions_envelope_en_view",
        "engineering_parameter_unit_7_overall_dimensions_envelope_en",
        "engineering_parameter_project_specific_value_7_payload_en",
        "engineering_parameter_project_specific_unit_7_payload_en",
        "engineering_parameter_value_7_overall_dimensions_envelope_ru_view",
        "engineering_parameter_unit_7_overall_dimensions_envelope_ru",
        "engineering_parameter_project_specific_value_7_payload_ru",
        "engineering_parameter_project_specific_unit_7_payload_ru",
    ]


@pytest.mark.parametrize(
    ("language", "expected"),
    (
        ("en", "Length=20; Width=3; Height=2"),
        ("ru", "Длина=20; Ширина=3; Высота=2"),
        ("sv", "Längd=20; Bredd=3; Höjd=2"),
    ),
)
def test_overall_envelope_display_labels_are_localized(language, expected):
    canonical = "length=20; width=3; height=2"

    assert (
        drawing_studio_page._format_overall_envelope_for_viewer(canonical, language)
        == expected
    )
    assert canonical == "length=20; width=3; height=2"


def test_envelope_edit_and_save_keep_canonical_syntax(
    monkeypatch,
    temporary_database,
    valid_concept,
):
    concept_id = _save_test_concept(valid_concept, "Localized envelope")
    parameter_set = service.build_empty_parameter_set()
    envelope = _universal(parameter_set, "overall_dimensions_envelope")
    envelope.update(
        {
            "value": "length=20; width=3; height=2",
            "unit": "m",
            "status": "confirmed",
            "source": "user",
        }
    )
    parameter_set["universal"] = [envelope]
    database.save_engineering_parameter_set(concept_id, parameter_set, "en")
    rendered_inputs = []

    class Column:
        def markdown(self, *_args, **_kwargs):
            return None

        def text_input(self, _label, value, **kwargs):
            rendered_inputs.append((value, kwargs["key"]))
            return value

    monkeypatch.setattr(
        drawing_studio_page.st,
        "columns",
        lambda *args, **kwargs: [Column(), Column(), Column(), Column()],
    )
    monkeypatch.setattr(drawing_studio_page.st, "space", lambda *args: None)

    drawing_studio_page._render_parameter_rows(
        concept_id,
        parameter_set,
        "universal",
        "ru",
        False,
    )
    rendered_values = drawing_studio_page._render_parameter_rows(
        concept_id,
        parameter_set,
        "universal",
        "ru",
        True,
    )
    parameter_application.save_engineering_parameter_values(
        concept_id,
        parameter_set,
        "universal",
        rendered_values,
    )

    stored = database.get_engineering_parameter_set(concept_id)
    stored_envelope = _universal(stored, "overall_dimensions_envelope")
    arrangement = build_general_arrangement(valid_concept, stored)
    assert rendered_inputs[0] == (
        "Длина=20; Ширина=3; Высота=2",
        f"engineering_parameter_value_{concept_id}_overall_dimensions_envelope_ru_view",
    )
    assert rendered_inputs[2] == (
        "length=20; width=3; height=2",
        f"engineering_parameter_value_{concept_id}_overall_dimensions_envelope_ru_edit",
    )
    assert stored_envelope["value"] == "length=20; width=3; height=2"
    assert arrangement.overall_envelope.length.value == 20000
    assert arrangement.overall_envelope.width.value == 3000
    assert arrangement.overall_envelope.height.value == 2000


def test_project_specific_displays_concept_components_without_storing_them(
    monkeypatch,
    temporary_database,
    valid_concept,
):
    concept_id = _save_test_concept(valid_concept, "Component display")
    parameter_set = service.build_empty_parameter_set()
    parameter_set["project_specific"] = [
        _project_parameter("payload", "25", "suggested")
    ]
    database.save_engineering_parameter_set(concept_id, parameter_set)
    stored_before = copy.deepcopy(database.get_engineering_parameter_set(concept_id))
    rendered_headings = []
    rendered_components = []
    concept_data = {
        "system_components": ["Main Frame", {"name": "Drive Unit"}],
    }

    monkeypatch.setattr(
        drawing_studio_page.st,
        "markdown",
        lambda value, **kwargs: rendered_headings.append(value),
    )
    monkeypatch.setattr(
        drawing_studio_page.st,
        "write",
        lambda marker, value: rendered_components.append((marker, value)),
    )

    drawing_studio_page._render_system_components(concept_data, "en")

    assert rendered_headings == ["**System Components**"]
    assert rendered_components == [("•", "Main Frame"), ("•", "Drive Unit")]
    assert database.get_engineering_parameter_set(concept_id) == stored_before
    assert all(
        parameter["key"] != "system_components"
        for parameter in stored_before["project_specific"]
    )


def test_block_saves_are_independent_and_update_internal_statuses(
    monkeypatch,
    temporary_database,
    valid_concept,
):
    first_id = _save_test_concept(valid_concept, "Editable project")
    second_id = _save_test_concept(valid_concept, "Isolated project")
    parameter_set = service.build_empty_parameter_set()
    parameter_set["project_specific"] = [
        _project_parameter("payload", "AI value", "suggested")
    ]
    database.save_engineering_parameter_set(first_id, parameter_set)
    isolated = service.build_empty_parameter_set()
    isolated_envelope = _universal(isolated, "overall_dimensions_envelope")
    isolated_envelope["value"] = "length=10; width=5; height=4"
    isolated_envelope["unit"] = "ft"
    isolated_envelope["status"] = "confirmed"
    database.save_engineering_parameter_set(second_id, isolated)

    reruns = []
    monkeypatch.setattr(
        drawing_studio_page.st,
        "session_state",
        {
            f"engineering_parameters_edit_mode_{first_id}_universal": True,
        },
    )
    monkeypatch.setattr(
        drawing_studio_page.st,
        "button",
        lambda _label, **kwargs: kwargs.get("key")
        == f"engineering_parameters_save_{first_id}_universal",
    )
    monkeypatch.setattr(
        drawing_studio_page.st,
        "container",
        lambda **kwargs: nullcontext(),
    )
    monkeypatch.setattr(
        drawing_studio_page.st,
        "subheader",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(drawing_studio_page.st, "rerun", lambda: reruns.append(True))
    monkeypatch.setattr(drawing_studio_page, "render_result_box", lambda *args, **kwargs: None)

    def render_rows(_concept_id, current, group_name, _language, edit_mode):
        assert edit_mode is (group_name == "universal")
        values = {
            parameter["key"]: (parameter["value"], parameter["unit"])
            for parameter in current[group_name]
        }
        if group_name == "universal":
            values["overall_dimensions_envelope"] = (
                "length=1; width=0.5; height=0.5",
                "m",
            )
        return values

    monkeypatch.setattr(drawing_studio_page, "_render_parameter_rows", render_rows)

    drawing_studio_page._render_engineering_parameters(
        first_id,
        valid_concept,
        "robotics_automation",
        "en",
    )

    reloaded = database.get_engineering_parameter_set(first_id)
    reloaded_envelope = _universal(reloaded, "overall_dimensions_envelope")
    assert reloaded_envelope["value"] == "length=1; width=0.5; height=0.5"
    assert reloaded_envelope["unit"] == "m"
    assert reloaded_envelope["status"] == "confirmed"
    assert reloaded_envelope["source"] == "user"
    assert _universal(reloaded, "mass_weight")["value"] is None
    assert _universal(reloaded, "mass_weight")["status"] == "missing"
    assert reloaded["project_specific"][0]["value"] == "AI value"
    assert reloaded["project_specific"][0]["status"] == "suggested"
    assert drawing_studio_page.st.session_state[
        f"engineering_parameters_edit_mode_{first_id}_universal"
    ] is False

    assert (
        _universal(
            database.get_engineering_parameter_set(second_id),
            "overall_dimensions_envelope",
        )["value"]
        == "length=10; width=5; height=4"
    )
    assert reruns == [True]


def test_ai_engineer_button_runs_one_workflow(monkeypatch):
    calls = []
    reruns = []
    button_keys = []
    session_state = {
        "engineering_parameter_value_12_mass_weight_en": "",
        "engineering_parameter_unit_12_mass_weight_en": "",
        "engineering_parameter_value_12_overall_dimensions_envelope_en_view": "",
        "engineering_parameter_value_12_overall_dimensions_envelope_en_edit": "",
        "engineering_parameter_unit_12_overall_dimensions_envelope_en": "",
        "engineering_parameter_project_specific_value_12_payload_en": "25",
        "unrelated": "preserved",
    }
    monkeypatch.setattr(
        drawing_studio_page,
        "get_engineering_parameter_set",
        lambda _concept_id: None,
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "load_engineering_parameters_for_viewer",
        lambda *_args: service.build_empty_parameter_set(),
    )
    monkeypatch.setattr(drawing_studio_page, "get_concept_prompt", lambda _concept_id: "prompt")
    monkeypatch.setattr(
        drawing_studio_page,
        "run_ai_engineer",
        lambda *args: calls.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "save_engineering_parameter_values",
        lambda *args: None,
    )
    monkeypatch.setattr(drawing_studio_page.st, "session_state", session_state)
    def click_ai_engineer(_label, **kwargs):
        button_keys.append(kwargs.get("key"))
        return kwargs.get("key") == "engineering_parameters_ai_engineer_12"

    monkeypatch.setattr(drawing_studio_page.st, "button", click_ai_engineer)
    monkeypatch.setattr(
        drawing_studio_page.st,
        "container",
        lambda **kwargs: nullcontext(),
    )
    monkeypatch.setattr(drawing_studio_page.st, "rerun", lambda: reruns.append(True))
    monkeypatch.setattr(drawing_studio_page.st, "subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr(drawing_studio_page, "render_result_box", lambda *args, **kwargs: None)
    monkeypatch.setattr(drawing_studio_page, "_render_parameter_rows", lambda *args: None)

    drawing_studio_page._render_engineering_parameters(
        12,
        {"title": "Robot"},
        "robotics_automation",
        "en",
    )

    assert len(calls) == 1
    assert calls[0] == (
        12,
        {"title": "Robot"},
        "robotics_automation",
        "prompt",
        "en",
    )
    assert "engineering_parameters_suggest_12" not in button_keys
    assert "engineering_parameters_edit_12_project_specific" not in button_keys
    assert "engineering_parameters_save_12_project_specific" not in button_keys
    assert session_state == {
        "engineering_parameter_project_specific_value_12_payload_en": "25",
        "unrelated": "preserved",
    }
    assert reruns == [True]


def test_all_engineering_parameter_ui_keys_exist_for_all_languages():
    keys = {
        key
        for key in TRANSLATIONS["en"]
        if key.startswith("engineering_parameters.")
    }
    assert len(keys) == 34
    assert all(keys <= set(TRANSLATIONS[language]) for language in LANGUAGES)


def test_viewer_translation_is_cached_and_preserves_canonical_parameters(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    concept_id = _save_test_concept(valid_concept, "Bridge")
    canonical = service.build_empty_parameter_set()
    parameter = _project_parameter(
        "assembly_time",
        "Quick modular assembly",
        "suggested",
        label="Assembly Time",
    )
    parameter["unit"] = "hours"
    canonical["project_specific"] = [parameter]
    core_parameter = _universal(canonical, "primary_materials")
    core_parameter.update(
        {
            "value": "Lightweight composite materials, Recycled aluminium",
            "status": "suggested",
            "source": "ai",
            "rationale": "Selected for low mass.",
        }
    )
    database.save_engineering_parameter_set(concept_id, canonical, "en")
    calls = []

    def translate(original, source_language, target_language):
        calls.append((source_language, target_language))
        translated = copy.deepcopy(original)
        translated["project_specific"][0].update(
            {
                "label": "Время сборки",
                "value": "Быстрая модульная сборка",
                "rationale": "Предполагается модульная конструкция.",
                "unit": "часы",
            }
        )
        _universal(translated, "primary_materials")["value"] = (
            "Лёгкие композитные материалы, переработанный алюминий"
        )
        return translated

    monkeypatch.setattr(
        concept_translation_service,
        "translate_engineering_parameter_set",
        translate,
    )

    english = parameter_application.load_engineering_parameters_for_viewer(
        concept_id,
        "en",
    )
    russian = parameter_application.load_engineering_parameters_for_viewer(
        concept_id,
        "ru",
    )
    russian_again = parameter_application.load_engineering_parameters_for_viewer(
        concept_id,
        "ru",
    )
    english_again = parameter_application.load_engineering_parameters_for_viewer(
        concept_id,
        "en",
    )
    parameter_application.load_engineering_parameters_for_viewer(concept_id, "ru")

    assert calls == [("en", "ru")]
    assert english_again == english == canonical
    assert russian_again == russian
    assert russian["project_specific"][0]["label"] == "Время сборки"
    assert russian["project_specific"][0]["value"] == "Быстрая модульная сборка"
    assert russian["project_specific"][0]["rationale"].startswith("Предполагается")
    assert russian["project_specific"][0]["unit"] == "часы"
    assert _universal(russian, "primary_materials")["value"].startswith("Лёгкие")
    assert database.get_engineering_parameter_set(concept_id) == canonical


def test_structured_translation_changes_only_display_fields(monkeypatch):
    parameter_set = service.build_empty_parameter_set()
    core_text = _universal(parameter_set, "operating_environment")
    core_text.update(
        {
            "value": "Outdoor, variable weather conditions",
            "source": "concept",
            "status": "suggested",
            "rationale": "Defines the operating context.",
        }
    )
    user_text = _universal(parameter_set, "primary_materials")
    user_text.update(
        {
            "value": "Lightweight composite materials, Recycled aluminium",
            "source": "user",
            "status": "confirmed",
        }
    )
    ai_text = _universal(parameter_set, "interfaces_connections")
    ai_text.update(
        {
            "value": "Modular connections for quick assembly",
            "source": "ai",
            "status": "suggested",
            "rationale": "Defines assembly interfaces.",
        }
    )
    manufacturing = _universal(parameter_set, "manufacturing_constraints")
    manufacturing.update(
        {
            "value": "Limited production capacity for initial prototypes",
            "source": "concept",
            "status": "suggested",
        }
    )
    maintenance = _universal(parameter_set, "service_maintenance_conditions")
    maintenance.update(
        {
            "value": "Regular inspections required post-deployment",
            "source": "ai",
            "status": "suggested",
        }
    )
    envelope = _universal(parameter_set, "overall_dimensions_envelope")
    envelope.update(
        {
            "value": "length=20; width=3; height=2",
            "unit": "m",
            "source": "ai",
            "status": "suggested",
            "rationale": "Known envelope.",
        }
    )
    hours = _project_parameter("assembly_time", "1-3", "suggested")
    hours["unit"] = "hours"
    meters = _project_parameter(
        "maximum_river_width",
        "Modular connections for quick assembly",
        "suggested",
        label="Maximum River Width",
    )
    meters["unit"] = "meters"
    technical_units = []
    for key, value, unit in (
        ("mass", "5000", "kg"),
        ("clearance", "1.5", "mm"),
        ("span", "10-20", "m"),
        ("efficiency", "15-20", "%"),
        ("energy", "100", "Wh"),
    ):
        parameter = _project_parameter(key, value, "suggested")
        parameter["unit"] = unit
        technical_units.append(parameter)
    parameter_set["project_specific"] = [hours, meters, *technical_units]
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        response_payload = json.loads(kwargs["messages"][-1]["content"])
        translated = copy.deepcopy(response_payload)
        _universal(translated, "operating_environment")["value"] = (
            "На открытом воздухе, переменные погодные условия"
        )
        _universal(translated, "primary_materials")["value"] = (
            "Лёгкие композитные материалы, переработанный алюминий"
        )
        _universal(translated, "interfaces_connections")["value"] = (
            "Модульные соединения для быстрой сборки"
        )
        _universal(translated, "manufacturing_constraints")["value"] = (
            "Ограниченные производственные мощности для первых прототипов"
        )
        _universal(translated, "service_maintenance_conditions")["value"] = (
            "После ввода в эксплуатацию требуются регулярные проверки"
        )
        for parameter in translated["project_specific"]:
            if parameter["label"] is not None:
                parameter["label"] = f"RU: {parameter['label']}"
            if parameter["value"] is not None:
                parameter["value"] = "Модульные соединения для быстрой сборки"
            if parameter["unit_text"] == "hours":
                parameter["unit_text"] = "часы"
            elif parameter["unit_text"] == "meters":
                parameter["unit_text"] = "метры"
            if parameter["rationale"] is not None:
                parameter["rationale"] = "Переведённое обоснование"
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps(translated, ensure_ascii=False)
                    )
                )
            ]
        )

    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=create,
            )
        )
    )
    monkeypatch.setattr(concept_translation_service, "get_text_client", lambda: client)

    translated = concept_translation_service.translate_engineering_parameter_set(
        parameter_set,
        "en",
        "ru",
    )

    assert len(calls) == 1
    request_payload = json.loads(calls[0]["messages"][-1]["content"])
    requested_project_units = {
        parameter["key"]: parameter["unit_text"]
        for parameter in request_payload["project_specific"]
    }
    assert requested_project_units == {
        "assembly_time": "hours",
        "maximum_river_width": "meters",
        "mass": None,
        "clearance": None,
        "span": None,
        "efficiency": None,
        "energy": None,
    }
    assert _universal(request_payload, "overall_dimensions_envelope")["value"] == (
        "length=20; width=3; height=2"
    )
    assert (
        _universal(request_payload, "overall_dimensions_envelope")["unit_text"]
        is None
    )
    assert _universal(translated, "operating_environment")["value"].startswith(
        "На открытом"
    )
    assert _universal(translated, "primary_materials")["value"].startswith(
        "Лёгкие"
    )
    assert _universal(translated, "interfaces_connections")["value"].startswith(
        "Модульные"
    )
    assert _universal(translated, "manufacturing_constraints")["value"].startswith(
        "Ограниченные"
    )
    assert _universal(
        translated,
        "service_maintenance_conditions",
    )["value"].startswith("После ввода")
    assert translated["project_specific"][0]["label"].startswith("RU:")
    assert translated["project_specific"][0]["unit"] == "часы"
    assert translated["project_specific"][0]["value"] == "1-3"
    assert translated["project_specific"][1]["value"].startswith("Модульные")
    assert translated["project_specific"][1]["unit"] == "метры"
    assert [parameter["unit"] for parameter in translated["project_specific"][2:]] == [
        "kg",
        "mm",
        "m",
        "%",
        "Wh",
    ]
    assert [parameter["value"] for parameter in translated["project_specific"][2:]] == [
        "5000",
        "1.5",
        "10-20",
        "15-20",
        "100",
    ]
    assert _universal(translated, "overall_dimensions_envelope")["value"] == (
        "length=20; width=3; height=2"
    )
    assert _universal(translated, "overall_dimensions_envelope")["unit"] == "m"
    assert translated["project_specific"][0]["status"] == "suggested"
