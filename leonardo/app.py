# ----------------------------
# import
 # ----------------------------

import os
import html
import base64
from pathlib import Path

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


# ----------------------------
# Helpers
# ----------------------------

def pretty_label(value):
    return str(value).replace("_", " ").title()


def safe_text(value):
    return html.escape(str(value)) if value is not None else ""


def safe_list(items):
    if not items:
        return ""
    if isinstance(items, list):
        return "<br>• ".join([""] + [safe_text(item) for item in items])
    return safe_text(items)


def image_to_base64(filename):
    image_path = Path(__file__).parent / filename

    if not image_path.exists():
        st.error(f"Image not found: {image_path}")
        return None

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def render_result_box(title, content):
    st.markdown(
        f"""
<div class="result-box">
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


# ----------------------------
# Page setup
# ----------------------------

st.set_page_config(
    page_title="Leonardo AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

if "current_concept_id" not in st.session_state:
    st.session_state["current_concept_id"] = None

if "loaded_concept" not in st.session_state:
    st.session_state["loaded_concept"] = None

if "leonardo_visual_asset" not in st.session_state:
    st.session_state["leonardo_visual_asset"] = None

if "blueprint_visual_asset" not in st.session_state:
    st.session_state["blueprint_visual_asset"] = None


# ----------------------------
# CSS
# ----------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&display=swap');

:root {
    --gold: #d9a84f;
    --gold-soft: #f4d28a;
    --bg: #06111f;
    --panel: rgba(8, 22, 38, 0.92);
    --line: rgba(217, 168, 79, 0.34);
    --text: #f8e7c2;
    --muted: #a8b3c3;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(217,168,79,0.11), transparent 28%),
        radial-gradient(circle at top right, rgba(59,130,246,0.08), transparent 26%),
        linear-gradient(180deg, #06111f 0%, #071525 48%, #08111f 100%) !important;
    color: var(--text);
}

header[data-testid="stHeader"],
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebarNav"],
.stDeployButton,
button[data-testid="stBaseButton-headerNoPadding"],
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
}

[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

.block-container {
    max-width: 1600px !important;
    padding-top: 0 !important;
    padding-bottom: 2.5rem !important;
    padding-left: 1.45rem !important;
    padding-right: 1.45rem !important;
    margin-top: 0 !important;
}

main .block-container {
    min-width: 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

[data-testid="stAppViewContainer"] {
    overflow-x: auto !important;
}

[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

[data-testid="stElementContainer"] {
    margin-top: 0 !important;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    width: 340px !important;
    min-width: 340px !important;
    padding: 0 !important;
    margin: 0 !important;
    background: linear-gradient(180deg, rgba(6,17,31,0.99), rgba(5,13,24,0.99)) !important;
    border-right: 1px solid var(--line);
    box-shadow: 8px 0 28px rgba(0,0,0,0.30);
}

section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
}

section[data-testid="stSidebar"] .block-container {
    margin: 0 !important;
    padding: 0.35rem 1.15rem 1rem 1.15rem !important;
    min-width: auto !important;
    max-width: none !important;
    min-height: 100vh !important;
    border-left: 1px solid rgba(217,168,79,0.34);
    border-right: 1px solid rgba(217,168,79,0.34);
    border-bottom: 1px solid rgba(217,168,79,0.34);
    border-top: none !important;
    border-radius: 0 0 20px 20px;
    background: linear-gradient(180deg, rgba(8,22,38,0.92), rgba(5,13,24,0.88)) !important;
    box-shadow: inset 0 0 30px rgba(217,168,79,0.045);
    box-sizing: border-box !important;
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] [data-testid="stExpander"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"],
section[data-testid="stSidebar"] [data-testid="stTextArea"],
section[data-testid="stSidebar"] [data-testid="stButton"] {
    margin-left: 0 !important;
    margin-right: 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

section[data-testid="stSidebar"] .sidebar-title,
section[data-testid="stSidebar"] .sidebar-group-title,
section[data-testid="stSidebar"] label {
    padding-left: 0 !important;
    margin-left: 0 !important;
}

section[data-testid="stSidebar"] .block-container::before,
section[data-testid="stSidebar"] .block-container::after {
    display: none !important;
    content: none !important;
}

.language-row {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin: 0.35rem 0 0.75rem 0;
    font-size: 21px;
}

.profile-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.35rem 0.25rem 0.9rem 0.25rem;
    margin-bottom: 0.95rem;
    border-bottom: 1px solid rgba(217,168,79,0.24);
}

.profile-avatar {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    background: linear-gradient(135deg, rgba(217,168,79,0.20), rgba(59,130,246,0.12));
    border: 1px solid rgba(217,168,79,0.55);
    flex: 0 0 auto;
}

.profile-name {
    font-family: "Cinzel", Georgia, serif;
    color: var(--gold-soft);
    font-size: 22px;
    font-weight: 700;
    line-height: 1.1;
}

.profile-email {
    color: #8b98aa;
    font-size: 12px;
    line-height: 1.35;
    margin-top: 4px;
    word-break: break-word;
}

.ornament-line {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(217,168,79,0.58), transparent);
    margin: 1rem 0 1.2rem 0;
}

.sidebar-title {
    font-family: "Cinzel", Georgia, serif;
    color: var(--gold);
    font-size: 25px;
    font-weight: 700;
    letter-spacing: 0.035em;
    line-height: 1.25;
    text-transform: uppercase;
    margin-bottom: 1.1rem;
}

.sidebar-group-title {
    font-family: "Cinzel", Georgia, serif;
    color: var(--text);
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin: 0.65rem 0 0.85rem 0;
}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p {
    color: #d6c6a5 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] input {
    background: rgba(3, 10, 20, 0.78) !important;
    border: 1px solid rgba(217,168,79,0.34) !important;
    border-radius: 10px !important;
    color: #f8e7c2 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] input {
    caret-color: transparent !important;
    color: transparent !important;
    opacity: 0 !important;
    width: 0 !important;
    min-width: 0 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] input::selection {
    background: transparent !important;
}

section[data-testid="stSidebar"] textarea {
    min-height: 118px !important;
    caret-color: auto !important;
}

div[data-testid="stButton"] > button {
    border-radius: 11px !important;
    min-height: 44px;
    border: 1px solid rgba(217,168,79,0.30) !important;
    background: rgba(8, 18, 31, 0.76) !important;
    color: #f8e7c2 !important;
    transition: all 0.15s ease;
    font-family: inherit;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    border-color: rgba(244,210,138,0.65) !important;
    box-shadow: 0 8px 22px rgba(0,0,0,0.20);
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(180deg, #f2c76d, #c88a2e) !important;
    color: #1b1206 !important;
    font-weight: 800 !important;
    border: 1px solid rgba(255,229,166,0.75) !important;
}

main [data-testid="stImage"]:first-of-type {
    margin: 0 0 1.1rem 0 !important;
    border: 1px solid rgba(217,168,79,0.42);
    border-radius: 14px;
    overflow: hidden;
    background: rgba(0, 0, 0, 0.60);
    box-shadow: 0 12px 36px rgba(0,0,0,0.34);
}

main [data-testid="stImage"]:first-of-type img {
    display: block;
    width: 100%;
    height: 150px;
    object-fit: cover;
    object-position: center;
}

.section-heading {
    font-family: "Cinzel", Georgia, serif;
    color: var(--gold);
    font-size: 34px;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0 0 0.15rem 0;
}

.heading-rule {
    width: 280px;
    height: 1px;
    margin-bottom: 1.25rem;
    background: linear-gradient(90deg, rgba(217,168,79,0.82), transparent);
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(180px, 1fr));
    gap: 18px;
    margin-bottom: 1.25rem;
}

.status-card {
    min-height: 76px;
    padding: 9px 14px;
    border-radius: 13px;
    background: linear-gradient(180deg, rgba(12,32,50,0.88), rgba(8,22,38,0.86));
    border: 1px solid rgba(217,168,79,0.25);
    box-shadow: inset 0 0 28px rgba(217,168,79,0.04);
}

.status-title {
    font-family: "Cinzel", Georgia, serif;
    color: var(--text);
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.01em;
    margin-bottom: 8px;
    line-height: 1.35;
}

.status-desc {
    color: var(--muted);
    font-size: 14px;
    line-height: 1.55;
}

.concept-empty {
    min-height: 220px;
    border: 1px solid rgba(217,168,79,0.42);
    border-radius: 16px;
    padding: 34px 42px;
    margin-bottom: 1.5rem;
    background:
        linear-gradient(90deg, rgba(5, 13, 24, 0.92) 0%, rgba(5, 13, 24, 0.72) 42%, rgba(5, 13, 24, 0.18) 100%),
        url("concept_panel.png");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    box-shadow: inset 0 0 28px rgba(217,168,79,0.08), 0 8px 24px rgba(0,0,0,0.24);
}

.concept-empty p {
    max-width: 560px;
    color: #d7dce5;
    font-size: 16px;
    line-height: 1.75;
    margin: 0.2rem 0 0.75rem 0;
    text-shadow: 0 2px 10px rgba(0,0,0,0.55);
}

.result-box {
    padding: 18px;
    border-radius: 14px;
    background: rgba(248,250,252,0.96);
    border: 1px solid #dbe3ec;
    margin-top: 12px;
    margin-bottom: 12px;
    color: #111827;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    overflow-wrap: anywhere;
}

.result-title {
    font-weight: 800;
    margin-bottom: 0.4rem;
}

.result-text {
    line-height: 1.6;
}

.mini-card {
    padding: 12px;
    border-radius: 12px;
    background: rgba(8, 18, 31, 0.80);
    border: 1px solid rgba(217,168,79,0.22);
    color: white;
    margin-bottom: 10px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}

.mini-card h4 {
    color: #f8e7c2;
    font-family: "Cinzel", Georgia, serif;
    font-size: 15px;
    line-height: 1.3;
    margin-top: 0;
}

.small-note {
    font-size: 12px;
    color: #9ca3af;
    margin-top: 6px;
}

div[data-testid="stExpander"] {
    border: 1px solid rgba(217,168,79,0.22) !important;
    border-radius: 11px !important;
    background: rgba(5, 13, 24, 0.52) !important;
}

/* ---------- FINAL SIDEBAR SAFETY PATCH ----------
   Keeps every sidebar element inside the visible left panel.
   This block must stay at the very end of CSS. */
section[data-testid="stSidebar"] {
    width: 370px !important;
    min-width: 370px !important;
    max-width: 370px !important;
    overflow: visible !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] .block-container {
    width: 100% !important;
    max-width: 100% !important;
    padding-left: 22px !important;
    padding-right: 22px !important;
    padding-top: 8px !important;
    box-sizing: border-box !important;
    overflow: visible !important;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stElementContainer"],
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] [data-testid="stExpander"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"],
section[data-testid="stSidebar"] [data-testid="stTextArea"],
section[data-testid="stSidebar"] [data-testid="stButton"] {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    box-sizing: border-box !important;
    overflow: visible !important;
}

section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

section[data-testid="stSidebar"] .sidebar-title {
    font-size: 24px !important;
    line-height: 1.18 !important;
    margin-left: 0 !important;
    padding-left: 0 !important;
    overflow-wrap: normal !important;
}

section[data-testid="stSidebar"] .sidebar-group-title,
section[data-testid="stSidebar"] label {
    margin-left: 0 !important;
    padding-left: 0 !important;
}

section[data-testid="stSidebar"] .profile-row,
section[data-testid="stSidebar"] .language-row,
section[data-testid="stSidebar"] .ornament-line {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

/* ---------- Button spacing fix ---------- */
section[data-testid="stSidebar"] [data-testid="stButton"] {
    margin-top: 8px !important;
    margin-bottom: 8px !important;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] {
    margin-top: 10px !important;
}

/* ---------- Compact sidebar / remove annoying sidebar scrolling ----------
   This block must stay at the very end of CSS. */
section[data-testid="stSidebar"] {
    overflow: visible !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] .block-container {
    overflow-y: hidden !important;
    padding-top: 0px !important;
    padding-bottom: 8px !important;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stElementContainer"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

section[data-testid="stSidebar"] .language-row {
    margin: 0.1rem 0 0.35rem 0 !important;
    font-size: 18px !important;
}

section[data-testid="stSidebar"] .profile-row {
    gap: 9px !important;
    padding: 0.2rem 0 0.45rem 0 !important;
    margin-bottom: 0.45rem !important;
}

section[data-testid="stSidebar"] .profile-avatar {
    width: 42px !important;
    height: 42px !important;
    font-size: 20px !important;
}

section[data-testid="stSidebar"] .profile-name {
    font-size: 18px !important;
}

section[data-testid="stSidebar"] .profile-email {
    font-size: 11px !important;
    margin-top: 2px !important;
}

section[data-testid="stSidebar"] .ornament-line {
    margin: 0.45rem 0 0.55rem 0 !important;
}

section[data-testid="stSidebar"] .sidebar-title {
    font-size: 22px !important;
    line-height: 1.1 !important;
    margin-bottom: 0.55rem !important;
}

section[data-testid="stSidebar"] .sidebar-group-title {
    font-size: 14px !important;
    margin: 0.35rem 0 0.35rem 0 !important;
}

section[data-testid="stSidebar"] label {
    font-size: 12px !important;
    margin-bottom: 2px !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    min-height: 38px !important;
    height: 38px !important;
}

section[data-testid="stSidebar"] textarea {
    min-height: 78px !important;
    height: 78px !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] {
    margin-top: 5px !important;
    margin-bottom: 5px !important;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    min-height: 38px !important;
    height: 38px !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] {
    margin-top: 6px !important;
}

/* ---------- Final sidebar spacing balance ----------
   Slightly separates sections after compact mode. Keep at very end. */
section[data-testid="stSidebar"] .language-row {
    margin: 0.25rem 0 0.7rem 0 !important;
}

section[data-testid="stSidebar"] .profile-row {
    margin-bottom: 0.9rem !important;
    padding-bottom: 0.75rem !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] {
    margin-top: 8px !important;
    margin-bottom: 8px !important;
}

section[data-testid="stSidebar"] .ornament-line {
    margin: 0.9rem 0 0.95rem 0 !important;
}

section[data-testid="stSidebar"] .sidebar-title {
    margin-top: 0.2rem !important;
    margin-bottom: 0.85rem !important;
}

section[data-testid="stSidebar"] .sidebar-group-title {
    margin-top: 0.55rem !important;
    margin-bottom: 0.55rem !important;
}

section[data-testid="stSidebar"] label {
    margin-top: 0.35rem !important;
    margin-bottom: 0.18rem !important;
}

section[data-testid="stSidebar"] [data-testid="stSelectbox"] {
    margin-bottom: 0.45rem !important;
}

section[data-testid="stSidebar"] [data-testid="stTextArea"] {
    margin-top: 0.2rem !important;
    margin-bottom: 0.65rem !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] {
    margin-top: 7px !important;
    margin-bottom: 7px !important;
}

/* ---------- Final top alignment patch ----------
   Pull sidebar content back to the top after spacing fixes. Keep at very end. */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div:first-child {
    margin-top: 0px !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}

section[data-testid="stSidebar"] .language-row {
    position: relative !important;
    z-index: 9999 !important;
    padding-top: 6px !important;
    margin-top: 0 !important;
    margin-bottom: 0.55rem !important;
    min-height: 24px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* ---------- Generated Concept image panel final fix ---------- */

.concept-empty {
    display: none !important;
}

.concept-empty-image-box {
    position: relative !important;
    width: 100% !important;
    max-width: 100% !important;
    height: 125px !important;
    min-height: 125px !important;
    border: 1px solid rgba(217,168,79,0.42) !important;
    border-radius: 16px !important;
    margin-bottom: 1.35rem !important;
    overflow: hidden !important;
    background: #06111f !important;
    box-shadow: inset 0 0 28px rgba(217,168,79,0.08), 0 8px 24px rgba(0,0,0,0.24) !important;
}

.concept-empty-image {
    position: absolute !important;
    inset: 0 !important;
    width: 104% !important;
    height: 104% !important;
    left: -2% !important;
    top: -2% !important;
    max-width: none !important;
    object-fit: cover !important;
    object-position: center !important;
    z-index: 0 !important;
}

.concept-empty-image-box::after {
    content: "" !important;
    position: absolute !important;
    inset: 0 !important;
    background: linear-gradient(
        90deg,
        rgba(5, 13, 24, 0.96) 0%,
        rgba(5, 13, 24, 0.78) 38%,
        rgba(5, 13, 24, 0.18) 100%
    ) !important;
    z-index: 1 !important;
}

.concept-empty-text {
    position: relative !important;
    z-index: 2 !important;
    padding: 16px 34px !important;
    max-width: 620px !important;
}

.concept-empty-text p {
    max-width: 620px !important;
    color: #f4d28a !important;
    font-family: "Cinzel", Georgia, serif !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    line-height: 1.65 !important;
    text-align: left !important;
    margin: 0.15rem 0 0.65rem 0 !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.75) !important;
}

/* ---------- Feature cards alignment fix ---------- */

.feature-card {
    min-height: 72px !important;
    height: auto !important;
    line-height: 1.3 !important;
    padding: 8px 14px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
    box-sizing: border-box !important;
    margin-bottom: 22px !important;

    background: linear-gradient(180deg, rgba(12,32,50,0.86), rgba(8,22,38,0.86)) !important;
    border: 1px solid rgba(217,168,79,0.22) !important;
    border-radius: 13px !important;
    box-shadow: inset 0 0 24px rgba(217,168,79,0.035) !important;
}

.feature-title {
    min-height: 18px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    margin-bottom: 2px !important;
    line-height: 1.25 !important;

    font-family: "Cinzel", Georgia, serif !important;
    color: #f8e7c2 !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}

.feature-icon {
    display: inline-flex !important;
    width: 28px !important;
    min-width: 28px !important;
    justify-content: center !important;
    align-items: center !important;
    margin-right: 4px !important;
    font-size: 22px !important;
}

.feature-text {
    margin-top: 0 !important;
    line-height: 1.25 !important;
    color: #a8b3c3 !important;
    font-size: 12px !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------
# Sidebar
# ----------------------------

def render_previous_concepts_sidebar():
    with st.expander("📦 Previous Concepts", expanded=False):
        concepts = get_concepts()

        if not concepts:
            st.info("No saved concepts yet.")
            return

        for concept_id, title, category, created_at, is_favorite in concepts:
            star = "⭐" if is_favorite else ""

            st.markdown(
                f"""
<div class="mini-card">
    <h4>{star} {safe_text(title)}</h4>
    <div class="small-note">
        Category: {safe_text(pretty_label(category))}<br>
        Created: {safe_text(created_at)}
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("📂", key=f"open_concept_{concept_id}", use_container_width=True, help="Open concept"):
                    selected_concept = get_concept_by_id(concept_id)
                    if selected_concept:
                        st.session_state["loaded_concept"] = selected_concept
                        st.session_state["current_concept_id"] = concept_id
                        st.rerun()

            with c2:
                star_label = "⭐" if is_favorite else "☆"
                if st.button(star_label, key=f"favorite_concept_{concept_id}", use_container_width=True, help="Favorite"):
                    toggle_concept_favorite(concept_id)
                    st.rerun()

            with c3:
                if st.button("🗑", key=f"delete_concept_{concept_id}", use_container_width=True, help="Delete concept"):
                    delete_concept(concept_id)
                    if st.session_state.get("current_concept_id") == concept_id:
                        st.session_state["loaded_concept"] = None
                        st.session_state["current_concept_id"] = None
                    st.rerun()


def render_voice_prompt():
    speak = st.button("🎙 Voice Prompt", use_container_width=True)

    if speak:
        components.html(
            """
<script>
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
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
}
</script>
""",
            height=0,
        )


def render_controls():
    with st.sidebar:
        st.markdown(
            """
<div class="language-row">
    <span title="English">🇬🇧</span>
    <span title="Svenska">🇸🇪</span>
    <span title="Русский">🇷🇺</span>
</div>

<div class="profile-row">
    <div class="profile-avatar">🧠</div>
    <div>
        <div class="profile-name">Aleksei</div>
        <div class="profile-email">luenko101985@gmail.com</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        nav1 = st.button("⌂  APP", key="nav_app", use_container_width=True)
        nav2 = st.button("▧  GALLERY", key="nav_gallery", use_container_width=True)

        if nav1:
            st.session_state["page"] = "app"
            st.rerun()

        if nav2:
            st.session_state["page"] = "gallery"
            st.rerun()

        render_previous_concepts_sidebar()

        st.markdown('<div class="ornament-line"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">Leonardo<br>Control</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-group-title">⚙️ Concept Settings</div>', unsafe_allow_html=True)

        category = st.selectbox(
            "Invention Category",
            CATEGORIES,
            format_func=pretty_label,
        )

        creativity_mode = st.selectbox(
            "Creativity Mode",
            ["Classic", "Bold", "Experimental"],
        )

        audience = st.selectbox(
            "Target Audience",
            ["Engineers", "Investors", "Students", "General Public"],
        )

        user_prompt = st.text_area(
            "Prompt / Idea",
            placeholder="Create a Renaissance-inspired rescue glider for dangerous mountain missions...",
            height=120,
        )

        generate = st.button("✨ Generate Concept", use_container_width=True, type="primary")
        regenerate = st.button("🔄 Regenerate", use_container_width=True)

        render_voice_prompt()

        with st.expander("📦 Included in Output", expanded=False):
            st.markdown(
                """
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
                """
            )

    return category, creativity_mode, audience, user_prompt, generate, regenerate


# ----------------------------
# Main UI
# ----------------------------

def render_banner():
    st.image("banner.png", use_container_width=True)


def render_system_status():
    openai_active = bool(os.getenv("OPENAI_API_KEY"))

    openai_title = "✅ OpenAI Integration: Active" if openai_active else "🟡 OpenAI Integration: Fallback"
    openai_desc = "Connected to OpenAI services and ready to generate." if openai_active else "API key not detected. Local fallback mode will be used."

    render_section_heading("System Status")
    
    st.markdown(
        f"""
<div class="status-grid">
    <div class="status-card">
        <div class="status-title">✅ Core Logic: Active</div>
        <div class="status-desc">The core reasoning engine is operational and ready.</div>
    </div>
    <div class="status-card">
        <div class="status-title">✅ Interface Layer: Active</div>
        <div class="status-desc">UI components are responsive and functioning.</div>
    </div>
    <div class="status-card">
        <div class="status-title">{openai_title}</div>
        <div class="status-desc">{openai_desc}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_empty_concept_area():
    render_section_heading("Generated Concept")

    concept_panel_base64 = image_to_base64("concept_panel.png")

    if concept_panel_base64:
        st.markdown(
            f"""
<div class="concept-empty-image-box">
    <img src="data:image/png;base64,{concept_panel_base64}" class="concept-empty-image">
    <div class="concept-empty-text">
        <p>Your invention concept will appear here.</p>
        <p>Leonardo AI will generate a complete Renaissance-inspired invention with modern engineering analysis.</p>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<div class="concept-empty">
    <p>Your invention concept will appear here.</p>
    <p>Leonardo AI will generate a complete Renaissance-inspired invention with modern engineering analysis.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    feature_cards = [
        ("🪶", "Title & Summary", "The name and brief overview of the invention."),
        ("⚙️", "Core Principle", "The fundamental principle behind how it works."),
        ("🖼️", "Leonardo Sketch", "A description of how Leonardo might have sketched it."),
        ("📦", "Blueprint Concept", "A modern engineering blueprint and structural concept."),
        ("⚗️", "Materials & Resources", "What materials are needed and how they are used."),
        ("🎯", "Use Cases", "Where and how this invention can be applied."),
    ]

    for row_start in range(0, len(feature_cards), 3):
        cols = st.columns(3)

        for col, card in zip(cols, feature_cards[row_start:row_start + 3]):
            icon, title, text = card

            with col:
                st.markdown(
                    f"""
<div class="feature-card">
    <div class="feature-title">
        <span class="feature-icon">{icon}</span>{title}
    </div>
    <div class="feature-text">{text}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

    st.markdown(
        """
<div class="feature-card">
    <div class="feature-title">
        <span class="feature-icon">📊</span>Investor Summary
    </div>
    <div class="feature-text">A brief pitch for potential investors and backers.</div>
</div>
""",
        unsafe_allow_html=True,
    )

def generate_or_load_concept(category, creativity_mode, audience, user_prompt, generate, regenerate):
    concept_data = st.session_state.get("loaded_concept")

    if generate or regenerate:
        st.session_state["leonardo_visual_asset"] = None
        st.session_state["blueprint_visual_asset"] = None
        st.session_state["loaded_concept"] = None

        prompt_text = user_prompt.strip() if user_prompt.strip() else f"Create an invention in {pretty_label(category)}"

        with st.spinner("Generating concept..."):
            concept_data = generate_concept(
                category=category,
                creativity_mode=creativity_mode,
                audience=audience,
                user_prompt=prompt_text,
            )

        concept_id = save_concept(
            title=concept_data["title"],
            category=category,
            prompt=prompt_text,
            concept_data=concept_data,
        )

        st.session_state["current_concept_id"] = concept_id

    return concept_data


# ----------------------------
# Voice Assistant
# ----------------------------

def render_voice_assistant(concept_data):
    st.markdown("## 🧠 Voice Assistant")

    title = concept_data.get("title", "")
    executive_summary = concept_data.get("executive_summary", "")
    market_demand = concept_data.get("market_demand", "")
    investor_summary = concept_data.get("investor_summary", "")
    modern_principle = concept_data.get("modern_principle", "")

    voice_language = st.selectbox(
        "Voice Language",
        ["English", "Русский"],
        key="voice_language_selector",
    )

    if voice_language == "Русский":
        summary_text = f"Название проекта: {title}. Краткое описание: {executive_summary}. Рыночный спрос: {market_demand}. Инвесторское резюме: {investor_summary}."
        investor_text = f"Инвесторская презентация проекта {title}. {investor_summary}. Рыночный спрос: {market_demand}."
        engineering_text = f"Инженерный обзор проекта {title}. {modern_principle}."
        speech_lang = "ru-RU"
    else:
        summary_text = f"Project title: {title}. Executive summary: {executive_summary}. Market demand: {market_demand}. Investor summary: {investor_summary}."
        investor_text = f"Investor pitch. {title}. {investor_summary}. Market demand: {market_demand}."
        engineering_text = f"Engineering overview for {title}. {modern_principle}."
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
        components.html("<script>window.speechSynthesis.pause();</script>", height=0)
    if resume_voice:
        components.html("<script>window.speechSynthesis.resume();</script>", height=0)
    if stop_voice:
        components.html("<script>window.speechSynthesis.cancel();</script>", height=0)


# ----------------------------
# Concept result
# ----------------------------

def render_generated_visuals():
    if not st.session_state["leonardo_visual_asset"] and not st.session_state["blueprint_visual_asset"]:
        return

    st.markdown("## Generated Visual Assets")

    if st.session_state["leonardo_visual_asset"]:
        render_result_box("Leonardo Visual Asset", "Generated image based on the Renaissance sketch prompt.")
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
        render_result_box("Blueprint Visual Asset", "Generated image based on the modern blueprint prompt.")
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
        image_bytes = image[3]
        is_favorite = image[5]

        with cols[idx % 2]:
            star_prefix = "⭐ " if is_favorite else ""
            st.markdown(f"### {star_prefix}{pretty_label(image_type)}")

            st.image(
                image_bytes,
                caption=pretty_label(image_type),
                use_container_width=True,
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
                    key=f"download_image_{image_id}",
                )


def render_concept_result(concept_data):
    title = concept_data["title"]

    st.success("Concept generated successfully.")

    st.markdown("## Leonardo Inspiration")
    render_result_box("Concept", concept_data["leonardo_concept"])
    render_result_box("Sketch Description", concept_data["leonardo_sketch_description"])

    st.markdown("## Modern Product Definition")
    render_result_box("Title", title)
    render_result_box("Product Name", concept_data["modern_product_name"])
    render_result_box("Category", concept_data["modern_category"])
    render_result_box("Executive Summary", concept_data["executive_summary"])

    st.markdown("## Business Need")
    render_result_box("Problem Statement", concept_data["problem_statement"])
    render_result_box("Target Users", concept_data["target_users"])
    render_result_box("Industries", concept_data["industries"])
    render_result_box("Use Cases", concept_data["use_cases"])

    st.markdown("## Engineering")
    render_result_box("Modern Principle", concept_data["modern_principle"])
    render_result_box("System Components", concept_data["system_components"])
    render_result_box("Materials", concept_data["materials"])
    render_result_box("Technical Requirements", concept_data["technical_requirements"])
    render_result_box("Modern Sketch Description", concept_data["modern_sketch_description"])

    st.markdown("## Visual Generation")
    render_result_box("Leonardo Sketch Prompt", concept_data["leonardo_sketch_description"])
    render_result_box("Modern Blueprint Prompt", concept_data["modern_sketch_description"])

    col1, col2 = st.columns(2)
    with col1:
        generate_leonardo_image = st.button("🖼 Generate Leonardo Sketch", use_container_width=True)
    with col2:
        generate_blueprint_image = st.button("📐 Generate Modern Blueprint", use_container_width=True)

    if generate_leonardo_image:
        with st.spinner("Generating Leonardo sketch..."):
            try:
                st.session_state["leonardo_visual_asset"] = generate_leonardo_image_prompt(
                    concept_data["leonardo_sketch_description"]
                )
            except Exception as e:
                st.error(f"Leonardo sketch generation failed: {e}")

    if generate_blueprint_image:
        with st.spinner("Generating modern blueprint..."):
            try:
                st.session_state["blueprint_visual_asset"] = generate_blueprint_image_prompt(
                    concept_data["modern_sketch_description"]
                )
            except Exception as e:
                st.error(f"Blueprint generation failed: {e}")

    render_generated_visuals()

    st.markdown("## Implementation Roadmap")
    guides = concept_data["implementation_guides"]
    render_complete_guide("Prototype", guides["prototype"])
    render_complete_guide("MVP", guides["mvp"])
    render_complete_guide("Pilot", guides["pilot"])
    render_complete_guide("Production", guides["production"])

    render_result_box("Deployment Strategy", concept_data["deployment_strategy"])

    st.markdown("## Risks and Constraints")
    render_result_box("Risks", concept_data["risks"])
    render_result_box("Constraints", concept_data["constraints"])

    st.markdown("## Commercial Outlook")
    render_result_box("Market Demand", concept_data["market_demand"])
    render_result_box("Startup Cost", concept_data["startup_cost"])
    render_result_box("ROI", concept_data["roi"])
    render_result_box("Investor Summary", concept_data["investor_summary"])

    render_voice_assistant(concept_data)

    st.markdown("## Delivery Metrics")
    render_result_box("Concept Difficulty", concept_data["difficulty"])
    render_result_box("Modern Difficulty", concept_data["modern_difficulty"])
    render_result_box("Development Time", concept_data["dev_time"])

    pdf_filename = f"{title.replace(' ', '_')}.pdf"

    if st.button("📦 Export Full Project Package (PDF)", key="export_pdf_main"):
        current_concept_id = st.session_state.get("current_concept_id")
        saved_images = get_images_for_concept(current_concept_id) if current_concept_id else []

        export_project_plan_pdf(
            concept_data,
            pdf_filename,
            saved_images=saved_images,
        )

        with open(pdf_filename, "rb") as pdf_file:
            st.download_button(
                label="Download PDF",
                data=pdf_file,
                file_name=pdf_filename,
                mime="application/pdf",
            )

    render_saved_images()


# ----------------------------
# App flow
# ----------------------------

category, creativity_mode, audience, user_prompt, generate, regenerate = render_controls()

render_banner()

if st.session_state.get("page", "app") == "gallery":
    st.markdown("## Gallery")
    render_saved_images()
    st.stop()

render_system_status()

concept_data = generate_or_load_concept(
    category=category,
    creativity_mode=creativity_mode,
    audience=audience,
    user_prompt=user_prompt,
    generate=generate,
    regenerate=regenerate,
)

if concept_data:
    render_concept_result(concept_data)
else:
    render_empty_concept_area()
