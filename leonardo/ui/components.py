import streamlit as st

from i18n import translate
from ui.formatting import safe_list, safe_text
from ui.state import get_current_language


_ROADMAP_SUBHEADING_ICONS = {
    "execution": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="5" cy="18" r="2"/><circle cx="19" cy="6" r="2"/><path d="M7 18h3a4 4 0 0 0 4-4v-4a4 4 0 0 1 4-4h-1M10 14l4 4M14 14l-4 4"/></svg>""",
    "architecture": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 18h18M5 18l2-8h10l2 8M8 10V7h8v3M12 3v4M9 22h6M12 18v4"/></svg>""",
    "resources": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><ellipse cx="9" cy="7" rx="5" ry="2.5"/><path d="M4 7v4c0 1.4 2.2 2.5 5 2.5s5-1.1 5-2.5V7M4 11v4c0 1.4 2.2 2.5 5 2.5 1.1 0 2.1-.2 3-.5"/><ellipse cx="16" cy="16" rx="4" ry="2"/><path d="M12 16v3c0 1.1 1.8 2 4 2s4-.9 4-2v-3"/></svg>""",
    "validation": """<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3 20 6v6c0 4.8-3.1 7.7-8 9-4.9-1.3-8-4.2-8-9V6l8-3Z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></svg>""",
}


def _render_roadmap_subheading(title, icon_name):
    st.markdown(
        f"""
<h3 class="roadmap-subheading">
    <span class="roadmap-subheading__icon">{_ROADMAP_SUBHEADING_ICONS[icon_name]}</span>
    {safe_text(title)}
</h3>
""",
        unsafe_allow_html=True,
    )


def render_result_box(
    title,
    content,
    extra_bottom_spacing=False,
    icon_svg=None,
    visual_variant=None,
):
    spacing_class = " result-box--control-gap" if extra_bottom_spacing else ""
    variant_class = (
        f" result-box--{visual_variant}"
        if visual_variant in {"blue", "risk", "constraint"}
        else ""
    )
    title_icon = (
        f'<span class="result-title-icon">{icon_svg}</span>' if icon_svg else ""
    )

    st.markdown(
        f"""
<div class="result-box{spacing_class}{variant_class}">
    <div class="result-title">{title_icon}{safe_text(title)}</div>
    <div class="result-text">{safe_list(content)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_generated_section_heading(title, icon_svg):
    st.markdown(
        f"""
<h2 class="generated-section-heading">
    <span class="generated-section-heading__icon">{icon_svg}</span>
    {safe_text(title)}
</h2>
""",
        unsafe_allow_html=True,
    )


def render_section_heading(title):
    st.markdown(
        f"""
<div class="section-heading">{safe_text(title)}</div>
<div class="heading-rule"></div>
""",
        unsafe_allow_html=True,
    )


def render_complete_guide(stage_name, guide, key=None):
    language = get_current_language()
    with st.expander(
        translate("guide.complete", language, stage=stage_name),
        key=key,
    ):
        _render_roadmap_subheading(
            translate("guide.execution_plan", language),
            "execution",
        )
        st.write(f"**{translate('guide.goal', language)}**", guide.get("execution_plan", {}).get("goal", ""))

        st.write(f"**{translate('guide.steps', language)}**")
        for step in guide.get("execution_plan", {}).get("steps", []):
            st.write("•", step)

        st.write(f"**{translate('guide.specialists', language)}**")
        for sp in guide.get("execution_plan", {}).get("specialists", []):
            st.write("•", sp)

        st.write(f"**{translate('guide.technologies', language)}**")
        for tech in guide.get("execution_plan", {}).get("technologies", []):
            st.write("•", tech)

        budget = guide.get("execution_plan", {}).get("estimated_budget")
        if budget:
            st.write(f"**{translate('guide.estimated_budget', language)}**", budget)

        st.write(f"**{translate('guide.stage_risks', language)}**")
        for risk in guide.get("execution_plan", {}).get("stage_risks", []):
            st.write("•", risk)

        st.write(f"**{translate('guide.readiness', language)}**")
        for rc in guide.get("execution_plan", {}).get("readiness_criteria", []):
            st.write("•", rc)

        expected_output = guide.get("execution_plan", {}).get("expected_output")
        if isinstance(expected_output, list):
            st.write(f"**{translate('guide.expected_output', language)}**")
            for out in expected_output:
                st.write("•", out)
        elif expected_output:
            st.write(f"**{translate('guide.expected_output', language)}**", expected_output)

        _render_roadmap_subheading(
            translate("guide.technical_architecture", language),
            "architecture",
        )
        st.write(f"**{translate('guide.system_schema', language)}**", guide.get("technical_architecture", {}).get("system_schema", ""))
        st.write(f"**{translate('guide.module_interaction', language)}**", guide.get("technical_architecture", {}).get("module_interaction", ""))
        st.write(f"**{translate('guide.process_flow', language)}**", guide.get("technical_architecture", {}).get("process_flow", ""))
        st.write(f"**{translate('guide.deployment_logic', language)}**", guide.get("technical_architecture", {}).get("deployment_logic", ""))

        _render_roadmap_subheading(
            translate("guide.resources_budget", language),
            "resources",
        )
        st.write(f"**{translate('guide.team', language)}**")
        for item in guide.get("resources_budget", {}).get("team", []):
            st.write("•", item)

        st.write(f"**{translate('guide.stack', language)}**")
        for item in guide.get("resources_budget", {}).get("stack", []):
            st.write("•", item)

        st.write(f"**{translate('guide.materials', language)}**")
        for item in guide.get("resources_budget", {}).get("materials", []):
            st.write("•", item)

        cost_notes = guide.get("resources_budget", {}).get("cost_notes")
        if cost_notes:
            st.write(f"**{translate('guide.cost_notes', language)}**", cost_notes)

        _render_roadmap_subheading(
            translate("guide.validation", language),
            "validation",
        )
        st.write(f"**{translate('guide.tests', language)}**")
        for item in guide.get("validation", {}).get("tests", []):
            st.write("•", item)

        st.write(f"**{translate('guide.kpi', language)}**")
        for item in guide.get("validation", {}).get("kpi", []):
            st.write("•", item)

        st.write(f"**{translate('guide.success_criteria', language)}**")
        for item in guide.get("validation", {}).get("success_criteria", []):
            st.write("•", item)
