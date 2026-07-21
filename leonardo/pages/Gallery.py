import streamlit as st

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


def _render_automatic_image_row(heading, images):
    st.markdown(f"#### {heading}")
    columns = st.columns(3)

    for index, (column, image) in enumerate(zip(columns, images), start=1):
        with column:
            if image is None:
                st.info(f"Image {index} is not available.")
            else:
                st.image(
                    image[4],
                    caption=f"Image {index}",
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
            f'{gallery_item["category"]} • Created: {gallery_item["created_at"]}'
        )
        _render_automatic_image_row(
            "Leonardo Vision",
            gallery_item["leonardo_images"],
        )
        _render_automatic_image_row(
            "Modern Implementation",
            gallery_item["modern_images"],
        )


st.set_page_config(
    page_title="Gallery",
    page_icon="🗂",
    layout="wide"
)

init_db()

st.title("🗂 Saved Image Gallery")
st.write("Browse all saved Leonardo sketches and modern blueprints.")

filter_option = st.selectbox(
    "Filter images",
    ["All", "Leonardo", "Blueprint", "Favorites"]
)

all_images = get_all_images()
concept_gallery_items = []
if filter_option in {"All", "Favorites"}:
    concept_gallery_items = build_concept_gallery_items(
        list_recent_concepts(limit=-1),
        all_images,
        favorites_only=filter_option == "Favorites",
    )

if filter_option == "All":
    images = all_images
elif filter_option == "Leonardo":
    images = get_images_by_type("leonardo")
elif filter_option == "Blueprint":
    images = get_images_by_type("blueprint")
else:
    images = get_favorite_images()

images = exclude_automatic_concept_images(images, image_type_index=2)

if not concept_gallery_items and not images:
    st.info("No images found for this filter.")
else:
    if concept_gallery_items:
        st.subheader("Generated Concepts")
        for gallery_item in concept_gallery_items:
            _render_concept_gallery_item(gallery_item)

    if concept_gallery_items and images:
        st.subheader("Saved Images")

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
            st.markdown(f"### {star_prefix}{image_type.capitalize()}")

            st.image(
                image_bytes,
                caption=f"{image_type.capitalize()} • Concept ID: {concept_id}",
                use_container_width=True
            )

            with st.expander("Prompt"):
                st.code(prompt, language="text")

            st.caption(f"Created: {created_at}")

            action1, action2, action3 = st.columns([1, 1, 1])

            with action1:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_gallery_{image_id}", help="Favorite"):
                    toggle_image_favorite(image_id)
                    st.rerun()

            with action2:
                if st.button("🗑", key=f"delete_gallery_{image_id}", help="Delete"):
                    delete_image_asset(image_id)
                    st.rerun()

            with action3:
                st.download_button(
                    label="⬇",
                    data=image_bytes,
                    file_name=f"{image_type}_{image_id}.png",
                    mime="image/png",
                    key=f"download_gallery_{image_id}",
                    help="Download",
                )
