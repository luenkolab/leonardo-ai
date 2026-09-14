import streamlit as st

from application.concepts import list_recent_concepts
from application.images import (
    build_concept_gallery_items,
    exclude_automatic_concept_images,
)
from database import (
    delete_image_asset,
    get_all_images,
    get_favorite_images,
    get_images_by_type,
    toggle_image_favorite,
)
from i18n import category_display_name, translate
from ui.formatting import safe_text
from ui.state import get_current_language


_GALLERY_HEADING_ICON = """
<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <rect x="3" y="5" width="15" height="15" rx="2"/>
    <path d="M7 5V3h14v14h-3"/>
    <circle cx="8.5" cy="10" r="1.5"/>
    <path d="m3 17 4.5-4.5 3.5 3.5 2.5-2.5L18 18"/>
</svg>
"""


def _render_automatic_image_row(heading, images, language):
    st.markdown(f"#### {heading}")
    columns = st.columns(3)

    for index, (column, image) in enumerate(zip(columns, images), start=1):
        with column:
            if image is None:
                st.info(translate("gallery.image_unavailable", language, index=index))
            else:
                st.image(
                    image[4],
                    caption=translate("common.image", language, index=index),
                    use_container_width=True,
                )


def _render_concept_gallery_item(gallery_item, language):
    favorite_prefix = "⭐ " if gallery_item["is_favorite"] else ""
    concept_id = gallery_item["concept_id"]
    category_label = category_display_name(gallery_item["category"], language)

    with st.expander(
        f'{favorite_prefix}{gallery_item["title"]}',
        expanded=False,
        key=f"gallery_concept_{concept_id}",
    ):
        st.caption(
            f'{category_label} • '
            f'{translate("common.created", language)}: {gallery_item["created_at"]}'
        )
        _render_automatic_image_row(
            translate("concept.leonardo_vision", language),
            gallery_item["leonardo_images"],
            language,
        )
        _render_automatic_image_row(
            translate("concept.modern_implementation", language),
            gallery_item["modern_images"],
            language,
        )


def render_gallery():
    language = get_current_language()
    st.markdown(
        f"""
<h1 class="gallery-page-heading">
    <span class="gallery-page-heading__icon">{_GALLERY_HEADING_ICON}</span>
    <span>{safe_text(translate('gallery.title', language))}</span>
</h1>
<p class="gallery-page-description">{safe_text(translate('gallery.description', language))}</p>
""",
        unsafe_allow_html=True,
    )

    filter_option = st.selectbox(
        translate("gallery.filter", language),
        ["all", "leonardo", "blueprint", "favorites"],
        format_func=lambda value: translate(f"gallery.filter.{value}", language),
        key="gallery_filter",
    )

    all_images = get_all_images()
    concept_gallery_items = []
    if filter_option in {"all", "favorites"}:
        concept_gallery_items = build_concept_gallery_items(
            list_recent_concepts(limit=-1),
            all_images,
            favorites_only=filter_option == "favorites",
        )

    if filter_option == "all":
        images = all_images
    elif filter_option == "leonardo":
        images = get_images_by_type("leonardo")
    elif filter_option == "blueprint":
        images = get_images_by_type("blueprint")
    else:
        images = get_favorite_images()

    images = exclude_automatic_concept_images(images, image_type_index=2)

    if not concept_gallery_items and not images:
        with st.container(key="gallery_empty_state"):
            st.info(translate("gallery.no_images", language))
    else:
        if concept_gallery_items:
            st.subheader(translate("gallery.generated_concepts", language))
            for gallery_item in concept_gallery_items:
                _render_concept_gallery_item(gallery_item, language)

        if concept_gallery_items and images:
            st.subheader(translate("gallery.saved_images", language))

    if images:
        columns = st.columns(2)

        for index, image in enumerate(images):
            image_id = image[0]
            concept_id = image[1]
            image_type = image[2]
            prompt = image[3]
            image_bytes = image[4]
            created_at = image[5]
            is_favorite = image[6]

            with columns[index % 2]:
                star_prefix = "⭐ " if is_favorite else ""
                image_type_label = translate(f"gallery.type.{image_type}", language)
                st.markdown(f"### {star_prefix}{image_type_label}")

                st.image(
                    image_bytes,
                    caption=(
                        f"{image_type_label} • "
                        f"{translate('gallery.concept_id', language)}: {concept_id}"
                    ),
                    use_container_width=True,
                )

                with st.expander(translate("common.prompt", language)):
                    st.code(prompt, language="text")

                st.caption(f"{translate('common.created', language)}: {created_at}")

                action1, action2, action3 = st.columns([1, 1, 1])

                with action1:
                    star_label = "⭐" if is_favorite else "☆"
                    if st.button(
                        star_label,
                        key=f"favorite_gallery_{image_id}",
                        help=translate("common.favorite", language),
                    ):
                        toggle_image_favorite(image_id)
                        st.rerun()

                with action2:
                    if st.button(
                        "🗑",
                        key=f"delete_gallery_{image_id}",
                        help=translate("common.delete", language),
                    ):
                        delete_image_asset(image_id)
                        st.rerun()

                with action3:
                    st.download_button(
                        label="⬇",
                        data=image_bytes,
                        file_name=f"{image_type}_{image_id}.png",
                        mime="image/png",
                        key=f"download_gallery_{image_id}",
                        help=translate("common.download", language),
                    )
