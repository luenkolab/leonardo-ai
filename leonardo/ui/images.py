import streamlit as st

from application.images import (
    exclude_automatic_concept_images,
    list_concept_images,
    remove_visual,
    save_visual,
    toggle_visual_favorite,
)
from ui.components import render_result_box
from ui.formatting import pretty_label
from ui.state import BLUEPRINT_ASSET, LEONARDO_ASSET, get_current_concept_id


def render_generated_visuals():
    if not st.session_state[LEONARDO_ASSET] and not st.session_state[BLUEPRINT_ASSET]:
        return

    st.markdown("## Generated Visual Assets")

    if st.session_state[LEONARDO_ASSET]:
        render_result_box("Leonardo Visual Asset", "Generated image based on the Renaissance sketch prompt.")
        st.image(
            st.session_state[LEONARDO_ASSET]["image_bytes"],
            caption="Leonardo Sketch",
            use_container_width=True,
        )

        action1, action2, action3 = st.columns([1, 1, 6])
        with action1:
            if st.button("⭐", key="save_leonardo_image", help="Save Leonardo image"):
                current_concept_id = get_current_concept_id()
                if current_concept_id:
                    save_visual(
                        current_concept_id,
                        "leonardo",
                        st.session_state[LEONARDO_ASSET],
                    )
                    st.success("Saved.")
                else:
                    st.error("No concept selected.")
        with action2:
            if st.button("🗑", key="clear_leonardo_asset", help="Clear Leonardo asset"):
                st.session_state[LEONARDO_ASSET] = None
                st.rerun()
        with action3:
            with st.expander("Prompt"):
                st.code(st.session_state[LEONARDO_ASSET]["prompt"], language="text")

    if st.session_state[BLUEPRINT_ASSET]:
        render_result_box("Blueprint Visual Asset", "Generated image based on the modern blueprint prompt.")
        st.image(
            st.session_state[BLUEPRINT_ASSET]["image_bytes"],
            caption="Modern Blueprint",
            use_container_width=True,
        )

        action1, action2, action3 = st.columns([1, 1, 6])
        with action1:
            if st.button("⭐", key="save_blueprint_image", help="Save Blueprint image"):
                current_concept_id = get_current_concept_id()
                if current_concept_id:
                    save_visual(
                        current_concept_id,
                        "blueprint",
                        st.session_state[BLUEPRINT_ASSET],
                    )
                    st.success("Saved.")
                else:
                    st.error("No concept selected.")
        with action2:
            if st.button("🗑", key="clear_blueprint_asset", help="Clear Blueprint asset"):
                st.session_state[BLUEPRINT_ASSET] = None
                st.rerun()
        with action3:
            with st.expander("Prompt"):
                st.code(st.session_state[BLUEPRINT_ASSET]["prompt"], language="text")


def render_saved_images():
    st.markdown("## Saved Images")

    current_concept_id = get_current_concept_id()

    if not current_concept_id:
        st.info("No concept selected.")
        return

    images = exclude_automatic_concept_images(
        list_concept_images(current_concept_id)
    )

    if not images:
        st.info("No saved images yet.")
        return

    cols = st.columns(2)

    for idx, image in enumerate(images):
        image_id = image[0]
        image_type = image[1]
        image_bytes = image[3]
        is_favorite = image[5]

        with cols[idx % 2]:
            star_prefix = "⭐ " if is_favorite else ""
            st.markdown(f"### {star_prefix}{pretty_label(image_type)}")

            st.image(
                image_bytes,
                caption=pretty_label(image_type),
                use_container_width=True,
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_image_{image_id}"):
                    toggle_visual_favorite(image_id)
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"delete_image_{image_id}", help="Delete image"):
                    remove_visual(image_id)
                    st.rerun()
            with col3:
                st.download_button(
                    label="Download",
                    data=image_bytes,
                    file_name=f"{image_type}_{image_id}.png",
                    mime="image/png",
                    key=f"download_image_{image_id}",
                )
