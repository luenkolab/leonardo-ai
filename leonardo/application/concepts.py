import json
from threading import Lock

from pydantic import ValidationError

from categories import require_category_key
from database import (
    delete_concept,
    get_concept_by_id,
    get_concept_language,
    get_concept_translation,
    get_concepts,
    save_concept,
    save_concept_translation,
    toggle_concept_favorite as _toggle_concept_favorite,
)
from i18n import DEFAULT_LANGUAGE, normalize_language
from services.concept_schema import validate_concept_data
from services.concept_service import generate_concept
from services import concept_translation_service


class ConceptLoadError(Exception):
    """Raised when a stored concept cannot be safely loaded."""


_INVALID_CONCEPT_MESSAGE = "Stored concept data is corrupted or outdated."
_TRANSLATION_LOCK = Lock()


def generate_and_save_concept(
    category,
    creativity_mode,
    audience,
    user_prompt,
    language="en",
) -> tuple[dict, int]:
    category_key = require_category_key(category)
    concept_data = generate_concept(
        category=category_key,
        creativity_mode=creativity_mode,
        audience=audience,
        user_prompt=user_prompt,
        language=language,
    )

    concept_id = save_concept(
        title=concept_data["title"],
        category=category_key,
        prompt=user_prompt,
        concept_data=concept_data,
        concept_language=language,
    )

    return concept_data, concept_id


def load_concept_with_language(concept_id: int) -> tuple[dict | None, str]:
    """Load a concept with its source language and legacy English fallback."""
    concept_data = load_concept(concept_id)
    stored_language = get_concept_language(concept_id)
    concept_language = normalize_language(stored_language or DEFAULT_LANGUAGE)
    return concept_data, concept_language


def load_concept_for_viewer(
    concept_id: int,
    viewer_language: str,
) -> tuple[dict | None, str | None]:
    """Resolve original or cached translated ConceptData for the viewer."""
    original = load_concept(concept_id)
    if original is None:
        return None, None

    stored_language = get_concept_language(concept_id)
    if stored_language is None:
        return original, None

    source_language = normalize_language(stored_language)
    target_language = normalize_language(viewer_language)
    if target_language == source_language:
        return original, source_language

    try:
        cached = get_concept_translation(concept_id, target_language)
        if cached is not None:
            return validate_concept_data(cached), source_language

        with _TRANSLATION_LOCK:
            cached = get_concept_translation(concept_id, target_language)
            if cached is not None:
                return validate_concept_data(cached), source_language

            translated = concept_translation_service.translate_concept_data(
                original,
                source_language,
                target_language,
            )
            translated = validate_concept_data(translated)
            save_concept_translation(
                concept_id,
                target_language,
                translated,
            )
            return translated, source_language
    except (ValueError, ValidationError, json.JSONDecodeError):
        raise ConceptLoadError(_INVALID_CONCEPT_MESSAGE) from None
    except Exception as exc:
        raise ConceptLoadError(_INVALID_CONCEPT_MESSAGE) from exc


def load_concept(concept_id: int) -> dict | None:
    try:
        concept_data = get_concept_by_id(concept_id)
    except json.JSONDecodeError:
        raise ConceptLoadError(_INVALID_CONCEPT_MESSAGE) from None

    if concept_data is None:
        concept_exists = any(
            stored_concept[0] == concept_id
            for stored_concept in get_concepts(limit=-1)
        )
        if concept_exists:
            raise ConceptLoadError(_INVALID_CONCEPT_MESSAGE)
        return None

    try:
        return validate_concept_data(concept_data)
    except ValidationError:
        raise ConceptLoadError(_INVALID_CONCEPT_MESSAGE) from None


def remove_concept(concept_id: int) -> None:
    delete_concept(concept_id)


def list_recent_concepts(limit: int = 10):
    return get_concepts(limit=limit)


def toggle_concept_favorite(concept_id: int) -> None:
    _toggle_concept_favorite(concept_id)
