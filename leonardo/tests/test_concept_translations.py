import copy
import json
from types import SimpleNamespace

import pytest

import database
from application import concepts
from services import concept_translation_service
from services.concept_schema import validate_concept_data


def _save_source_concept(concept_data, language="ru", title=None):
    return database.save_concept(
        title=title or concept_data["title"],
        category="robotics",
        prompt="original prompt",
        concept_data=concept_data,
        concept_language=language,
    )


def _translated_copy(concept_data, language):
    translated = copy.deepcopy(concept_data)
    translated["title"] = f'{concept_data["title"]} [{language}]'
    return translated


def test_source_language_returns_original_without_translation(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    concept_id = _save_source_concept(valid_concept, "ru")
    calls = []
    monkeypatch.setattr(
        concept_translation_service,
        "translate_concept_data",
        lambda *args: calls.append(args),
    )

    viewed, source_language = concepts.load_concept_for_viewer(concept_id, "ru")

    assert viewed == valid_concept
    assert source_language == "ru"
    assert calls == []


def test_missing_translation_is_generated_validated_and_saved_once(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    concept_id = _save_source_concept(valid_concept, "ru")
    expected = _translated_copy(valid_concept, "en")
    calls = []

    def translate(original, source_language, target_language):
        calls.append((original, source_language, target_language))
        return expected

    monkeypatch.setattr(
        concept_translation_service,
        "translate_concept_data",
        translate,
    )

    viewed, source_language = concepts.load_concept_for_viewer(concept_id, "en")
    viewed_again, _ = concepts.load_concept_for_viewer(concept_id, "en")

    assert viewed == validate_concept_data(expected)
    assert viewed_again == viewed
    assert source_language == "ru"
    assert len(calls) == 1
    assert database.get_concept_translation(concept_id, "en") == expected


def test_second_view_reuses_cached_translation_without_api_call(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    concept_id = _save_source_concept(valid_concept, "ru")
    expected = _translated_copy(valid_concept, "en")
    database.save_concept_translation(concept_id, "en", expected)

    def unexpected_translation(*args):
        raise AssertionError("Cached translation must prevent an API call")

    monkeypatch.setattr(
        concept_translation_service,
        "translate_concept_data",
        unexpected_translation,
    )

    viewed, source_language = concepts.load_concept_for_viewer(concept_id, "en")

    assert viewed == expected
    assert source_language == "ru"


def test_translation_upsert_keeps_one_row_per_concept_and_language(
    temporary_database,
    valid_concept,
):
    concept_id = _save_source_concept(valid_concept, "ru")
    first = _translated_copy(valid_concept, "en-first")
    second = _translated_copy(valid_concept, "en-second")

    database.save_concept_translation(concept_id, "en", first)
    database.save_concept_translation(concept_id, "en", second)

    with database.get_connection() as connection:
        row_count = connection.execute(
            """
            SELECT COUNT(*) FROM concept_translations
            WHERE concept_id = ? AND language_code = 'en'
            """,
            (concept_id,),
        ).fetchone()[0]

    assert row_count == 1
    assert database.get_concept_translation(concept_id, "en") == second


def test_each_target_language_has_an_independent_cache_entry(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    concept_id = _save_source_concept(valid_concept, "ru")
    calls = []

    def translate(original, source_language, target_language):
        calls.append(target_language)
        return _translated_copy(original, target_language)

    monkeypatch.setattr(
        concept_translation_service,
        "translate_concept_data",
        translate,
    )

    english, _ = concepts.load_concept_for_viewer(concept_id, "en")
    swedish, _ = concepts.load_concept_for_viewer(concept_id, "sv")
    english_again, _ = concepts.load_concept_for_viewer(concept_id, "en")

    assert calls == ["en", "sv"]
    assert english["title"].endswith("[en]")
    assert swedish["title"].endswith("[sv]")
    assert english_again == english


def test_switching_viewer_language_never_changes_original_concept_json(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    concept_id = _save_source_concept(valid_concept, "ru")
    original_before = database.get_concept_by_id(concept_id)
    monkeypatch.setattr(
        concept_translation_service,
        "translate_concept_data",
        lambda original, source, target: _translated_copy(original, target),
    )

    concepts.load_concept_for_viewer(concept_id, "en")
    concepts.load_concept_for_viewer(concept_id, "sv")
    original_view, _ = concepts.load_concept_for_viewer(concept_id, "ru")

    assert database.get_concept_by_id(concept_id) == original_before
    assert original_view == valid_concept


def test_translation_service_preserves_structure_and_validates_result(
    valid_concept,
    monkeypatch,
):
    translated = _translated_copy(valid_concept, "sv")
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
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
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )
    monkeypatch.setattr(
        concept_translation_service,
        "get_text_client",
        lambda: client,
    )

    result = concept_translation_service.translate_concept_data(
        valid_concept,
        "ru",
        "sv",
    )

    assert result == validate_concept_data(translated)
    assert captured["model"] == "gpt-4o-mini"
    assert captured["temperature"] == 0
    assert captured["response_format"] == {"type": "json_object"}


def test_translation_service_rejects_changed_array_structure(
    valid_concept,
    monkeypatch,
):
    invalid_translation = copy.deepcopy(valid_concept)
    invalid_translation["target_users"].append("unexpected item")
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(
                                content=json.dumps(invalid_translation)
                            )
                        )
                    ]
                )
            )
        )
    )
    monkeypatch.setattr(
        concept_translation_service,
        "get_text_client",
        lambda: client,
    )

    with pytest.raises(ValueError, match="list structure"):
        concept_translation_service.translate_concept_data(
            valid_concept,
            "ru",
            "en",
        )


def test_legacy_backfill_assigns_only_known_concept_languages(
    temporary_database,
    valid_concept,
):
    serialized = json.dumps(valid_concept, ensure_ascii=False)
    connection = database.get_connection()
    try:
        connection.executemany(
            """
            INSERT INTO concepts (id, title, category, prompt, concept_json)
            VALUES (?, ?, 'robotics', 'legacy', ?)
            """,
            (
                (19, "AquaClean Station", serialized),
                (23, "Модульная система аварийных мостов", serialized),
                (24, "Unknown legacy concept", serialized),
            ),
        )
        connection.commit()
    finally:
        connection.close()

    database.init_db()

    assert database.get_concept_language(19) == "en"
    assert database.get_concept_language(23) == "ru"
    assert database.get_concept_language(24) is None


def test_unknown_legacy_source_returns_original_without_translation(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    connection = database.get_connection()
    try:
        cursor = connection.execute(
            """
            INSERT INTO concepts (title, category, prompt, concept_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                "Unknown legacy concept",
                "robotics",
                "legacy",
                json.dumps(valid_concept, ensure_ascii=False),
            ),
        )
        connection.commit()
        concept_id = cursor.lastrowid
    finally:
        connection.close()

    def unexpected_translation(*args):
        raise AssertionError("Unknown source language must not trigger translation")

    monkeypatch.setattr(
        concept_translation_service,
        "translate_concept_data",
        unexpected_translation,
    )

    viewed, source_language = concepts.load_concept_for_viewer(concept_id, "sv")

    assert viewed == valid_concept
    assert source_language is None
