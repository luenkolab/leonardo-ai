import json

from pydantic import ValidationError

from database import (
    delete_concept,
    get_concept_by_id,
    get_concepts,
    save_concept,
    toggle_concept_favorite as _toggle_concept_favorite,
)
from services.concept_schema import validate_concept_data
from services.concept_service import generate_concept


class ConceptLoadError(Exception):
    """Raised when a stored concept cannot be safely loaded."""


_INVALID_CONCEPT_MESSAGE = "Stored concept data is corrupted or outdated."


def generate_and_save_concept(
    category,
    creativity_mode,
    audience,
    user_prompt,
    language="en",
) -> tuple[dict, int]:
    concept_data = generate_concept(
        category=category,
        creativity_mode=creativity_mode,
        audience=audience,
        user_prompt=user_prompt,
        language=language,
    )

    concept_id = save_concept(
        title=concept_data["title"],
        category=category,
        prompt=user_prompt,
        concept_data=concept_data,
    )

    return concept_data, concept_id


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
