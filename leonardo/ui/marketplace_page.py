import streamlit as st

from application.marketplace import (
    get_published_marketplace_project,
    list_published_marketplace_projects,
)
from categories import CATEGORY_KEYS, normalize_category
from i18n import category_display_name, translate
from ui.formatting import safe_text
from ui.marketplace_project_page import (
    marketplace_image_data_uri,
    render_marketplace_project,
)
from ui.state import get_current_language


MARKETPLACE_SEARCH = "marketplace_search"
MARKETPLACE_CATEGORY = "marketplace_category"
MARKETPLACE_FILTERS = "marketplace_filters"
MARKETPLACE_VIEW = "marketplace_view"
MARKETPLACE_PROJECT_ID = "marketplace_project_id"
MARKETPLACE_PROJECTS_VIEW = "projects"
MARKETPLACE_PROJECT_DETAIL_VIEW = "project_detail"
_MARKETPLACE_FILTERS_BUTTON = "marketplace_filters_button"
_MARKETPLACE_ACTIVE_CATEGORY = "marketplace_active_category"
_MARKETPLACE_CATALOG_SNAPSHOT = "_marketplace_catalog_snapshot"

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
        "investment_highlights": (
            "Modular deployment model for time-critical access restoration.",
            "Pilot-stage project seeking strategic delivery partners.",
        ),
        "market_opportunity": "Emergency response and transport operators need deployable access when permanent corridors are disrupted.",
        "technology_solution": "Configurable structural modules combine transportability, rapid field deployment and resilient corridor access.",
        "roadmap": ("Validate the pilot deployment workflow.", "Secure strategic operating partners.", "Prepare repeatable field deployment."),
        "risks": ("Field conditions may extend deployment time.", "Adoption depends on operator validation and deployment readiness."),
        "commercial_outlook": "The current funding objective is strategic partnership for pilot validation and deployment scale-up.",
    },
    {
        "id": "aquaclean_station",
        "name": "AquaClean Station",
        "category": "water",
        "summary": "Distributed water treatment designed for communities, remote sites and temporary operations.",
        "stage": "MVP",
        "funding": "Seeking seed funding",
        "tags": ("Water", "Circular", "Infrastructure"),
        "investment_highlights": (
            "Distributed treatment model for permanent and temporary sites.",
            "MVP-stage system with infrastructure and circular-use relevance.",
        ),
        "market_opportunity": "Communities, remote sites and temporary operations require dependable local water treatment capacity.",
        "technology_solution": "A distributed station packages treatment functions into a deployable operating unit for varied sites.",
        "roadmap": ("Complete MVP validation.", "Secure pilot sites.", "Prepare repeatable site deployment."),
        "risks": ("Water conditions vary between deployment sites.", "Pilot adoption depends on reliable operation and maintenance."),
        "commercial_outlook": "Seed funding supports MVP validation and the transition to operating pilot sites.",
    },
    {
        "id": "gridwise_storage",
        "name": "GridWise Storage",
        "category": "energy",
        "summary": "Adaptive energy storage coordination for facilities balancing resilience and operating cost.",
        "stage": "Prototype",
        "funding": "Seeking technical partners",
        "tags": ("Storage", "Energy", "Control"),
        "investment_highlights": (
            "Adaptive coordination connects resilience with operating-cost control.",
            "Prototype-stage opportunity for energy and controls partners.",
        ),
        "market_opportunity": "Facilities balancing resilience and energy cost need more adaptive coordination of storage assets.",
        "technology_solution": "Control software coordinates facility storage behavior against operating and resilience priorities.",
        "roadmap": ("Validate the control prototype.", "Integrate with a partner facility.", "Measure resilience and cost outcomes."),
        "risks": ("Integration depends on compatible facility systems.", "Performance varies with operating profiles and available storage."),
        "commercial_outlook": "Technical partnerships are the immediate route to prototype integration and measured facility outcomes.",
    },
    {
        "id": "carelink_mobile",
        "name": "CareLink Mobile",
        "category": "health_biotech",
        "summary": "Field-ready diagnostic support connecting mobile care teams with specialist workflows.",
        "stage": "MVP",
        "funding": "Seeking pilot sites",
        "tags": ("Health", "Mobile", "Workflow"),
        "investment_highlights": (
            "Mobile workflow connects field teams with specialist support.",
            "MVP-stage project ready to validate with operating care sites.",
        ),
        "market_opportunity": "Mobile care teams need structured diagnostic support when specialist access is limited.",
        "technology_solution": "A field-ready mobile workflow connects frontline diagnostic activity with specialist review processes.",
        "roadmap": ("Validate the MVP workflow.", "Run a controlled care-site pilot.", "Refine integration for repeatable use."),
        "risks": ("Clinical workflows differ across pilot sites.", "Adoption depends on operator trust and appropriate governance."),
        "commercial_outlook": "Pilot-site partnerships are required to validate workflow fit before broader commercial development.",
    },
    {
        "id": "forgevision",
        "name": "ForgeVision",
        "category": "manufacturing_industry",
        "summary": "Visual quality intelligence for smaller manufacturers introducing traceable inspection.",
        "stage": "Pilot",
        "funding": "Seeking growth capital",
        "tags": ("Vision", "Quality", "AI"),
        "investment_highlights": (
            "Traceable visual inspection for smaller manufacturing operations.",
            "Pilot-stage product positioned for repeatable quality workflows.",
        ),
        "market_opportunity": "Smaller manufacturers need accessible inspection tooling that improves consistency and traceability.",
        "technology_solution": "Visual quality intelligence records inspection outcomes and supports repeatable manufacturing checks.",
        "roadmap": ("Complete pilot measurement.", "Standardize deployment workflows.", "Prepare growth across manufacturing sites."),
        "risks": ("Inspection performance depends on representative production data.", "Site variation can increase configuration effort."),
        "commercial_outlook": "Growth capital supports repeatable deployment after pilot performance is demonstrated.",
    },
    {
        "id": "terrain_rover",
        "name": "Terrain Rover",
        "category": "robotics_automation",
        "summary": "Configurable autonomous inspection for difficult industrial and infrastructure environments.",
        "stage": "Prototype",
        "funding": "Seeking development funding",
        "tags": ("Robotics", "Inspection", "Autonomy"),
        "investment_highlights": (
            "Configurable autonomous inspection for difficult environments.",
            "Prototype-stage platform with industrial and infrastructure relevance.",
        ),
        "market_opportunity": "Operators need safer and more repeatable inspection in environments that are difficult to access.",
        "technology_solution": "A configurable robotic platform combines autonomous movement with inspection workflows for varied sites.",
        "roadmap": ("Validate mobility and inspection prototype functions.", "Test in a controlled operating environment.", "Prepare an operator-led pilot."),
        "risks": ("Terrain and site conditions can affect autonomous operation.", "Deployment depends on reliable inspection performance and operator oversight."),
        "commercial_outlook": "Development funding supports prototype validation before an operator-led pilot can be pursued.",
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


def _open_marketplace_project(project_id):
    st.session_state[_MARKETPLACE_CATALOG_SNAPSHOT] = {
        MARKETPLACE_SEARCH: st.session_state.get(MARKETPLACE_SEARCH, ""),
        MARKETPLACE_CATEGORY: st.session_state.get(MARKETPLACE_CATEGORY, "all"),
        MARKETPLACE_FILTERS: st.session_state.get(MARKETPLACE_FILTERS, False),
    }
    st.session_state[MARKETPLACE_PROJECT_ID] = project_id
    st.session_state[MARKETPLACE_VIEW] = MARKETPLACE_PROJECT_DETAIL_VIEW


def _back_to_marketplace():
    catalog_state = st.session_state.get(_MARKETPLACE_CATALOG_SNAPSHOT, {})
    for key in (MARKETPLACE_SEARCH, MARKETPLACE_CATEGORY, MARKETPLACE_FILTERS):
        if key in catalog_state:
            st.session_state[key] = catalog_state[key]
    st.session_state[MARKETPLACE_VIEW] = MARKETPLACE_PROJECTS_VIEW
    st.session_state[MARKETPLACE_PROJECT_ID] = None


def get_marketplace_project(project_id, language=None):
    real_project = get_published_marketplace_project(project_id, language)
    if real_project is not None:
        return real_project
    return next(
        (project for project in _DEMO_PROJECTS if project["id"] == project_id),
        None,
    )


def get_marketplace_projects(language=None):
    real_projects = list_published_marketplace_projects(language)
    return real_projects or _DEMO_PROJECTS


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
                project.get("stage", ""),
                project.get("funding", ""),
                *project.get("tags", ()),
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
    images = project.get("project_images", ())
    if images:
        image_content = (
            f'<img src="{marketplace_image_data_uri(images[0]["image_data"])}" '
            f'alt="{safe_text(project["name"])}">'
        )
    else:
        image_content = f"<span>{_PROJECT_IMAGE_ICON}</span>"
    metadata = "".join(
        (
            (
                f"<span><strong>{safe_text(translate('marketplace.stage', language))}</strong>"
                f"{safe_text(project['stage'])}</span>"
                if project.get("stage")
                else ""
            ),
            (
                f"<span><strong>{safe_text(translate('marketplace.funding', language))}</strong>"
                f"{safe_text(project['funding'])}</span>"
                if project.get("funding")
                else ""
            ),
        )
    )
    return f"""
<div class="marketplace-card__content">
    <div class="marketplace-card__image">
        {image_content}
    </div>
    <div class="marketplace-card__identity">
        <h3>{safe_text(project['name'])}</h3>
        <p>{safe_text(category)}</p>
    </div>
    <p class="marketplace-card__summary">{safe_text(project['summary'])}</p>
    <div class="marketplace-card__meta">{metadata}</div>
    <div class="marketplace-card__tags">{tags}</div>
</div>
"""


def _render_marketplace_catalog(language):
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
        get_marketplace_projects(language),
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
                    on_click=_open_marketplace_project,
                    args=(project["id"],),
                )


def render_marketplace():
    language = get_current_language()
    if MARKETPLACE_VIEW not in st.session_state:
        st.session_state[MARKETPLACE_VIEW] = MARKETPLACE_PROJECTS_VIEW
    if MARKETPLACE_PROJECT_ID not in st.session_state:
        st.session_state[MARKETPLACE_PROJECT_ID] = None

    catalog_root = st.container(key="marketplace_catalog_root")
    project_detail_root = st.container(key="marketplace_project_detail_root")
    if st.session_state[MARKETPLACE_VIEW] == MARKETPLACE_PROJECT_DETAIL_VIEW:
        project = get_marketplace_project(
            st.session_state[MARKETPLACE_PROJECT_ID],
            language,
        )
        if project is not None:
            catalog_root.empty()
            with project_detail_root.container():
                render_marketplace_project(project, language, _back_to_marketplace)
            return
        _back_to_marketplace()

    project_detail_root.empty()
    with catalog_root.container():
        _render_marketplace_catalog(language)
