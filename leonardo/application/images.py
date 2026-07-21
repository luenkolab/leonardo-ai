from concurrent.futures import ThreadPoolExecutor, as_completed

from database import (
    delete_image_asset,
    get_images_for_concept,
    save_image_asset,
    toggle_image_favorite,
)
from services.image_service import (
    build_design_blueprint,
    build_leonardo_concept_image_prompts,
    build_modern_concept_image_prompts,
    generate_concept_image,
    generate_blueprint_image_prompt,
    generate_leonardo_image_prompt,
)


LEONARDO_CONCEPT_IMAGE_TYPES = (
    "leonardo_concept_1",
    "leonardo_concept_2",
    "leonardo_concept_3",
)
MODERN_CONCEPT_IMAGE_TYPES = (
    "modern_concept_1",
    "modern_concept_2",
    "modern_concept_3",
)
CONCEPT_IMAGE_TYPES = LEONARDO_CONCEPT_IMAGE_TYPES + MODERN_CONCEPT_IMAGE_TYPES
CONCEPT_IMAGE_MAX_WORKERS = 2


def generate_leonardo_visual(prompt: str) -> dict:
    return generate_leonardo_image_prompt(prompt)


def generate_blueprint_visual(prompt: str) -> dict:
    return generate_blueprint_image_prompt(prompt)


def save_visual(concept_id, image_type, asset) -> None:
    save_image_asset(
        concept_id=concept_id,
        image_type=image_type,
        prompt=asset["prompt"],
        image_bytes=asset["image_bytes"],
    )


def list_concept_images(concept_id):
    return get_images_for_concept(concept_id)


def remove_visual(image_id) -> None:
    delete_image_asset(image_id)


def toggle_visual_favorite(image_id) -> None:
    toggle_image_favorite(image_id)


def is_automatic_concept_image_type(image_type) -> bool:
    return image_type in CONCEPT_IMAGE_TYPES


def exclude_automatic_concept_images(images, image_type_index=1):
    return [
        image
        for image in images
        if not is_automatic_concept_image_type(image[image_type_index])
    ]


def map_automatic_concept_images(images):
    mapped_images = {}
    for image in images:
        image_type = image[1]
        if image_type in CONCEPT_IMAGE_TYPES and image_type not in mapped_images:
            mapped_images[image_type] = image
    return mapped_images


def group_automatic_concept_images(images):
    grouped_images = {}

    for image in images:
        concept_id = image[1]
        image_type = image[2]
        if image_type not in CONCEPT_IMAGE_TYPES:
            continue

        concept_images = grouped_images.setdefault(concept_id, {})
        concept_images.setdefault(image_type, image)

    return grouped_images


def build_concept_gallery_items(concepts, images, favorites_only=False):
    grouped_images = group_automatic_concept_images(images)
    gallery_items = []

    for concept_id, title, category, created_at, is_favorite in concepts:
        if concept_id not in grouped_images:
            continue
        if favorites_only and not is_favorite:
            continue

        concept_images = grouped_images[concept_id]
        gallery_items.append(
            {
                "concept_id": concept_id,
                "title": title,
                "category": category,
                "created_at": created_at,
                "is_favorite": is_favorite,
                "leonardo_images": tuple(
                    concept_images.get(image_type)
                    for image_type in LEONARDO_CONCEPT_IMAGE_TYPES
                ),
                "modern_images": tuple(
                    concept_images.get(image_type)
                    for image_type in MODERN_CONCEPT_IMAGE_TYPES
                ),
            }
        )

    return gallery_items


def generate_and_save_concept_images(concept_data, concept_id):
    existing_images = map_automatic_concept_images(list_concept_images(concept_id))
    design_blueprint = build_design_blueprint(concept_data)
    prompts = {
        **build_leonardo_concept_image_prompts(concept_data, design_blueprint),
        **build_modern_concept_image_prompts(concept_data, design_blueprint),
    }
    results = {}
    pending_prompts = {}

    for image_type in CONCEPT_IMAGE_TYPES:
        if image_type in existing_images:
            results[image_type] = {"status": "skipped"}
        else:
            pending_prompts[image_type] = prompts[image_type]

    with ThreadPoolExecutor(max_workers=CONCEPT_IMAGE_MAX_WORKERS) as executor:
        futures = {
            executor.submit(generate_concept_image, prompt): image_type
            for image_type, prompt in pending_prompts.items()
        }

        for future in as_completed(futures):
            image_type = futures[future]
            try:
                asset = future.result()
                current_images = map_automatic_concept_images(
                    list_concept_images(concept_id)
                )
                if image_type in current_images:
                    results[image_type] = {"status": "skipped"}
                    continue

                save_visual(concept_id, image_type, asset)
                results[image_type] = {"status": "saved"}
            except Exception:
                results[image_type] = {
                    "status": "failed",
                    "error": "Image generation failed. Please try again later.",
                }

    return results
