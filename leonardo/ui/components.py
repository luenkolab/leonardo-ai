import streamlit as st

from ui.formatting import safe_list, safe_text


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
    with st.expander(f"Complete Guide: {stage_name}"):
        st.subheader("🧭 Execution Plan")
        st.write("**Goal:**", guide.get("execution_plan", {}).get("goal", ""))

        st.write("**Steps:**")
        for step in guide.get("execution_plan", {}).get("steps", []):
            st.write("•", step)

        st.write("**Specialists:**")
        for sp in guide.get("execution_plan", {}).get("specialists", []):
            st.write("•", sp)

        st.write("**Technologies:**")
        for tech in guide.get("execution_plan", {}).get("technologies", []):
            st.write("•", tech)

        budget = guide.get("execution_plan", {}).get("estimated_budget")
        if budget:
            st.write("**Estimated Budget:**", budget)

        st.write("**Stage Risks:**")
        for risk in guide.get("execution_plan", {}).get("stage_risks", []):
            st.write("•", risk)

        st.write("**Readiness Criteria:**")
        for rc in guide.get("execution_plan", {}).get("readiness_criteria", []):
            st.write("•", rc)

        expected_output = guide.get("execution_plan", {}).get("expected_output")
        if isinstance(expected_output, list):
            st.write("**Expected Output:**")
            for out in expected_output:
                st.write("•", out)
        elif expected_output:
            st.write("**Expected Output:**", expected_output)

        st.subheader("🏗 Technical Architecture")
        st.write("**System Schema:**", guide.get("technical_architecture", {}).get("system_schema", ""))
        st.write("**Module Interaction:**", guide.get("technical_architecture", {}).get("module_interaction", ""))
        st.write("**Process Flow:**", guide.get("technical_architecture", {}).get("process_flow", ""))
        st.write("**Deployment Logic:**", guide.get("technical_architecture", {}).get("deployment_logic", ""))

        st.subheader("💰 Resources & Budget")
        st.write("**Team:**")
        for item in guide.get("resources_budget", {}).get("team", []):
            st.write("•", item)

        st.write("**Stack:**")
        for item in guide.get("resources_budget", {}).get("stack", []):
            st.write("•", item)

        st.write("**Materials:**")
        for item in guide.get("resources_budget", {}).get("materials", []):
            st.write("•", item)

        cost_notes = guide.get("resources_budget", {}).get("cost_notes")
        if cost_notes:
            st.write("**Cost Notes:**", cost_notes)

        st.subheader("✅ Validation")
        st.write("**Tests:**")
        for item in guide.get("validation", {}).get("tests", []):
            st.write("•", item)

        st.write("**KPI:**")
        for item in guide.get("validation", {}).get("kpi", []):
            st.write("•", item)

        st.write("**Success Criteria:**")
        for item in guide.get("validation", {}).get("success_criteria", []):
            st.write("•", item)
