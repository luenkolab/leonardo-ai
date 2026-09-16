import pytest

from ui import state
from ui.router import render_current_page


@pytest.mark.parametrize(
    "selected_page",
    ("app", "gallery", "marketplace", "drawing_studio"),
)
def test_route_renders_only_selected_screen(selected_page):
    rendered = []

    render_current_page(
        selected_page,
        app_renderer=lambda: rendered.append("app"),
        gallery_renderer=lambda: rendered.append("gallery"),
        marketplace_renderer=lambda: rendered.append("marketplace"),
        drawing_studio_renderer=lambda: rendered.append("drawing_studio"),
    )

    assert rendered == [selected_page]


def test_marketplace_route_does_not_call_concept_or_image_generation():
    calls = {"concept_generation": 0, "image_generation": 0, "marketplace": 0}

    def forbidden_app_renderer():
        calls["concept_generation"] += 1
        calls["image_generation"] += 1

    def marketplace_renderer():
        calls["marketplace"] += 1

    render_current_page(
        "marketplace",
        app_renderer=forbidden_app_renderer,
        gallery_renderer=lambda: None,
        marketplace_renderer=marketplace_renderer,
        drawing_studio_renderer=lambda: None,
    )

    assert calls == {
        "concept_generation": 0,
        "image_generation": 0,
        "marketplace": 1,
    }


def test_switching_routes_preserves_current_concept_and_generate_images(monkeypatch):
    current_concept = {"title": "Preserved concept"}
    session_state = {
        state.CURRENT_PAGE: "app",
        state.CURRENT_CONCEPT: current_concept,
        state.CURRENT_CONCEPT_ID: 42,
        state.GENERATE_IMAGES: True,
        state.USER_PROMPT: "Preserved prompt",
    }
    monkeypatch.setattr(state.st, "session_state", session_state)

    for page in ("marketplace", "gallery", "drawing_studio", "app"):
        state.set_current_page(page)
        assert state.get_current_page() == page
        assert session_state[state.CURRENT_CONCEPT] is current_concept
        assert session_state[state.CURRENT_CONCEPT_ID] == 42
        assert session_state[state.GENERATE_IMAGES] is True
        assert session_state[state.USER_PROMPT] == "Preserved prompt"


def test_unknown_route_is_rejected():
    with pytest.raises(ValueError, match="Unsupported page"):
        render_current_page(
            "unknown",
            app_renderer=lambda: None,
            gallery_renderer=lambda: None,
            marketplace_renderer=lambda: None,
            drawing_studio_renderer=lambda: None,
        )
