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

    assert len(keys) == 12
    assert not any("bridge" in key or "river" in key for key in keys)
    assert all(item["status"] == "missing" for item in parameter_set["universal"])


def test_component_geometry_survives_validation_save_and_load(
    temporary_database,
    valid_concept,
):
    concept_id = _save_test_concept(valid_concept, "Geometry contract")
    parameter_set = service.build_empty_parameter_set()
    parameter_set["universal"][0]["value"] = "SI"
    parameter_set["project_specific"] = [_project_parameter("payload", "25")]
    parameter_set["component_geometry"] = {
        "main-frame": {
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
        "length": "1.2",
        "width": None,
        "height": "0.6",
        "x": "0",
        "y": None,
        "z": "25",
        "unit": "m",
    }
    assert loaded["universal"][0]["value"] == "SI"
    assert loaded["project_specific"][0]["value"] == "25"
    assert "unknown_top_level" not in loaded


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
    parameter_set["universal"][0]["value"] = "SI"
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
    assert loaded["universal"][0]["value"] == "SI"
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


def test_repeated_suggestions_preserve_confirmed_and_user_edited_values():
    parameter_set = service.build_empty_parameter_set()
    parameter_set["project_specific"] = [
        _project_parameter("payload", "25 kg", "confirmed", "ai"),
        _project_parameter("operating_cycle", "AI cycle", "suggested", "ai"),
    ]
    parameter_set["project_specific"][1]["value"] = "User cycle"
    parameter_set["project_specific"][1]["source"] = "user"
    suggestions = [
        _project_parameter("payload", "40 kg", "suggested"),
        _project_parameter("operating_cycle", "AI cycle", "suggested"),
        _project_parameter("reach", "1–2 m preliminary range", "suggested"),
        _project_parameter("reach", "duplicate", "suggested"),
        _project_parameter(
            "alternate_reach_key",
            "duplicate by label",
            "suggested",
            label="Reach",
        ),
        _project_parameter("unit_system", "SI", "suggested", label="Unit System"),
    ]

    merged = service.merge_project_suggestions(parameter_set, suggestions)
    by_key = {item["key"]: item for item in merged["project_specific"]}

    assert by_key["payload"]["value"] == "25 kg"
    assert by_key["operating_cycle"]["value"] == "User cycle"
    assert by_key["reach"]["value"] == "1–2 m preliminary range"
    assert list(item["key"] for item in merged["project_specific"]).count("reach") == 1
    assert "alternate_reach_key" not in by_key
    assert "unit_system" not in by_key


def test_ai_suggestion_uses_shared_client_once_and_returns_structured_data(
    monkeypatch,
    valid_concept,
):
    calls = []
    payload = {
        "project_specific": [
            _project_parameter("payload", None, "missing"),
            _project_parameter("reach", "1–2 m preliminary range", "suggested"),
        ]
    }
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

    result = service.suggest_project_parameters(
        valid_concept,
        "robotics_automation",
        "A configurable service robot",
        "en",
    )

    assert len(calls) == 1
    assert [item["key"] for item in result] == ["payload", "reach"]
    assert result[0]["value"] is None
    prompt = "\n".join(message["content"] for message in calls[0]["messages"])
    assert "Never invent unsupported precision" in prompt
    assert "Do not infer measurements from images" in prompt
    assert "A configurable service robot" in prompt
    assert "technical_requirements" in prompt


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
        "suggest_project_parameters",
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


def test_edit_enables_value_and_unit_fields_in_both_parameter_blocks(monkeypatch):
    field_states = []

    class Column:
        def markdown(self, *args, **kwargs):
            return None

        def text_input(self, _label, value, **kwargs):
            field_states.append(kwargs["disabled"])
            return value

    parameter_set = service.build_empty_parameter_set()
    parameter_set["universal"] = parameter_set["universal"][:1]
    parameter_set["project_specific"] = [
        _project_parameter("payload", "25", "suggested")
    ]
    captions = []
    monkeypatch.setattr(
        drawing_studio_page.st,
        "columns",
        lambda *args, **kwargs: [Column(), Column(), Column(), Column()],
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
    drawing_studio_page._render_parameter_rows(
        5,
        parameter_set,
        "project_specific",
        "en",
        False,
    )
    assert field_states == [True, True, True, True]
    assert captions == ["AI Suggestion: Needed for project preparation"]

    field_states.clear()
    drawing_studio_page._render_parameter_rows(
        5,
        parameter_set,
        "universal",
        "en",
        True,
    )
    drawing_studio_page._render_parameter_rows(
        5,
        parameter_set,
        "project_specific",
        "en",
        True,
    )
    assert field_states == [False, False, False, False]


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
    isolated["universal"][0]["value"] = "Imperial"
    isolated["universal"][0]["status"] = "confirmed"
    database.save_engineering_parameter_set(second_id, isolated)

    reruns = []
    ai_calls = []
    active_group = ["universal"]
    monkeypatch.setattr(
        drawing_studio_page.st,
        "session_state",
        {
            f"engineering_parameters_edit_mode_{first_id}_universal": True,
            f"engineering_parameters_edit_mode_{first_id}_project_specific": False,
        },
    )
    monkeypatch.setattr(
        drawing_studio_page.st,
        "button",
        lambda _label, **kwargs: kwargs.get("key")
        == f"engineering_parameters_save_{first_id}_{active_group[0]}",
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
    monkeypatch.setattr(
        drawing_studio_page,
        "suggest_project_parameters",
        lambda *args: ai_calls.append(args),
    )

    def render_rows(_concept_id, current, group_name, _language, edit_mode):
        assert edit_mode is (group_name == active_group[0])
        values = {
            parameter["key"]: (parameter["value"], parameter["unit"])
            for parameter in current[group_name]
        }
        if group_name == "universal" and active_group[0] == "universal":
            values[current[group_name][0]["key"]] = ("SI", "system")
        if group_name == "project_specific" and active_group[0] == "project_specific":
            values[current[group_name][0]["key"]] = ("Reviewed AI value", "kg")
        return values

    monkeypatch.setattr(drawing_studio_page, "_render_parameter_rows", render_rows)

    drawing_studio_page._render_engineering_parameters(
        first_id,
        valid_concept,
        "robotics_automation",
        "en",
    )

    reloaded = database.get_engineering_parameter_set(first_id)
    assert reloaded["universal"][0]["value"] == "SI"
    assert reloaded["universal"][0]["unit"] == "system"
    assert reloaded["universal"][0]["status"] == "confirmed"
    assert reloaded["universal"][1]["value"] is None
    assert reloaded["universal"][1]["status"] == "missing"
    assert reloaded["project_specific"][0]["value"] == "AI value"
    assert reloaded["project_specific"][0]["status"] == "suggested"
    assert drawing_studio_page.st.session_state[
        f"engineering_parameters_edit_mode_{first_id}_universal"
    ] is False

    active_group[0] = "project_specific"
    drawing_studio_page.st.session_state[
        f"engineering_parameters_edit_mode_{first_id}_project_specific"
    ] = True
    drawing_studio_page._render_engineering_parameters(
        first_id,
        valid_concept,
        "robotics_automation",
        "en",
    )

    reloaded = database.get_engineering_parameter_set(first_id)
    assert reloaded["project_specific"][0]["value"] == "Reviewed AI value"
    assert reloaded["project_specific"][0]["unit"] == "kg"
    assert reloaded["project_specific"][0]["status"] == "confirmed"
    assert database.get_engineering_parameter_set(second_id)["universal"][0]["value"] == "Imperial"
    assert drawing_studio_page.st.session_state[
        f"engineering_parameters_edit_mode_{first_id}_project_specific"
    ] is False
    assert ai_calls == []
    assert reruns == [True, True]


def test_suggest_button_makes_one_call_and_saves_merged_set(monkeypatch):
    calls = []
    saved = []
    reruns = []
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
        "suggest_project_parameters",
        lambda *args: calls.append(args) or [_project_parameter("payload")],
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "save_engineering_parameter_set",
        lambda *args, **kwargs: saved.append((args, kwargs)),
    )
    monkeypatch.setattr(drawing_studio_page.st, "session_state", {})
    monkeypatch.setattr(
        drawing_studio_page.st,
        "button",
        lambda _label, **kwargs: kwargs.get("key") == "engineering_parameters_suggest_12",
    )
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
    assert saved[0][0][0] == 12
    assert saved[0][0][1]["project_specific"][0]["key"] == "payload"
    assert saved[0][1] == {"source_language": "en"}
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
        "1-3 hours",
        "suggested",
        label="Assembly Time",
    )
    parameter["unit"] = "hours"
    canonical["project_specific"] = [parameter]
    database.save_engineering_parameter_set(concept_id, canonical, "en")
    calls = []

    def translate(original, source_language, target_language):
        calls.append((source_language, target_language))
        translated = copy.deepcopy(original)
        translated["project_specific"][0].update(
            {
                "label": "Время сборки",
                "rationale": "Предполагается модульная конструкция.",
                "unit": "часы",
            }
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
    assert russian["project_specific"][0]["rationale"].startswith("Предполагается")
    assert russian["project_specific"][0]["unit"] == "часы"
    assert russian["project_specific"][0]["value"] == "1-3 hours"
    assert database.get_engineering_parameter_set(concept_id) == canonical


def test_structured_translation_changes_only_display_fields(monkeypatch):
    parameter_set = service.build_empty_parameter_set()
    hours = _project_parameter("assembly_time", "1-3 hours", "suggested")
    hours["unit"] = "hours"
    percent = _project_parameter("efficiency", "15-20", "suggested")
    percent["unit"] = "%"
    parameter_set["project_specific"] = [hours, percent]
    response_payload = {
        "project_specific": [
            {
                "key": "assembly_time",
                "label": "Время сборки",
                "rationale": "Необходимо для подготовки проекта",
                "unit": "часы",
            },
            {
                "key": "efficiency",
                "label": "Эффективность",
                "rationale": "Необходимо для подготовки проекта",
                "unit": "%",
            },
        ]
    }
    calls = []
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: calls.append(kwargs)
                or SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(
                                content=json.dumps(
                                    response_payload,
                                    ensure_ascii=False,
                                )
                            )
                        )
                    ]
                )
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
    assert translated["project_specific"][0]["unit"] == "часы"
    assert translated["project_specific"][1]["unit"] == "%"
    assert translated["project_specific"][0]["value"] == "1-3 hours"
    assert translated["project_specific"][0]["status"] == "suggested"
