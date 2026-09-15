from application.concepts import ConceptLoadError, load_concept_for_viewer
from categories import normalize_category
from database import (
    get_images_for_concept,
    get_published_concept_by_id,
    get_published_concepts,
    is_concept_published,
    set_concept_published,
)
from i18n import DEFAULT_LANGUAGE, normalize_language


REAL_PROJECT_PREFIX = "concept_"


def publish_concept(concept_id):
    return set_concept_published(concept_id, True)


def remove_concept_from_marketplace(concept_id):
    return set_concept_published(concept_id, False)


def concept_is_published(concept_id):
    return is_concept_published(concept_id)


def _non_empty(*values):
    return tuple(value for value in values if value)


def _map_images(concept_id):
    return tuple(
        {
            "id": image_id,
            "concept_id": concept_id,
            "image_type": image_type,
            "prompt": prompt,
            "image_data": bytes(image_data),
            "created_at": created_at,
            "is_favorite": bool(is_favorite),
        }
        for image_id, image_type, prompt, image_data, created_at, is_favorite
        in get_images_for_concept(concept_id)
        if str(image_type).startswith("modern_concept_")
    )


def _map_published_row(row, viewer_language=None):
    concept_id, _title, category, _raw_content, source_language, created_at = row
    canonical_category = normalize_category(category)
    if canonical_category is None:
        return None

    try:
        language = normalize_language(
            viewer_language or source_language or DEFAULT_LANGUAGE
        )
        content, _ = load_concept_for_viewer(concept_id, language)
    except ConceptLoadError:
        return None
    if content is None:
        return None

    roadmap = content["implementation_roadmap"]
    project_images = _map_images(concept_id)
    source_view = (
        source_language is None
        or language == normalize_language(source_language)
    )
    return {
        "id": f"{REAL_PROJECT_PREFIX}{concept_id}",
        "concept_id": concept_id,
        "source": "real",
        "name": _title if source_view else content["title"],
        "category": canonical_category,
        "summary": content["executive_summary"],
        "stage": "",
        "funding": "",
        "tags": tuple(content["industries"][:3]),
        "investment_highlights": _non_empty(
            content["investor_summary"],
            content["roi"],
        ),
        "market_opportunity": content["market_demand"],
        "technology_solution": _non_empty(
            content["modern_principle"],
            *content["system_components"],
        ),
        "roadmap": _non_empty(
            roadmap["prototype"],
            roadmap["mvp"],
            roadmap["pilot"],
            roadmap["production"],
        ),
        "risks": _non_empty(*content["risks"], *content["constraints"]),
        "commercial_outlook": _non_empty(
            content["market_demand"],
            content["startup_cost"],
            content["roi"],
            content["investor_summary"],
        ),
        "project_images": project_images,
        "source_language": source_language,
        "created_at": created_at,
    }


def list_published_marketplace_projects(viewer_language=None):
    projects = (
        _map_published_row(row, viewer_language)
        for row in get_published_concepts()
    )
    return tuple(project for project in projects if project is not None)


def get_published_marketplace_project(project_id, viewer_language=None):
    if not str(project_id).startswith(REAL_PROJECT_PREFIX):
        return None
    raw_id = str(project_id)[len(REAL_PROJECT_PREFIX):]
    if not raw_id.isdigit():
        return None
    row = get_published_concept_by_id(int(raw_id))
    return (
        _map_published_row(row, viewer_language)
        if row is not None
        else None
    )
