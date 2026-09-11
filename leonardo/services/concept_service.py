from pydantic import ValidationError

from services.ai_service import generate_ai_concept
from services.concept_schema import validate_concept_data
from services.fallback_service import build_fallback_concept


def generate_concept(
    category,
    creativity_mode,
    audience,
    user_prompt,
    language="en",
):
    """
    Main concept generation logic
    Decides between AI and fallback
    """

    try:
        # Try AI first
        concept = generate_ai_concept(
            category=category,
            creativity_mode=creativity_mode,
            audience=audience,
            user_prompt=user_prompt,
            language=language,
        )
        return validate_concept_data(concept)

    except ValidationError as e:
        print(f"AI concept validation failed with {e.error_count()} schema error(s)")
    except Exception as e:
        print(f"AI generation or validation failed: {e}")

    fallback = build_fallback_concept(
        category=category,
        prompt_text=user_prompt,
        creativity_mode=creativity_mode,
        audience=audience,
        language=language,
    )

    try:
        return validate_concept_data(fallback)
    except ValidationError as e:
        raise RuntimeError("Fallback concept does not satisfy the concept schema") from e
