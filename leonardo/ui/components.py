import streamlit as st

from i18n import translate
from ui.formatting import safe_list, safe_text
from ui.state import get_current_language


def render_result_box(title, content, extra_bottom_spacing=False):
    spacing_class = " result-box--control-gap" if extra_bottom_spacing else ""

    st.markdown(
        f"""
<div class="result-box{spacing_class}">
    <div class="result-title">{safe_text(title)}</div>
    <div class="result-text">{safe_list(content)}</div>
</div>
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


def render_complete_guide(stage_name, guide):
    language = get_current_language()
    with st.expander(translate("guide.complete", language, stage=stage_name)):
        st.subheader(f"🧭 {translate('guide.execution_plan', language)}")
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

        st.subheader(f"🏗 {translate('guide.technical_architecture', language)}")
        st.write(f"**{translate('guide.system_schema', language)}**", guide.get("technical_architecture", {}).get("system_schema", ""))
        st.write(f"**{translate('guide.module_interaction', language)}**", guide.get("technical_architecture", {}).get("module_interaction", ""))
        st.write(f"**{translate('guide.process_flow', language)}**", guide.get("technical_architecture", {}).get("process_flow", ""))
        st.write(f"**{translate('guide.deployment_logic', language)}**", guide.get("technical_architecture", {}).get("deployment_logic", ""))

        st.subheader(f"💰 {translate('guide.resources_budget', language)}")
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

        st.subheader(f"✅ {translate('guide.validation', language)}")
        st.write(f"**{translate('guide.tests', language)}**")
        for item in guide.get("validation", {}).get("tests", []):
            st.write("•", item)

        st.write(f"**{translate('guide.kpi', language)}**")
        for item in guide.get("validation", {}).get("kpi", []):
            st.write("•", item)

        st.write(f"**{translate('guide.success_criteria', language)}**")
        for item in guide.get("validation", {}).get("success_criteria", []):
            st.write("•", item)
