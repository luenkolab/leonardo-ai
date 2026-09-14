import json

from i18n import ai_language_name
from services.concept_schema import validate_concept_data
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
