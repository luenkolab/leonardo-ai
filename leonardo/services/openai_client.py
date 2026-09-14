import os

from openai import OpenAI


def get_text_client() -> OpenAI:
    """Return the shared OpenAI client used by text-generation services."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)
