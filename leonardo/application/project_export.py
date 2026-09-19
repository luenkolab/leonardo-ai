from application.images import list_concept_images
from pdf_export import export_drawing_package_pdf, export_project_plan_pdf


def export_project_package(
    concept_data,
    concept_id,
    language="en",
) -> bytes:
    saved_images = list_concept_images(concept_id) if concept_id else []
    return export_project_plan_pdf(
        concept_data,
        saved_images=saved_images,
        language=language,
    )


def export_drawing_package(package, language="en") -> bytes:
    return export_drawing_package_pdf(package, language=language)
