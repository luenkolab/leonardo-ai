import base64
import json
from contextlib import nullcontext
from types import SimpleNamespace

import database
from application import images as application_images
from services import image_service
from ui import concept_page, state


def _image_record(image_id, image_type, image_bytes=b"image"):
    return (image_id, image_type, "prompt", image_bytes, "test-date", 0)


def _gallery_record(image_id, image_type, image_bytes=b"image"):
    return (image_id, 100, image_type, "prompt", image_bytes, "test-date", 0)


def _build_prompt_sets(concept_data):
    design_blueprint = image_service.build_design_blueprint(concept_data)
    return (
        design_blueprint,
        image_service.build_leonardo_concept_image_prompts(
            concept_data,
            design_blueprint,
        ),
        image_service.build_modern_concept_image_prompts(
            concept_data,
            design_blueprint,
        ),
    )


def test_six_prompt_roles_have_stable_type_mapping(valid_concept):
    _, leonardo_prompts, modern_prompts = _build_prompt_sets(valid_concept)

    assert tuple(leonardo_prompts) == application_images.LEONARDO_CONCEPT_IMAGE_TYPES
    assert tuple(modern_prompts) == application_images.MODERN_CONCEPT_IMAGE_TYPES
    assert tuple(leonardo_prompts) + tuple(modern_prompts) == (
        application_images.CONCEPT_IMAGE_TYPES
    )
    assert len(set(leonardo_prompts.values())) == 3
    assert len(set(modern_prompts.values())) == 3
    assert all(valid_concept["title"] in prompt for prompt in leonardo_prompts.values())
    assert all(valid_concept["title"] in prompt for prompt in modern_prompts.values())
    assert application_images.CONCEPT_IMAGE_MAX_WORKERS == 2


def test_shared_identity_is_concise_era_neutral_and_used_in_all_prompts(
    valid_concept,
):
    identity_text = image_service._concept_identity(valid_concept)
    identity = json.loads(identity_text)
    design_blueprint, leonardo, modern = _build_prompt_sets(valid_concept)
    prompts = {**leonardo, **modern}

    assert tuple(identity) == (
        "core_inputs",
        "core_outputs",
        "intended_operating_environment",
        "main_physical_form",
        "primary_purpose",
        "primary_users",
    )
    assert all(
        design_blueprint["shared_invention_lineage"]["purpose"] in prompt
        for prompt in prompts.values()
    )
    assert all(len(value) <= 320 for value in identity.values())
    assert valid_concept["title"] in identity["primary_purpose"]
    assert valid_concept["target_users"][0] in identity["primary_users"]
    assert valid_concept["use_cases"][0] in identity["core_inputs"]
    assert "selected era" in identity["main_physical_form"]


def test_all_six_prompts_use_the_required_section_structure(valid_concept):
    _, leonardo, modern = _build_prompt_sets(valid_concept)
    prompts = {**leonardo, **modern}
    section_headings = (
        "1. Design Blueprint — highest priority",
        "2. Machine identity lock",
        "3. Exact image role",
        "4. Required scene and camera composition",
        "5. Required functional elements",
        "6. Era and engineering interpretation",
        "7. Required materials and mechanisms",
        "8. Explicit prohibited elements",
        "9. Continuity requirements",
        "10. Square-image readability requirements",
    )

    for prompt in prompts.values():
        positions = [prompt.index(heading) for heading in section_headings]
        assert positions == sorted(positions)
        assert "no split screen" in prompt
        assert "no collage" in prompt
        assert "no multiple panels" in prompt
        assert "logos" in prompt
        assert "watermarks" in prompt
        assert "pseudo-text" in prompt


def test_leonardo_prompts_enforce_historical_reconstruction(valid_concept):
    _, prompts, _ = _build_prompt_sets(valid_concept)

    for prompt in prompts.values():
        assert "year 1505" in prompt
        assert "High Renaissance engineer" in prompt
        assert "pre-industrial mechanical interpretation" in prompt
        assert "not a modern product placed in a Renaissance room" in prompt
        for mechanism in (
            "carved timber",
            "bronze",
            "leather belts",
            "rope drives",
            "wooden or bronze gears",
            "pulleys",
            "cams",
            "counterweights",
            "water power",
            "human power",
            "wind power",
            "glass lenses",
        ):
            assert mechanism in prompt
        for prohibited in (
            "electric motors",
            "batteries",
            "LEDs",
            "touchscreens",
            "computer-vision cameras",
            "microchips",
            "circuit boards",
            "artificial-intelligence interfaces",
            "contemporary robotic arms",
            "plastics",
            "aluminium extrusions",
            "carbon fibre",
            "injection-moulded parts",
            "stainless-steel appliance housings",
            "contemporary industrial housings",
        ):
            assert prohibited in prompt
        assert "Do not render a sketch, blueprint, diagram" in prompt


def test_modern_prompts_allow_realistic_contemporary_engineering(valid_concept):
    _, _, prompts = _build_prompt_sets(valid_concept)

    for prompt in prompts.values():
        for allowed in (
            "electric actuators",
            "computer vision",
            "modern sensors",
            "robotics",
            "contemporary safety systems",
            "aluminium",
            "structural steel",
            "safety glass",
            "durable polymers",
        ):
            assert allowed in prompt
        for prohibited in (
            "impossible holograms",
            "glowing fantasy interfaces",
            "excessive neon",
            "spaceship interiors",
            "unexplained futuristic technology",
            "random humanoid robots",
        ):
            assert prohibited in prompt
        assert "commercially plausible" in prompt
        assert "buildable, maintainable, usable" in prompt


def test_each_role_has_a_distinct_camera_composition(valid_concept):
    _, leonardo, modern = _build_prompt_sets(valid_concept)

    assert "Three-quarter wide view" in leonardo["leonardo_concept_1"]
    assert "65–80% of the frame" in leonardo["leonardo_concept_1"]
    assert "Medium-close technical cinematic view" in leonardo["leonardo_concept_2"]
    assert "different side, lower height, or oblique angle" in leonardo[
        "leonardo_concept_2"
    ]
    assert "Wider contextual scene" in leonardo["leonardo_concept_3"]
    assert "one to three historically dressed" in leonardo["leonardo_concept_3"]

    assert "Clean three-quarter wide" in modern["modern_concept_1"]
    assert "65–80% of the frame" in modern["modern_concept_1"]
    assert "Medium-close operational view" in modern["modern_concept_2"]
    assert "different side, lower or higher camera position" in modern[
        "modern_concept_2"
    ]
    assert "Wider human-context scene" in modern["modern_concept_3"]
    assert "authentic present-day users" in modern["modern_concept_3"]


def test_leonardo_and_modern_sets_are_semantically_distinct(valid_concept):
    _, leonardo_prompts, modern_prompts = _build_prompt_sets(valid_concept)
    leonardo = "\n".join(leonardo_prompts.values())
    modern = "\n".join(modern_prompts.values())

    assert "genuine historical reconstruction" in leonardo
    assert "historically plausible in 1505" in leonardo
    assert "present-day engineering implementation" not in leonardo
    assert "realistic present-day engineering implementation" in modern
    assert "contemporary manufacturing and safety practices" in modern
    assert "genuine historical reconstruction" not in modern


def test_within_set_continuity_is_explicit(valid_concept):
    _, leonardo, modern = _build_prompt_sets(valid_concept)

    for prompt in leonardo.values():
        assert "same carved timber frame" in prompt
        assert "same bronze or brass drive system" in prompt
        assert "same selected dominant mechanical feature" in prompt
        assert "Keep intake, process, and output locations consistent" in prompt

    for prompt in modern.values():
        assert "same product geometry" in prompt
        assert "same intake and output openings" in prompt
        assert "Change viewpoint, process state, and user activity" in prompt
        assert "practical technological descendant" in prompt


def test_design_blueprint_has_all_required_fields(valid_concept):
    design_blueprint = image_service.build_design_blueprint(valid_concept)

    assert set(design_blueprint) == {
        "shared_invention_lineage",
        "leonardo_blueprint",
        "modern_blueprint",
    }
    assert set(image_service.DESIGN_BLUEPRINT_FIELDS).issubset(
        design_blueprint["leonardo_blueprint"]
    )
    assert set(image_service.DESIGN_BLUEPRINT_FIELDS).issubset(
        design_blueprint["modern_blueprint"]
    )
    assert all(
        design_blueprint["leonardo_blueprint"][field]
        for field in image_service.DESIGN_BLUEPRINT_FIELDS
    )
    assert all(
        design_blueprint["modern_blueprint"][field]
        for field in image_service.DESIGN_BLUEPRINT_FIELDS
    )


def test_era_blueprints_share_lineage_but_use_different_engineering(valid_concept):
    design_blueprint = image_service.build_design_blueprint(valid_concept)
    lineage = design_blueprint["shared_invention_lineage"]
    leonardo = json.dumps(
        design_blueprint["leonardo_blueprint"],
        ensure_ascii=False,
    ).lower()
    modern = json.dumps(
        design_blueprint["modern_blueprint"],
        ensure_ascii=False,
    ).lower()

    assert lineage["purpose"] == design_blueprint["leonardo_blueprint"][
        "primary_function"
    ]
    assert lineage["purpose"] == design_blueprint["modern_blueprint"][
        "primary_function"
    ]
    for required_historical_detail in (
        "oak",
        "gear train",
        "six-spoke",
        "leather belt",
        "bronze",
        "counterweight",
        "control levers",
        "water wheel",
        "spring barrel",
    ):
        assert required_historical_detail in leonardo
    for required_modern_detail in (
        "graphite cabinet",
        "panoramic safety-glass window",
        "robotic arms",
        "sensor",
        "three pull-out collection bins",
        "service doors",
        "12-inch landscape touchscreen",
    ):
        assert required_modern_detail in modern
    assert design_blueprint["leonardo_blueprint"]["overall_silhouette"] != (
        design_blueprint["modern_blueprint"]["overall_silhouette"]
    )
    assert "robotic arms" not in leonardo
    assert "oak" not in modern


def test_all_six_prompts_embed_blueprint_before_role_and_lock_identity(valid_concept):
    design_blueprint, leonardo, modern = _build_prompt_sets(valid_concept)
    lock_wording = """This image must depict exactly the same machine described below.

Do not redesign the product.

Do not invent a new geometry.

Only change camera position, activity, environment and human interaction."""
    prompt_sets = (
        (
            leonardo,
            image_service._serialize_era_blueprint(
                design_blueprint,
                "leonardo_blueprint",
            ),
        ),
        (
            modern,
            image_service._serialize_era_blueprint(
                design_blueprint,
                "modern_blueprint",
            ),
        ),
    )

    for prompts, serialized_blueprint in prompt_sets:
        for prompt in prompts.values():
            assert prompt.startswith(
                "1. Design Blueprint — highest priority\n" + serialized_blueprint
            )
            assert prompt.count(serialized_blueprint) == 1
            assert lock_wording in prompt
            assert prompt.index(serialized_blueprint) < prompt.index(lock_wording)
            assert prompt.index(lock_wording) < prompt.index("3. Exact image role")
            assert "must not add, remove, relocate, resize, or restyle" in prompt


def test_blueprint_is_built_once_and_reused_by_both_prompt_builders(
    monkeypatch,
    valid_concept,
):
    blueprint = {"single": "blueprint"}
    events = []
    records = [
        _image_record(index, image_type)
        for index, image_type in enumerate(
            application_images.CONCEPT_IMAGE_TYPES,
            start=1,
        )
    ]

    def build_once(concept_data):
        events.append("build-blueprint")
        return blueprint

    def build_leonardo(concept_data, received_blueprint):
        events.append(("build-leonardo-prompts", received_blueprint is blueprint))
        return {
            image_type: image_type
            for image_type in application_images.LEONARDO_CONCEPT_IMAGE_TYPES
        }

    def build_modern(concept_data, received_blueprint):
        events.append(("build-modern-prompts", received_blueprint is blueprint))
        return {
            image_type: image_type
            for image_type in application_images.MODERN_CONCEPT_IMAGE_TYPES
        }

    monkeypatch.setattr(application_images, "build_design_blueprint", build_once)
    monkeypatch.setattr(
        application_images,
        "build_leonardo_concept_image_prompts",
        build_leonardo,
    )
    monkeypatch.setattr(
        application_images,
        "build_modern_concept_image_prompts",
        build_modern,
    )
    monkeypatch.setattr(
        application_images,
        "list_concept_images",
        lambda concept_id: records,
    )

    application_images.generate_and_save_concept_images(valid_concept, concept_id=55)

    assert events == [
        "build-blueprint",
        ("build-leonardo-prompts", True),
        ("build-modern-prompts", True),
    ]


def test_generation_event_is_started_after_concept_is_saved(
    valid_concept,
    monkeypatch,
):
    events = []

    monkeypatch.setattr(concept_page, "get_current_concept", lambda: None)
    monkeypatch.setattr(
        concept_page,
        "clear_transient_visuals",
        lambda: events.append("clear-visuals"),
    )
    monkeypatch.setattr(
        concept_page,
        "generate_and_save_concept",
        lambda **kwargs: (events.append("save-concept") or (valid_concept, 42)),
    )
    monkeypatch.setattr(
        concept_page,
        "set_current_concept",
        lambda concept, concept_id: events.append(("set-concept", concept_id)),
    )
    monkeypatch.setattr(
        concept_page,
        "start_automatic_image_generation",
        lambda concept_id: events.append(("start-images", concept_id)),
    )
    monkeypatch.setattr(concept_page.st, "spinner", lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(concept_page.st, "rerun", lambda: events.append("rerun"))

    concept_page.generate_or_load_concept(
        category="robotics",
        creativity_mode="Bold",
        audience="Engineers",
        user_prompt="A practical rescue device",
        generate=True,
        regenerate=False,
    )

    assert events == [
        "clear-visuals",
        "save-concept",
        ("set-concept", 42),
        ("start-images", 42),
        "rerun",
    ]


def test_loading_saved_concept_does_not_start_generation(monkeypatch, valid_concept):
    session_state = {}
    monkeypatch.setattr(state.st, "session_state", session_state)

    state.initialize_session_state()
    state.set_current_concept(valid_concept, 17)

    assert state.get_automatic_image_pending_concept_id() is None

    state.start_automatic_image_generation(18)
    state.set_current_concept(valid_concept, 17)
    state.clear_automatic_image_generation_state()

    assert state.get_current_concept_id() == 17
    assert state.get_automatic_image_pending_concept_id() is None
    assert state.get_automatic_image_errors(17) == {}


def test_existing_image_types_are_skipped(monkeypatch, valid_concept):
    existing_types = {
        "leonardo_concept_1",
        "modern_concept_2",
    }
    records = [
        _image_record(index, image_type)
        for index, image_type in enumerate(existing_types, start=1)
    ]
    generated_prompts = []
    saved_types = []

    monkeypatch.setattr(
        application_images,
        "list_concept_images",
        lambda concept_id: list(records),
    )
    monkeypatch.setattr(
        application_images,
        "generate_concept_image",
        lambda prompt: generated_prompts.append(prompt)
        or {"prompt": prompt, "image_bytes": b"generated"},
    )

    def save_visual(concept_id, image_type, asset):
        saved_types.append(image_type)
        records.append(_image_record(len(records) + 1, image_type, asset["image_bytes"]))

    monkeypatch.setattr(application_images, "save_visual", save_visual)

    results = application_images.generate_and_save_concept_images(
        valid_concept,
        concept_id=55,
    )

    assert set(saved_types) == set(application_images.CONCEPT_IMAGE_TYPES) - existing_types
    assert len(generated_prompts) == 4
    assert all(results[image_type]["status"] == "skipped" for image_type in existing_types)


def test_all_existing_images_prevent_duplicate_generation(
    monkeypatch,
    valid_concept,
):
    records = [
        _image_record(index, image_type)
        for index, image_type in enumerate(
            application_images.CONCEPT_IMAGE_TYPES,
            start=1,
        )
    ]
    monkeypatch.setattr(
        application_images,
        "list_concept_images",
        lambda concept_id: records,
    )

    def unexpected_generation(prompt):
        raise AssertionError("An existing slot must not be regenerated")

    monkeypatch.setattr(
        application_images,
        "generate_concept_image",
        unexpected_generation,
    )

    results = application_images.generate_and_save_concept_images(
        valid_concept,
        concept_id=55,
    )

    assert set(results) == set(application_images.CONCEPT_IMAGE_TYPES)
    assert {result["status"] for result in results.values()} == {"skipped"}


def test_rerun_without_matching_pending_marker_does_not_generate(
    monkeypatch,
    valid_concept,
):
    monkeypatch.setattr(
        concept_page,
        "get_automatic_image_pending_concept_id",
        lambda: None,
    )

    def unexpected_generation(*args, **kwargs):
        raise AssertionError("Generation must require a matching pending marker")

    monkeypatch.setattr(
        concept_page,
        "generate_and_save_concept_images",
        unexpected_generation,
    )

    concept_page._run_pending_automatic_image_generation(valid_concept, 55)


def test_partial_failure_keeps_and_persists_successful_images(
    temporary_database,
    valid_concept,
    png_bytes,
    monkeypatch,
):
    concept_id = database.save_concept(
        title=valid_concept["title"],
        category="robotics",
        prompt="test prompt",
        concept_data=valid_concept,
    )
    failed_type = "modern_concept_2"
    prompts = {
        image_type: image_type
        for image_type in application_images.CONCEPT_IMAGE_TYPES
    }

    monkeypatch.setattr(
        application_images,
        "build_leonardo_concept_image_prompts",
        lambda concept, design_blueprint: {
            image_type: prompts[image_type]
            for image_type in application_images.LEONARDO_CONCEPT_IMAGE_TYPES
        },
    )
    monkeypatch.setattr(
        application_images,
        "build_modern_concept_image_prompts",
        lambda concept, design_blueprint: {
            image_type: prompts[image_type]
            for image_type in application_images.MODERN_CONCEPT_IMAGE_TYPES
        },
    )

    def generate(prompt):
        if prompt == failed_type:
            raise RuntimeError("mock image failure")
        return {"prompt": prompt, "image_bytes": png_bytes}

    monkeypatch.setattr(application_images, "generate_concept_image", generate)

    results = application_images.generate_and_save_concept_images(
        valid_concept,
        concept_id,
    )
    stored_images = database.get_images_for_concept(concept_id)
    stored_types = {image[1] for image in stored_images}

    assert results[failed_type]["status"] == "failed"
    assert stored_types == set(application_images.CONCEPT_IMAGE_TYPES) - {failed_type}
    assert len(stored_images) == 5


def test_manual_types_and_legacy_views_remain_isolated():
    concept_records = [
        _image_record(1, "leonardo"),
        _image_record(2, "blueprint"),
        _image_record(3, "leonardo_concept_1"),
        _image_record(4, "modern_concept_3"),
    ]
    gallery_records = [
        _gallery_record(1, "leonardo"),
        _gallery_record(2, "blueprint"),
        _gallery_record(3, "leonardo_concept_2"),
        _gallery_record(4, "modern_concept_1"),
    ]

    assert "leonardo" not in application_images.CONCEPT_IMAGE_TYPES
    assert "blueprint" not in application_images.CONCEPT_IMAGE_TYPES
    assert [
        image[1]
        for image in application_images.exclude_automatic_concept_images(
            concept_records
        )
    ] == ["leonardo", "blueprint"]
    assert [
        image[2]
        for image in application_images.exclude_automatic_concept_images(
            gallery_records,
            image_type_index=2,
        )
    ] == ["leonardo", "blueprint"]


def test_current_sdk_image_call_and_png_validation(png_bytes, monkeypatch):
    captured = {}

    def generate(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            data=[SimpleNamespace(b64_json=base64.b64encode(png_bytes).decode("ascii"))]
        )

    client = SimpleNamespace(images=SimpleNamespace(generate=generate))
    monkeypatch.setattr(image_service, "_get_concept_image_client", lambda: client)

    asset = image_service.generate_concept_image("test role prompt")

    assert asset == {"prompt": "test role prompt", "image_bytes": png_bytes}
    assert captured["model"] == "gpt-image-2"
    assert captured["size"] == "1024x1024"
    assert captured["quality"] == "medium"
    assert captured["output_format"] == "png"
    assert captured["timeout"] == 120.0


def test_rate_limit_retry_uses_bounded_backoff(png_bytes, monkeypatch):
    attempts = []
    sleeps = []

    class MockRateLimitError(Exception):
        status_code = 429
        response = SimpleNamespace(headers={"retry-after": "30"})

    def generate(**kwargs):
        attempts.append(kwargs)
        if len(attempts) == 1:
            raise MockRateLimitError("mock rate limit")
        return SimpleNamespace(
            data=[SimpleNamespace(b64_json=base64.b64encode(png_bytes).decode("ascii"))]
        )

    client = SimpleNamespace(images=SimpleNamespace(generate=generate))
    monkeypatch.setattr(image_service, "_get_concept_image_client", lambda: client)
    monkeypatch.setattr(image_service.time, "sleep", sleeps.append)

    image_service.generate_concept_image("retry prompt")

    assert len(attempts) == 2
    assert sleeps == [image_service.CONCEPT_IMAGE_MAX_BACKOFF_SECONDS]


def test_invalid_image_payload_is_rejected(monkeypatch):
    client = SimpleNamespace(
        images=SimpleNamespace(
            generate=lambda **kwargs: SimpleNamespace(
                data=[SimpleNamespace(b64_json=base64.b64encode(b"not-an-image").decode("ascii"))]
            )
        )
    )
    monkeypatch.setattr(image_service, "_get_concept_image_client", lambda: client)

    try:
        image_service.generate_concept_image("invalid image")
    except ValueError as exc:
        assert "not a PNG" in str(exc)
    else:
        raise AssertionError("Unreadable image bytes must be rejected")


def test_slot_renders_saved_and_neutral_empty_states(png_bytes, monkeypatch):
    rendered = []
    monkeypatch.setattr(
        concept_page.st,
        "markdown",
        lambda body, **kwargs: rendered.append((body, kwargs)),
    )
    image_type = "leonardo_concept_1"
    accessible_label = "Leonardo Vision 1"

    concept_page._render_concept_image_slot(
        image_type,
        accessible_label,
        {image_type: _image_record(1, image_type, png_bytes)},
        False,
        {},
    )
    concept_page._render_concept_image_slot(
        image_type,
        accessible_label,
        {},
        True,
        {},
    )
    concept_page._render_concept_image_slot(
        image_type,
        accessible_label,
        {},
        False,
        {image_type: "mock failure"},
    )
    concept_page._render_concept_image_slot(
        image_type,
        accessible_label,
        {},
        False,
        {},
    )

    assert '<img src="data:image/png;base64,' in rendered[0][0]
    assert 'aria-busy="true"' in rendered[1][0]
    assert "concept-image-slot--loading" in rendered[1][0]
    assert "concept-image-slot--error" in rendered[2][0]
    assert rendered[3][0].endswith("></div>")
    assert all(kwargs == {"unsafe_allow_html": True} for _, kwargs in rendered)

    rendered_html = "\n".join(body for body, _ in rendered)
    for removed_text in (
        "Leonardo scene image",
        "Modern use-case image",
        "Generating image…",
        "Image generation failed",
    ):
        assert removed_text not in rendered_html


def test_result_sections_render_three_slots_for_each_image_family(
    valid_concept,
    monkeypatch,
):
    rendered_types = []
    monkeypatch.setattr(
        concept_page,
        "_render_concept_image_slot",
        lambda image_type, *args: rendered_types.append(image_type),
    )
    monkeypatch.setattr(
        concept_page.st,
        "container",
        lambda **kwargs: nullcontext(),
    )
    monkeypatch.setattr(
        concept_page.st,
        "columns",
        lambda count: [nullcontext() for _ in range(count)],
    )
    monkeypatch.setattr(concept_page.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(concept_page.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(concept_page, "render_result_box", lambda *args, **kwargs: None)

    concept_page._render_leonardo_vision(valid_concept, {}, False, {})
    concept_page._render_modern_implementation(
        valid_concept,
        valid_concept["title"],
        {},
        False,
        {},
    )

    assert tuple(rendered_types) == (
        *application_images.LEONARDO_CONCEPT_IMAGE_TYPES,
        *application_images.MODERN_CONCEPT_IMAGE_TYPES,
    )
