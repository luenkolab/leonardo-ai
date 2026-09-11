import streamlit as st

from i18n import DEFAULT_LANGUAGE, LANGUAGE_SESSION_KEY, translate
from application.concepts import list_recent_concepts
from application.images import (
    build_concept_gallery_items,
    exclude_automatic_concept_images,
)
from database import (
    init_db,
    get_all_images,
    get_favorite_images,
    get_images_by_type,
    delete_image_asset,
    toggle_image_favorite,
)
from ui.sidebar import render_language_selector
from ui.state import get_current_language, initialize_session_state


def _render_automatic_image_row(heading, images):
    st.markdown(f"#### {heading}")
    columns = st.columns(3)

    for index, (column, image) in enumerate(zip(columns, images), start=1):
        with column:
            if image is None:
                st.info(translate("gallery.image_unavailable", get_current_language(), index=index))
            else:
                st.image(
                    image[4],
                    caption=translate("common.image", get_current_language(), index=index),
                    use_container_width=True,
                )


def _render_concept_gallery_item(gallery_item):
    favorite_prefix = "⭐ " if gallery_item["is_favorite"] else ""
    concept_id = gallery_item["concept_id"]

    with st.expander(
        f'{favorite_prefix}{gallery_item["title"]}',
        expanded=False,
        key=f"gallery_concept_{concept_id}",
    ):
        st.caption(
            f'{translate(f"option.category.{gallery_item["category"]}", get_current_language())} • '
            f'{translate("common.created", get_current_language())}: {gallery_item["created_at"]}'
        )
        _render_automatic_image_row(
            translate("concept.leonardo_vision", get_current_language()),
            gallery_item["leonardo_images"],
        )
        _render_automatic_image_row(
            translate("concept.modern_implementation", get_current_language()),
            gallery_item["modern_images"],
        )


st.set_page_config(
    page_title=translate(
        "gallery.page_title",
        st.session_state.get(LANGUAGE_SESSION_KEY, DEFAULT_LANGUAGE),
    ),
    page_icon="🗂",
    layout="wide"
)

init_db()
initialize_session_state()

with st.sidebar:
    render_language_selector()

language = get_current_language()
st.title(f"🗂 {translate('gallery.title', language)}")
st.write(translate("gallery.description", language))

filter_option = st.selectbox(
    translate("gallery.filter", language),
    ["all", "leonardo", "blueprint", "favorites"],
    format_func=lambda value: translate(f"gallery.filter.{value}", language),
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
    st.info(translate("gallery.no_images", language))
else:
    if concept_gallery_items:
        st.subheader(translate("gallery.generated_concepts", language))
        for gallery_item in concept_gallery_items:
            _render_concept_gallery_item(gallery_item)

    if concept_gallery_items and images:
        st.subheader(translate("gallery.saved_images", language))

if images:
    cols = st.columns(2)

    for idx, image in enumerate(images):
        image_id = image[0]
        concept_id = image[1]
        image_type = image[2]
        prompt = image[3]
        image_bytes = image[4]
        created_at = image[5]
        is_favorite = image[6]

        with cols[idx % 2]:
            star_prefix = "⭐ " if is_favorite else ""
            image_type_label = translate(f"gallery.type.{image_type}", language)
            st.markdown(f"### {star_prefix}{image_type_label}")

            st.image(
                image_bytes,
                caption=f"{image_type_label} • {translate('gallery.concept_id', language)}: {concept_id}",
                use_container_width=True
            )

            with st.expander(translate("common.prompt", language)):
                st.code(prompt, language="text")

            st.caption(f"{translate('common.created', language)}: {created_at}")

            action1, action2, action3 = st.columns([1, 1, 1])

            with action1:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_gallery_{image_id}", help=translate("common.favorite", language)):
                    toggle_image_favorite(image_id)
                    st.rerun()

            with action2:
                if st.button("🗑", key=f"delete_gallery_{image_id}", help=translate("common.delete", language)):
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
