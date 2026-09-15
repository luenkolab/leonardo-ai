import inspect

from categories import CATEGORY_KEYS
from i18n import (
    LANGUAGES,
    TRANSLATIONS,
    _MARKETPLACE_TRANSLATIONS,
    category_display_name,
    translate,
)
from ui.marketplace_page import (
    MARKETPLACE_CATEGORIES,
    MARKETPLACE_CATEGORY,
    MARKETPLACE_FILTERS,
    MARKETPLACE_PROJECT_DETAIL_VIEW,
    MARKETPLACE_PROJECT_ID,
    MARKETPLACE_PROJECTS_VIEW,
    MARKETPLACE_SEARCH,
    MARKETPLACE_VIEW,
    _DEMO_PROJECTS,
    _back_to_marketplace,
    _clear_marketplace_category,
    _close_marketplace_filters,
    _open_marketplace_project,
    _project_card_markup,
    _toggle_marketplace_filters,
    filter_marketplace_projects,
    get_marketplace_project,
)
from ui import marketplace_page
from ui import marketplace_project_page
from ui.marketplace_project_page import (
    _carousel_state_key,
    _change_carousel_image,
    marketplace_carousel_state,
    render_marketplace_project,
)


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
        "marketplace.back",
        "marketplace.previous_image",
        "marketplace.next_image",
        "marketplace.detail.overview",
        "marketplace.detail.investment_highlights",
        "marketplace.detail.market_opportunity",
        "marketplace.detail.technology_solution",
        "marketplace.detail.roadmap",
        "marketplace.detail.risks",
        "marketplace.detail.commercial_outlook",
        "marketplace.publish",
        "marketplace.published",
        "marketplace.remove",
    }

    assert all(
        required_keys.issubset(TRANSLATIONS[language])
        for language in LANGUAGES
    )


def test_project_detail_static_labels_resolve_through_i18n_for_all_languages():
    keys = (
        "marketplace.back",
        "marketplace.previous_image",
        "marketplace.next_image",
        "marketplace.detail.overview",
        "marketplace.detail.investment_highlights",
        "marketplace.detail.market_opportunity",
        "marketplace.detail.technology_solution",
        "marketplace.detail.roadmap",
        "marketplace.detail.risks",
        "marketplace.detail.commercial_outlook",
    )

    assert all(
        translate(key, language) != key
        for language in LANGUAGES
        for key in keys
    )
    assert all(
        set(keys).issubset(_MARKETPLACE_TRANSLATIONS[language])
        for language in LANGUAGES
        if language != "en"
    )
    assert translate("marketplace.back", "ru") == "Назад в маркетплейс"
    assert translate("marketplace.detail.overview", "ru") == "Обзор"
    assert category_display_name("construction_architecture", "ru") == (
        "Строительство и архитектура"
    )
    assert category_display_name("construction_architecture", "en") == (
        "Construction & Architecture"
    )


def test_project_card_and_detail_render_viewer_language_content(monkeypatch):
    project = {
        "id": "concept_23",
        "concept_id": 23,
        "name": "English Project",
        "category": "construction_architecture",
        "summary": "English summary",
        "stage": "",
        "funding": "",
        "tags": ("Construction", "Infrastructure"),
        "investment_highlights": ("English investment case",),
        "market_opportunity": "English market demand",
        "technology_solution": ("English technology",),
        "roadmap": ("English prototype",),
        "risks": ("English risk",),
        "commercial_outlook": ("English outlook",),
        "project_images": (),
    }
    rendered = []
    monkeypatch.setattr(
        marketplace_project_page.st,
        "button",
        lambda *args, **kwargs: False,
    )
    monkeypatch.setattr(
        marketplace_project_page.st,
        "markdown",
        lambda body, **kwargs: rendered.append(body),
    )
    monkeypatch.setattr(
        marketplace_project_page,
        "_render_project_carousel",
        lambda project, language: None,
    )

    card_markup = _project_card_markup(project, "en")
    render_marketplace_project(project, "en", lambda: None)
    detail_markup = "".join(rendered)

    assert "English Project" in card_markup
    assert "English summary" in card_markup
    assert "Construction" in card_markup
    assert "English Project" in detail_markup
    assert "English summary" in detail_markup
    assert "English investment case" in detail_markup
    assert "English market demand" in detail_markup
    assert "English technology" in detail_markup
    assert "English prototype" in detail_markup
    assert "English risk" in detail_markup
    assert "English outlook" in detail_markup


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


def test_view_project_uses_stable_id_and_back_preserves_catalog_state(monkeypatch):
    session_state = {
        MARKETPLACE_SEARCH: "water",
        MARKETPLACE_CATEGORY: "water",
        MARKETPLACE_FILTERS: True,
        "current_concept_id": 23,
        "generate_images": False,
    }
    monkeypatch.setattr(marketplace_page.st, "session_state", session_state)

    _open_marketplace_project("aquaclean_station")
    assert session_state[MARKETPLACE_VIEW] == MARKETPLACE_PROJECT_DETAIL_VIEW
    assert session_state[MARKETPLACE_PROJECT_ID] == "aquaclean_station"

    _back_to_marketplace()
    assert session_state[MARKETPLACE_VIEW] == MARKETPLACE_PROJECTS_VIEW
    assert session_state[MARKETPLACE_PROJECT_ID] is None
    assert session_state[MARKETPLACE_SEARCH] == "water"
    assert session_state[MARKETPLACE_CATEGORY] == "water"
    assert session_state[MARKETPLACE_FILTERS] is True
    assert session_state["current_concept_id"] == 23
    assert session_state["generate_images"] is False


def test_marketplace_renders_exactly_one_subview(monkeypatch):
    session_state = {
        MARKETPLACE_VIEW: MARKETPLACE_PROJECT_DETAIL_VIEW,
        MARKETPLACE_PROJECT_ID: "swiftbridge",
    }
    rendered = []
    monkeypatch.setattr(marketplace_page.st, "session_state", session_state)
    monkeypatch.setattr(marketplace_page, "get_current_language", lambda: "en")
    monkeypatch.setattr(
        marketplace_page,
        "render_marketplace_project",
        lambda project, language, on_back: rendered.append(("detail", project["id"])),
    )
    monkeypatch.setattr(
        marketplace_page,
        "_render_marketplace_catalog",
        lambda language: rendered.append(("catalog", language)),
    )

    marketplace_page.render_marketplace()
    assert rendered == [("detail", "swiftbridge")]

    rendered.clear()
    session_state[MARKETPLACE_VIEW] = MARKETPLACE_PROJECTS_VIEW
    marketplace_page.render_marketplace()
    assert rendered == [("catalog", "en")]


def test_invalid_marketplace_project_returns_to_catalog(monkeypatch):
    session_state = {
        MARKETPLACE_VIEW: MARKETPLACE_PROJECT_DETAIL_VIEW,
        MARKETPLACE_PROJECT_ID: "missing-project",
    }
    rendered = []
    monkeypatch.setattr(marketplace_page.st, "session_state", session_state)
    monkeypatch.setattr(marketplace_page, "get_current_language", lambda: "en")
    monkeypatch.setattr(
        marketplace_page,
        "_render_marketplace_catalog",
        lambda language: rendered.append(language),
    )

    marketplace_page.render_marketplace()

    assert rendered == ["en"]
    assert session_state[MARKETPLACE_VIEW] == MARKETPLACE_PROJECTS_VIEW
    assert session_state[MARKETPLACE_PROJECT_ID] is None


def test_marketplace_project_lookup_uses_stable_project_identifier():
    assert get_marketplace_project("swiftbridge")["name"] == "SwiftBridge"
    assert get_marketplace_project("aquaclean_station")["name"] == "AquaClean Station"
    assert get_marketplace_project("missing-project") is None


def test_project_detail_has_no_ai_or_persistence_dependencies():
    source = inspect.getsource(marketplace_project_page)
    assert "openai" not in source.casefold()
    assert "database" not in source.casefold()
    assert "concept_translation" not in source.casefold()
    assert "image_generation" not in source.casefold()


def _carousel_project(project_id, image_count, concept_id=41):
    return {
        "id": project_id,
        "concept_id": concept_id,
        "project_images": tuple(
            {
                "id": index,
                "concept_id": concept_id,
                "image_data": f"image-{index}".encode(),
            }
            for index in range(image_count)
        ),
    }


def test_marketplace_carousel_zero_images_uses_empty_state():
    carousel = marketplace_carousel_state(_carousel_project("concept_41", 0))

    assert carousel == {
        "images": (),
        "index": 0,
        "current": None,
        "previous": None,
        "next": None,
    }


def test_marketplace_carousel_one_image_has_no_side_navigation():
    carousel = marketplace_carousel_state(_carousel_project("concept_41", 1))

    assert carousel["current"]["id"] == 0
    assert carousel["previous"] is None
    assert carousel["next"] is None


def test_marketplace_carousel_two_images_wraps_cyclically():
    project = _carousel_project("concept_41", 2)

    first = marketplace_carousel_state(project, 0)
    wrapped_previous = marketplace_carousel_state(project, -1)
    wrapped_next = marketplace_carousel_state(project, 2)

    assert first["current"]["id"] == 0
    assert first["previous"]["id"] == 1
    assert first["next"]["id"] == 1
    assert wrapped_previous["current"]["id"] == 1
    assert wrapped_next["current"]["id"] == 0


def test_marketplace_carousel_three_images_maps_previous_current_next():
    carousel = marketplace_carousel_state(
        _carousel_project("concept_41", 3),
        1,
    )

    assert carousel["previous"]["id"] == 0
    assert carousel["current"]["id"] == 1
    assert carousel["next"]["id"] == 2


def test_marketplace_carousel_state_is_isolated_per_project(monkeypatch):
    session_state = {
        MARKETPLACE_VIEW: MARKETPLACE_PROJECT_DETAIL_VIEW,
        MARKETPLACE_PROJECT_ID: "concept_41",
    }
    monkeypatch.setattr(marketplace_project_page.st, "session_state", session_state)

    _change_carousel_image("concept_41", 3, 1)
    _change_carousel_image("concept_99", 2, -1)

    assert session_state[_carousel_state_key("concept_41")] == 1
    assert session_state[_carousel_state_key("concept_99")] == 1
    assert session_state[MARKETPLACE_VIEW] == MARKETPLACE_PROJECT_DETAIL_VIEW
    assert session_state[MARKETPLACE_PROJECT_ID] == "concept_41"


def test_marketplace_carousel_rejects_images_owned_by_another_concept():
    project = _carousel_project("concept_41", 2, concept_id=41)
    project["project_images"] += (
        {"id": 99, "concept_id": 99, "image_data": b"foreign"},
    )

    carousel = marketplace_carousel_state(project)

    assert [image["id"] for image in carousel["images"]] == [0, 1]
