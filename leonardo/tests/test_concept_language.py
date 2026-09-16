import copy
import json

import database
from application import concepts as concept_application
from i18n import translate
from ui import concept_page, state


def _generate_for_language(valid_concept, language):
    concept = copy.deepcopy(valid_concept)
    concept["title"] = f"Concept {language}"
    return concept


def test_concept_language_is_immutable_across_ui_language_switches(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    session_state = {}
    monkeypatch.setattr(state.st, "session_state", session_state)
    monkeypatch.setattr(
        concept_application,
        "generate_concept",
        lambda language, **kwargs: _generate_for_language(valid_concept, language),
    )

    state.initialize_session_state()
    session_state[state.LANGUAGE] = "ru"
    concept_a, concept_a_id = concept_application.generate_and_save_concept(
        "robotics",
        "Bold",
        "Engineers",
        "Концепция A",
        language=state.get_current_language(),
    )
    state.set_current_concept(concept_a, concept_a_id, "ru")

    assert database.get_concept_language(concept_a_id) == "ru"
    assert state.get_current_concept_language() == "ru"
    assert translate("concept.roadmap", state.get_current_concept_language()) == translate(
        "concept.roadmap",
        "ru",
    )

    session_state[state.LANGUAGE] = "en"

    assert state.get_current_language() == "en"
    assert state.get_current_concept_language() == "ru"

    concept_b, concept_b_id = concept_application.generate_and_save_concept(
        "robotics",
        "Bold",
        "Engineers",
        "Concept B",
        language=state.get_current_language(),
    )
    state.set_current_concept(concept_b, concept_b_id, "en")

    assert concept_b_id != concept_a_id
    assert database.get_concept_language(concept_b_id) == "en"
    assert state.get_current_concept_language() == "en"

    loaded_a, language_a = concept_application.load_concept_with_language(
        concept_a_id
    )
    state.set_current_concept(loaded_a, concept_a_id, language_a)
    assert state.get_current_concept_language() == "ru"
    assert translate("concept.business_need", language_a) == translate(
        "concept.business_need",
        "ru",
    )

    loaded_b, language_b = concept_application.load_concept_with_language(
        concept_b_id
    )
    state.set_current_concept(loaded_b, concept_b_id, language_b)
    assert state.get_current_concept_language() == "en"
    assert translate("concept.business_need", language_b) == translate(
        "concept.business_need",
        "en",
    )

    session_state[state.LANGUAGE] = "de"
    assert state.get_current_language() == "de"
    assert state.get_current_concept_language() == "en"


def test_legacy_concept_without_language_uses_stable_english_fallback(
    temporary_database,
    valid_concept,
):
    connection = database.get_connection()
    try:
        cursor = connection.execute(
            """
            INSERT INTO concepts (title, category, prompt, concept_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                valid_concept["title"],
                "robotics",
                "legacy prompt",
                json.dumps(valid_concept, ensure_ascii=False),
            ),
        )
        connection.commit()
        concept_id = cursor.lastrowid
    finally:
        connection.close()

    loaded, language = concept_application.load_concept_with_language(concept_id)

    assert loaded == valid_concept
    assert database.get_concept_language(concept_id) is None
    assert language == "en"


def test_concept_renderer_passes_viewer_language_to_every_section(
    valid_concept,
    monkeypatch,
):
    rendered_languages = []
    monkeypatch.setattr(concept_page, "get_current_concept_id", lambda: None)
    monkeypatch.setattr(concept_page, "get_current_language", lambda: "sv")
    monkeypatch.setattr(concept_page.st, "success", lambda value: None)

    for function_name in (
        "_render_leonardo_vision",
        "_render_modern_implementation",
        "_render_engineering_drawing_studio",
        "_render_implementation_roadmap",
        "_render_risks_and_constraints",
        "_render_commercial_outlook",
        "render_voice_assistant",
        "_render_delivery_metrics",
        "_render_pdf_export",
    ):
        monkeypatch.setattr(
            concept_page,
            function_name,
            lambda *args: rendered_languages.append(args[-1]),
        )

    concept_page.render_concept_result(valid_concept)

    assert rendered_languages == ["sv"] * 9
