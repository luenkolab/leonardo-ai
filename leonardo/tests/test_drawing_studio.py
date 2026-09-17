from contextlib import nullcontext

from application.images import MODERN_CONCEPT_IMAGE_TYPES
from services import concept_service, image_service
from ui import concept_page, drawing_studio_page, state


def test_open_drawing_studio_uses_existing_page_route(monkeypatch):
    page_updates = []
    reruns = []
    monkeypatch.setattr(
        concept_page,
        "render_generated_section_heading",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(concept_page.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(concept_page.st, "button", lambda *args, **kwargs: True)
    monkeypatch.setattr(concept_page.st, "rerun", lambda: reruns.append(True))
    monkeypatch.setattr(concept_page, "set_current_page", page_updates.append)

    concept_page._render_engineering_drawing_studio("en")

    assert page_updates == ["drawing_studio"]
    assert reruns == [True]


def test_back_to_concept_preserves_current_concept_state(monkeypatch, valid_concept):
    session_state = {
        state.CURRENT_PAGE: "drawing_studio",
        state.CURRENT_CONCEPT: valid_concept,
        state.CURRENT_CONCEPT_ID: 73,
        state.CURRENT_CONCEPT_LANGUAGE: "ru",
        state.LANGUAGE: "en",
        state.GENERATE_IMAGES: True,
    }
    monkeypatch.setattr(state.st, "session_state", session_state)
    monkeypatch.setattr(drawing_studio_page.st, "container", lambda **kwargs: nullcontext())
    monkeypatch.setattr(
        drawing_studio_page.st,
        "button",
        lambda *args, key=None, **kwargs: key == "drawing_studio_back",
    )
    monkeypatch.setattr(drawing_studio_page.st, "rerun", lambda: None)

    drawing_studio_page.render_drawing_studio()

    assert state.get_current_page() == "app"
    assert state.get_current_concept() is valid_concept
    assert state.get_current_concept_id() == 73
    assert state.get_current_concept_language() == "ru"
    assert state.get_generate_images_enabled() is True


def test_studio_uses_current_concept_and_only_modern_references(
    monkeypatch,
    valid_concept,
):
    image_lookups = []
    rendered_slots = []
    result_boxes = []
    headings = []
    spaces = []
    engineering_parameter_renders = []
    concept_images = {
        "leonardo_concept_1": (1, 91, "leonardo_concept_1", "prompt", b"old", "date", 0),
        "modern_concept_1": (2, 91, "modern_concept_1", "prompt", b"one", "date", 0),
        "modern_concept_3": (3, 91, "modern_concept_3", "prompt", b"three", "date", 0),
    }
    session_state = {
        state.CURRENT_PAGE: "drawing_studio",
        state.CURRENT_CONCEPT: valid_concept,
        state.CURRENT_CONCEPT_ID: 91,
        state.CURRENT_CONCEPT_LANGUAGE: "en",
        state.LANGUAGE: "en",
    }
    monkeypatch.setattr(state.st, "session_state", session_state)
    monkeypatch.setattr(drawing_studio_page.st, "container", lambda **kwargs: nullcontext())
    monkeypatch.setattr(drawing_studio_page.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(drawing_studio_page.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(drawing_studio_page.st, "space", spaces.append)
    monkeypatch.setattr(
        drawing_studio_page.st,
        "columns",
        lambda count: [nullcontext() for _ in range(count)],
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "render_generated_section_heading",
        lambda title, icon_svg=None, **kwargs: headings.append(
            (title, icon_svg, kwargs)
        ),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "render_result_box",
        lambda title, content, **kwargs: result_boxes.append((title, content, kwargs)),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_engineering_parameters",
        lambda *args: engineering_parameter_renders.append(args),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "load_concept_for_viewer",
        lambda concept_id, language: (valid_concept, "en"),
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "list_recent_concepts",
        lambda limit=-1: [(91, valid_concept["title"], "robotics_automation", "date", 0)],
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "get_concept_image_slots",
        lambda concept_id, image_types: image_lookups.append(
            (concept_id, image_types)
        )
        or concept_images,
    )
    monkeypatch.setattr(
        drawing_studio_page,
        "_render_concept_image_slot",
        lambda image_type, _label, images, *_args: rendered_slots.append(
            (image_type, set(images))
        ),
    )
    monkeypatch.setattr(
        image_service,
        "generate_concept_image",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Studio must not call the image API")
        ),
    )
    monkeypatch.setattr(
        concept_service,
        "generate_concept",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Studio must not generate concept text")
        ),
    )

    drawing_studio_page.render_drawing_studio()

    assert image_lookups == [(91, MODERN_CONCEPT_IMAGE_TYPES)]
    assert headings[0][1] == drawing_studio_page._STUDIO_SECTION_ICON
    assert all(icon_svg == "" for _title, icon_svg, _kwargs in headings[1:])
    engineering_heading = next(
        heading for heading in headings if heading[0] == "Engineering Data"
    )
    assert engineering_heading[2] == {}
    assert spaces == [40, 40]
    assert tuple(image_type for image_type, _images in rendered_slots) == (
        MODERN_CONCEPT_IMAGE_TYPES
    )
    assert all(
        images <= set(MODERN_CONCEPT_IMAGE_TYPES)
        for _image_type, images in rendered_slots
    )
    rendered_contents = [content for _title, content, _kwargs in result_boxes]
    for field_name in (
        "technical_requirements",
        "materials",
        "system_components",
        "constraints",
        "risks",
    ):
        assert valid_concept[field_name] in rendered_contents
    assert engineering_parameter_renders == [
        (91, valid_concept, "robotics_automation", "en")
    ]
    assert rendered_contents.count("Not generated") == 6
