import streamlit as st

from i18n import translate
from application.images import (
    exclude_automatic_concept_images,
    list_concept_images,
    remove_visual,
    save_visual,
    toggle_visual_favorite,
)
from ui.components import render_generated_section_heading, render_result_box
from ui.state import BLUEPRINT_ASSET, LEONARDO_ASSET, get_current_concept_id, get_current_language


_SAVED_IMAGES_ICON = """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="5" y="5" width="16" height="14" rx="2"/><path d="M5 16l4-4 3 3 3-3 6 6"/><circle cx="16.5" cy="9.5" r="1.5"/><path d="M3 17V5a2 2 0 0 1 2-2h14"/></svg>"""


def render_generated_visuals(language):
    if not st.session_state[LEONARDO_ASSET] and not st.session_state[BLUEPRINT_ASSET]:
        return

    st.markdown(f"## {translate('images.generated_assets', language)}")

    if st.session_state[LEONARDO_ASSET]:
        render_result_box(translate("images.leonardo_asset", language), translate("images.leonardo_asset_description", language))
        st.image(
            st.session_state[LEONARDO_ASSET]["image_bytes"],
            caption=translate("images.leonardo_caption", language),
            use_container_width=True,
        )

        action1, action2, action3 = st.columns([1, 1, 6])
        with action1:
            if st.button("⭐", key="save_leonardo_image", help=translate("images.save_leonardo", language)):
                current_concept_id = get_current_concept_id()
                if current_concept_id:
                    save_visual(
                        current_concept_id,
                        "leonardo",
                        st.session_state[LEONARDO_ASSET],
                    )
                    st.success(translate("images.saved", language))
                else:
                    st.error(translate("images.no_concept", language))
        with action2:
            if st.button("🗑", key="clear_leonardo_asset", help=translate("images.clear_leonardo", language)):
                st.session_state[LEONARDO_ASSET] = None
                st.rerun()
        with action3:
            with st.expander(translate("common.prompt", language)):
                st.code(st.session_state[LEONARDO_ASSET]["prompt"], language="text")

    if st.session_state[BLUEPRINT_ASSET]:
        render_result_box(translate("images.blueprint_asset", language), translate("images.blueprint_asset_description", language))
        st.image(
            st.session_state[BLUEPRINT_ASSET]["image_bytes"],
            caption=translate("images.blueprint_caption", language),
            use_container_width=True,
        )

        action1, action2, action3 = st.columns([1, 1, 6])
        with action1:
            if st.button("⭐", key="save_blueprint_image", help=translate("images.save_blueprint", language)):
                current_concept_id = get_current_concept_id()
                if current_concept_id:
                    save_visual(
                        current_concept_id,
                        "blueprint",
                        st.session_state[BLUEPRINT_ASSET],
                    )
                    st.success(translate("images.saved", language))
                else:
                    st.error(translate("images.no_concept", language))
        with action2:
            if st.button("🗑", key="clear_blueprint_asset", help=translate("images.clear_blueprint", language)):
                st.session_state[BLUEPRINT_ASSET] = None
                st.rerun()
        with action3:
            with st.expander(translate("common.prompt", language)):
                st.code(st.session_state[BLUEPRINT_ASSET]["prompt"], language="text")


def render_saved_images():
    language = get_current_language()
    render_generated_section_heading(
        translate("images.saved_images", language),
        _SAVED_IMAGES_ICON,
    )

    current_concept_id = get_current_concept_id()

    if not current_concept_id:
        with st.container(key="saved_images_empty_state"):
            st.info(translate("images.no_concept", language))
        return

    images = exclude_automatic_concept_images(
        list_concept_images(current_concept_id)
    )

    if not images:
        with st.container(key="saved_images_empty_state"):
            st.info(translate("images.none_saved", language))
        return

    cols = st.columns(2)

    for idx, image in enumerate(images):
        image_id = image[0]
        image_type = image[1]
        image_bytes = image[3]
        is_favorite = image[5]

        with cols[idx % 2]:
            star_prefix = "⭐ " if is_favorite else ""
            image_type_label = translate(f"gallery.type.{image_type}", language)
            st.markdown(f"### {star_prefix}{image_type_label}")

            st.image(
                image_bytes,
                caption=image_type_label,
                use_container_width=True,
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_image_{image_id}"):
                    toggle_visual_favorite(image_id)
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"delete_image_{image_id}", help=translate("common.delete", language)):
                    remove_visual(image_id)
                    st.rerun()
            with col3:
                st.download_button(
                    label=translate("common.download", language),
                    data=image_bytes,
                    file_name=f"{image_type}_{image_id}.png",
                    mime="image/png",
                    key=f"download_image_{image_id}",
                )
