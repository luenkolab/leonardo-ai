from services.ai_service import generate_ai_concept
from services.fallback_service import build_fallback_concept


def generate_concept(
    category,
    creativity_mode,
    audience,
    user_prompt,
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
        )

        if concept and isinstance(concept, dict) and "title" in concept:
            return concept

    except Exception as e:
        print(f"AI generation failed: {e}")

    # fallback
    return build_fallback_concept(
        category=category,
        prompt_text=user_prompt,
        creativity_mode=creativity_mode,
        audience=audience,
    )