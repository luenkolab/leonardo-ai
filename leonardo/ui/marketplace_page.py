import streamlit as st

from categories import CATEGORY_KEYS, normalize_category
from i18n import category_display_name, translate
from ui.formatting import safe_text
from ui.state import get_current_language


MARKETPLACE_SEARCH = "marketplace_search"
MARKETPLACE_CATEGORY = "marketplace_category"
MARKETPLACE_FILTERS = "marketplace_filters"
_MARKETPLACE_FILTERS_BUTTON = "marketplace_filters_button"
_MARKETPLACE_ACTIVE_CATEGORY = "marketplace_active_category"

_MARKETPLACE_HEADING_ICON = """
<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path d="M4 20V9h16v11M7 9V5h10v4M3 20h18"/>
    <path d="M8 13h3v3H8zM15 12v8M17.5 4.5 19 3M6.5 4.5 5 3"/>
</svg>
"""

_PROJECT_IMAGE_ICON = """
<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <rect x="3" y="4" width="18" height="16" rx="2"/>
    <circle cx="8.5" cy="9" r="1.5"/>
    <path d="m3 17 5-5 4 4 3-3 6 6"/>
</svg>
"""

_DEMO_PROJECTS = (
    {
        "id": "swiftbridge",
        "name": "SwiftBridge",
        "category": "transport_mobility",
        "summary": "Rapidly deployable modular access for disrupted transport corridors and emergency response.",
        "stage": "Pilot",
        "funding": "Seeking strategic partners",
        "tags": ("Modular", "Resilience", "Deployment"),
    },
    {
        "id": "aquaclean_station",
        "name": "AquaClean Station",
        "category": "water",
        "summary": "Distributed water treatment designed for communities, remote sites and temporary operations.",
        "stage": "MVP",
        "funding": "Seeking seed funding",
        "tags": ("Water", "Circular", "Infrastructure"),
    },
    {
        "id": "gridwise_storage",
        "name": "GridWise Storage",
        "category": "energy",
        "summary": "Adaptive energy storage coordination for facilities balancing resilience and operating cost.",
        "stage": "Prototype",
        "funding": "Seeking technical partners",
        "tags": ("Storage", "Energy", "Control"),
    },
    {
        "id": "carelink_mobile",
        "name": "CareLink Mobile",
        "category": "health_biotech",
        "summary": "Field-ready diagnostic support connecting mobile care teams with specialist workflows.",
        "stage": "MVP",
        "funding": "Seeking pilot sites",
        "tags": ("Health", "Mobile", "Workflow"),
    },
    {
        "id": "forgevision",
        "name": "ForgeVision",
        "category": "manufacturing_industry",
        "summary": "Visual quality intelligence for smaller manufacturers introducing traceable inspection.",
        "stage": "Pilot",
        "funding": "Seeking growth capital",
        "tags": ("Vision", "Quality", "AI"),
    },
    {
        "id": "terrain_rover",
        "name": "Terrain Rover",
        "category": "robotics_automation",
        "summary": "Configurable autonomous inspection for difficult industrial and infrastructure environments.",
        "stage": "Prototype",
        "funding": "Seeking development funding",
        "tags": ("Robotics", "Inspection", "Autonomy"),
    },
)

MARKETPLACE_CATEGORIES = ("all", *CATEGORY_KEYS)


def _toggle_marketplace_filters():
    st.session_state[MARKETPLACE_FILTERS] = not bool(
        st.session_state.get(MARKETPLACE_FILTERS, False)
    )


def _clear_marketplace_category():
    st.session_state[MARKETPLACE_CATEGORY] = "all"


def _close_marketplace_filters():
    st.session_state[MARKETPLACE_FILTERS] = False


def filter_marketplace_projects(projects, search_text="", category="all"):
    normalized_search = " ".join(str(search_text).casefold().split())
    selected_category = category or "all"
    filtered = []
    for project in projects:
        searchable = " ".join(
            (
                project["name"],
                project["category"],
                project["summary"],
                project["stage"],
                project["funding"],
                *project["tags"],
            )
        ).casefold()
        category_matches = selected_category == "all" or (
            project["category"] == selected_category
        )
        if category_matches and normalized_search in searchable:
            filtered.append(project)
    return filtered


def _project_card_markup(project, language):
    tags = "".join(
        f'<span class="marketplace-card__tag">{safe_text(tag)}</span>'
        for tag in project["tags"]
    )
    category = category_display_name(project["category"], language)
    return f"""
<div class="marketplace-card__content">
    <div class="marketplace-card__image" aria-hidden="true">
        <span>{_PROJECT_IMAGE_ICON}</span>
    </div>
    <div class="marketplace-card__identity">
        <h3>{safe_text(project['name'])}</h3>
        <p>{safe_text(category)}</p>
    </div>
    <p class="marketplace-card__summary">{safe_text(project['summary'])}</p>
    <div class="marketplace-card__meta">
        <span><strong>{safe_text(translate('marketplace.stage', language))}</strong>{safe_text(project['stage'])}</span>
        <span><strong>{safe_text(translate('marketplace.funding', language))}</strong>{safe_text(project['funding'])}</span>
    </div>
    <div class="marketplace-card__tags">{tags}</div>
</div>
"""


def render_marketplace():
    language = get_current_language()
    stored_category = st.session_state.get(MARKETPLACE_CATEGORY, "all")
    if stored_category != "all":
        stored_category = normalize_category(stored_category) or "all"
    st.session_state[MARKETPLACE_CATEGORY] = stored_category
    if MARKETPLACE_FILTERS not in st.session_state:
        st.session_state[MARKETPLACE_FILTERS] = False
    st.markdown(
        f"""
<div class="marketplace-page">
    <div class="marketplace-page__heading">
        <span class="marketplace-page__heading-icon">{_MARKETPLACE_HEADING_ICON}</span>
        <h1>{safe_text(translate('marketplace.title', language))}</h1>
    </div>
    <p class="marketplace-page__subtitle">{safe_text(translate('marketplace.subtitle', language))}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(key="marketplace_toolbar"):
        search_column, filter_column = st.columns([5, 1])
        with search_column:
            search_text = st.text_input(
                translate("marketplace.search", language),
                placeholder=translate("marketplace.search", language),
                label_visibility="collapsed",
                key=MARKETPLACE_SEARCH,
            )
        with filter_column:
            st.button(
                translate("marketplace.filters", language),
                key=_MARKETPLACE_FILTERS_BUTTON,
                use_container_width=True,
                on_click=_toggle_marketplace_filters,
            )

        filters_open = st.session_state[MARKETPLACE_FILTERS]
        if filters_open:
            with st.container(key="marketplace_filter_panel"):
                selected_category = st.segmented_control(
                    translate("marketplace.categories", language),
                    MARKETPLACE_CATEGORIES,
                    format_func=lambda value: (
                        translate("marketplace.category.all", language)
                        if value == "all"
                        else category_display_name(value, language)
                    ),
                    default="all",
                    label_visibility="collapsed",
                    key=MARKETPLACE_CATEGORY,
                    on_change=_close_marketplace_filters,
                )
        else:
            selected_category = stored_category
            if selected_category != "all":
                st.button(
                    f"{category_display_name(selected_category, language)} ×",
                    key=_MARKETPLACE_ACTIVE_CATEGORY,
                    on_click=_clear_marketplace_category,
                    type="primary",
                )

    projects = filter_marketplace_projects(
        _DEMO_PROJECTS,
        search_text=search_text,
        category=selected_category,
    )

    if not projects:
        st.markdown(
            f'<div class="marketplace-empty">{safe_text(translate("marketplace.no_projects", language))}</div>',
            unsafe_allow_html=True,
        )
        return

    with st.container(key="marketplace_grid"):
        columns = st.columns(len(projects))
        for column, project in zip(columns, projects):
            with column:
                st.markdown(
                    _project_card_markup(project, language),
                    unsafe_allow_html=True,
                )
                st.button(
                    translate("marketplace.view_project", language),
                    key=f'marketplace_view_{project["id"]}',
                    use_container_width=True,
                )
