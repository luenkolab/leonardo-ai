# ----------------------------
# Imports
# ----------------------------

import os
import streamlit as st
import streamlit.components.v1 as components
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


def render_profile_card():
    concepts = get_concepts()
    total_concepts = len(concepts)
    favorite_concepts = sum(1 for item in concepts if item[4])

    current_concept_id = st.session_state.get("current_concept_id")
    saved_images = get_images_for_concept(current_concept_id) if current_concept_id else []
    total_images = len(saved_images)

    st.markdown(
        f"""<div class="profile-card">
<div class="profile-top">
    <div class="profile-avatar">🧠</div>
    <div class="profile-role-badge">Creator / Student</div>
</div>
<div class="profile-name">Aleksei</div>
<div class="profile-meta">Building Renaissance-inspired invention systems for modern product thinking.</div>
<div class="profile-stats-grid">
    <div class="profile-stat-box">
        <div class="profile-stat-label">Saved Concepts</div>
        <div class="profile-stat-value">{total_concepts}</div>
    </div>
    <div class="profile-stat-box">
        <div class="profile-stat-label">Favorites</div>
        <div class="profile-stat-value">{favorite_concepts}</div>
    </div>
    <div class="profile-stat-box">
        <div class="profile-stat-label">Saved Images</div>
        <div class="profile-stat-value">{total_images}</div>
    </div>
</div>
</div>""",
        unsafe_allow_html=True
    )


def render_topbar_menu():
    if "show_topbar_menu" not in st.session_state:
        st.session_state["show_topbar_menu"] = False

    if st.button("⋮", key="topbar_menu_button", help="Interface"):
        st.session_state["show_topbar_menu"] = not st.session_state["show_topbar_menu"]

    if st.session_state["show_topbar_menu"]:
        st.markdown('<div class="topbar-menu-panel">', unsafe_allow_html=True)

        selected_language = st.selectbox(
            "Language",
            ["English", "Русский", "Svenska"],
            index=["English", "Русский", "Svenska"].index(
                st.session_state.get("selected_language", "English")
            ),
            key="selected_language_menu"
        )

        theme_mode = st.selectbox(
            "Theme style",
            ["Leonardo Dark", "Midnight Blue", "Warm Sepia"],
            index=["Leonardo Dark", "Midnight Blue", "Warm Sepia"].index(
                st.session_state.get("theme_mode", "Leonardo Dark")
            ),
            key="theme_mode_menu"
        )

        st.session_state["selected_language"] = selected_language
        st.session_state["theme_mode"] = theme_mode

        st.markdown("</div>", unsafe_allow_html=True)


def render_topbar_menu_button():
    if st.button("⋮", key="topbar_menu_toggle", help="Interface settings"):
        st.session_state["show_topbar_menu"] = not st.session_state["show_topbar_menu"]
        st.rerun()


def render_controls():
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Leonardo Control</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-group-title">⚙️ Concept Settings</div>', unsafe_allow_html=True)

        category = st.selectbox(
            "Invention category",
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
            placeholder="Create a Renaissance-inspired rescue glider for dangerous mountain missions...",
            height=140
        )

        render_voice_prompt()

        st.markdown('<div class="sidebar-group-title">🚀 Actions</div>', unsafe_allow_html=True)

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
            '<div class="status-warn">🟡 OpenAI Integration: Not detected — fallback mode will be used</div>',
            unsafe_allow_html=True
        )


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


def render_voice_assistant(concept_data):
    st.markdown("## 🧠 Voice Assistant")

    title = concept_data.get("title", "")
    executive_summary = concept_data.get("executive_summary", "")
    market_demand = concept_data.get("market_demand", "")
    investor_summary = concept_data.get("investor_summary", "")
    modern_principle = concept_data.get("modern_principle", "")

    voice_language = st.selectbox(
        "Voice language",
        ["English", "Русский"],
        key="voice_language_selector"
    )

    if voice_language == "Русский":
        summary_text = (
            f"Название проекта: {title}. "
            f"Краткое описание: {executive_summary}. "
            f"Рыночный спрос: {market_demand}. "
            f"Инвесторское резюме: {investor_summary}."
        )

        investor_text = (
            f"Инвесторская презентация проекта {title}. "
            f"{investor_summary}. "
            f"Рыночный спрос: {market_demand}."
        )

        engineering_text = (
            f"Инженерный обзор проекта {title}. "
            f"{modern_principle}."
        )

        speech_lang = "ru-RU"

    else:
        summary_text = (
            f"Project title: {title}. "
            f"Executive summary: {executive_summary}. "
            f"Market demand: {market_demand}. "
            f"Investor summary: {investor_summary}."
        )

        investor_text = (
            f"Investor pitch. {title}. "
            f"{investor_summary}. "
            f"Market demand: {market_demand}."
        )

        engineering_text = (
            f"Engineering overview for {title}. "
            f"{modern_principle}."
        )

        speech_lang = "en-US"

    top1, top2, top3 = st.columns(3)

    with top1:
        play_summary = st.button("▶ Summary", key="voice_summary", use_container_width=True)

    with top2:
        play_investor = st.button("🎧 Investor", key="voice_investor", use_container_width=True)

    with top3:
        play_engineering = st.button("⚙ Engineering", key="voice_engineering", use_container_width=True)

    bottom1, bottom2, bottom3 = st.columns(3)

    with bottom1:
        pause_voice = st.button("⏸ Pause", key="voice_pause", use_container_width=True)

    with bottom2:
        resume_voice = st.button("▶ Resume", key="voice_resume", use_container_width=True)

    with bottom3:
        stop_voice = st.button("⏹ Stop", key="voice_stop", use_container_width=True)

    def speak(text, lang):
        escaped = (
            text.replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace('"', '\\"')
            .replace("\n", " ")
        )

        components.html(
            f"""
            <script>
                const text = "{escaped}";
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                utterance.lang = "{lang}";
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utterance);
            </script>
            """,
            height=0,
        )

    if play_summary:
        speak(summary_text, speech_lang)

    if play_investor:
        speak(investor_text, speech_lang)

    if play_engineering:
        speak(engineering_text, speech_lang)

    if pause_voice:
        components.html(
            """
            <script>
                window.speechSynthesis.pause();
            </script>
            """,
            height=0,
        )

    if resume_voice:
        components.html(
            """
            <script>
                window.speechSynthesis.resume();
            </script>
            """,
            height=0,
        )


def render_voice_prompt():
    speak = st.button("🎙 Voice Prompt", use_container_width=True)
    
    if speak:
        components.html(
            """
            <script>
            const recognition = new webkitSpeechRecognition();
            recognition.lang = "en-US";
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onresult = function(event) {
                const text = event.results[0][0].transcript;
                const streamlitDoc = window.parent.document;
                const textarea = streamlitDoc.querySelector('textarea');

                if (textarea) {
                    textarea.value = text;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };

            recognition.start();
            </script>
            """,
            height=0,
        )

st.set_page_config(
    page_title="Leonardo AI",
    page_icon="🎨",
    layout="wide"
)

init_db()

if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = "English"

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Leonardo Dark"

if "leonardo_visual_asset" not in st.session_state:
    st.session_state["leonardo_visual_asset"] = None

if "blueprint_visual_asset" not in st.session_state:
    st.session_state["blueprint_visual_asset"] = None

if "show_topbar_menu" not in st.session_state:
    st.session_state["show_topbar_menu"] = False

# ----------------------------
# Theme variables
# ----------------------------

theme_mode = st.session_state.get("theme_mode", "Leonardo Dark")

if theme_mode == "Warm Sepia":
    bg_main = "#1a120b"
    bg_grad_1 = "rgba(180, 120, 40, 0.18)"
    bg_grad_2 = "rgba(120, 80, 30, 0.10)"
    hero_from = "rgba(88, 49, 20, 0.94)"
    hero_to = "rgba(30, 22, 16, 0.92)"
elif theme_mode == "Midnight Blue":
    bg_main = "#081120"
    bg_grad_1 = "rgba(59, 130, 246, 0.16)"
    bg_grad_2 = "rgba(99, 102, 241, 0.10)"
    hero_from = "rgba(15, 23, 42, 0.95)"
    hero_to = "rgba(17, 24, 39, 0.95)"
else:
    bg_main = "#0b1220"
    bg_grad_1 = "rgba(180, 120, 40, 0.10)"
    bg_grad_2 = "rgba(59, 130, 246, 0.10)"
    hero_from = "rgba(58, 33, 14, 0.90)"
    hero_to = "rgba(15, 23, 42, 0.92)"

selected_language = st.session_state.get("selected_language", "English")


# ----------------------------
# CSS
# ----------------------------

st.markdown(
    f"""
    <style>
    /* ---------- App shell ---------- */
    .stApp {{
        background:
            radial-gradient(circle at top left, {bg_grad_1}, transparent 28%),
            radial-gradient(circle at top right, {bg_grad_2}, transparent 24%),
            linear-gradient(180deg, {bg_main} 0%, #0f172a 100%);
    }}

    header[data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stToolbar"] {{
        right: 0.75rem;
        top: 0.5rem;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    [data-testid="stAppViewContainer"] {{
        max-width: 100%;
    }}

    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100% !important;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }}

    /* ---------- Hero banner ---------- */
    .hero-banner {{
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(212, 175, 55, 0.28);
        border-radius: 24px;
        padding: 34px 36px;
        margin-bottom: 22px;
        background:
            linear-gradient(135deg, {hero_from}, {hero_to}),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1600' height='500' viewBox='0 0 1600 500'%3E%3Cg opacity='0.08' stroke='%23d6b36a' fill='none'%3E%3Cpath d='M0 260 C180 180 320 340 480 260 S800 180 960 250 1280 340 1600 200' stroke-width='2'/%3E%3Cpath d='M90 80 L250 80 L250 180 L90 180 Z'/%3E%3Ccircle cx='1180' cy='120' r='70'/%3E%3Cpath d='M1140 120 L1220 120 M1180 80 L1180 160'/%3E%3Cpath d='M580 120 L760 120 L850 210 L670 210 Z'/%3E%3C/g%3E%3C/svg%3E");
        background-size: cover;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
        width: 100%;
    }}

    .hero-image-banner {{
        background:
            linear-gradient(90deg, rgba(8, 12, 24, 0.35), rgba(8, 12, 24, 0.75)),
            url("YOUR_IMAGE_PATH_HERE");

        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;

        min-height: 420px;
    }}

    .hero-overlay {{
        position: relative;
        z-index: 2;
    }}

    .hero-badge {{
        display: inline-block;
        padding: 7px 14px;
        border-radius: 999px;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #f5deb3;
        background: rgba(212, 175, 55, 0.12);
        border: 1px solid rgba(212, 175, 55, 0.22);
        margin-bottom: 14px;
    }}

    .hero-title {{
        font-size: 54px;
        font-weight: 800;
        line-height: 1.05;
        margin: 0;
        color: #f8e7c2;
        letter-spacing: 0.02em;
        text-shadow: 0 2px 18px rgba(0,0,0,0.35);
    }}

    .hero-subtitle {{
        font-size: 22px;
        font-style: italic;
        color: #e8d7b1;
        margin-top: 10px;
        margin-bottom: 16px;
    }}

    .hero-description {{
        max-width: 860px;
        font-size: 16px;
        line-height: 1.65;
        color: #d1d5db;
        margin-bottom: 0;
    }}

    /* ---------- Profile card ---------- */
    .profile-card {{
        background: linear-gradient(180deg, rgba(17,24,39,0.95), rgba(15,23,42,0.95));
        border: 1px solid rgba(212, 175, 55, 0.22);
        border-radius: 22px;
        padding: 22px;
        margin-bottom: 16px;
        color: white;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    }}

    .profile-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
        gap: 12px;
    }}

    .profile-avatar {{
        width: 54px;
        height: 54px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        background: linear-gradient(135deg, rgba(212,175,55,0.22), rgba(59,130,246,0.18));
        border: 1px solid rgba(212,175,55,0.25);
        flex-shrink: 0;
    }}

    .profile-role-badge {{
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 13px;
        color: #f8e7c2;
        border: 1px solid rgba(212,175,55,0.2);
        background: rgba(212,175,55,0.08);
        white-space: nowrap;
    }}

    .profile-name {{
        font-size: 24px;
        font-weight: 700;
        margin: 0 0 8px 0;
        color: #f9fafb;
    }}

    .profile-meta {{
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 18px;
    }}

    .profile-stats-grid {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 12px;
    }}

    .profile-stat-box {{
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 14px;
        padding: 12px 14px;
    }}

    .profile-stat-label {{
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 6px;
    }}

    .profile-stat-value {{
        font-size: 26px;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.1;
    }}

    /* ---------- Content cards ---------- */
    .section-card {{
        background: linear-gradient(180deg, rgba(15,23,42,0.94), rgba(17,24,39,0.96));
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.20);
    }}

    .section-title {{
        font-size: 30px;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 12px;
    }}

    .section-text {{
        font-size: 16px;
        line-height: 1.7;
        color: #d1d5db;
    }}

    .status-good {{
        padding: 12px 14px;
        border-radius: 12px;
        background: rgba(22, 101, 52, 0.22);
        border: 1px solid rgba(34, 197, 94, 0.28);
        color: #dcfce7;
        margin-bottom: 10px;
        font-weight: 500;
    }}

    .status-warn {{
        padding: 12px 14px;
        border-radius: 12px;
        background: rgba(146, 64, 14, 0.22);
        border: 1px solid rgba(245, 158, 11, 0.28);
        color: #fde68a;
        margin-bottom: 10px;
        font-weight: 500;
    }}

    .result-box {{
        padding: 18px;
        border-radius: 16px;
        background: rgba(248,250,252,0.96);
        border: 1px solid #dbe3ec;
        margin-top: 12px;
        margin-bottom: 12px;
        color: #111827;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    }}

    .mini-card {{
        padding: 16px;
        border-radius: 16px;
        background: #111827;
        border: 1px solid #374151;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.18);
    }}

    .small-note {{
        font-size: 13px;
        color: #9ca3af;
        margin-top: 6px;
    }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(16,24,40,0.98), rgba(10,15,28,0.98));
        border-right: 1px solid rgba(148,163,184,0.12);
    }}

    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.4rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }}

    .sidebar-title {{
        font-size: 26px;
        font-weight: 800;
        color: #f8e7c2;
        margin-bottom: 4px;
    }}

    .sidebar-subtitle {{
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 18px;
    }}

    .sidebar-group-title {{
        font-size: 15px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 10px;
    }}

    div[data-testid="stButton"] > button[kind="secondary"],
    div[data-testid="stButton"] > button[kind="primary"] {{
        border-radius: 12px !important;
    }}

    .topbar-menu-panel {{
        margin-top: 8px;
        padding: 12px;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.96);
        border: 1px solid rgba(148,163,184,0.18);
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }}

    /* ---------- Micro interactions ---------- */
    button {{
        transition: all 0.15s ease;
    }}

    button:hover {{
        transform: translateY(-1px);
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ----------------------------
# Top bar
# ----------------------------

topbar_left, topbar_right = st.columns([20, 1], vertical_alignment="top")

with topbar_left:
    st.image("banner.png", use_container_width=True)

with topbar_right:
    render_topbar_menu_button()

if st.session_state["show_topbar_menu"]:
    with st.container():
        menu_col1, menu_col2, menu_col3 = st.columns([6, 2, 1])

        with menu_col2:
            selected_language = st.selectbox(
                "Language",
                ["English", "Русский", "Svenska"],
                index=["English", "Русский", "Svenska"].index(
                    st.session_state.get("selected_language", "English")
                ),
                key="selected_language_menu"
            )

            theme_mode = st.selectbox(
                "Theme style",
                ["Leonardo Dark", "Midnight Blue", "Warm Sepia"],
                index=["Leonardo Dark", "Midnight Blue", "Warm Sepia"].index(
                    st.session_state.get("theme_mode", "Leonardo Dark")
                ),
                key="theme_mode_menu"
            )

            st.session_state["selected_language"] = selected_language
            st.session_state["theme_mode"] = theme_mode

        with menu_col3:
            if st.button("✕", key="close_topbar_menu", help="Close menu"):
                st.session_state["show_topbar_menu"] = False
                st.rerun()


# ----------------------------
# Layout
# ----------------------------

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

        render_voice_assistant(concept_data)

        st.markdown("## Delivery Metrics")
        st.markdown(f'<div class="result-box"><b>Concept Difficulty:</b><br>{difficulty}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Modern Difficulty:</b><br>{modern_difficulty}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box"><b>Development Time:</b><br>{dev_time}</div>', unsafe_allow_html=True)
       
        pdf_filename = f"{title.replace(' ', '_')}.pdf"

        if st.button("📦 Export Full Project Package (PDF)", key="export_pdf_main"):
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
                if st.button("🗑", key=f"delete_image_{image_id}", help="Delete image"):
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

    if not concepts:
        st.info("No saved concepts yet.")
        return

    cols = st.columns(2)

    for idx, (concept_id, title, category, created_at, is_favorite) in enumerate(concepts):

        with cols[idx % 2]:

            star = "⭐" if is_favorite else ""

            st.markdown(
                f"""<div class="mini-card">
            <h4 style="margin-top:0;">{star} {title}</h4>
            <div class="small-note">
                Category: {category}<br>
                Created: {created_at}
            </div>
            </div>""",
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📂", key=f"open_{concept_id}", use_container_width=True, help="Open concept"):
                    selected_concept = get_concept_by_id(concept_id)

                    if selected_concept:
                        st.session_state["loaded_concept"] = selected_concept
                        st.session_state["current_concept_id"] = concept_id
                        st.rerun()

            with col2:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_{concept_id}", use_container_width=True, help="Favorite"):
                    toggle_concept_favorite(concept_id)
                    st.rerun()

            with col3:
                if st.button("🗑", key=f"delete_{concept_id}", use_container_width=True, help="Delete concept"):
                    delete_concept(concept_id)

                    if (
                        "loaded_concept" in st.session_state
                        and st.session_state["loaded_concept"]
                        and st.session_state["loaded_concept"].get("title") == title
                    ):
                        st.session_state["loaded_concept"] = None

                    st.rerun()


category, creativity_mode, audience, user_prompt, generate, regenerate = render_controls()

left, right = st.columns([1.05, 2.35], vertical_alignment="top")

with left:
    render_profile_card()
        
with right:
    st.markdown(
        """<div class="section-card">
    <div class="section-title">About the System</div>
    <div class="section-text">
        Leonardo AI generates invention concepts inspired by Renaissance engineering and
        translates them into modern product ideas with practical commercial potential.
    </div>
    </div>""",
        unsafe_allow_html=True
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


