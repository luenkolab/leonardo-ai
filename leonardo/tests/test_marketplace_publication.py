import copy
import json
import sqlite3

import database
from application import marketplace
from services import concept_translation_service
from ui import marketplace_page


def _save_concept(
    concept_data,
    category="robotics_automation",
    title=None,
    language="en",
):
    return database.save_concept(
        title=title or concept_data["title"],
        category=category,
        prompt="marketplace publication test",
        concept_data=concept_data,
        concept_language=language,
    )


def _publication_row(concept_id):
    connection = database.get_connection()
    try:
        return connection.execute(
            "SELECT id, title, is_published FROM concepts WHERE id = ?",
            (concept_id,),
        ).fetchone()
    finally:
        connection.close()


def test_new_and_existing_concepts_are_unpublished_after_idempotent_migration(
    tmp_path,
    monkeypatch,
    valid_concept,
):
    database_path = tmp_path / "legacy-leonardo.db"
    monkeypatch.setattr(database, "DB_PATH", database_path)
    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        CREATE TABLE concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            prompt TEXT,
            concept_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    concept_id = connection.execute(
        """
        INSERT INTO concepts (title, category, prompt, concept_json)
        VALUES (?, ?, ?, ?)
        """,
        (
            valid_concept["title"],
            "robotics_automation",
            "legacy prompt",
            json.dumps(valid_concept),
        ),
    ).lastrowid
    connection.commit()
    connection.close()

    database.init_db()
    database.init_db()

    new_concept_id = _save_concept(valid_concept, title="New concept")

    connection = database.get_connection()
    try:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(concepts)")
        }
        publication_state = connection.execute(
            "SELECT id, is_published FROM concepts ORDER BY id"
        ).fetchall()
    finally:
        connection.close()

    assert "is_published" in columns
    assert publication_state == [(concept_id, 0), (new_concept_id, 0)]
    assert marketplace.list_published_marketplace_projects() == ()


def test_publish_is_idempotent_and_does_not_copy_or_change_concept(
    temporary_database,
    valid_concept,
):
    concept_id = _save_concept(valid_concept)
    original = database.get_concept_by_id(concept_id)

    assert marketplace.publish_concept(concept_id) is True
    assert marketplace.publish_concept(concept_id) is True

    projects = marketplace.list_published_marketplace_projects()
    connection = database.get_connection()
    try:
        concept_count = connection.execute(
            "SELECT COUNT(*) FROM concepts WHERE id = ?",
            (concept_id,),
        ).fetchone()[0]
    finally:
        connection.close()

    assert [project["id"] for project in projects] == [f"concept_{concept_id}"]
    assert concept_count == 1
    assert database.get_concept_by_id(concept_id) == original


def test_publication_survives_database_reinitialization_and_fresh_reads(
    temporary_database,
    valid_concept,
):
    concept_id = _save_concept(valid_concept, title="Persistent project")

    assert _publication_row(concept_id) == (
        concept_id,
        "Persistent project",
        0,
    )
    marketplace.publish_concept(concept_id)
    assert _publication_row(concept_id)[2] == 1

    database.init_db()
    database.init_db()

    assert _publication_row(concept_id)[2] == 1
    assert database.is_concept_published(concept_id) is True
    assert [
        project["id"]
        for project in marketplace.list_published_marketplace_projects()
    ] == [f"concept_{concept_id}"]


def test_updating_published_concept_fields_preserves_publication_flag(
    temporary_database,
    valid_concept,
):
    concept_id = _save_concept(valid_concept, title="Published before update")
    marketplace.publish_concept(concept_id)

    connection = database.get_connection()
    try:
        connection.execute(
            "UPDATE concepts SET title = ? WHERE id = ?",
            ("Published after update", concept_id),
        )
        connection.commit()
    finally:
        connection.close()

    assert _publication_row(concept_id) == (
        concept_id,
        "Published after update",
        1,
    )
    assert marketplace.get_published_marketplace_project(
        f"concept_{concept_id}"
    )["name"] == "Published after update"


def test_marketplace_route_changes_do_not_change_publication(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    concept_id = _save_concept(valid_concept, title="Published route project")
    marketplace.publish_concept(concept_id)
    session_state = {}
    monkeypatch.setattr(marketplace_page.st, "session_state", session_state)

    marketplace_page._open_marketplace_project(f"concept_{concept_id}")
    marketplace_page._back_to_marketplace()

    assert _publication_row(concept_id)[2] == 1
    assert marketplace_page.get_marketplace_projects()[0]["id"] == (
        f"concept_{concept_id}"
    )


def test_remove_publication_survives_database_reinitialization(
    temporary_database,
    valid_concept,
):
    concept_id = _save_concept(valid_concept)
    marketplace.publish_concept(concept_id)

    marketplace.remove_concept_from_marketplace(concept_id)
    database.init_db()

    assert _publication_row(concept_id)[2] == 0
    assert database.is_concept_published(concept_id) is False
    assert marketplace.list_published_marketplace_projects() == ()


def test_remove_from_marketplace_preserves_concept_and_images(
    temporary_database,
    valid_concept,
    png_bytes,
):
    concept_id = _save_concept(valid_concept)
    database.save_image_asset(concept_id, "leonardo_concept_1", "prompt", png_bytes)
    marketplace.publish_concept(concept_id)

    assert marketplace.remove_concept_from_marketplace(concept_id) is True

    assert marketplace.list_published_marketplace_projects() == ()
    assert database.get_concept_by_id(concept_id) == valid_concept
    assert len(database.get_images_for_concept(concept_id)) == 1


def test_published_project_maps_existing_title_category_and_content(
    temporary_database,
    valid_concept,
):
    concept_data = copy.deepcopy(valid_concept)
    concept_data["executive_summary"] = "Specific saved project summary"
    concept_data["market_demand"] = "Specific existing market demand"
    concept_id = _save_concept(
        concept_data,
        category="water",
        title="Published Water Project",
    )
    marketplace.publish_concept(concept_id)

    project = marketplace.get_published_marketplace_project(
        f"concept_{concept_id}"
    )

    assert project["name"] == "Published Water Project"
    assert project["category"] == "water"
    assert project["summary"] == "Specific saved project summary"
    assert project["market_opportunity"] == "Specific existing market demand"


def test_real_project_view_uses_stable_concept_identifier(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    concept_id = _save_concept(valid_concept, title="Stable Real Project")
    marketplace.publish_concept(concept_id)
    session_state = {}
    monkeypatch.setattr(marketplace_page.st, "session_state", session_state)

    project_id = f"concept_{concept_id}"
    marketplace_page._open_marketplace_project(project_id)
    project = marketplace_page.get_marketplace_project(project_id)

    assert session_state[marketplace_page.MARKETPLACE_PROJECT_ID] == project_id
    assert session_state[marketplace_page.MARKETPLACE_VIEW] == (
        marketplace_page.MARKETPLACE_PROJECT_DETAIL_VIEW
    )
    assert project["concept_id"] == concept_id
    assert project["name"] == "Stable Real Project"


def test_real_project_loads_only_its_own_images(
    temporary_database,
    valid_concept,
    png_bytes,
):
    first_id = _save_concept(valid_concept, title="First")
    second_data = copy.deepcopy(valid_concept)
    second_data["title"] = "Second"
    second_id = _save_concept(second_data, title="Second")
    database.save_image_asset(first_id, "leonardo_concept_1", "first-old", png_bytes)
    database.save_image_asset(first_id, "modern_concept_1", "first", png_bytes)
    database.save_image_asset(second_id, "modern_concept_1", "second", png_bytes)
    marketplace.publish_concept(first_id)
    marketplace.publish_concept(second_id)

    first = marketplace.get_published_marketplace_project(f"concept_{first_id}")
    second = marketplace.get_published_marketplace_project(f"concept_{second_id}")

    assert {image["concept_id"] for image in first["project_images"]} == {first_id}
    assert {image["prompt"] for image in first["project_images"]} == {"first"}
    assert {image["image_type"] for image in first["project_images"]} == {
        "modern_concept_1"
    }
    assert {image["concept_id"] for image in second["project_images"]} == {second_id}
    assert {image["prompt"] for image in second["project_images"]} == {"second"}


def test_marketplace_reuses_viewer_translation_for_catalog_and_detail(
    temporary_database,
    valid_concept,
    monkeypatch,
):
    source = copy.deepcopy(valid_concept)
    source.update(
        {
            "title": "Русский проект",
            "executive_summary": "Русское описание",
            "industries": ["Строительство", "Инфраструктура"],
        }
    )
    translated = copy.deepcopy(source)
    translated.update(
        {
            "title": "English Project",
            "executive_summary": "English summary",
            "industries": ["Construction", "Infrastructure"],
            "investor_summary": "English investment case",
            "roi": "English ROI assumptions",
            "market_demand": "English market demand",
            "modern_principle": "English technical principle",
            "system_components": ["English module"],
            "risks": ["English risk"],
            "constraints": ["English constraint"],
            "startup_cost": "English preliminary cost",
        }
    )
    translated["implementation_roadmap"] = {
        "prototype": "English prototype",
        "mvp": "English MVP",
        "pilot": "English pilot",
        "production": "English production",
    }
    concept_id = _save_concept(
        source,
        category="construction_architecture",
        title="Русский проект",
        language="ru",
    )
    marketplace.publish_concept(concept_id)
    calls = []

    def translate(original, source_language, target_language):
        calls.append((source_language, target_language))
        return translated

    monkeypatch.setattr(
        concept_translation_service,
        "translate_concept_data",
        translate,
    )

    source_project = marketplace.list_published_marketplace_projects("ru")[0]
    english_catalog_project = marketplace.list_published_marketplace_projects("en")[0]
    english_detail_project = marketplace.get_published_marketplace_project(
        f"concept_{concept_id}",
        "en",
    )

    assert source_project["name"] == "Русский проект"
    assert source_project["summary"] == "Русское описание"
    assert source_project["tags"] == ("Строительство", "Инфраструктура")
    assert english_catalog_project["name"] == "English Project"
    assert english_catalog_project["summary"] == "English summary"
    assert english_catalog_project["tags"] == (
        "Construction",
        "Infrastructure",
    )
    assert english_detail_project == english_catalog_project
    assert english_detail_project["investment_highlights"] == (
        "English investment case",
        "English ROI assumptions",
    )
    assert english_detail_project["market_opportunity"] == (
        "English market demand"
    )
    assert english_detail_project["technology_solution"] == (
        "English technical principle",
        "English module",
    )
    assert english_detail_project["roadmap"] == (
        "English prototype",
        "English MVP",
        "English pilot",
        "English production",
    )
    assert english_detail_project["risks"] == (
        "English risk",
        "English constraint",
    )
    assert calls == [("ru", "en")]
    assert database.get_concept_by_id(concept_id) == source
    assert database.get_concept_translation(concept_id, "en") == translated


def test_real_project_without_images_uses_existing_placeholder(
    temporary_database,
    valid_concept,
):
    concept_id = _save_concept(valid_concept)
    marketplace.publish_concept(concept_id)
    project = marketplace.get_published_marketplace_project(f"concept_{concept_id}")

    markup = marketplace_page._project_card_markup(project, "en")

    assert project["project_images"] == ()
    assert "<svg" in markup
    assert "<img" not in markup


def test_marketplace_search_and_category_filter_real_projects(
    temporary_database,
    valid_concept,
):
    water_data = copy.deepcopy(valid_concept)
    water_data["executive_summary"] = "Remote membrane treatment platform"
    water_id = _save_concept(water_data, "water", "Aqua Field System")
    robotics_id = _save_concept(
        valid_concept,
        "robotics_automation",
        "Factory Rover",
    )
    marketplace.publish_concept(water_id)
    marketplace.publish_concept(robotics_id)
    projects = marketplace_page.get_marketplace_projects()

    assert [
        project["id"]
        for project in marketplace_page.filter_marketplace_projects(
            projects,
            search_text="membrane treatment",
        )
    ] == [f"concept_{water_id}"]
    assert [
        project["id"]
        for project in marketplace_page.filter_marketplace_projects(
            projects,
            category="water",
        )
    ] == [f"concept_{water_id}"]


def test_demo_projects_remain_fallback_only_without_real_publications(
    temporary_database,
    valid_concept,
):
    _save_concept(valid_concept)

    assert marketplace_page.get_marketplace_projects() is marketplace_page._DEMO_PROJECTS

    concept_id = _save_concept(valid_concept, title="Published real project")
    marketplace.publish_concept(concept_id)

    projects = marketplace_page.get_marketplace_projects()
    assert [project["id"] for project in projects] == [f"concept_{concept_id}"]
    assert not any(project["id"] == "swiftbridge" for project in projects)


def test_unpublished_real_project_cannot_be_opened_from_marketplace(
    temporary_database,
    valid_concept,
):
    concept_id = _save_concept(valid_concept)

    assert marketplace.get_published_marketplace_project(
        f"concept_{concept_id}"
    ) is None
    assert marketplace_page.get_marketplace_project(f"concept_{concept_id}") is None
