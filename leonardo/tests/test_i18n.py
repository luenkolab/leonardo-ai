from types import SimpleNamespace

import ai_generator
import pdf_export
from i18n import LANGUAGES, TRANSLATIONS, language_display_name, translate
from ui import state


FEATURE_CARD_KEYS = (
    "home.feature.title_summary.title",
    "home.feature.title_summary.text",
    "home.feature.core.title",
    "home.feature.core.text",
    "home.feature.sketch.title",
    "home.feature.sketch.text",
    "home.feature.blueprint.title",
    "home.feature.blueprint.text",
    "home.feature.materials.title",
    "home.feature.materials.text",
    "home.feature.use_cases.title",
    "home.feature.use_cases.text",
    "home.feature.investor.title",
    "home.feature.investor.text",
    "home.feature.commercial_metrics.title",
    "home.feature.commercial_metrics.text",
    "home.feature.implementation_metrics.title",
    "home.feature.implementation_metrics.text",
)


def test_all_supported_languages_are_registered():
    assert list(LANGUAGES) == [
        "en", "es", "pt", "fr", "de", "it", "ru",
        "sv", "fi", "pl", "zh", "ja", "ko",
    ]
    assert set(TRANSLATIONS) == set(LANGUAGES)
    assert all(language_display_name(code).startswith("🌐 ") for code in LANGUAGES)


def test_feature_cards_are_fully_translated_in_every_language():
    english_values = {key: translate(key, "en") for key in FEATURE_CARD_KEYS}

    for language in LANGUAGES:
        assert all(key in TRANSLATIONS[language] for key in FEATURE_CARD_KEYS)
        if language != "en":
            assert all(
                translate(key, language) != english_values[key]
                for key in FEATURE_CARD_KEYS
            )


def test_feature_card_localization_for_representative_languages():
    expected = {
        "en": ("Core Principle", "The name and brief overview of the idea."),
        "ru": ("Основной принцип", "Название и краткое описание идеи."),
        "es": ("Principio fundamental", "El nombre y una breve descripción general de la idea."),
        "zh": ("核心原理", "创意的名称和简要概述。"),
        "ja": ("中核原理", "アイデアの名称と簡単な概要です。"),
    }

    for language, (core_title, summary_text) in expected.items():
        assert translate("home.feature.core.title", language) == core_title
        assert translate("home.feature.title_summary.text", language) == summary_text


def test_generate_images_setting_is_translated_in_every_language():
    expected = {
        "en": "Generate Images",
        "es": "Generar imágenes",
        "pt": "Gerar imagens",
        "fr": "Générer des images",
        "de": "Bilder generieren",
        "it": "Genera immagini",
        "ru": "Создавать изображения",
        "sv": "Generera bilder",
        "fi": "Luo kuvat",
        "pl": "Generuj obrazy",
        "zh": "生成图像",
        "ja": "画像を生成",
        "ko": "이미지 생성",
    }

    assert {
        language: translate("sidebar.generate_images", language)
        for language in LANGUAGES
    } == expected


def test_engineering_drawing_studio_ui_is_translated_in_every_language():
    keys = (
        "concept.engineering_drawing_studio",
        "concept.engineering_drawing_studio_description",
        "concept.open_drawing_studio",
    )
    english = {key: translate(key, "en") for key in keys}

    for language in LANGUAGES:
        assert all(key in TRANSLATIONS[language] for key in keys)
        if language != "en":
            assert all(translate(key, language) != english[key] for key in keys)


def test_drawing_studio_screen_is_translated_in_every_language():
    keys = (
        "drawing_studio.back_to_concept",
        "drawing_studio.subtitle",
        "drawing_studio.project_context",
        "drawing_studio.project",
        "drawing_studio.short_summary",
        "drawing_studio.reference_visuals",
        "drawing_studio.reference_notice",
        "drawing_studio.engineering_data",
        "drawing_studio.engineering_parameters",
        "drawing_studio.parameters_description",
        "drawing_studio.drawing_package",
        "drawing_studio.general_arrangement",
        "drawing_studio.geometry_data_prepared",
        "drawing_studio.additional_geometry_data_required",
        "drawing_studio.envelope.length",
        "drawing_studio.envelope.width",
        "drawing_studio.envelope.height",
        "drawing_studio.envelope.invalid_value",
        "drawing_studio.ga.top_view",
        "drawing_studio.ga.front_view",
        "drawing_studio.ga.side_view",
        "drawing_studio.ga.insufficient_view_data",
        "drawing_studio.orthographic_views",
        "drawing_studio.assembly_drawings",
        "drawing_studio.component_detail_drawings",
        "drawing_studio.connections_fasteners",
        "drawing_studio.bill_of_materials",
        "drawing_studio.not_generated",
    )
    english = {key: translate(key, "en") for key in keys}

    for language in LANGUAGES:
        assert all(key in TRANSLATIONS[language] for key in keys)
        if language != "en":
            assert all(translate(key, language) != english[key] for key in keys)


def test_unknown_language_and_missing_locale_value_fall_back_to_english():
    assert translate("concept.title", "unknown") == "Title"
    assert translate("missing.translation.key", "ru") == "missing.translation.key"


def test_language_state_initialization_preserves_current_concept(monkeypatch):
    concept = {"title": "Existing concept"}
    session_state = {state.CURRENT_CONCEPT: concept, state.CURRENT_CONCEPT_ID: 7}
    monkeypatch.setattr(state.st, "session_state", session_state)

    state.initialize_session_state()
    session_state[state.LANGUAGE] = "ru"

    assert state.get_current_language() == "ru"
    assert state.get_current_concept() is concept
    assert state.get_current_concept_id() == 7


def test_selected_language_is_included_in_ai_prompt(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_generator, "_get_client", lambda: client)

    ai_generator.generate_leonardo_concept(
        category="robotics",
        user_prompt_text="idea",
        creativity="Bold",
        audience="Engineers",
        language="ru",
    )

    combined_prompt = " ".join(message["content"] for message in captured["messages"])
    assert "Write every user-facing JSON value in Russian" in combined_prompt
    assert "Response language: Russian" in combined_prompt
    assert "Category: Робототехника и автоматизация" in combined_prompt


def test_problem_statement_prompt_preserves_all_material_context_conditions(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_generator, "_get_client", lambda: client)
    problem_context = (
        "The system is required during grid outages, isolated-site operations, "
        "and temporary evacuation events."
    )

    ai_generator.generate_leonardo_concept(
        category="energy",
        user_prompt_text=problem_context,
        creativity="Classic",
        audience="Engineers",
        language="en",
    )

    combined_prompt = " ".join(message["content"] for message in captured["messages"])
    assert problem_context in combined_prompt
    assert "preserve every material problem driver, operating context, failure situation" in combined_prompt
    assert "include all of them explicitly or consolidate them without losing any condition" in combined_prompt
    assert "do not silently drop an item that changes the intended use" in combined_prompt
    assert "rather than copying the User prompt verbatim or retelling the full concept" in combined_prompt
    assert "consistent with target_users, use_cases, executive_summary, and mandatory capabilities" in combined_prompt


def test_risks_and_constraints_prompt_preserves_required_capabilities(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_generator, "_get_client", lambda: client)
    required_capability = "The system must operate continuously during network outages."

    ai_generator.generate_leonardo_concept(
        category="energy",
        user_prompt_text=required_capability,
        creativity="Classic",
        audience="Engineers",
        language="en",
    )

    combined_prompt = " ".join(message["content"] for message in captured["messages"])
    assert required_capability in combined_prompt
    assert "treat mandatory capabilities in the User prompt" in combined_prompt
    assert "never state or imply that a mandatory or already-stated capability is simply absent" in combined_prompt
    assert "state what is limited, why it is limited, and which implementation or operating area is affected" in combined_prompt
    assert "rewrite any direct contradiction" in combined_prompt


def test_technical_requirements_prompt_demands_verifiable_operational_criteria(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_generator, "_get_client", lambda: client)
    required_capability = "The system must remain operable throughout an off-grid duty cycle."

    ai_generator.generate_leonardo_concept(
        category="energy",
        user_prompt_text=required_capability,
        creativity="Classic",
        audience="Engineers",
        language="en",
    )

    combined_prompt = " ".join(message["content"] for message in captured["messages"])
    assert required_capability in combined_prompt
    assert "measurable, verifiable, or operationally defined" in combined_prompt
    assert "operating condition, load, accuracy, range" in combined_prompt
    assert "verification method" in combined_prompt
    assert "Do not invent unsupported numerical precision" in combined_prompt
    assert "without fabricating a threshold" in combined_prompt
    assert "consistent with modern_principle, system_components, materials" in combined_prompt


def test_modern_sketch_prompt_preserves_visually_representable_capabilities(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_generator, "_get_client", lambda: client)
    required_capability = "The system must visibly coordinate field deployment and remote condition sensing."

    ai_generator.generate_leonardo_concept(
        category="energy",
        user_prompt_text=required_capability,
        creativity="Classic",
        audience="Engineers",
        language="en",
    )

    combined_prompt = " ".join(message["content"] for message in captured["messages"])
    assert required_capability in combined_prompt
    assert "preserve every mandatory capability from the User prompt that can be represented visually" in combined_prompt
    assert "assembly methods, transport or deployment workflow" in combined_prompt
    assert "sensing or monitoring elements, automation mechanisms" in combined_prompt
    assert "interactions between major subsystems" in combined_prompt
    assert "do not omit them in favor of a generic product render" in combined_prompt
    assert "Do not invent visual features" in combined_prompt


def test_commercial_outlook_prompt_rejects_unsupported_financial_claims(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_generator, "_get_client", lambda: client)

    ai_generator.generate_leonardo_concept(
        category="robotics",
        user_prompt_text="A configurable inspection system for small industrial operators.",
        creativity="Classic",
        audience="Small business owners",
        language="en",
    )

    combined_prompt = " ".join(message["content"] for message in captured["messages"])
    assert "do not invent market size, TAM, SAM, SOM, CAGR, growth statistics" in combined_prompt
    assert "do not give a single precise monetary amount without sufficient basis" in combined_prompt
    assert "preliminary estimate or range" in combined_prompt
    assert "Do not choose a currency arbitrarily" in combined_prompt
    assert "do not state an exact return percentage or payback period without explicit assumptions" in combined_prompt
    assert "If roi includes a number, state the assumptions that produce it" in combined_prompt
    assert "do not promise fast payback, guaranteed returns, low investment risk, or high profitability" in combined_prompt
    assert "investor_summary must agree with market_demand, startup_cost, roi" in combined_prompt
    assert "distinguish facts known or derived from the concept from estimates, assumptions, and unknowns" in combined_prompt


def test_implementation_metrics_prompt_requires_scaled_consistent_estimates(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_generator, "_get_client", lambda: client)

    ai_generator.generate_leonardo_concept(
        category="robotics",
        user_prompt_text="A configurable inspection system for small industrial operators.",
        creativity="Classic",
        audience="Engineers",
        language="en",
    )

    combined_prompt = " ".join(message["content"] for message in captured["messages"])
    assert "difficulty must begin with an explicit score from 1–10 in the form N/10" in combined_prompt
    assert "explain the concept-specific factors behind that score" in combined_prompt
    assert "modern_difficulty must use the same 1–10 scale" in combined_prompt
    assert "rather than repeat difficulty" in combined_prompt
    assert "make it easier or harder than the underlying concept" in combined_prompt
    assert "dev_time must state the product maturity being estimated" in combined_prompt
    assert "consistent with implementation_roadmap, implementation_guides" in combined_prompt
    assert "use a realistic time range" in combined_prompt
    assert "instead of inventing an exact duration" in combined_prompt
    assert "not marketing descriptions" in combined_prompt


def test_roadmap_guides_and_dev_time_form_consistent_lifecycle(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_generator, "_get_client", lambda: client)

    ai_generator.generate_leonardo_concept(
        category="robotics",
        user_prompt_text="A configurable inspection system for small industrial operators.",
        creativity="Classic",
        audience="Engineers",
        language="en",
    )

    combined_prompt = " ".join(message["content"] for message in captured["messages"])
    assert "strict Prototype → MVP → Pilot → Production lifecycle" in combined_prompt
    assert "Prototype validates the key technical hypothesis" in combined_prompt
    assert "MVP builds on that evidence as the minimum usable real-world version" in combined_prompt
    assert "Pilot validates the MVP in a limited real environment" in combined_prompt
    assert "Production is scalable and operationally ready" in combined_prompt
    assert "must depend on evidence and outputs from the preceding stage" in combined_prompt
    assert "execution_plan, technical_architecture, resources_budget, and validation appropriate to that stage" in combined_prompt
    assert "consistent with technical_requirements, risks, constraints, and dev_time" in combined_prompt
    assert "dev_time must name its target maturity milestone" in combined_prompt
    assert "cross-check roadmap, guides, and dev_time for temporal contradictions" in combined_prompt


def test_implementation_guides_prompt_requires_concept_specific_evidence(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_generator, "_get_client", lambda: client)

    ai_generator.generate_leonardo_concept(
        category="robotics",
        user_prompt_text="A configurable inspection system for small industrial operators.",
        creativity="Classic",
        audience="Engineers",
        language="en",
    )

    combined_prompt = " ".join(message["content"] for message in captured["messages"])
    assert "specific concept at this specific lifecycle stage" in combined_prompt
    assert "derive concrete product-specific actions from the User prompt and system_components" in combined_prompt
    assert "without naming what is built, tested, measured, or learned" in combined_prompt
    assert "concept-relevant hardware, software, sensing, materials, interfaces" in combined_prompt
    assert "stage-specific relationships rather than using a universal architecture template" in combined_prompt
    assert "justify each resource through a concrete task or dependency of that stage" in combined_prompt
    assert "estimate or range with principal cost drivers" in combined_prompt
    assert "never unsupported precision" in combined_prompt
    assert "define measurable stage-exit tests" in combined_prompt
    assert "consistent with technical_requirements" in combined_prompt
    assert "without a specific acceptance criterion" in combined_prompt


def test_pdf_export_supports_latin_cyrillic_and_cjk(valid_concept):
    for language in ("es", "ru", "zh", "ja", "ko"):
        value = pdf_export.export_project_plan_pdf(valid_concept, language=language)
        assert value.startswith(b"%PDF")
        assert len(value) > 100
