import os
import streamlit as st

from services.image_service import generate_leonardo_image_prompt, generate_blueprint_image_prompt
from services.concept_service import generate_concept
from config import CATEGORIES
from pdf_export import export_project_plan_pdf
from database import (
    init_db,
    save_concept,
    get_concepts,
    get_concept_by_id,
    delete_concept,
    save_image_asset,
    get_images_for_concept,
    delete_image_asset,
    toggle_concept_favorite,
    toggle_image_favorite,
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


def render_profile_card(selected_language):
    st.markdown(
        f"""
        <div class="profile-card">
            <h3 style="margin-top:0;">👤 User Panel</h3>
            <p style="margin-bottom:6px;"><b>Name:</b> Aleksei</p>
            <p style="margin-bottom:6px;"><b>Role:</b> Creator / Student</p>
            <p style="margin-bottom:0;"><b>Language:</b> {selected_language}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_controls():
    st.markdown("## Concept Settings")

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

    generate = st.button("✨ Generate Concept", use_container_width=True)
    regenerate = st.button("🔄 Regenerate", use_container_width=True)

    with st.expander("📦 Included in Output", expanded=False):
        st.markdown("""
        - ✅ Leonardo-style invention idea
        - ✅ Principle of operation
        - ✅ Leonardo sketch description
        - ✅ Modern implementation
        - ✅ Modern blueprint prompt
        - ✅ Market demand estimate
        - ✅ ROI analysis
        - ✅ Difficulty level
        - ✅ Development timeline
        - ✅ Materials / technologies
        - ✅ Use cases
        - ✅ Investor summary
        """)

    return category, creativity_mode, audience, user_prompt, generate, regenerate    


def render_system_status():
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

st.set_page_config(
    page_title="Leonardo AI",
    page_icon="🎨",
    layout="wide"
)

init_db()

if "leonardo_visual_asset" not in st.session_state:
    st.session_state["leonardo_visual_asset"] = None

if "blueprint_visual_asset" not in st.session_state:
    st.session_state["blueprint_visual_asset"] = None

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

# ----------------------------
# Top bar
# ----------------------------
top1, top2 = st.columns([3, 1])

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

# ----------------------------
# Layout
# ----------------------------
def generate_or_load_concept(category, creativity_mode, audience, user_prompt, generate, regenerate):
    should_generate = generate or regenerate
    concept_data = None

    if "loaded_concept" in st.session_state:
        concept_data = st.session_state["loaded_concept"]

    if should_generate:
        st.session_state["leonardo_visual_asset"] = None
        st.session_state["blueprint_visual_asset"] = None
        
        prompt_text = user_prompt.strip() if user_prompt.strip() else f"Create an invention in {category}"

        with st.spinner("Generating concept..."):
            concept_data = generate_concept(
                category=category,
                creativity_mode=creativity_mode,
                audience=audience,
                user_prompt=prompt_text,
            )

        title = concept_data["title"]

        concept_id = save_concept(
            title=title,
            category=category,
            prompt=prompt_text,
            concept_data=concept_data,
        )

        st.session_state["current_concept_id"] = concept_id

    return concept_data


def render_concept_result(concept_data):
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
        
        st.markdown("## Visual Generation")
        st.markdown(f'<div class="result-box"><b>Leonardo Sketch Prompt:</b><br>{leonardo_sketch_description}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Modern Blueprint Prompt:</b><br>{modern_sketch_description}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)

        with col1:
            generate_leonardo_image = st.button("🖼 Generate Leonardo Sketch", use_container_width=True)

        with col2:
            generate_blueprint_image = st.button("📐 Generate Modern Blueprint", use_container_width=True)
        
        if generate_leonardo_image:
            with st.spinner("Generating Leonardo sketch..."):
                try:
                    st.session_state["leonardo_visual_asset"] = generate_leonardo_image_prompt(
                        leonardo_sketch_description
                    )
                except Exception as e:
                    st.error(f"Leonardo sketch generation failed: {e}")

        if generate_blueprint_image:
            with st.spinner("Generating modern blueprint..."):
                try:
                    st.session_state["blueprint_visual_asset"] = generate_blueprint_image_prompt(
                        modern_sketch_description
                    )
                except Exception as e:
                    st.error(f"Blueprint generation failed: {e}")

        if st.session_state["leonardo_visual_asset"] or st.session_state["blueprint_visual_asset"]:
            st.markdown("## Generated Visual Assets")

            if st.session_state["leonardo_visual_asset"]:
                st.markdown(
                    '<div class="result-box"><b>Leonardo Visual Asset</b><br>Generated image based on the Renaissance sketch prompt.</div>',
                    unsafe_allow_html=True
                )
                st.image(
                    st.session_state["leonardo_visual_asset"]["image_bytes"],
                    caption="Leonardo Sketch",
                    use_container_width=True,
                )

                action1, action2, action3 = st.columns([1, 1, 6])

                with action1:
                    if st.button("⭐", key="save_leonardo_image", help="Save Leonardo image"):
                        current_concept_id = st.session_state.get("current_concept_id")

                        if current_concept_id:
                            save_image_asset(
                                concept_id=current_concept_id,
                                image_type="leonardo",
                                prompt=st.session_state["leonardo_visual_asset"]["prompt"],
                                image_bytes=st.session_state["leonardo_visual_asset"]["image_bytes"],
                            )
                            st.success("Saved.")
                        else:
                            st.error("No concept selected.")

                with action2:
                    if st.button("🗑", key="clear_leonardo_asset", help="Clear Leonardo asset"):
                        st.session_state["leonardo_visual_asset"] = None
                        st.rerun()

                with action3:
                    with st.expander("Prompt"):
                        st.code(st.session_state["leonardo_visual_asset"]["prompt"], language="text")

            if st.session_state["blueprint_visual_asset"]:
                st.markdown(
                    '<div class="result-box"><b>Blueprint Visual Asset</b><br>Generated image based on the modern blueprint prompt.</div>',
                    unsafe_allow_html=True
                )
                st.image(
                    st.session_state["blueprint_visual_asset"]["image_bytes"],
                    caption="Modern Blueprint",
                    use_container_width=True,
                )

                action1, action2, action3 = st.columns([1, 1, 6])

                with action1:
                    if st.button("⭐", key="save_blueprint_image", help="Save Blueprint image"):
                        current_concept_id = st.session_state.get("current_concept_id")

                        if current_concept_id:
                            save_image_asset(
                                concept_id=current_concept_id,
                                image_type="blueprint",
                                prompt=st.session_state["blueprint_visual_asset"]["prompt"],
                                image_bytes=st.session_state["blueprint_visual_asset"]["image_bytes"],
                            )
                            st.success("Saved.")
                        else:
                            st.error("No concept selected.")

                with action2:
                    if st.button("🗑", key="clear_blueprint_asset", help="Clear Blueprint asset"):
                        st.session_state["blueprint_visual_asset"] = None
                        st.rerun()

                with action3:
                    with st.expander("Prompt"):
                        st.code(st.session_state["blueprint_visual_asset"]["prompt"], language="text")
        
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
            current_concept_id = st.session_state.get("current_concept_id")
            saved_images = get_images_for_concept(current_concept_id) if current_concept_id else []

            export_project_plan_pdf(
                concept_data,
                pdf_filename,
                saved_images=saved_images
            )

            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf",
                )

        render_saved_images()


def render_saved_images():
    st.markdown("## Saved Images")

    current_concept_id = st.session_state.get("current_concept_id")

    if not current_concept_id:
        st.info("No concept selected.")
        return

    images = get_images_for_concept(current_concept_id)

    if not images:
        st.info("No saved images yet.")
        return

    cols = st.columns(2)

    for idx, image in enumerate(images):
        image_id = image[0]
        image_type = image[1]
        prompt = image[2]
        image_bytes = image[3]
        created_at = image[4]
        is_favorite = image[5]

        with cols[idx % 2]:
            star_prefix = "⭐ " if is_favorite else ""
            st.markdown(f"### {star_prefix}{image_type.capitalize()}")

            st.image(
                image_bytes,
                caption=f"{image_type.capitalize()}",
                use_container_width=True
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_image_{image_id}"):
                    toggle_image_favorite(image_id)
                    st.rerun()

            with col2:
                if st.button("Delete", key=f"delete_image_{image_id}"):
                    delete_image_asset(image_id)
                    st.rerun()

            with col3:
                st.download_button(
                    label="Download",
                    data=image_bytes,
                    file_name=f"{image_type}_{image_id}.png",
                    mime="image/png",
                    key=f"download_image_{image_id}"
                )


def render_previous_concepts():
    st.markdown("## Previous Concepts")

    concepts = get_concepts()

    if concepts:
        for concept_id, saved_title, saved_category, created_at, is_favorite in concepts:
            col1, col2, col3 = st.columns([5, 1, 1])

            with col1:
                if st.button(
                    f"Open: {saved_title} ({saved_category}) — {created_at}",
                    key=f"open_{concept_id}"
                ):
                    selected_concept = get_concept_by_id(concept_id)

                    if selected_concept:
                        st.session_state["loaded_concept"] = selected_concept
                        st.session_state["current_concept_id"] = concept_id
                        st.rerun()

            with col2:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_{concept_id}"):
                    toggle_concept_favorite(concept_id)
                    st.rerun()

            with col3:
                if st.button("🗑", key=f"delete_{concept_id}"):
                    delete_concept(concept_id)

                    if (
                        "loaded_concept" in st.session_state
                        and st.session_state["loaded_concept"]
                        and st.session_state["loaded_concept"].get("title") == saved_title
                    ):
                        st.session_state["loaded_concept"] = None

                    st.rerun()
    else:
        st.info("No saved concepts yet.")


left, right = st.columns([1, 2])

with left:
    render_profile_card(selected_language)
    category, creativity_mode, audience, user_prompt, generate, regenerate = render_controls()

with right:
    st.markdown("## About the System")
    st.write(
        "Leonardo AI generates invention concepts inspired by Renaissance engineering and "
        "translates them into modern product ideas with practical commercial potential."
    )

    st.info(
        "Generate structured invention concepts inspired by Renaissance thinking and adapted "
        "for modern engineering, product strategy, and commercial evaluation."
    )

    render_system_status()

    concept_data = generate_or_load_concept(
        category,
        creativity_mode,
        audience,
        user_prompt,
        generate,
        regenerate,
    )

    if concept_data:
        render_concept_result(concept_data)

    render_previous_concepts()


