from contextlib import nullcontext

from ui import sidebar


def test_custom_gallery_button_switches_to_grouped_gallery_page(monkeypatch):
    switched_pages = []
    internal_page_updates = []

    monkeypatch.setattr(sidebar.st, "sidebar", nullcontext())
    monkeypatch.setattr(sidebar.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        sidebar.st,
        "button",
        lambda *args, key=None, **kwargs: key == "nav_gallery",
    )
    monkeypatch.setattr(
        sidebar.st,
        "selectbox",
        lambda label, options, **kwargs: options[0],
    )
    monkeypatch.setattr(sidebar.st, "text_area", lambda *args, **kwargs: "")
    monkeypatch.setattr(sidebar.st, "expander", lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(sidebar.st, "switch_page", switched_pages.append)
    monkeypatch.setattr(sidebar, "set_current_page", internal_page_updates.append)
    monkeypatch.setattr(sidebar, "render_previous_concepts_sidebar", lambda: None)
    monkeypatch.setattr(sidebar, "render_voice_prompt", lambda: None)

    sidebar.render_controls()

    assert switched_pages == ["pages/Gallery.py"]
    assert internal_page_updates == []
