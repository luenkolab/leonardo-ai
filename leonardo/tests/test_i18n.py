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


def test_pdf_export_supports_latin_cyrillic_and_cjk(valid_concept):
    for language in ("es", "ru", "zh", "ja", "ko"):
        value = pdf_export.export_project_plan_pdf(valid_concept, language=language)
        assert value.startswith(b"%PDF")
        assert len(value) > 100
