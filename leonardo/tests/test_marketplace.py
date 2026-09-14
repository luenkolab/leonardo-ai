from categories import CATEGORY_KEYS
from i18n import LANGUAGES, TRANSLATIONS
from ui.marketplace_page import (
    MARKETPLACE_CATEGORIES,
    _DEMO_PROJECTS,
    _clear_marketplace_category,
    _close_marketplace_filters,
    _toggle_marketplace_filters,
    filter_marketplace_projects,
)
from ui import marketplace_page


def test_marketplace_search_and_categories_filter_local_demo_records():
    assert [
        project["id"]
        for project in filter_marketplace_projects(
            _DEMO_PROJECTS,
            search_text="water treatment",
        )
    ] == ["aquaclean_station"]
    assert MARKETPLACE_CATEGORIES == ("all", *CATEGORY_KEYS)
    assert all(
        project["category"] == "energy"
        for project in filter_marketplace_projects(
            _DEMO_PROJECTS,
            category="energy",
        )
    )


def test_marketplace_demo_projects_use_canonical_categories():
    assert {
        project["id"]: project["category"] for project in _DEMO_PROJECTS
    } == {
        "swiftbridge": "transport_mobility",
        "aquaclean_station": "water",
        "gridwise_storage": "energy",
        "carelink_mobile": "health_biotech",
        "forgevision": "manufacturing_industry",
        "terrain_rover": "robotics_automation",
    }


def test_marketplace_ui_is_translated_for_all_supported_languages():
    required_keys = {
        "nav.marketplace",
        "marketplace.title",
        "marketplace.subtitle",
        "marketplace.search",
        "marketplace.filters",
        "marketplace.category.all",
        "marketplace.view_project",
    }

    assert all(
        required_keys.issubset(TRANSLATIONS[language])
        for language in LANGUAGES
    )


def test_marketplace_filter_panel_and_active_category_use_existing_state(monkeypatch):
    session_state = {
        marketplace_page.MARKETPLACE_FILTERS: False,
        marketplace_page.MARKETPLACE_CATEGORY: "transport_mobility",
    }
    monkeypatch.setattr(marketplace_page.st, "session_state", session_state)

    _toggle_marketplace_filters()
    assert session_state[marketplace_page.MARKETPLACE_FILTERS] is True
    _toggle_marketplace_filters()
    assert session_state[marketplace_page.MARKETPLACE_FILTERS] is False

    _clear_marketplace_category()
    assert session_state[marketplace_page.MARKETPLACE_CATEGORY] == "all"

    session_state[marketplace_page.MARKETPLACE_FILTERS] = True
    _close_marketplace_filters()
    assert session_state[marketplace_page.MARKETPLACE_FILTERS] is False
