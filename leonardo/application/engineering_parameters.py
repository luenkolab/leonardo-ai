from threading import Lock

from database import (
    get_engineering_parameter_set,
    get_engineering_parameter_set_source_language,
    get_engineering_parameter_translation,
    save_engineering_parameter_set,
    save_engineering_parameter_translation,
)
from i18n import normalize_language
from services import concept_translation_service
from services.engineering_parameters_service import (
    build_empty_parameter_set,
    validate_parameter_set,
)


_TRANSLATION_LOCK = Lock()


def load_engineering_parameters_for_viewer(concept_id, viewer_language):
    """Return canonical or cached viewer-language engineering parameters."""
    original = validate_parameter_set(
        get_engineering_parameter_set(concept_id) or build_empty_parameter_set()
    )
    source_language = get_engineering_parameter_set_source_language(concept_id)
    target_language = normalize_language(viewer_language)
    if (
        source_language is None
        or target_language == source_language
        or not original["project_specific"]
    ):
        return original

    cached = get_engineering_parameter_translation(concept_id, target_language)
    if cached is not None:
        return validate_parameter_set(cached)

    with _TRANSLATION_LOCK:
        cached = get_engineering_parameter_translation(concept_id, target_language)
        if cached is not None:
            return validate_parameter_set(cached)
        translated = concept_translation_service.translate_engineering_parameter_set(
            original,
            source_language,
            target_language,
        )
        save_engineering_parameter_translation(
            concept_id,
            target_language,
            translated,
        )
        return translated


def save_engineering_parameter_values(
    concept_id,
    displayed_parameter_set,
    group_name,
    rendered_values,
):
    """Save edits without persisting translated labels, rationales, or units."""
    canonical = validate_parameter_set(
        get_engineering_parameter_set(concept_id) or build_empty_parameter_set()
    )
    displayed = validate_parameter_set(displayed_parameter_set)
    displayed_by_key = {
        parameter["key"]: parameter for parameter in displayed[group_name]
    }
    for parameter in canonical[group_name]:
        value, unit = rendered_values[parameter["key"]]
        parameter["value"] = value
        if unit != displayed_by_key[parameter["key"]]["unit"]:
            parameter["unit"] = unit
        parameter["status"] = "confirmed" if value else "missing"
    save_engineering_parameter_set(concept_id, canonical)
