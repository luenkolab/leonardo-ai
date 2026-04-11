import os
import base64
from openai import OpenAI


def _get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


def _generate_image(prompt_text, size="1024x1024"):
    client = _get_client()

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt_text,
        size=size,
    )

    image_base64 = result.data[0].b64_json

    return {
        "prompt": prompt_text,
        "image_bytes": base64.b64decode(image_base64),
    }


def generate_leonardo_image_prompt(prompt_text):
    return _generate_image(prompt_text, size="1024x1024")


def generate_blueprint_image_prompt(prompt_text):
    enhanced_prompt = f"""
    Create a clean modern engineering blueprint based on this concept:

    {prompt_text}

    Required visual style:
    - modern technical blueprint
    - CAD presentation board
    - clean white or light background
    - precise thin linework
    - orthographic views
    - front view, side view, top view
    - labeled modules and engineering subsystems
    - arrows, dimensions, technical annotations
    - product design documentation layout

    Strictly avoid:
    - sepia tone
    - hand-drawn sketch style
    - Renaissance notebook style
    - artistic rendering
    - vintage paper texture
    - painterly shading
    """

    return _generate_image(enhanced_prompt, size="1024x1024")