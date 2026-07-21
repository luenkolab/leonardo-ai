import database
from application.concepts import remove_concept
from application.images import (
    CONCEPT_IMAGE_TYPES,
    LEONARDO_CONCEPT_IMAGE_TYPES,
    MODERN_CONCEPT_IMAGE_TYPES,
    build_concept_gallery_items,
    exclude_automatic_concept_images,
)


def _gallery_record(image_id, concept_id, image_type, is_favorite=0):
    return (
        image_id,
        concept_id,
        image_type,
        f"prompt-{image_type}",
        f"bytes-{concept_id}-{image_type}".encode(),
        "2026-07-20 12:00:00",
        is_favorite,
    )


def _automatic_records(concept_id, first_image_id=1):
    return [
        _gallery_record(image_id, concept_id, image_type)
        for image_id, image_type in enumerate(
            CONCEPT_IMAGE_TYPES,
            start=first_image_id,
        )
    ]


def test_six_automatic_images_form_one_gallery_item_with_separate_eras():
    concepts = [(42, "Test Concept", "robotics", "2026-07-20", 0)]
    automatic_images = _automatic_records(42)
    manual_image = _gallery_record(100, 42, "leonardo")

    gallery_items = build_concept_gallery_items(
        concepts,
        [manual_image, *reversed(automatic_images)],
    )

    assert len(gallery_items) == 1
    gallery_item = gallery_items[0]
    assert tuple(image[2] for image in gallery_item["leonardo_images"]) == (
        LEONARDO_CONCEPT_IMAGE_TYPES
    )
    assert tuple(image[2] for image in gallery_item["modern_images"]) == (
        MODERN_CONCEPT_IMAGE_TYPES
    )
    assert len(gallery_item["leonardo_images"]) == 3
    assert len(gallery_item["modern_images"]) == 3
    assert exclude_automatic_concept_images(
        [manual_image, *automatic_images],
        image_type_index=2,
    ) == [manual_image]


def test_gallery_images_are_grouped_only_with_their_own_concept():
    concepts = [
        (10, "Concept A", "mobility", "2026-07-20", 0),
        (20, "Concept B", "energy", "2026-07-19", 0),
    ]
    images = []
    first_records = _automatic_records(10, first_image_id=1)
    second_records = _automatic_records(20, first_image_id=101)
    for first, second in zip(first_records, second_records):
        images.extend((second, first))

    gallery_items = build_concept_gallery_items(concepts, images)

    assert [item["concept_id"] for item in gallery_items] == [10, 20]
    for gallery_item in gallery_items:
        grouped_images = (
            *gallery_item["leonardo_images"],
            *gallery_item["modern_images"],
        )
        assert all(
            image[1] == gallery_item["concept_id"] for image in grouped_images
        )


def test_gallery_preserves_concept_metadata_and_favorite_filter():
    concepts = [
        (7, "Favorite Concept", "robotics", "2026-07-20", 1),
        (8, "Regular Concept", "health", "2026-07-19", 0),
    ]
    images = [*_automatic_records(7), *_automatic_records(8, first_image_id=20)]

    all_items = build_concept_gallery_items(concepts, images)
    favorite_items = build_concept_gallery_items(
        concepts,
        images,
        favorites_only=True,
    )

    assert all_items[0] | {
        "leonardo_images": (),
        "modern_images": (),
    } == {
        "concept_id": 7,
        "title": "Favorite Concept",
        "category": "robotics",
        "created_at": "2026-07-20",
        "is_favorite": 1,
        "leonardo_images": (),
        "modern_images": (),
    }
    assert [item["concept_id"] for item in favorite_items] == [7]
    assert favorite_items[0]["is_favorite"] == 1


def test_deleting_concept_removes_gallery_item_and_its_images(
    temporary_database,
    valid_concept,
    png_bytes,
):
    first_concept_id = database.save_concept(
        title="First Concept",
        category="robotics",
        prompt="first",
        concept_data=valid_concept,
    )
    second_concept_id = database.save_concept(
        title="Second Concept",
        category="energy",
        prompt="second",
        concept_data=valid_concept,
    )
    for concept_id in (first_concept_id, second_concept_id):
        for image_type in CONCEPT_IMAGE_TYPES:
            database.save_image_asset(
                concept_id=concept_id,
                image_type=image_type,
                prompt=f"prompt-{image_type}",
                image_bytes=png_bytes,
            )

    remove_concept(first_concept_id)
    gallery_items = build_concept_gallery_items(
        database.get_concepts(limit=-1),
        database.get_all_images(),
    )

    assert database.get_images_for_concept(first_concept_id) == []
    assert [item["concept_id"] for item in gallery_items] == [second_concept_id]
    remaining_images = (
        *gallery_items[0]["leonardo_images"],
        *gallery_items[0]["modern_images"],
    )
    assert len(remaining_images) == 6
    assert all(image[1] == second_concept_id for image in remaining_images)
