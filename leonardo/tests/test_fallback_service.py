import inspect
import json
import re
from pathlib import Path

import pytest

from config import CATEGORIES
from i18n import LANGUAGES
from services import concept_service, fallback_service, fallback_translations
from services.concept_schema import ConceptData, validate_concept_data
from services.fallback_service import build_fallback_concept
from services.fallback_translations import SUPPORTED_FALLBACK_LANGUAGES


BASE_ARGUMENTS = {
    "category": "robotics",
    "prompt_text": "умная кормушка для домашних животных",
    "creativity_mode": "Bold",
    "audience": "Small business owners",
}


def _all_text_values(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from _all_text_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _all_text_values(nested)
    elif isinstance(value, str):
        yield value


def test_same_input_is_deterministic():
    first = build_fallback_concept(**BASE_ARGUMENTS)
    second = build_fallback_concept(**BASE_ARGUMENTS)

    assert first == second


def test_english_fallback_preserves_existing_output():
    result = build_fallback_concept(**BASE_ARGUMENTS, language="en")

    assert result["title"].endswith("Balanced Concept")
    assert result["leonardo_concept"].startswith(
        "A preliminary fallback interpretation"
    )
    assert "This local fallback concept treats" in result["executive_summary"]


@pytest.mark.parametrize(
    ("language", "prompt", "expected_text"),
    [
        ("ru", "умная система полива", "Эта локальная концепция"),
        ("es", "sistema inteligente de riego", "Este concepto local"),
        ("ja", "スマート給水システム", "このローカルコンセプト"),
        ("zh", "智能灌溉系统", "此本地概念"),
    ],
)
def test_localized_fallback_uses_selected_language(
    language,
    prompt,
    expected_text,
):
    result = build_fallback_concept(
        category="robotics",
        prompt_text=prompt,
        creativity_mode="Bold",
        audience="Engineers",
        language=language,
    )

    assert validate_concept_data(result) == result
    assert prompt in result["executive_summary"]
    assert expected_text in result["executive_summary"]


def test_all_i18n_languages_have_schema_complete_fallbacks():
    assert set(SUPPORTED_FALLBACK_LANGUAGES) == set(LANGUAGES)
    required_template_keys = set(fallback_translations._ENGLISH_PACK)
    assert all(
        required_template_keys <= set(pack)
        for pack in fallback_translations._PACKS.values()
    )

    for language in LANGUAGES:
        result = build_fallback_concept(
            category="robotics",
            prompt_text="idea locale" if language != "en" else "local idea",
            creativity_mode="Experimental",
            audience="Students",
            language=language,
        )

        assert validate_concept_data(result) == result
        assert len(result) == 27
        assert set(result) == set(ConceptData.model_fields)


def test_unknown_language_falls_back_to_english():
    unknown = build_fallback_concept(**BASE_ARGUMENTS, language="xx-unknown")
    english = build_fallback_concept(**BASE_ARGUMENTS, language="en")

    assert unknown == english


def test_missing_localized_template_falls_back_to_english(monkeypatch):
    monkeypatch.delitem(fallback_translations._PACKS["ru"], "market")

    result = build_fallback_concept(
        category="robotics",
        prompt_text="умная система полива",
        creativity_mode="Bold",
        audience="Engineers",
        language="ru",
    )

    assert result["market_demand"].startswith("Demand among")


@pytest.mark.parametrize(
    ("language", "prompt"),
    [
        ("ru", "умная система полива"),
        ("es", "sistema inteligente de riego"),
        ("ja", "スマート給水システム"),
    ],
)
def test_key_english_template_sentences_do_not_leak_into_localized_results(
    language,
    prompt,
):
    result = build_fallback_concept(
        category="robotics",
        prompt_text=prompt,
        creativity_mode="Bold",
        audience="Engineers",
        language=language,
    )
    rendered_text = "\n".join(_all_text_values(result))

    for english_fragment in (
        "A preliminary fallback interpretation",
        "This local fallback concept treats",
        "The stated challenge is",
        "Primary use case:",
        "Fallback mode cannot establish",
        "Timeline is undetermined in fallback mode",
        "Not estimated in fallback mode",
        "User need → explicit input",
    ):
        assert english_fragment not in rendered_text


def test_different_prompts_change_meaningful_sections():
    prompts = [
        "умная кормушка для домашних животных",
        "приложение для изучения шведского языка",
        "сервис прогнозирования спроса для магазина",
    ]
    concepts = [
        build_fallback_concept(
            category="robotics",
            prompt_text=prompt,
            creativity_mode="Bold",
            audience="Small business owners",
        )
        for prompt in prompts
    ]

    for field in (
        "title",
        "problem_statement",
        "modern_principle",
        "system_components",
        "risks",
    ):
        values = {
            json.dumps(concept[field], ensure_ascii=False, sort_keys=True)
            for concept in concepts
        }
        assert len(values) == len(prompts)


def test_audience_changes_value_implementation_and_commercial_sections():
    audiences = ["Students", "Small business owners", "Older users"]
    concepts = [
        build_fallback_concept(
            category="robotics",
            prompt_text=BASE_ARGUMENTS["prompt_text"],
            creativity_mode="Bold",
            audience=audience,
        )
        for audience in audiences
    ]

    for field in (
        "executive_summary",
        "target_users",
        "implementation_guides",
        "market_demand",
        "deployment_strategy",
    ):
        assert len(
            {
                json.dumps(concept[field], ensure_ascii=False, sort_keys=True)
                for concept in concepts
            }
        ) == len(audiences)


def test_creativity_changes_roadmap_risks_and_optional_features():
    concepts = [
        build_fallback_concept(
            category="robotics",
            prompt_text=BASE_ARGUMENTS["prompt_text"],
            creativity_mode=mode,
            audience="Students",
        )
        for mode in ("Classic", "Bold", "Experimental")
    ]

    assert len({json.dumps(c["implementation_roadmap"], sort_keys=True) for c in concepts}) == 3
    assert len({json.dumps(c["risks"], sort_keys=True) for c in concepts}) == 3
    component_counts = [len(c["system_components"]) for c in concepts]
    assert component_counts[0] + 1 == component_counts[1]
    assert component_counts[1] + 1 == component_counts[2]


def test_unknown_creativity_uses_medium_behavior():
    unknown = build_fallback_concept(
        category="robotics",
        prompt_text=BASE_ARGUMENTS["prompt_text"],
        creativity_mode="unexpected-mode",
        audience="Students",
    )
    medium = build_fallback_concept(
        category="robotics",
        prompt_text=BASE_ARGUMENTS["prompt_text"],
        creativity_mode="Bold",
        audience="Students",
    )

    assert unknown == medium


def test_empty_prompt_and_audience_are_safely_normalized():
    empty = build_fallback_concept("robotics", "", "Classic", "")
    whitespace = build_fallback_concept("robotics", " \n\t ", "Classic", "  ")

    assert empty == whitespace
    assert "a practical idea that requires a clearer user brief" in empty["executive_summary"]
    assert "prospective users" in empty["executive_summary"]


@pytest.mark.parametrize("category", CATEGORIES)
def test_all_categories_pass_schema_validation(category):
    result = build_fallback_concept(
        category=category,
        prompt_text="generic practical idea",
        creativity_mode="Classic",
        audience="Students",
    )

    assert validate_concept_data(result) == result
    assert len(result) == 27
    assert set(result) == set(ConceptData.model_fields)


@pytest.mark.parametrize(
    "prompt",
    [
        "Кириллица: помощник для сложной задачи",
        "emoji 🚀🧭",
        'quotes "double" and \'single\'\nwith a newline',
        '__import__("os").system("touch regression-marker")',
    ],
)
def test_special_and_code_like_prompts_remain_plain_text(prompt, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = build_fallback_concept("robotics", prompt, "Classic", "Students")

    assert validate_concept_data(result) == result
    assert " ".join(prompt.split()) in result["executive_summary"]
    assert not (tmp_path / "regression-marker").exists()


def test_fallback_source_has_no_nondeterministic_or_external_api_dependencies():
    source = inspect.getsource(fallback_service).lower()

    for forbidden in (
        "import random",
        "from random",
        "import time",
        "from time",
        "import uuid",
        "from uuid",
        "hash(",
        "openai",
        "requests",
        "http://",
        "https://",
    ):
        assert forbidden not in source


def test_fallback_avoids_unsupported_commercial_claims():
    result = build_fallback_concept(**BASE_ARGUMENTS)
    text = json.dumps(result, ensure_ascii=False)

    for pattern in (
        r"\b\d+(?:[.,]\d+)?\s*%",
        r"\bmarket size\b",
        r"\bpatent(?:ed|s)?\b",
        r"\bguarantee(?:d|s)?\b",
    ):
        assert re.search(pattern, text, flags=re.IGNORECASE) is None


@pytest.mark.parametrize(
    "ai_behavior",
    [
        TimeoutError("mock timeout"),
        {"title": "incomplete AI response"},
    ],
    ids=["timeout", "schema-validation-failure"],
)
def test_ai_failure_returns_contextual_valid_fallback(monkeypatch, ai_behavior):
    if isinstance(ai_behavior, Exception):
        def fail_ai(**kwargs):
            raise ai_behavior

        monkeypatch.setattr(concept_service, "generate_ai_concept", fail_ai)
    else:
        monkeypatch.setattr(
            concept_service,
            "generate_ai_concept",
            lambda **kwargs: ai_behavior,
        )

    result = concept_service.generate_concept(
        category="robotics",
        creativity_mode="Experimental",
        audience="Older users",
        user_prompt="умная кормушка для домашних животных",
    )

    assert validate_concept_data(result) == result
    assert "умная кормушка для домашних животных" in result["executive_summary"]
    assert "Older users" in result["executive_summary"]
    assert "Exploratory Concept" in result["title"]


def test_concept_service_passes_selected_language_to_fallback(monkeypatch):
    monkeypatch.setattr(
        concept_service,
        "generate_ai_concept",
        lambda **kwargs: (_ for _ in ()).throw(TimeoutError("mock timeout")),
    )

    result = concept_service.generate_concept(
        category="robotics",
        creativity_mode="Bold",
        audience="Engineers",
        user_prompt="умная система полива",
        language="ru",
    )

    assert validate_concept_data(result) == result
    assert "Эта локальная концепция" in result["executive_summary"]
    assert "Инженеры" in result["executive_summary"]
