import json
from types import SimpleNamespace

import database
from i18n import LANGUAGES, TRANSLATIONS
from services import engineering_parameters_service as service
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


def test_universal_core_is_generic_and_supports_missing_and_not_applicable():
    parameter_set = service.build_empty_parameter_set()
    keys = {item["key"] for item in parameter_set["universal"]}

    assert len(keys) == 12
    assert not any("bridge" in key or "river" in key for key in keys)
    assert all(item["status"] == "missing" for item in parameter_set["universal"])
    assert service.calculate_readiness(parameter_set) == "incomplete"

    parameter_set["universal"][0]["status"] = "confirmed"
    assert service.calculate_readiness(parameter_set) == "partial"
    for item in parameter_set["universal"]:
        item["status"] = "not_applicable"
    assert service.calculate_readiness(parameter_set) == "ready"


def test_repeated_suggestions_preserve_confirmed_and_user_edited_values():
    parameter_set = service.build_empty_parameter_set()
    parameter_set["project_specific"] = [
        _project_parameter("payload", "25 kg", "confirmed", "ai"),
        _project_parameter("operating_cycle", "AI cycle", "suggested", "ai"),
    ]
    parameter_set = service.update_parameter(
        parameter_set,
        "project_specific",
        "operating_cycle",
        "User cycle",
        None,
        "edit",
    )
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


def test_confirm_and_not_applicable_actions_update_readiness():
    parameter_set = service.build_empty_parameter_set()
    first_key = parameter_set["universal"][0]["key"]
    parameter_set = service.update_parameter(
        parameter_set,
        "universal",
        first_key,
        "SI",
        None,
        "confirm",
    )
    assert parameter_set["universal"][0]["status"] == "confirmed"
    assert service.calculate_readiness(parameter_set) == "partial"

    for parameter in list(parameter_set["universal"])[1:]:
        parameter_set = service.update_parameter(
            parameter_set,
            "universal",
            parameter["key"],
            None,
            None,
            "not_applicable",
        )
    assert service.calculate_readiness(parameter_set) == "ready"


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
        "suggest_project_parameters",
        lambda *args: calls.append(args),
    )
    monkeypatch.setattr(drawing_studio_page.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(drawing_studio_page.st, "subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr(drawing_studio_page, "render_result_box", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_parameter_rows",
        lambda _concept_id, _parameter_set, group, _language: rendered_groups.append(group),
    )

    drawing_studio_page._render_engineering_parameters(
        11,
        {"title": "Project"},
        "robotics_automation",
        "en",
    )

    assert calls == []
    assert rendered_groups == ["universal", "project_specific"]


def test_suggest_button_makes_one_call_and_saves_merged_set(monkeypatch):
    calls = []
    saved = []
    reruns = []
    monkeypatch.setattr(
        drawing_studio_page,
        "get_engineering_parameter_set",
        lambda _concept_id: None,
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
        lambda *args: saved.append(args),
    )
    monkeypatch.setattr(drawing_studio_page.st, "button", lambda *args, **kwargs: True)
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
    assert saved[0][0] == 12
    assert saved[0][1]["project_specific"][0]["key"] == "payload"
    assert reruns == [True]


def test_all_engineering_parameter_ui_keys_exist_for_all_languages():
    keys = {
        key
        for key in TRANSLATIONS["en"]
        if key.startswith("engineering_parameters.")
    }
    assert len(keys) == 36
    assert all(keys <= set(TRANSLATIONS[language]) for language in LANGUAGES)
