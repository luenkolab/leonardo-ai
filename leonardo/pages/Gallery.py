import streamlit as st

from database import (
    init_db,
    get_all_images,
    get_favorite_images,
    get_images_by_type,
    delete_image_asset,
    toggle_image_favorite,
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

if filter_option == "All":
    images = get_all_images()
elif filter_option == "Leonardo":
    images = get_images_by_type("leonardo")
elif filter_option == "Blueprint":
    images = get_images_by_type("blueprint")
else:
    images = get_favorite_images()

if not images:
    st.info("No images found for this filter.")
else:
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

            col1, col2, col3 = st.columns(3)

            with col1:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_gallery_{image_id}"):
                    toggle_image_favorite(image_id)
                    st.rerun()

            with col2:
                if st.button("Delete", key=f"delete_gallery_{image_id}"):
                    delete_image_asset(image_id)
                    st.rerun()

            with col3:
                st.download_button(
                    label="Download",
                    data=image_bytes,
                    file_name=f"{image_type}_{image_id}.png",
                    mime="image/png",
                    key=f"download_gallery_{image_id}"
                )