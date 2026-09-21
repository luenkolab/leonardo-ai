import json
from copy import deepcopy

from i18n import ai_language_name
from services.concept_schema import validate_concept_data
from services.engineering_parameters_service import validate_parameter_set
from services.openai_client import get_text_client


TRANSLATION_MODEL = "gpt-4o-mini"


def _validate_matching_structure(original, translated, path="concept"):
    if isinstance(original, dict):
        if not isinstance(translated, dict) or set(translated) != set(original):
            raise ValueError(f"Translation changed object keys at {path}")
        for key, original_value in original.items():
            _validate_matching_structure(
                original_value,
                translated[key],
                f"{path}.{key}",
            )
        return

    if isinstance(original, list):
        if not isinstance(translated, list) or len(translated) != len(original):
            raise ValueError(f"Translation changed list structure at {path}")
        for index, (original_value, translated_value) in enumerate(
            zip(original, translated)
        ):
            _validate_matching_structure(
                original_value,
                translated_value,
                f"{path}[{index}]",
            )
        return

    if isinstance(original, str):
        if not isinstance(translated, str):
            raise ValueError(f"Translation changed string type at {path}")
        return

    if translated != original or type(translated) is not type(original):
        raise ValueError(f"Translation changed non-text value at {path}")


def _translate_structured_text(
    original,
    source_language,
    target_language,
    subject,
    extra_rules=(),
):
    """Translate natural-language values in structured JSON data."""
    rules = "\n".join(f"- {rule}" for rule in extra_rules)
    system_prompt = f"""
You are a precise technical translator.
Translate the supplied {subject} from {ai_language_name(source_language)} to
{ai_language_name(target_language)}.

Return only one valid JSON object.
Rules:
- Keep every JSON key exactly unchanged.
- Keep all arrays, nesting, array lengths, and value types exactly unchanged.
- Translate only natural-language string values and strings inside lists.
- Do not recalculate numeric values or convert currencies or measurement quantities between unit systems.
- Preserve identifiers, technical codes, and proper product or brand names.
- Do not add, remove, correct, summarize, reinterpret, or improve information.
- Preserve empty strings as empty strings.
{rules}
"""
    response = get_text_client().chat.completions.create(
        model=TRANSLATION_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(original, ensure_ascii=False)},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Empty response from OpenAI")

    translated = json.loads(content)
    _validate_matching_structure(original, translated, subject)
    return translated


def translate_concept_data(
    original_concept,
    source_language,
    target_language,
):
    """Translate ConceptData values while preserving its exact JSON structure."""
    original = validate_concept_data(original_concept)
    translated = _translate_structured_text(
        original,
        source_language,
        target_language,
        "invention concept",
    )
    return validate_concept_data(translated)


def translate_engineering_parameter_set(
    original_parameter_set,
    source_language,
    target_language,
):
    """Translate engineering display text through structured translation."""
    original = validate_parameter_set(original_parameter_set)
    payload = {
        group_name: [
            {
                "key": parameter["key"],
                "label": (
                    parameter["label"]
                    if group_name == "project_specific"
                    else None
                ),
                "value": parameter["value"],
                "unit_text": (
                    parameter["unit"]
                    if parameter["unit"]
                    and parameter["unit"].isalpha()
                    and parameter["unit"].islower()
                    and len(parameter["unit"]) > 3
                    else None
                ),
                "rationale": parameter["rationale"],
            }
            for parameter in original[group_name]
        ]
        for group_name in ("universal", "project_specific")
    }
    translated = _translate_structured_text(
        payload,
        source_language,
        target_language,
        "engineering parameters",
        (
            "Keep every parameter key value exactly unchanged.",
            "Preserve numeric values, ranges, and structured expressions exactly.",
            "unit_text is ordinary natural-language text and must be translated.",
            "Preserve technical unit symbols such as m, mm, cm, kg, %, Wh, W, "
            "kW, N, kN, V, A, and °C exactly.",
        ),
    )

    display = deepcopy(original)
    for group_name in ("universal", "project_specific"):
        for source, target, translated_field in zip(
            original[group_name],
            display[group_name],
            translated[group_name],
        ):
            if translated_field["key"] != source["key"]:
                raise ValueError("Translation changed engineering parameter key")
            if group_name == "project_specific":
                target["label"] = translated_field["label"]
            value = source["value"]
            if value and "=" not in value and any(char.isalpha() for char in value):
                target["value"] = translated_field["value"]
            unit = source["unit"] or ""
            if unit.isalpha() and unit.islower() and len(unit) > 3:
                target["unit"] = translated_field["unit_text"]
            if source["rationale"] is not None:
                target["rationale"] = translated_field["rationale"]
    return validate_parameter_set(display)
