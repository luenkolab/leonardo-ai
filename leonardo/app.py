import os
import streamlit as st
import json

from database import init_db, save_concept, get_concepts, get_concept_by_id, delete_concept
from services.concept_service import generate_concept
from config import CATEGORIES, DIFFICULTY, MATERIALS, USE_CASES
from utils import generate_dev_time, generate_investor_summary
from pdf_export import export_project_plan_pdf
from database import get_concept_by_id

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

        st.write("**System Schema:**",
            guide.get("technical_architecture", {}).get("system_schema", ""))

        st.write("**Module Interaction:**",
            guide.get("technical_architecture", {}).get("module_interaction", ""))

        st.write("**Process Flow:**",
            guide.get("technical_architecture", {}).get("process_flow", ""))

        st.write("**Deployment Logic:**",
            guide.get("technical_architecture", {}).get("deployment_logic", ""))


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

st.set_page_config(
    page_title="Leonardo AI",
    page_icon="🎨",
    layout="wide"
)

init_db()

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 8px;
        color: #f9fafb;
    }
    .subtitle {
        font-size: 18px;
        color: #9ca3af;
        margin-bottom: 20px;
    }
    .topbar {
        background: linear-gradient(90deg, #111827, #1f2937);
        border: 1px solid #374151;
        border-radius: 18px;
        padding: 18px 22px;
        margin-bottom: 18px;
    }
    .topbar-title {
        font-size: 26px;
        font-weight: 700;
        color: #f9fafb;
        margin-bottom: 4px;
    }
    .topbar-subtitle {
        font-size: 14px;
        color: #9ca3af;
    }
    .profile-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
        color: white;
    }
    .feature-box {
        padding: 14px;
        border-radius: 12px;
        background-color: #1f2937;
        border: 1px solid #374151;
        margin-bottom: 10px;
        color: white;
    }
    .result-box {
        padding: 18px;
        border-radius: 16px;
        background-color: #f8fafc;
        border: 1px solid #d1d5db;
        margin-top: 12px;
        margin-bottom: 12px;
        color: #111827;
    }
    .status-good {
        padding: 10px 14px;
        border-radius: 10px;
        background: #052e16;
        border: 1px solid #166534;
        color: #dcfce7;
        margin-bottom: 8px;
    }
    .status-warn {
        padding: 10px 14px;
        border-radius: 10px;
        background: #3f2a00;
        border: 1px solid #92400e;
        color: #fde68a;
        margin-bottom: 8px;
    }
    .mini-card {
        padding: 14px;
        border-radius: 14px;
        background: #111827;
        border: 1px solid #374151;
        color: white;
        margin-bottom: 10px;
    }
    .small-note {
        font-size: 13px;
        color: #9ca3af;
        margin-top: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Helpers
# ----------------------------

# ----------------------------
# Session state
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ----------------------------
# Top bar
# ----------------------------
top1, top2, top3 = st.columns([2, 1, 1])

with top1:
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-title">🎨 Leonardo AI</div>
            <div class="topbar-subtitle">
                Renaissance Invention Generator with Modern Engineering Analysis
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with top2:
    selected_language = st.selectbox(
        "Language",
        ["English", "Русский", "Svenska"],
        index=0
    )

with top3:
    app_mode = st.selectbox(
        "Mode",
        ["Demo", "Presentation", "Prototype"],
        index=2
    )

# ----------------------------
# Layout
# ----------------------------
left, right = st.columns([1, 2])

with left:
    st.markdown(
        """
        <div class="profile-card">
            <h3 style="margin-top:0;">👤 User Panel</h3>
            <p style="margin-bottom:6px;"><b>Name:</b> Aleksei</p>
            <p style="margin-bottom:6px;"><b>Role:</b> Creator / Student</p>
            <p style="margin-bottom:0;"><b>Language:</b> Selected above</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## Project Controls")

    category = st.selectbox(
    "Choose invention category",
    CATEGORIES
    )

    creativity_mode = st.selectbox(
        "Creativity mode",
        ["Classic", "Bold", "Experimental"]
    )

    audience = st.selectbox(
        "Target audience",
        ["Engineers", "Investors", "Students", "General Public"]
    )

    user_prompt = st.text_area(
        "Prompt / Idea",
        placeholder="Example: Create a Renaissance-inspired rescue glider for dangerous mountain missions...",
        height=120
    )

    st.markdown("### 🎤 Voice Prompt")
    st.button("🎙 Start Voice Prompt", use_container_width=True)
    st.caption("Demo UI ready. Real speech-to-text transcription can be connected later.")

    st.markdown("### AI Modules")
    image_module = st.toggle("Enable image generation concept", value=True)
    blueprint_module = st.toggle("Enable blueprint concept", value=True)
    voice_module = st.toggle("Enable voice assistant concept", value=True)

    generate = st.button("✨ Generate Full Concept", use_container_width=True)
    regenerate = st.button("🔄 Generate Again", use_container_width=True)

    st.markdown("## Included in Output")
    st.markdown(
        """
        <div class="feature-box">✅ Leonardo-style invention idea</div>
        <div class="feature-box">✅ Principle of operation</div>
        <div class="feature-box">✅ Leonardo sketch description</div>
        <div class="feature-box">✅ Modern implementation</div>
        <div class="feature-box">✅ Modern sketch description</div>
        <div class="feature-box">✅ Market demand estimate</div>
        <div class="feature-box">✅ ROI analysis</div>
        <div class="feature-box">✅ Difficulty level</div>
        <div class="feature-box">✅ Development timeline</div>
        <div class="feature-box">✅ Materials / technologies</div>
        <div class="feature-box">✅ Use cases</div>
        <div class="feature-box">✅ Investor summary</div>
        <div class="feature-box">✅ Voice assistant interaction concept</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="small-note">For CS50 submission, core logic remains in project.py. Production mode uses OpenAI when API key is available.</div>',
        unsafe_allow_html=True
    )

with right:
    st.markdown("## About the System")
    st.write(
        "Leonardo AI generates invention concepts inspired by Renaissance engineering and "
        "translates them into modern product ideas with practical commercial potential."
    )

    st.info(
        "Use this app to demonstrate creative engineering thinking, concept generation, "
        "and product presentation for your final project and future product development."
    )

    st.markdown("## System Status")
    st.markdown('<div class="status-good">✅ Core Logic: Active</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-good">✅ Interface Layer: Active</div>', unsafe_allow_html=True)

    if os.getenv("OPENAI_API_KEY"):
        st.markdown('<div class="status-good">✅ OpenAI Integration: Active</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="status-warn">🟡 OpenAI Integration: Not detected, fallback mode will be used</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="status-warn">🟡 Voice Prompt Transcription: Demo UI only (speech-to-text not connected yet)</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="status-good">✅ Image Module: Concept Ready</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-good">✅ Blueprint Engine: Concept Ready</div>', unsafe_allow_html=True)

    should_generate = generate or regenerate

    concept_data = None

    if "loaded_concept" in st.session_state:
        concept_data = st.session_state["loaded_concept"]
    
    if should_generate:
        prompt_text = user_prompt.strip() if user_prompt.strip() else f"Create an invention in {category}"

        with st.spinner("Generating concept..."):
            concept_data = generate_concept(
                category=category,
                creativity_mode=creativity_mode,
                audience=audience,
                user_prompt=prompt_text,
            )

        title = concept_data["title"]

        save_concept(
            title=title,
            category=category,
            prompt=prompt_text,
            concept_data=concept_data,
        )
        
    if concept_data:
        title = concept_data["title"]

        leonardo_concept = concept_data["leonardo_concept"]
        leonardo_sketch_description = concept_data["leonardo_sketch_description"]

        modern_product_name = concept_data["modern_product_name"]
        modern_category = concept_data["modern_category"]
        executive_summary = concept_data["executive_summary"]

        problem_statement = concept_data["problem_statement"]
        target_users = concept_data["target_users"]
        industries = concept_data["industries"]
        use_cases = concept_data["use_cases"]

        modern_principle = concept_data["modern_principle"]
        system_components = concept_data["system_components"]
        materials = concept_data["materials"]
        technical_requirements = concept_data["technical_requirements"]
        modern_sketch_description = concept_data["modern_sketch_description"]

        implementation_roadmap = concept_data["implementation_roadmap"]
        implementation_guides = concept_data["implementation_guides"]
        deployment_strategy = concept_data["deployment_strategy"]

        risks = concept_data["risks"]
        constraints = concept_data["constraints"]

        market_demand = concept_data["market_demand"]
        startup_cost = concept_data["startup_cost"]
        roi = concept_data["roi"]
        investor_summary = concept_data["investor_summary"]

        difficulty = concept_data["difficulty"]
        modern_difficulty = concept_data["modern_difficulty"]
        dev_time = concept_data["dev_time"]

        st.success("Concept generated successfully.")

        st.markdown("## Leonardo Inspiration")
        st.markdown(f'<div class="result-box"><b>Concept:</b><br>{leonardo_concept}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Sketch Description:</b><br>{leonardo_sketch_description}</div>', unsafe_allow_html=True)

        st.markdown("## Modern Product Definition")
        st.markdown(f'<div class="result-box"><b>Title:</b><br>{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Product Name:</b><br>{modern_product_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Category:</b><br>{modern_category}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Executive Summary:</b><br>{executive_summary}</div>', unsafe_allow_html=True)

        st.markdown("## Business Need")
        st.markdown(f'<div class="result-box"><b>Problem Statement:</b><br>{problem_statement}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Target Users:</b><br>' + "<br>• ".join([""] + target_users) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Industries:</b><br>' + "<br>• ".join([""] + industries) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Use Cases:</b><br>' + "<br>• ".join([""] + use_cases) + '</div>', unsafe_allow_html=True)

        st.markdown("## Engineering")
        st.markdown(f'<div class="result-box"><b>Modern Principle:</b><br>{modern_principle}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>System Components:</b><br>' + "<br>• ".join([""] + system_components) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Materials:</b><br>' + "<br>• ".join([""] + materials) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Technical Requirements:</b><br>' + "<br>• ".join([""] + technical_requirements) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Modern Sketch Description:</b><br>{modern_sketch_description}</div>', unsafe_allow_html=True)

        st.markdown("## Implementation Roadmap")
        render_complete_guide("Prototype", implementation_guides["prototype"])
        render_complete_guide("MVP", implementation_guides["mvp"])
        render_complete_guide("Pilot", implementation_guides["pilot"])
        render_complete_guide("Production", implementation_guides["production"])

        st.markdown(f'<div class="result-box"><b>Deployment Strategy:</b><br>{deployment_strategy}</div>', unsafe_allow_html=True)

        st.markdown("## Risks and Constraints")
        st.markdown(f'<div class="result-box"><b>Risks:</b><br>' + "<br>• ".join([""] + risks) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Constraints:</b><br>' + "<br>• ".join([""] + constraints) + '</div>', unsafe_allow_html=True)

        st.markdown("## Commercial Outlook")
        st.markdown(f'<div class="result-box"><b>Market Demand:</b><br>{market_demand}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Startup Cost:</b><br>{startup_cost}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>ROI:</b><br>{roi}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Investor Summary:</b><br>{investor_summary}</div>', unsafe_allow_html=True)

        st.markdown("## Delivery Metrics")
        st.markdown(f'<div class="result-box"><b>Concept Difficulty:</b><br>{difficulty}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Modern Difficulty:</b><br>{modern_difficulty}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Development Time:</b><br>{dev_time}</div>', unsafe_allow_html=True)

        pdf_filename = f"{title.replace(' ', '_')}.pdf"

        if st.button("📄 Export Full Project Plan (PDF)", key="export_pdf_loaded"):
            export_project_plan_pdf(concept_data, pdf_filename)

            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf",
                )
        
        if not image_module:
            image_concept = "Image generation concept is currently disabled."
        if not blueprint_module:
            blueprint_concept = "Blueprint concept is currently disabled."
        if not voice_module:
            voice_assistant_concept = "Voice assistant module is currently disabled."

        if creativity_mode == "Bold":
            extra_note = "This concept emphasizes disruptive innovation and stronger commercial appeal."
        elif creativity_mode == "Experimental":
            extra_note = "This concept emphasizes unusual engineering ideas and speculative future applications."
        else:
            extra_note = "This concept stays close to classical engineering logic and historical inspiration."

        if audience == "Investors":
            audience_note = "Presentation focus: scalability, profitability, and market opportunity."
        elif audience == "Engineers":
            audience_note = "Presentation focus: mechanism design, functionality, materials, and architecture."
        elif audience == "Students":
            audience_note = "Presentation focus: clarity, learning value, and simple explanation."
        else:
            audience_note = "Presentation focus: accessibility, visual appeal, and easy understanding."

        st.session_state.history.insert(0, {"title": title, "category": category})
        st.session_state.history = st.session_state.history[:5]

        st.success("Concept generated successfully.")

        st.markdown("## Leonardo Inspiration")
        st.markdown(f'<div class="result-box"><b>Concept:</b><br>{leonardo_concept}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Sketch Description:</b><br>{leonardo_sketch_description}</div>', unsafe_allow_html=True)

        st.markdown("## Modern Product Definition")
        st.markdown(f'<div class="result-box"><b>Title:</b><br>{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Product Name:</b><br>{modern_product_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Category:</b><br>{modern_category}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Executive Summary:</b><br>{executive_summary}</div>', unsafe_allow_html=True)

        st.markdown("## Business Need")
        st.markdown(f'<div class="result-box"><b>Problem Statement:</b><br>{problem_statement}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Target Users:</b><br>' + "<br>• ".join([""] + target_users) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Industries:</b><br>' + "<br>• ".join([""] + industries) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Use Cases:</b><br>' + "<br>• ".join([""] + use_cases) + '</div>', unsafe_allow_html=True)

        st.markdown("## Engineering")
        st.markdown(f'<div class="result-box"><b>Modern Principle:</b><br>{modern_principle}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>System Components:</b><br>' + "<br>• ".join([""] + system_components) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Materials:</b><br>' + "<br>• ".join([""] + materials) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Technical Requirements:</b><br>' + "<br>• ".join([""] + technical_requirements) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Modern Sketch Description:</b><br>{modern_sketch_description}</div>', unsafe_allow_html=True)

        st.markdown("## Implementation Roadmap")

        render_complete_guide("Prototype", implementation_guides["prototype"])
        render_complete_guide("MVP", implementation_guides["mvp"])
        render_complete_guide("Pilot", implementation_guides["pilot"])
        render_complete_guide("Production", implementation_guides["production"])

        st.markdown(f'<div class="result-box"><b>Deployment Strategy:</b><br>{deployment_strategy}</div>', unsafe_allow_html=True)

        st.markdown("## Risks and Constraints")
        st.markdown(f'<div class="result-box"><b>Risks:</b><br>' + "<br>• ".join([""] + risks) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Constraints:</b><br>' + "<br>• ".join([""] + constraints) + '</div>', unsafe_allow_html=True)

        st.markdown("## Commercial Outlook")
        st.markdown(f'<div class="result-box"><b>Market Demand:</b><br>{market_demand}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Startup Cost:</b><br>{startup_cost}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>ROI:</b><br>{roi}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Investor Summary:</b><br>{investor_summary}</div>', unsafe_allow_html=True)

        st.markdown("## Delivery Metrics")
        st.markdown(f'<div class="result-box"><b>Concept Difficulty:</b><br>{difficulty}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Modern Difficulty:</b><br>{modern_difficulty}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Development Time:</b><br>{dev_time}</div>', unsafe_allow_html=True)
        
        pdf_filename = f"{title.replace(' ', '_')}.pdf"

        if st.button("📄 Export Full Project Plan (PDF)", key="export_pdf_main"):
            export_project_plan_pdf(concept_data, pdf_filename)

            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf",
                )
        
    st.markdown("## Previous Concepts")

    concepts = get_concepts()

    if concepts:
        for concept_id, saved_title, saved_category, created_at in concepts:
            col1, col2 = st.columns([5, 1])

            with col1:
                if st.button(f"Open: {saved_title} ({saved_category}) — {created_at}"):

                    selected_concept = get_concept_by_id(concept_id)

                    if selected_concept:
                        concept_data = selected_concept
                        st.session_state["loaded_concept"] = concept_data
                        st.rerun()

                        