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


def translate_concept_data(
    original_concept,
    source_language,
    target_language,
):
    """Translate ConceptData values while preserving its exact JSON structure."""
    original = validate_concept_data(original_concept)
    source_name = ai_language_name(source_language)
    target_name = ai_language_name(target_language)

    system_prompt = f"""
You are a precise technical translator.
Translate the supplied invention concept from {source_name} to {target_name}.

Return only one valid JSON object.
Rules:
- Keep every JSON key exactly unchanged.
- Keep all arrays, nesting, array lengths, and value types exactly unchanged.
- Translate only natural-language string values and strings inside lists.
- Do not recalculate numbers or convert currencies or measurement units.
- Preserve identifiers, technical codes, and proper product or brand names.
- Do not add, remove, correct, summarize, reinterpret, or improve information.
- Preserve empty strings as empty strings.
"""
    response = get_text_client().chat.completions.create(
        model=TRANSLATION_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(original, ensure_ascii=False),
            },
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Empty response from OpenAI")

    translated = json.loads(content)
    _validate_matching_structure(original, translated)
    return validate_concept_data(translated)


def translate_engineering_parameter_set(
    original_parameter_set,
    source_language,
    target_language,
):
    """Translate only project-specific engineering display fields."""
    original = validate_parameter_set(original_parameter_set)
    payload = {
        "project_specific": [
            {
                "key": parameter["key"],
                "label": parameter["label"],
                "rationale": parameter["rationale"],
                "unit": parameter["unit"],
            }
            for parameter in original["project_specific"]
        ]
    }
    system_prompt = f"""
You are a precise technical translator.
Translate the supplied engineering parameter display fields from
{ai_language_name(source_language)} to {ai_language_name(target_language)}.

Return only one valid JSON object with the exact same structure.
Rules:
- Keep every key value exactly unchanged.
- Translate label and rationale natural-language text.
- Translate every natural-language unit word into the target language.
- Unit words such as hours and meters must not remain in the source language.
- Preserve technical unit symbols exactly, including %, mm, cm, m, kg, kW, V, and A.
- Preserve null values and all value types.
- Do not add, remove, reorder, summarize, or reinterpret parameters.
"""
    response = get_text_client().chat.completions.create(
        model=TRANSLATION_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Empty response from OpenAI")
    translated = json.loads(content)
    _validate_matching_structure(payload, translated, "engineering_parameters")

    fields = translated["project_specific"]
    display = deepcopy(original)
    technical_units = {"%", "mm", "cm", "m", "kg", "kW", "V", "A"}
    for source, target, translated_field in zip(
        original["project_specific"],
        display["project_specific"],
        fields,
    ):
        if translated_field["key"] != source["key"]:
            raise ValueError("Translation changed engineering parameter key")
        if (
            source["unit"] in technical_units
            and translated_field["unit"] != source["unit"]
        ):
            raise ValueError("Translation changed a technical unit symbol")
        if (
            source["unit"]
            and source["unit"] not in technical_units
            and translated_field["unit"] == source["unit"]
        ):
            raise ValueError("Translation left a textual unit untranslated")
        target["label"] = translated_field["label"]
        target["rationale"] = translated_field["rationale"]
        target["unit"] = translated_field["unit"]
    return validate_parameter_set(display)
