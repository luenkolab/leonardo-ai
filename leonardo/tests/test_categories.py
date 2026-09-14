import json

import pytest

import database
from application import concepts
from categories import (
    CATEGORY_KEYS,
    CATEGORY_TRANSLATIONS,
    normalize_category,
    require_category_key,
)
from i18n import LANGUAGES, category_display_name
from ui import marketplace_page, sidebar, state


def test_canonical_taxonomy_has_exactly_18_unique_ordered_keys():
    assert len(CATEGORY_KEYS) == 18
    assert len(set(CATEGORY_KEYS)) == 18
    assert CATEGORY_KEYS[0] == "ai_software"
    assert CATEGORY_KEYS[-1] == "consumer_lifestyle"


def test_english_category_display_names_are_unique():
    names = CATEGORY_TRANSLATIONS["en"]
    assert len(names) == 18
    assert len(set(names)) == 18


def test_idea_category_and_marketplace_share_the_canonical_taxonomy():
    assert sidebar.CATEGORY_KEYS is CATEGORY_KEYS
    assert marketplace_page.MARKETPLACE_CATEGORIES == ("all", *CATEGORY_KEYS)
    assert "all" not in CATEGORY_KEYS


@pytest.mark.parametrize(
    ("legacy", "canonical"),
    [
        ("Transport", "transport_mobility"),
        ("Architecture", "construction_architecture"),
        ("Medicine", "health_biotech"),
        ("Robotics", "robotics_automation"),
    ],
)
def test_explicit_legacy_category_mapping(legacy, canonical):
    assert normalize_category(legacy) == canonical


def test_invalid_or_ambiguous_category_is_not_canonicalized():
    assert normalize_category("invented-category") is None
    assert normalize_category("Exploration") is None
    with pytest.raises(ValueError):
        require_category_key("invented-category")


def test_generation_boundary_rejects_arbitrary_category(monkeypatch):
    monkeypatch.setattr(
        concepts,
        "generate_concept",
        lambda **kwargs: pytest.fail("generation must not start"),
    )

    with pytest.raises(ValueError):
        concepts.generate_and_save_concept(
            "invented-category",
            "Classic",
            "Engineers",
            "idea",
        )


def test_all_categories_have_translations_in_all_13_languages():
    assert set(CATEGORY_TRANSLATIONS) == set(LANGUAGES)
    for language in LANGUAGES:
        assert len(CATEGORY_TRANSLATIONS[language]) == len(CATEGORY_KEYS)
        assert all(category_display_name(key, language) for key in CATEGORY_KEYS)


def test_legacy_database_migration_is_idempotent_and_preserves_content(
    temporary_database,
):
    concept_data = {"title": "unchanged", "modern_category": "Legacy label"}
    connection = database.get_connection()
    connection.executemany(
        """
        INSERT INTO concepts (title, category, prompt, concept_json)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("Transport legacy", "Transport", "prompt A", json.dumps(concept_data)),
            ("Unknown legacy", "Exploration", "prompt B", json.dumps(concept_data)),
        ],
    )
    connection.commit()
    connection.close()

    database.init_db()
    database.init_db()

    connection = database.get_connection()
    rows = connection.execute(
        "SELECT title, category, prompt, concept_json FROM concepts ORDER BY id"
    ).fetchall()
    connection.close()

    assert rows[0] == (
        "Transport legacy",
        "transport_mobility",
        "prompt A",
        json.dumps(concept_data),
    )
    assert rows[1][1] == "Exploration"
    assert json.loads(rows[1][3]) == concept_data


def test_session_state_normalizes_known_legacy_category(monkeypatch):
    session_state = {state.IDEA_CATEGORY: "Robotics"}
    monkeypatch.setattr(state.st, "session_state", session_state)

    state.initialize_session_state()

    assert session_state[state.IDEA_CATEGORY] == "robotics_automation"
