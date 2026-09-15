import base64

import streamlit as st

from i18n import category_display_name, translate
from ui.formatting import safe_text


_PROJECT_DETAIL_ICONS = {
    "hero": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9" r="1.5"/><path d="m3 17 5-5 4 4 3-3 6 6"/></svg>""",
    "overview": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 3h10l4 4v14H5zM15 3v5h5M8 12h8M8 16h8"/></svg>""",
    "highlights": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20V5M4 20h17"/><path d="m7 16 4-4 3 2 6-7M16 7h4v4"/></svg>""",
    "market": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="8"/><path d="M12 4v16M4 12h16M6.5 7.5h11M6.5 16.5h11"/></svg>""",
    "technology": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M8 3h8v4h4v10h-4v4H8v-4H4V7h4z"/><path d="M9 9h6v6H9zM12 3V1M12 23v-2M4 12H2M22 12h-2"/></svg>""",
    "roadmap": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="5" cy="18" r="2"/><circle cx="19" cy="6" r="2"/><path d="M7 18h3a4 4 0 0 0 4-4v-4a4 4 0 0 1 4-4h-1M10 14l4 4M14 14l-4 4"/></svg>""",
    "risks": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v5M12 17.5h.01"/></svg>""",
    "commercial": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20V5M4 20h17"/><path d="m7 16 4-4 3 2 6-7M16 7h4v4"/></svg>""",
}


def marketplace_image_data_uri(image_data):
    image_bytes = bytes(image_data)
    if image_bytes.startswith(b"\xff\xd8\xff"):
        mime_type = "image/jpeg"
    elif image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        mime_type = "image/webp"
    else:
        mime_type = "image/png"
    encoded_image = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded_image}"


def marketplace_carousel_state(project, image_index=0):
    concept_id = project.get("concept_id")
    images = tuple(
        image
        for image in project.get("project_images", ())
        if concept_id is None or image.get("concept_id") == concept_id
    )
    if not images:
        return {
            "images": (),
            "index": 0,
            "current": None,
            "previous": None,
            "next": None,
        }

    index = int(image_index) % len(images)
    return {
        "images": images,
        "index": index,
        "current": images[index],
        "previous": images[(index - 1) % len(images)] if len(images) > 1 else None,
        "next": images[(index + 1) % len(images)] if len(images) > 1 else None,
    }


def _carousel_state_key(project_id):
    return f"marketplace_image_index_{project_id}"


def _change_carousel_image(project_id, image_count, step):
    state_key = _carousel_state_key(project_id)
    current_index = int(st.session_state.get(state_key, 0))
    st.session_state[state_key] = (current_index + step) % image_count


def _carousel_image_markup(image, class_name, alt_text=""):
    return (
        f'<div class="{class_name}">'
        f'<img src="{marketplace_image_data_uri(image["image_data"])}" '
        f'alt="{safe_text(alt_text)}">'
        "</div>"
    )


def _carousel_preview_markup(image, class_name):
    return (
        f'<img class="{class_name}" '
        f'src="{marketplace_image_data_uri(image["image_data"])}" alt="">'
    )


def _render_project_carousel(project, language):
    project_id = project["id"]
    state_key = _carousel_state_key(project_id)
    carousel = marketplace_carousel_state(
        project,
        st.session_state.get(state_key, 0),
    )
    st.session_state[state_key] = carousel["index"]
    image_count = len(carousel["images"])

    with st.container(key="marketplace_project_carousel"):
        if image_count == 0:
            st.markdown(
                '<div class="marketplace-project-hero" aria-hidden="true">'
                f"<span>{_PROJECT_DETAIL_ICONS['hero']}</span>"
                "</div>",
                unsafe_allow_html=True,
            )
            return

        slides = []
        if carousel["previous"] is not None:
            slides.append(
                _carousel_preview_markup(
                    carousel["previous"],
                    "marketplace-project-carousel__preview "
                    "marketplace-project-carousel__preview--previous",
                )
            )
        slides.append(
            _carousel_image_markup(
                carousel["current"],
                "marketplace-project-carousel__current",
                project["name"],
            )
        )
        if carousel["next"] is not None:
            slides.append(
                _carousel_preview_markup(
                    carousel["next"],
                    "marketplace-project-carousel__preview "
                    "marketplace-project-carousel__preview--next",
                )
            )
        st.markdown(
            '<div class="marketplace-project-hero '
            'marketplace-project-carousel__stage">'
            f'{"".join(slides)}</div>',
            unsafe_allow_html=True,
        )

        if image_count > 1:
            previous_column, _, next_column = st.columns([1, 8, 1])
            with previous_column:
                st.button(
                    " ",
                    key=f"marketplace_carousel_previous_{project_id}",
                    help=translate("marketplace.previous_image", language),
                    on_click=_change_carousel_image,
                    args=(project_id, image_count, -1),
                )
            with next_column:
                st.button(
                    " ",
                    key=f"marketplace_carousel_next_{project_id}",
                    help=translate("marketplace.next_image", language),
                    on_click=_change_carousel_image,
                    args=(project_id, image_count, 1),
                )

        st.markdown(
            '<div class="marketplace-project-carousel__indicator">'
            f'{carousel["index"] + 1} / {image_count}'
            "</div>",
            unsafe_allow_html=True,
        )


def _section_markup(title, content, icon_name):
    if isinstance(content, (tuple, list)):
        body = "<ul>" + "".join(
            f"<li>{safe_text(item)}</li>" for item in content
        ) + "</ul>"
    else:
        body = f"<p>{safe_text(content)}</p>"
    return (
        '<section class="marketplace-project-section">'
        '<h2><span class="marketplace-project-section__icon">'
        f'{_PROJECT_DETAIL_ICONS[icon_name]}</span>{safe_text(title)}</h2>'
        f'<div class="marketplace-project-section__body">{body}</div>'
        "</section>"
    )


def render_marketplace_project(project, language, on_back):
    category = category_display_name(project["category"], language)
    meta_items = [
        (
            translate("marketplace.stage", language),
            project.get("stage"),
        ),
        (
            translate("marketplace.funding", language),
            project.get("funding"),
        ),
    ]
    meta_markup = "".join(
        f"<div><span>{safe_text(label)}</span><strong>{safe_text(value)}</strong></div>"
        for label, value in meta_items
        if value
    )
    meta_section = (
        '<div class="marketplace-project-meta">'
        f"{meta_markup}</div>"
        if meta_markup
        else ""
    )
    page_class = "marketplace-project-page"
    if not meta_markup:
        page_class += " marketplace-project-page--without-meta"
    st.button(
        translate("marketplace.back", language),
        key="marketplace_project_back",
        on_click=on_back,
    )

    st.markdown(
        "".join(
            (
                '<header class="marketplace-project-header">',
                f"<h1>{safe_text(project['name'])}</h1>",
                f'<div class="marketplace-project-header__category">{safe_text(category)}</div>',
                f"<p>{safe_text(project['summary'])}</p>",
                "</header>",
            )
        ),
        unsafe_allow_html=True,
    )
    _render_project_carousel(project, language)

    detail_markup = "".join(
        (
            f'<div class="{page_class}">',
            meta_section,
            _section_markup(
                translate("marketplace.detail.overview", language),
                project["summary"],
                "overview",
            ),
            '<div class="marketplace-project-section-grid">',
            _section_markup(
                translate("marketplace.detail.investment_highlights", language),
                project["investment_highlights"],
                "highlights",
            ),
            _section_markup(
                translate("marketplace.detail.market_opportunity", language),
                project["market_opportunity"],
                "market",
            ),
            "</div>",
            _section_markup(
                translate("marketplace.detail.technology_solution", language),
                project["technology_solution"],
                "technology",
            ),
            _section_markup(
                translate("marketplace.detail.roadmap", language),
                project["roadmap"],
                "roadmap",
            ),
            '<div class="marketplace-project-section-grid">',
            _section_markup(
                translate("marketplace.detail.risks", language),
                project["risks"],
                "risks",
            ),
            _section_markup(
                translate("marketplace.detail.commercial_outlook", language),
                project["commercial_outlook"],
                "commercial",
            ),
            "</div>",
            "</div>",
        )
    )
    st.markdown(detail_markup, unsafe_allow_html=True)
