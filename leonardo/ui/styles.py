import streamlit as st


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Noto+Sans:wght@400;500;600;700&display=swap');

:root {
    --gold: #d9a84f;
    --line: rgba(217, 168, 79, 0.34);
    --text: #f8e7c2;
    --control-background: linear-gradient(
        180deg,
        rgba(18, 35, 52, 0.98) 0%,
        rgba(10, 23, 37, 0.98) 55%,
        rgba(6, 17, 29, 0.98) 100%
    );
    --control-depth:
        inset 0 1px 0 rgba(255, 235, 190, 0.06),
        inset 0 -1px 0 rgba(0, 0, 0, 0.28);
    --control-hover-background: linear-gradient(
        180deg,
        rgba(23, 42, 60, 0.98) 0%,
        rgba(13, 29, 45, 0.98) 55%,
        rgba(8, 21, 34, 0.98) 100%
    );
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    font-family: "Noto Sans", "Noto Sans CJK SC", "Noto Sans JP", "Noto Sans KR", "Segoe UI", Arial, sans-serif;
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
    padding-bottom: 2.5rem !important;
    margin-top: 0 !important;
}

[data-testid="stMain"] [data-testid="stMainBlockContainer"] {
    min-width: 0 !important;
    width: 100% !important;
    max-width: 1240px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-left: 20px !important;
    padding-right: 20px !important;
    box-sizing: border-box !important;
    container-type: inline-size;
    container-name: main-content;
}

[data-testid="stMain"] {
    min-width: 0 !important;
    overflow-x: clip !important;
}

[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

[data-testid="stElementContainer"] {
    margin-top: 0 !important;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    width: 370px !important;
    min-width: 370px !important;
    max-width: 370px !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: visible !important;
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
    min-width: auto !important;
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

section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] .block-container {
    width: 100% !important;
    max-width: 100% !important;
    padding: 0 22px 8px !important;
    box-sizing: border-box !important;
    overflow-x: visible !important;
    overflow-y: hidden !important;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stElementContainer"],
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] [data-testid="stExpander"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"],
section[data-testid="stSidebar"] [data-testid="stTextArea"],
section[data-testid="stSidebar"] [data-testid="stButton"] {
    margin-left: 0 !important;
    margin-right: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow: visible !important;
}

section[data-testid="stSidebar"] [data-testid="stElementContainer"] {
    margin-bottom: 0 !important;
}

section[data-testid="stSidebar"] .block-container::before,
section[data-testid="stSidebar"] .block-container::after {
    display: none !important;
    content: none !important;
}

section[data-testid="stSidebar"] .ornament-line {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(217,168,79,0.58), transparent);
    margin: 0.9rem 0 0.95rem !important;
}

section[data-testid="stSidebar"] .sidebar-title {
    font-family: "Cinzel", Georgia, serif;
    color: var(--gold);
    font-size: 22px !important;
    font-weight: 700;
    letter-spacing: 0.035em;
    line-height: 1.1 !important;
    text-transform: uppercase;
    margin: calc(0.2rem + 4px) 0 0.85rem !important;
    padding-left: 0 !important;
    overflow-wrap: normal !important;
}

section[data-testid="stSidebar"] .sidebar-group-title {
    font-family: "Cinzel", Georgia, serif;
    color: var(--text);
    font-size: 14px !important;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin: 0.55rem 0 !important;
    padding-left: 0 !important;
}

section[data-testid="stSidebar"] label {
    margin: 0.35rem 0 0.18rem !important;
    padding-left: 0 !important;
    font-size: 12px !important;
    color: #d6c6a5 !important;
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: #d6c6a5 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(3, 10, 20, 0.78) !important;
    border: 1px solid rgba(217,168,79,0.34) !important;
    border-radius: 10px !important;
    color: #f8e7c2 !important;
    min-height: 38px !important;
    height: 38px !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

section[data-testid="stSidebar"] textarea {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 78px !important;
    height: 78px !important;
    box-sizing: border-box !important;
    background: rgba(3, 10, 20, 0.78) !important;
    border: 1px solid rgba(217,168,79,0.34) !important;
    border-radius: 10px !important;
    color: #f8e7c2 !important;
    caret-color: auto !important;
}

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

body:has(input[role="combobox"][aria-expanded="true"])
div[data-baseweb="popover"] {
    background: linear-gradient(180deg, #0b1b2a 0%, #07111c 100%) !important;
    box-shadow: inset 0 0 0 1px rgba(217,168,79,0.34) !important;
}

body:has(input[role="combobox"][aria-expanded="true"])
div[data-baseweb="popover"] > div,
body:has(input[role="combobox"][aria-expanded="true"])
[data-testid="stSelectboxVirtualDropdown"] {
    background: transparent !important;
}

body:has(input[role="combobox"][aria-expanded="true"])
div[data-baseweb="popover"] [role="option"],
body:has(input[role="combobox"][aria-expanded="true"])
div[data-baseweb="popover"] [role="option"] * {
    color: #f3e7c4 !important;
}

body:has(input[role="combobox"][aria-expanded="true"])
div[data-baseweb="popover"] [role="option"]:hover > div {
    background: rgba(234, 215, 164, 0.08) !important;
}

body:has(input[role="combobox"][aria-expanded="true"])
div[data-baseweb="popover"] [role="option"][aria-selected="true"] > div {
    background: rgba(30, 48, 65, 0.95) !important;
}

body:has(input[role="combobox"][aria-expanded="true"])
div[data-baseweb="popover"] [role="option"][aria-selected="true"],
body:has(input[role="combobox"][aria-expanded="true"])
div[data-baseweb="popover"] [role="option"][aria-selected="true"] * {
    color: #ead7a4 !important;
}

section[data-testid="stSidebar"] [data-testid="stTextArea"]
[data-testid="stTextAreaRootElement"]:focus-within {
    border-color: transparent !important;
    outline: none !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] [data-testid="stTextArea"] textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] [data-testid="stTextArea"]
[data-testid="InputInstructions"] {
    display: none !important;
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

:is(
    .st-key-generate_leonardo_manual,
    .st-key-generate_blueprint_manual,
    .st-key-voice_summary,
    .st-key-voice_investor,
    .st-key-voice_engineering,
    .st-key-voice_pause,
    .st-key-voice_resume,
    .st-key-voice_stop,
    .st-key-export_pdf_main,
    .st-key-download_pdf_main,
    .st-key-publish_current_concept_to_marketplace,
    .st-key-remove_current_concept_from_marketplace
) :is([data-testid="stButton"], [data-testid="stDownloadButton"]) > button {
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
    border-color: rgba(217,168,79,0.34) !important;
    box-shadow: var(--control-depth) !important;
}

:is(
    .st-key-generate_leonardo_manual,
    .st-key-generate_blueprint_manual,
    .st-key-voice_summary,
    .st-key-voice_investor,
    .st-key-voice_engineering,
    .st-key-voice_pause,
    .st-key-voice_resume,
    .st-key-voice_stop,
    .st-key-export_pdf_main,
    .st-key-download_pdf_main,
    .st-key-publish_current_concept_to_marketplace,
    .st-key-remove_current_concept_from_marketplace
) :is([data-testid="stButton"], [data-testid="stDownloadButton"]) > button:hover {
    background: var(--control-hover-background) !important;
    border-color: rgba(234,215,164,0.52) !important;
}

:is(
    .st-key-generate_leonardo_manual,
    .st-key-generate_blueprint_manual,
    .st-key-voice_summary,
    .st-key-voice_investor,
    .st-key-voice_engineering,
    .st-key-voice_pause,
    .st-key-voice_resume,
    .st-key-voice_stop,
    .st-key-export_pdf_main,
    .st-key-download_pdf_main
) button p {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    color: #f3e7c4 !important;
}

:is(
    .st-key-generate_leonardo_manual,
    .st-key-generate_blueprint_manual,
    .st-key-voice_summary,
    .st-key-voice_investor,
    .st-key-voice_engineering,
    .st-key-voice_pause,
    .st-key-voice_resume,
    .st-key-voice_stop,
    .st-key-export_pdf_main,
    .st-key-download_pdf_main
) button p::before {
    content: "";
    display: inline-block;
    width: 20px;
    height: 20px;
    flex: 0 0 20px;
    background-color: #ead7a4;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-position: center;
    -webkit-mask-size: contain;
    mask-size: contain;
}

.st-key-generate_leonardo_manual button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='16' rx='2'/%3E%3Ccircle cx='8.5' cy='9' r='1.5'/%3E%3Cpath d='m3 17 5-5 4 4 3-3 6 6'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='16' rx='2'/%3E%3Ccircle cx='8.5' cy='9' r='1.5'/%3E%3Cpath d='m3 17 5-5 4 4 3-3 6 6'/%3E%3C/svg%3E");
}

.st-key-generate_blueprint_manual button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='5' r='2'/%3E%3Cpath d='m11 7-5 13M13 7l5 13M8.2 14h7.6M5 20h4M15 20h4'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='5' r='2'/%3E%3Cpath d='m11 7-5 13M13 7l5 13M8.2 14h7.6M5 20h4M15 20h4'/%3E%3C/svg%3E");
}

.st-key-voice_summary button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 3h8l4 4v14H6Z'/%3E%3Cpath d='M14 3v5h4M9 13h6M9 17h6'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 3h8l4 4v14H6Z'/%3E%3Cpath d='M14 3v5h4M9 13h6M9 17h6'/%3E%3C/svg%3E");
}

.st-key-voice_investor button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 13v-2a8 8 0 0 1 16 0v2M4 13H2v5h4v-5H4ZM20 13h2v5h-4v-5h2ZM18 18c-1 2-3 3-6 3'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 13v-2a8 8 0 0 1 16 0v2M4 13H2v5h4v-5H4ZM20 13h2v5h-4v-5h2ZM18 18c-1 2-3 3-6 3'/%3E%3C/svg%3E");
}

.st-key-voice_engineering button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1'/%3E%3C/svg%3E");
}

.st-key-voice_pause button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7 5v14M17 5v14' fill='none' stroke='black' stroke-width='2.2' stroke-linecap='round'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7 5v14M17 5v14' fill='none' stroke='black' stroke-width='2.2' stroke-linecap='round'/%3E%3C/svg%3E");
}

.st-key-voice_resume button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='m8 5 11 7-11 7V5Z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='m8 5 11 7-11 7V5Z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3C/svg%3E");
}

.st-key-voice_stop button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect x='6' y='6' width='12' height='12' rx='1' fill='none' stroke='black' stroke-width='1.8'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect x='6' y='6' width='12' height='12' rx='1' fill='none' stroke='black' stroke-width='1.8'/%3E%3C/svg%3E");
}

:is(.st-key-export_pdf_main, .st-key-download_pdf_main) button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 3h8l4 4v14H6Z'/%3E%3Cpath d='M14 3v5h4M12 11v6M9.5 14.5 12 17l2.5-2.5'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 3h8l4 4v14H6Z'/%3E%3Cpath d='M14 3v5h4M12 11v6M9.5 14.5 12 17l2.5-2.5'/%3E%3C/svg%3E");
}

.st-key-voice_language_selector div[data-baseweb="select"] > div {
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
    border: 1px solid rgba(217,168,79,0.34) !important;
    border-radius: 10px !important;
    box-shadow: var(--control-depth) !important;
}

.st-key-voice_language_selector div[data-baseweb="select"] svg {
    color: #ead7a4 !important;
    fill: #ead7a4 !important;
}

:is(
    .st-key-generate_leonardo_manual,
    .st-key-generate_blueprint_manual,
    .st-key-voice_summary,
    .st-key-voice_investor,
    .st-key-voice_engineering,
    .st-key-voice_pause,
    .st-key-voice_resume,
    .st-key-voice_stop,
    .st-key-export_pdf_main,
    .st-key-download_pdf_main,
    .st-key-publish_current_concept_to_marketplace,
    .st-key-remove_current_concept_from_marketplace
) :is([data-testid="stButton"], [data-testid="stDownloadButton"]) > button:is(:focus, :focus-visible),
.st-key-voice_language_selector [data-baseweb="select"]:focus-within,
.st-key-voice_language_selector [data-baseweb="select"]:focus-within > div,
:is(
    .st-key-roadmap_prototype,
    .st-key-roadmap_mvp,
    .st-key-roadmap_pilot,
    .st-key-roadmap_production
) summary:is(:focus, :focus-visible) {
    outline: none !important;
    box-shadow: none !important;
    border-color: rgba(234,215,164,0.52) !important;
}

.st-key-saved_images_empty_state [data-testid="stAlert"] {
    color: #c9c1b0 !important;
    background: linear-gradient(180deg, rgba(11,27,42,0.96) 0%, rgba(7,17,28,0.98) 100%) !important;
    border: 1px solid rgba(93,161,218,0.36) !important;
    border-radius: 11px !important;
    box-shadow: inset 0 1px 0 rgba(190,225,255,0.05) !important;
}

.st-key-saved_images_empty_state [data-testid="stAlert"] p {
    color: #c9c1b0 !important;
}

.st-key-main_banner [data-testid="stImage"] {
    width: 100% !important;
    max-width: 100% !important;
    aspect-ratio: 6 / 1;
    margin: 12px 0 1.1rem 0 !important;
    border: 1px solid rgba(217,168,79,0.42);
    border-radius: 14px;
    overflow: hidden;
    background: rgba(0, 0, 0, 0.60);
    box-shadow: 0 12px 36px rgba(0,0,0,0.34);
}

.st-key-main_banner [data-testid="stImage"] img {
    display: block;
    width: 100% !important;
    height: 100% !important;
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

.concept-empty {
    display: none !important;
}

.result-box {
    padding: 18px;
    border-radius: 14px;
    background: linear-gradient(
        180deg,
        rgba(15,32,49,0.96) 0%,
        rgba(8,21,35,0.98) 100%
    );
    border: 1px solid rgba(79,168,255,0.36);
    margin-top: 12px;
    margin-bottom: 12px;
    color: #F2EADB;
    box-shadow:
        inset 0 1px 0 rgba(255,235,190,0.045),
        0 4px 14px rgba(0,0,0,0.16);
    overflow-wrap: anywhere;
}

.result-box--constraint {
    border-color: rgba(112,166,211,0.38);
}

.result-box.result-box--control-gap {
    margin-bottom: 30px !important;
}

.st-key-voice_pause,
.st-key-voice_resume,
.st-key-voice_stop,
.st-key-voice_summary,
.st-key-voice_investor,
.st-key-voice_engineering {
    margin-top: 14px !important;
}

.result-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 800;
    margin-bottom: 0.4rem;
    color: #82BEF8;
}

.result-text {
    line-height: 1.6;
    color: #F2EADB;
}

.result-title-icon {
    display: inline-flex;
    width: 19px;
    height: 19px;
    flex: 0 0 19px;
    color: #82BEF8;
}

.result-title-icon svg,
.generated-section-heading__icon svg {
    display: block;
    width: 100%;
    height: 100%;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.generated-section-heading,
.st-key-modern_section h2 {
    font-family: "Cinzel", Georgia, serif !important;
    color: #D6A84B !important;
    font-weight: 600 !important;
    letter-spacing: -0.005em !important;
    text-transform: none !important;
    font-variant: normal !important;
    font-variant-caps: normal !important;
    line-height: 1.2 !important;
}

.generated-section-heading {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

.generated-section-heading__icon {
    display: inline-flex;
    width: 26px;
    height: 26px;
    flex: 0 0 26px;
    color: #ead7a4;
}

.result-box .result-text > .result-list {
    margin: 0.2rem 0 0.15rem 0;
    padding-left: 1.2rem;
}

.result-box .result-text > .result-list > li {
    margin: 0.08rem 0;
    padding: 0;
    line-height: 1.45;
}

.result-box .result-text > .result-list > li:last-child {
    margin-bottom: 0;
}

.st-key-previous_concepts .mini-card {
    padding: 7px 10px;
    border-radius: 12px;
    background: linear-gradient(
        180deg,
        rgba(15, 32, 49, 0.94) 0%,
        rgba(10, 24, 39, 0.94) 56%,
        rgba(7, 18, 31, 0.96) 100%
    );
    border: 1px solid rgba(217,168,79,0.34);
    color: #d8cfbd;
    margin-bottom: 10px;
    box-shadow:
        inset 0 1px 0 rgba(255, 235, 190, 0.045),
        inset 0 -1px 0 rgba(0, 0, 0, 0.20),
        0 6px 18px rgba(0,0,0,0.18);
}

.st-key-previous_concepts .mini-card h4 {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    color: #f3e7c4;
    font-family: "Cinzel", Georgia, serif;
    font-size: 15px;
    line-height: 1.3;
    margin: 0;
    padding: 0 !important;
}

.st-key-previous_concepts .small-note {
    font-size: 12px;
    color: #c9c1b0;
    line-height: 1.35;
    margin-top: 2px;
}

div[data-testid="stExpander"] {
    color: #f3e7c4 !important;
    border: 1px solid rgba(217,168,79,0.34) !important;
    border-radius: 11px !important;
    background: linear-gradient(180deg, rgba(11,27,42,0.98) 0%, rgba(7,17,28,0.98) 100%) !important;
}

:is(
    .st-key-roadmap_prototype,
    .st-key-roadmap_mvp,
    .st-key-roadmap_pilot,
    .st-key-roadmap_production
) [data-testid="stExpander"] summary {
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
}

:is(
    .st-key-roadmap_prototype,
    .st-key-roadmap_mvp,
    .st-key-roadmap_pilot,
    .st-key-roadmap_production
) [data-testid="stExpander"] summary:hover {
    background: var(--control-hover-background) !important;
}

:is(
    .st-key-roadmap_prototype,
    .st-key-roadmap_mvp,
    .st-key-roadmap_pilot,
    .st-key-roadmap_production
) :is(summary p, summary svg, [data-testid="stExpanderDetails"]) {
    color: #f3e7c4 !important;
}

:is(
    .st-key-roadmap_prototype,
    .st-key-roadmap_mvp,
    .st-key-roadmap_pilot,
    .st-key-roadmap_production
) [data-testid="stExpanderDetails"] {
    background: linear-gradient(180deg, rgba(11,27,42,0.72) 0%, rgba(7,17,28,0.78) 100%) !important;
}

:is(
    .st-key-roadmap_prototype,
    .st-key-roadmap_mvp,
    .st-key-roadmap_pilot,
    .st-key-roadmap_production
) .roadmap-subheading {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    color: #82BEF8 !important;
}

:is(
    .st-key-roadmap_prototype,
    .st-key-roadmap_mvp,
    .st-key-roadmap_pilot,
    .st-key-roadmap_production
) .roadmap-subheading__icon {
    display: inline-flex;
    width: 22px;
    height: 22px;
    flex: 0 0 22px;
    color: #82BEF8;
}

:is(
    .st-key-roadmap_prototype,
    .st-key-roadmap_mvp,
    .st-key-roadmap_pilot,
    .st-key-roadmap_production
) .roadmap-subheading__icon svg {
    display: block;
    width: 100%;
    height: 100%;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}

section[data-testid="stSidebar"] [data-testid="stButton"] {
    margin-top: 7px !important;
    margin-bottom: 7px !important;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    min-height: 38px !important;
    height: 38px !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] {
    margin-top: 8px !important;
    margin-bottom: 8px !important;
}

section[data-testid="stSidebar"] [data-testid="stSelectbox"] {
    margin-bottom: 0.45rem !important;
}

section[data-testid="stSidebar"] [data-testid="stTextArea"] {
    margin-top: 0.2rem !important;
    margin-bottom: 0.65rem !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
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

/* ---------- Unified top sidebar navigation ---------- */

section[data-testid="stSidebar"] .st-key-language {
    margin-top: 12px !important;
}

section[data-testid="stSidebar"] .st-key-nav_app button,
section[data-testid="stSidebar"] .st-key-nav_gallery button,
section[data-testid="stSidebar"] .st-key-nav_marketplace button {
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 12px !important;
}

section[data-testid="stSidebar"] .st-key-nav_app button p,
section[data-testid="stSidebar"] .st-key-nav_gallery button p,
section[data-testid="stSidebar"] .st-key-nav_marketplace button p {
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    text-align: left !important;
}

section[data-testid="stSidebar"] .st-key-nav_app button > div,
section[data-testid="stSidebar"] .st-key-nav_gallery button > div,
section[data-testid="stSidebar"] .st-key-nav_marketplace button > div,
section[data-testid="stSidebar"] .st-key-nav_app button > div > span,
section[data-testid="stSidebar"] .st-key-nav_gallery button > div > span,
section[data-testid="stSidebar"] .st-key-nav_marketplace button > div > span,
section[data-testid="stSidebar"] .st-key-nav_app button [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] .st-key-nav_gallery button [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] .st-key-nav_marketplace button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
}

:is(
    section[data-testid="stSidebar"] .st-key-language,
    .st-key-voice_language_selector
) div[data-baseweb="select"] > div {
    padding-left: 12px !important;
    align-items: center !important;
}

:is(
    section[data-testid="stSidebar"] .st-key-language,
    .st-key-voice_language_selector
) div[data-baseweb="select"] > div > div:first-of-type {
    margin-left: 0 !important;
    padding-left: 0 !important;
}

section[data-testid="stSidebar"] .st-key-language div[data-baseweb="select"] > div::before,
.st-key-voice_language_selector div[data-baseweb="select"] > div::before,
section[data-testid="stSidebar"] .st-key-nav_app button p::before,
section[data-testid="stSidebar"] .st-key-nav_gallery button p::before,
section[data-testid="stSidebar"] .st-key-nav_marketplace button p::before,
section[data-testid="stSidebar"] .st-key-generate_images [data-testid="stWidgetLabel"]::before,
section[data-testid="stSidebar"] .st-key-previous_concepts [data-testid="stExpander"] summary p::before {
    content: "" !important;
    display: inline-block !important;
    width: 21px !important;
    min-width: 21px !important;
    height: 21px !important;
    flex: 0 0 21px !important;
    background-color: #ead7a4 !important;
    -webkit-mask-position: center !important;
    -webkit-mask-repeat: no-repeat !important;
    -webkit-mask-size: contain !important;
    mask-position: center !important;
    mask-repeat: no-repeat !important;
    mask-size: contain !important;
}

:is(
    section[data-testid="stSidebar"] .st-key-language,
    .st-key-voice_language_selector
) div[data-baseweb="select"] > div::before {
    margin-right: 10px !important;
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M3 12h18M12 3c2.5 2.5 4 5.5 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.5-4-9s1.5-6.5 4-9Z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M3 12h18M12 3c2.5 2.5 4 5.5 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.5-4-9s1.5-6.5 4-9Z'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-nav_app button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 11.5 9-7.5 9 7.5M5.5 10v10h13V10M9.5 20v-6h5v6'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 11.5 9-7.5 9 7.5M5.5 10v10h13V10M9.5 20v-6h5v6'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-nav_gallery button p::before,
section[data-testid="stSidebar"] .st-key-generate_images [data-testid="stWidgetLabel"]::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='16' rx='2'/%3E%3Ccircle cx='8.5' cy='9' r='1.5'/%3E%3Cpath d='m3 17 5-5 4 4 3-3 6 6'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='16' rx='2'/%3E%3Ccircle cx='8.5' cy='9' r='1.5'/%3E%3Cpath d='m3 17 5-5 4 4 3-3 6 6'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-nav_marketplace button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 20V9h16v11M7 9V5h10v4M3 20h18'/%3E%3Cpath d='M8 13h3v3H8zM15 12v8M17.5 4.5 19 3M6.5 4.5 5 3'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 20V9h16v11M7 9V5h10v4M3 20h18'/%3E%3Cpath d='M8 13h3v3H8zM15 12v8M17.5 4.5 19 3M6.5 4.5 5 3'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-generate_images [data-baseweb="checkbox"] {
    align-items: center !important;
    background: transparent !important;
}

section[data-testid="stSidebar"] .st-key-generate_images [data-baseweb="checkbox"] > div:first-child {
    width: 40px !important;
    min-width: 40px !important;
    height: 19px !important;
    min-height: 19px !important;
    padding: 2px !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    display: inline-flex !important;
    align-items: center !important;
    vertical-align: middle !important;
    transform: translateY(-2px) !important;
    border: 1px solid rgba(217, 168, 79, 0.46) !important;
    border-radius: 999px !important;
    background: linear-gradient(
        180deg,
        rgba(12, 29, 45, 0.99) 0%,
        rgba(6, 17, 29, 0.99) 100%
    ) !important;
    box-shadow: inset 0 1px 0 rgba(255, 244, 210, 0.10) !important;
}

section[data-testid="stSidebar"] .st-key-generate_images [data-baseweb="checkbox"] > div:first-child > div {
    width: 14px !important;
    height: 14px !important;
    border-radius: 999px !important;
    background: #f3e7c4 !important;
    box-shadow: none !important;
    transform: translateX(0) !important;
}

section[data-testid="stSidebar"] .st-key-generate_images [data-baseweb="checkbox"]:has(input:checked) > div:first-child {
    border-color: rgba(234, 215, 164, 0.82) !important;
    background: linear-gradient(
        180deg,
        rgba(72, 57, 29, 0.98) 0%,
        rgba(22, 31, 39, 0.99) 52%,
        rgba(9, 21, 34, 0.99) 100%
    ) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 244, 210, 0.12),
        0 0 7px rgba(217, 168, 79, 0.10) !important;
}

section[data-testid="stSidebar"] .st-key-generate_images [data-baseweb="checkbox"]:has(input:checked) > div:first-child > div {
    background: #f0d99b !important;
    box-shadow: 0 0 6px rgba(234, 215, 164, 0.16) !important;
    transform: translateX(20px) !important;
}

section[data-testid="stSidebar"] .st-key-generate_images [data-baseweb="checkbox"]:focus-within {
    background: transparent !important;
}

section[data-testid="stSidebar"] .st-key-generate_images [data-baseweb="checkbox"] input:is(:focus, :focus-visible) {
    outline: none !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] .st-key-generate_images [data-testid="stWidgetLabel"] {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    color: #ead7a4 !important;
}

section[data-testid="stSidebar"] .st-key-generate_images [data-testid="stWidgetLabel"] p {
    color: #ead7a4 !important;
}

section[data-testid="stSidebar"] .st-key-previous_concepts [data-testid="stExpander"] summary p {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

section[data-testid="stSidebar"] .st-key-previous_concepts [data-testid="stExpander"] summary > span {
    position: relative !important;
    width: 100% !important;
}

section[data-testid="stSidebar"] .st-key-previous_concepts [data-testid="stExpander"] summary > span > span:first-child {
    position: absolute !important;
    right: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
}

section[data-testid="stSidebar"] .st-key-previous_concepts [data-testid="stExpander"] summary > span > div {
    width: calc(100% - 28px) !important;
    margin-left: 0 !important;
}

section[data-testid="stSidebar"] .st-key-previous_concepts [data-testid="stExpander"] summary p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 12a9 9 0 1 0 3-6.7M3 4v5h5M12 7v5l3 2'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 12a9 9 0 1 0 3-6.7M3 4v5h5M12 7v5l3 2'/%3E%3C/svg%3E") !important;
}

/* ---------- Unified SVG system for the remaining sidebar controls ---------- */

section[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]),
section[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]) p,
section[data-testid="stSidebar"] .sidebar-group-title--settings {
    color: #ead7a4 !important;
}

section[data-testid="stSidebar"] .st-key-nav_app [data-testid="stButton"] button p,
section[data-testid="stSidebar"] .st-key-nav_gallery [data-testid="stButton"] button p,
section[data-testid="stSidebar"] .st-key-nav_marketplace [data-testid="stButton"] button p,
section[data-testid="stSidebar"] .st-key-previous_concepts [data-testid="stExpander"] summary p,
section[data-testid="stSidebar"] .st-key-regenerate_idea [data-testid="stButton"] button p,
section[data-testid="stSidebar"] .st-key-voice_prompt [data-testid="stButton"] button p {
    color: #f3e7c4 !important;
}

section[data-testid="stSidebar"] .st-key-language div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] .st-key-nav_app [data-testid="stButton"] > button,
section[data-testid="stSidebar"] .st-key-nav_gallery [data-testid="stButton"] > button,
section[data-testid="stSidebar"] .st-key-nav_marketplace [data-testid="stButton"] > button,
section[data-testid="stSidebar"] .st-key-previous_concepts [data-testid="stExpander"] summary,
section[data-testid="stSidebar"] .st-key-regenerate_idea [data-testid="stButton"] > button,
section[data-testid="stSidebar"] .st-key-voice_prompt [data-testid="stButton"] > button,
.st-key-previous_concepts [class*="st-key-open_concept_"] button,
.st-key-previous_concepts [class*="st-key-favorite_concept_"] button,
.st-key-previous_concepts [class*="st-key-delete_concept_"] button {
    background: var(--control-background) !important;
    box-shadow: var(--control-depth) !important;
}

section[data-testid="stSidebar"] .st-key-nav_app [data-testid="stButton"] > button:hover,
section[data-testid="stSidebar"] .st-key-nav_gallery [data-testid="stButton"] > button:hover,
section[data-testid="stSidebar"] .st-key-nav_marketplace [data-testid="stButton"] > button:hover,
section[data-testid="stSidebar"] .st-key-regenerate_idea [data-testid="stButton"] > button:hover,
section[data-testid="stSidebar"] .st-key-voice_prompt [data-testid="stButton"] > button:hover {
    box-shadow:
        inset 0 1px 0 rgba(255, 235, 190, 0.06),
        inset 0 -1px 0 rgba(0, 0, 0, 0.28),
        0 8px 22px rgba(0, 0, 0, 0.20) !important;
}

section[data-testid="stSidebar"] .sidebar-group-title--settings,
section[data-testid="stSidebar"] .st-key-generate_idea button p,
section[data-testid="stSidebar"] .st-key-regenerate_idea button p,
section[data-testid="stSidebar"] .st-key-voice_prompt button p {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

section[data-testid="stSidebar"] .sidebar-group-title--settings::before,
section[data-testid="stSidebar"] .st-key-generate_idea button p::before,
section[data-testid="stSidebar"] .st-key-regenerate_idea button p::before,
section[data-testid="stSidebar"] .st-key-voice_prompt button p::before,
section[data-testid="stSidebar"] .mini-card-favorite,
section[data-testid="stSidebar"] .st-key-previous_concepts [class*="st-key-open_concept_"] button [data-testid="stMarkdownContainer"]::before,
section[data-testid="stSidebar"] .st-key-previous_concepts [class*="st-key-favorite_concept_"] button [data-testid="stMarkdownContainer"]::before,
section[data-testid="stSidebar"] .st-key-previous_concepts [class*="st-key-delete_concept_"] button [data-testid="stMarkdownContainer"]::before {
    content: "" !important;
    display: inline-block !important;
    width: 21px !important;
    min-width: 21px !important;
    height: 21px !important;
    flex: 0 0 21px !important;
    background-color: #ead7a4 !important;
    -webkit-mask-position: center !important;
    -webkit-mask-repeat: no-repeat !important;
    -webkit-mask-size: contain !important;
    mask-position: center !important;
    mask-repeat: no-repeat !important;
    mask-size: contain !important;
}

section[data-testid="stSidebar"] .sidebar-group-title--settings::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21h-4v-.08A1.7 1.7 0 0 0 9 19.37a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.63 15 1.7 1.7 0 0 0 3.08 14H3v-4h.08A1.7 1.7 0 0 0 4.63 9a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.63h.01A1.7 1.7 0 0 0 10 3.08V3h4v.08a1.7 1.7 0 0 0 1.03 1.55 1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.37 9v.01A1.7 1.7 0 0 0 20.92 10H21v4h-.08A1.7 1.7 0 0 0 19.4 15Z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21h-4v-.08A1.7 1.7 0 0 0 9 19.37a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.63 15 1.7 1.7 0 0 0 3.08 14H3v-4h.08A1.7 1.7 0 0 0 4.63 9a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.63h.01A1.7 1.7 0 0 0 10 3.08V3h4v.08a1.7 1.7 0 0 0 1.03 1.55 1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.37 9v.01A1.7 1.7 0 0 0 20.92 10H21v4h-.08A1.7 1.7 0 0 0 19.4 15Z'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-generate_idea button p::before {
    background-color: #1b1206 !important;
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 18h6M10 22h4M8.5 15.5A7 7 0 1 1 15.5 15.5c-.9.7-1.5 1.5-1.5 2.5h-4c0-1-.6-1.8-1.5-2.5Z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 18h6M10 22h4M8.5 15.5A7 7 0 1 1 15.5 15.5c-.9.7-1.5 1.5-1.5 2.5h-4c0-1-.6-1.8-1.5-2.5Z'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-regenerate_idea button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 11a8 8 0 1 0-2.34 5.66M20 4v7h-7'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 11a8 8 0 1 0-2.34 5.66M20 4v7h-7'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-voice_prompt button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='9' y='3' width='6' height='11' rx='3'/%3E%3Cpath d='M5 11a7 7 0 0 0 14 0M12 18v3M8 21h8'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='9' y='3' width='6' height='11' rx='3'/%3E%3Cpath d='M5 11a7 7 0 0 0 14 0M12 18v3M8 21h8'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .mini-card-favorite,
section[data-testid="stSidebar"] .st-key-previous_concepts [class*="st-key-favorite_concept_"] button [data-testid="stMarkdownContainer"]::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z'/%3E%3C/svg%3E") !important;
}

/* ---------- Gallery page ---------- */

.gallery-page-heading {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    margin: 12px 0 0.35rem !important;
    color: var(--gold) !important;
    font-family: "Cinzel", Georgia, serif !important;
    font-size: clamp(24px, 2.7vw, 34px) !important;
    font-weight: 700 !important;
    line-height: 1.15 !important;
    letter-spacing: 0.025em !important;
}

.gallery-page-heading > span:last-child {
    min-width: 0 !important;
    overflow-wrap: break-word !important;
}

.gallery-page-heading__icon {
    width: 30px !important;
    min-width: 30px !important;
    height: 30px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    color: #ead7a4 !important;
}

.gallery-page-heading__icon svg {
    width: 30px !important;
    height: 30px !important;
    display: block !important;
    fill: none !important;
    stroke: currentColor !important;
    stroke-width: 1.8 !important;
    stroke-linecap: round !important;
    stroke-linejoin: round !important;
}

.gallery-page-description {
    margin: 0 0 1.2rem !important;
    color: #c9c1b0 !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] h2,
body:has(.gallery-page-heading) [data-testid="stMain"] h3 {
    color: var(--gold) !important;
    font-family: "Cinzel", Georgia, serif !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] h4 {
    color: #f3e7c4 !important;
    font-family: "Cinzel", Georgia, serif !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] h3#generated-concepts,
body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stSelectbox"] label,
body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stSelectbox"] label p {
    color: #d6a84b !important;
    font-family: "Cinzel", Georgia, serif !important;
    font-size: 1.3rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
    letter-spacing: 0.025em !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
    border: 1px solid rgba(217,168,79,0.34) !important;
    border-radius: 10px !important;
    box-shadow: var(--control-depth) !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stSelectbox"] svg {
    color: #ead7a4 !important;
    fill: #ead7a4 !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stExpander"] {
    color: #f3e7c4 !important;
    background: linear-gradient(180deg, rgba(11,27,42,0.98) 0%, rgba(7,17,28,0.98) 100%) !important;
    border-color: rgba(217,168,79,0.34) !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stExpander"] summary {
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stExpander"] summary:hover {
    background: var(--control-hover-background) !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stExpander"] summary p,
body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stExpander"] summary svg {
    color: #f3e7c4 !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stExpanderDetails"] {
    color: #f3e7c4 !important;
    background: linear-gradient(180deg, rgba(11,27,42,0.72) 0%, rgba(7,17,28,0.78) 100%) !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stCaptionContainer"],
body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stCaptionContainer"] p {
    color: #c9c1b0 !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stImage"] {
    overflow: hidden !important;
    border: 1px solid rgba(217,168,79,0.30) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 0 rgba(255,235,190,0.04) !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stAlert"],
body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stCode"] {
    color: #f3e7c4 !important;
    background: linear-gradient(180deg, rgba(11,27,42,0.92) 0%, rgba(7,17,28,0.94) 100%) !important;
    border: 1px solid rgba(217,168,79,0.30) !important;
    border-radius: 11px !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stAlert"] p,
body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stCode"] code {
    color: #f3e7c4 !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] .st-key-gallery_empty_state {
    width: 100% !important;
    margin-top: 14px !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] .st-key-gallery_empty_state [data-testid="stAlert"] {
    width: 100% !important;
    height: 40px !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] .st-key-gallery_empty_state [data-testid="stAlertContainer"] {
    height: 38px !important;
    min-height: 38px !important;
    padding: 7px 16px !important;
    box-sizing: border-box !important;
    align-items: center !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] :is([data-testid="stButton"], [data-testid="stDownloadButton"]) > button {
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
    border-color: rgba(217,168,79,0.34) !important;
    box-shadow: var(--control-depth) !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] :is([data-testid="stButton"], [data-testid="stDownloadButton"]) > button:hover {
    background: var(--control-hover-background) !important;
    border-color: rgba(234,215,164,0.52) !important;
}

body:has(.gallery-page-heading) :is(
    a[data-testid="stSidebarNavLink"],
    button,
    summary,
    input,
    textarea
):is(:focus, :focus-visible) {
    outline: none !important;
}

body:has(.gallery-page-heading) :is(
    a[data-testid="stSidebarNavLink"],
    [data-testid="stMain"] button
):is(:focus, :focus-visible) {
    border-color: rgba(234,215,164,0.52) !important;
    box-shadow: var(--control-depth) !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-baseweb="select"]:focus-within {
    outline: none !important;
    box-shadow: none !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] [data-baseweb="select"]:focus-within > div {
    border-color: rgba(234,215,164,0.52) !important;
    box-shadow: var(--control-depth) !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] :is(
    [data-testid="stTextInputRootElement"],
    [data-testid="stTextAreaRootElement"]
):focus-within {
    border-color: transparent !important;
    outline: none !important;
    box-shadow: none !important;
}

body:has(.gallery-page-heading) [data-testid="stMain"] summary:is(:focus, :focus-visible) {
    box-shadow: none !important;
}

body:has(.gallery-page-heading) [class*="st-key-gallery_concept_"] [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    gap: 16px !important;
}

body:has(.gallery-page-heading) [class*="st-key-gallery_concept_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: 100% !important;
    min-width: 0 !important;
    flex: none !important;
}

@container main-content (max-width: 799px) {
    body:has(.gallery-page-heading) [class*="st-key-gallery_concept_"] [data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}

@container main-content (max-width: 559px) {
    body:has(.gallery-page-heading) [class*="st-key-gallery_concept_"] [data-testid="stHorizontalBlock"] {
        grid-template-columns: minmax(0, 1fr) !important;
    }
}

@media (max-width: 1169px) {
    body:has(.gallery-page-heading) [class*="st-key-gallery_concept_"] [data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}

@media (max-width: 849px) {
    body:has(.gallery-page-heading) [class*="st-key-gallery_concept_"] [data-testid="stHorizontalBlock"] {
        grid-template-columns: minmax(0, 1fr) !important;
    }
}

/* ---------- Investor Marketplace ---------- */

@keyframes marketplace-page-enter {
    from { opacity: 0; }
    to { opacity: 1; }
}

.marketplace-page {
    margin-top: 12px;
}

.marketplace-page__heading {
    display: flex;
    align-items: center;
    gap: 12px;
}

.marketplace-page__heading h1 {
    margin: 0;
    color: #d6a84b;
    font-family: "Cinzel", Georgia, serif;
    font-size: clamp(24px, 2.7vw, 34px);
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: 0.025em;
}

.marketplace-page__heading-icon {
    width: 30px;
    height: 30px;
    flex: 0 0 30px;
    color: #ead7a4;
}

.marketplace-page__heading-icon svg,
.marketplace-card__image svg {
    width: 100%;
    height: 100%;
    display: block;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.marketplace-page__subtitle {
    margin: 0.35rem 0 1.2rem;
    color: #c9c1b0;
    font-size: 16px;
    font-weight: 500;
    line-height: 1.4;
}

.st-key-marketplace_toolbar > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) 150px !important;
    gap: 12px !important;
    align-items: center !important;
}

.st-key-marketplace_toolbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: 100% !important;
    min-width: 0 !important;
    flex: none !important;
}

.st-key-marketplace_toolbar [data-testid="stTextInputRootElement"] {
    min-height: 40px;
    color: #f3e7c4;
    background: var(--control-background);
    border: 1px solid rgba(217,168,79,0.34);
    border-radius: 10px;
    box-shadow: var(--control-depth);
}

.st-key-marketplace_toolbar [data-testid="stTextInputRootElement"] input {
    color: #f3e7c4;
    background: transparent;
}

.st-key-marketplace_toolbar [data-testid="stTextInputRootElement"] input::placeholder {
    color: #a8b3c3;
    opacity: 1;
}

.st-key-marketplace_toolbar [data-testid="stTextInputRootElement"]:focus-within {
    outline: none;
    border-color: rgba(234,215,164,0.52);
    box-shadow: var(--control-depth);
}

.st-key-marketplace_filters_button [data-testid="stButton"] > button {
    min-height: 40px !important;
    height: 40px !important;
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
    border: 1px solid rgba(217,168,79,0.34) !important;
    border-radius: 10px !important;
    box-shadow: var(--control-depth) !important;
}

.st-key-marketplace_grid [data-testid="stButton"] button {
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
    border: 1px solid rgba(217,168,79,0.34) !important;
    border-radius: 10px !important;
    box-shadow: var(--control-depth) !important;
}

.st-key-marketplace_filters_button [data-testid="stButton"] > button:hover,
.st-key-marketplace_grid [data-testid="stButton"] button:hover {
    background: var(--control-hover-background) !important;
    border-color: rgba(234,215,164,0.52) !important;
}

.st-key-marketplace_filters_button [data-testid="stButton"] > button:is(:focus, :focus-visible),
.st-key-marketplace_grid [data-testid="stButton"] button:is(:focus, :focus-visible) {
    outline: none !important;
    box-shadow: var(--control-depth) !important;
}

.st-key-marketplace_category [data-testid="stButtonGroup"] {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.st-key-marketplace_filter_panel {
    width: 100%;
    margin-top: 12px;
}

.st-key-marketplace_category [data-testid="stButtonGroup"] button,
div.st-key-marketplace_active_category div[data-testid="stButton"] > button {
    width: auto !important;
    min-height: 32px !important;
    height: 32px !important;
    padding: 0 13px !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    color: #c9c1b0 !important;
    background: linear-gradient(180deg, rgba(13,38,60,0.92), rgba(7,25,42,0.96)) !important;
    border: 1px solid rgba(79,168,255,0.30) !important;
    border-radius: 999px !important;
    box-shadow: inset 0 1px 0 rgba(207,234,255,0.035) !important;
}

.st-key-marketplace_category [data-testid="stButtonGroup"] button[kind="segmented_controlActive"],
div.st-key-marketplace_active_category div[data-testid="stButton"] > button[kind="primary"] {
    color: #f3e7c4 !important;
    background: linear-gradient(180deg, rgba(92,66,27,0.98), rgba(42,31,19,0.98)) !important;
    border-color: rgba(234,215,164,0.62) !important;
}

.st-key-marketplace_active_category {
    margin-top: 12px;
}

div.st-key-marketplace_active_category div[data-testid="stButton"] > button {
    width: fit-content !important;
}

div.st-key-marketplace_active_category div[data-testid="stButton"] > button:is(:hover, :focus, :focus-visible),
.st-key-marketplace_category [data-testid="stButtonGroup"] button:is(:hover, :focus, :focus-visible) {
    outline: none !important;
    transform: none !important;
    border-color: rgba(234,215,164,0.52) !important;
    box-shadow: inset 0 1px 0 rgba(207,234,255,0.035) !important;
}

.st-key-marketplace_grid {
    margin-top: 18px;
}

.st-key-marketplace_grid [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    gap: 16px !important;
    align-items: stretch !important;
}

.st-key-marketplace_grid [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: 100% !important;
    min-width: 0 !important;
    height: 100% !important;
    display: flex !important;
    flex: none !important;
    padding: 14px !important;
    background: linear-gradient(180deg, rgba(13,38,60,0.96), rgba(7,25,42,0.98)) !important;
    border: 1px solid rgba(79,168,255,0.36) !important;
    border-radius: 14px !important;
    box-shadow:
        inset 0 1px 0 rgba(207,234,255,0.035),
        0 8px 20px rgba(0,0,0,0.20) !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

.st-key-marketplace_grid [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div,
.st-key-marketplace_grid [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] [data-testid="stVerticalBlock"] {
    width: 100% !important;
    min-width: 0 !important;
    height: 100% !important;
}

.st-key-marketplace_grid [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] [data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
}

.marketplace-card__content {
    display: flex;
    flex: 1 1 auto;
    min-width: 0;
    flex-direction: column;
}

.marketplace-card__image {
    width: 100%;
    aspect-ratio: 1 / 1;
    display: grid;
    place-items: center;
    overflow: hidden;
    color: #82BEF8;
    background:
        radial-gradient(circle at 70% 25%, rgba(79,168,255,0.13), transparent 34%),
        linear-gradient(145deg, rgba(10,31,51,0.98), rgba(5,18,31,0.98));
    border: 1px solid rgba(79,168,255,0.30);
    border-radius: 10px;
    box-sizing: border-box;
}

.marketplace-card__image span {
    width: 52px;
    height: 52px;
    opacity: 0.72;
}

.marketplace-card__image img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
}

.marketplace-card__identity {
    min-height: 62px;
    margin-top: 12px;
}

.marketplace-card__identity h3 {
    margin: 0;
    color: #ead7a4;
    font-family: "Cinzel", Georgia, serif;
    font-size: 18px;
    font-weight: 600;
    line-height: 1.25;
    display: -webkit-box;
    overflow: hidden;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
}

.marketplace-card__identity p {
    margin: 4px 0 0;
    color: #82BEF8;
    font-size: 12px;
    line-height: 1.3;
}

.marketplace-card__summary {
    min-height: 63px;
    margin: 0 0 12px;
    color: #f3e7c4;
    font-size: 13px;
    line-height: 1.55;
    display: -webkit-box;
    overflow: hidden;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
}

.marketplace-card__meta {
    min-height: 68px;
    display: grid;
    gap: 7px;
    color: #c9c1b0;
    font-size: 12px;
    line-height: 1.35;
}

.marketplace-card__meta span,
.marketplace-card__meta strong {
    display: block;
}

.marketplace-card__meta strong {
    margin-bottom: 2px;
    color: #82BEF8;
    font-weight: 600;
}

.marketplace-card__tags {
    min-height: 58px;
    display: flex;
    align-content: flex-start;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 12px;
}

.marketplace-card__tag {
    height: 24px;
    padding: 0 9px;
    display: inline-flex;
    align-items: center;
    color: #c9c1b0;
    background: rgba(79,168,255,0.08);
    border: 1px solid rgba(79,168,255,0.24);
    border-radius: 999px;
    font-size: 11px;
    line-height: 1;
    box-sizing: border-box;
}

.st-key-marketplace_grid [data-testid="stButton"] {
    margin-top: auto !important;
    padding-top: 10px !important;
}

.marketplace-empty {
    margin-top: 18px;
    padding: 18px 20px;
    color: #c9c1b0;
    background: linear-gradient(180deg, rgba(13,38,60,0.92), rgba(7,25,42,0.96));
    border: 1px solid rgba(79,168,255,0.30);
    border-radius: 12px;
}

.st-key-marketplace_project_back {
    width: fit-content;
    margin: 0 0 16px;
    margin-top: 12px !important;
}

.st-key-marketplace_project_back [data-testid="stButton"] > button {
    width: fit-content !important;
    min-height: 36px !important;
    padding: 0 14px !important;
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
    border: 1px solid rgba(217,168,79,0.34) !important;
    border-radius: 10px !important;
    box-shadow: var(--control-depth) !important;
}

.st-key-marketplace_project_back [data-testid="stMarkdownContainer"] p {
    display: flex;
    align-items: center;
    gap: 8px;
}

.st-key-marketplace_project_back [data-testid="stMarkdownContainer"] p::before {
    content: "";
    width: 18px;
    height: 18px;
    flex: 0 0 18px;
    background: #ead7a4;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m15 18-6-6 6-6M9 12h11'/%3E%3C/svg%3E") center / contain no-repeat;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m15 18-6-6 6-6M9 12h11'/%3E%3C/svg%3E") center / contain no-repeat;
}

.st-key-marketplace_project_back [data-testid="stButton"] > button:hover {
    transform: none !important;
    background: var(--control-hover-background) !important;
    border-color: rgba(234,215,164,0.52) !important;
    box-shadow: var(--control-depth) !important;
}

.st-key-marketplace_project_back [data-testid="stButton"] > button:is(:focus, :focus-visible) {
    outline: none !important;
    box-shadow: var(--control-depth) !important;
}

.marketplace-project-page {
    min-width: 0;
    padding-bottom: 24px;
}

.marketplace-project-page--without-meta {
    padding-top: 40px;
}

.marketplace-project-header h1 {
    margin: 0;
    color: #d6a84b;
    font-family: "Cinzel", Georgia, serif;
    font-size: clamp(28px, 3vw, 40px);
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: 0.025em;
}

.marketplace-project-header__category {
    margin-top: 7px;
    color: #82BEF8;
    font-size: 13px;
    font-weight: 600;
}

.marketplace-project-header > p {
    max-width: 820px;
    margin: 12px 0 20px;
    color: #f3e7c4;
    font-size: 16px;
    line-height: 1.55;
}

.marketplace-project-hero {
    width: 100%;
    height: clamp(240px, 34vw, 420px);
    display: grid;
    place-items: center;
    position: relative;
    overflow: hidden;
    color: #82BEF8;
    background:
        radial-gradient(circle at 70% 28%, rgba(79,168,255,0.14), transparent 32%),
        linear-gradient(145deg, rgba(10,31,51,0.98), rgba(5,18,31,0.99));
    border: 1px solid rgba(79,168,255,0.36);
    border-radius: 14px;
    box-shadow:
        inset 0 1px 0 rgba(207,234,255,0.045),
        0 8px 24px rgba(0,0,0,0.20);
    box-sizing: border-box;
}

.st-key-marketplace_project_carousel {
    position: relative;
    min-width: 0;
}

.marketplace-project-carousel__current {
    position: absolute;
    inset: 16px auto;
    left: 50%;
    width: min(62%, 560px);
    z-index: 2;
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: minmax(0, 1fr);
    place-items: center;
    transform: translateX(-50%);
    box-sizing: border-box;
    animation: marketplace-page-enter 150ms ease-out both;
}

.marketplace-project-carousel__preview {
    width: auto !important;
    height: auto !important;
    max-width: 36%;
    max-height: 70%;
    position: absolute;
    top: 50%;
    z-index: 1;
    transform: translateY(-50%);
    display: block;
    object-fit: contain !important;
    opacity: 0.42;
    filter: blur(2px) brightness(0.58);
    background: rgba(3,14,25,0.92);
    border: 1px solid rgba(79,168,255,0.30);
    border-radius: 12px;
    box-sizing: border-box;
}

.marketplace-project-carousel__preview--previous {
    left: -18%;
}

.marketplace-project-carousel__preview--next {
    right: -18%;
}

.marketplace-project-carousel__current img {
    width: auto !important;
    height: auto !important;
    max-width: 100%;
    max-height: 100%;
    display: block;
    object-fit: contain !important;
    background: rgba(3,14,25,0.92);
    border: 1px solid rgba(79,168,255,0.30);
    border-radius: 12px;
    box-shadow:
        inset 0 1px 0 rgba(207,234,255,0.06),
        0 8px 24px rgba(0,0,0,0.24);
    box-sizing: border-box;
}

.st-key-marketplace_project_carousel [data-testid="stHorizontalBlock"] {
    width: 100% !important;
    height: clamp(240px, 34vw, 420px) !important;
    padding: 0 14px !important;
    position: absolute !important;
    inset: 0 !important;
    z-index: 3;
    align-items: center !important;
    pointer-events: none;
    box-sizing: border-box;
}

.st-key-marketplace_project_carousel [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    pointer-events: none;
}

.st-key-marketplace_project_carousel [class*="st-key-marketplace_carousel_"] {
    pointer-events: auto;
}

.st-key-marketplace_project_carousel [class*="st-key-marketplace_carousel_"] button {
    width: 38px !important;
    min-width: 38px !important;
    height: 38px !important;
    min-height: 38px !important;
    padding: 0 !important;
    color: #ead7a4 !important;
    background: var(--control-background) !important;
    border: 1px solid rgba(217,168,79,0.42) !important;
    border-radius: 999px !important;
    box-shadow: var(--control-depth) !important;
}

.st-key-marketplace_project_carousel [class*="st-key-marketplace_carousel_"] button:hover {
    transform: none !important;
    background: var(--control-hover-background) !important;
    border-color: rgba(234,215,164,0.58) !important;
}

.st-key-marketplace_project_carousel [class*="st-key-marketplace_carousel_"] button:is(:focus, :focus-visible) {
    outline: none !important;
    box-shadow: var(--control-depth) !important;
}

.st-key-marketplace_project_carousel [class*="st-key-marketplace_carousel_"] [data-testid="stMarkdownContainer"]::before {
    content: "";
    width: 20px;
    height: 20px;
    display: block;
    background: #ead7a4;
    -webkit-mask: var(--marketplace-carousel-arrow) center / contain no-repeat;
    mask: var(--marketplace-carousel-arrow) center / contain no-repeat;
}

.st-key-marketplace_project_carousel [class*="st-key-marketplace_carousel_previous_"] {
    --marketplace-carousel-arrow: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m15 18-6-6 6-6'/%3E%3C/svg%3E");
}

.st-key-marketplace_project_carousel [class*="st-key-marketplace_carousel_next_"] {
    --marketplace-carousel-arrow: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m9 18 6-6-6-6'/%3E%3C/svg%3E");
}

.marketplace-project-carousel__indicator {
    margin-top: 8px;
    color: #c9c1b0;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.2;
    text-align: center;
}

.marketplace-project-hero > span {
    width: clamp(58px, 7vw, 86px);
    height: clamp(58px, 7vw, 86px);
    opacity: 0.68;
}

.marketplace-project-hero svg,
.marketplace-project-section__icon svg {
    width: 100%;
    height: 100%;
    display: block;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.marketplace-project-meta {
    margin: 16px 0 24px;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.marketplace-project-meta > div {
    min-width: 0;
    padding: 12px 14px;
    background: linear-gradient(180deg, rgba(13,38,60,0.94), rgba(7,25,42,0.97));
    border: 1px solid rgba(79,168,255,0.30);
    border-radius: 10px;
    box-shadow: inset 0 1px 0 rgba(207,234,255,0.035);
}

.marketplace-project-meta span,
.marketplace-project-meta strong {
    display: block;
}

.marketplace-project-meta span {
    color: #82BEF8;
    font-size: 12px;
    font-weight: 600;
}

.marketplace-project-meta strong {
    margin-top: 4px;
    color: #f3e7c4;
    font-size: 13px;
    font-weight: 500;
    line-height: 1.35;
}

.marketplace-project-section-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.marketplace-project-section {
    min-width: 0;
    margin: 0 0 16px;
    display: flex;
    flex-direction: column;
}

.marketplace-project-section > h2 {
    margin: 0 0 9px;
    display: flex;
    align-items: center;
    gap: 9px;
    color: #d6a84b;
    font-family: "Cinzel", Georgia, serif;
    font-size: 20px;
    font-weight: 600;
    line-height: 1.25;
    letter-spacing: 0.02em;
}

.marketplace-project-section > h2 > span:first-child {
    display: flex;
    align-items: center;
    gap: 9px;
}

.marketplace-project-section__icon {
    width: 24px;
    height: 24px;
    display: inline-flex;
    flex: 0 0 24px;
    color: #ead7a4;
}

.marketplace-project-section__icon svg {
    width: 24px !important;
    height: 24px !important;
    flex: 0 0 24px;
}

.marketplace-project-section__body {
    flex: 1;
    padding: 15px 17px;
    color: #f3e7c4;
    background: linear-gradient(180deg, rgba(13,38,60,0.94), rgba(7,25,42,0.98));
    border: 1px solid rgba(79,168,255,0.36);
    border-radius: 12px;
    box-shadow: inset 0 1px 0 rgba(207,234,255,0.04);
    box-sizing: border-box;
}

.marketplace-project-section__body p,
.marketplace-project-section__body ul {
    margin: 0;
    color: #f3e7c4;
    font-size: 14px;
    line-height: 1.55;
}

.marketplace-project-section__body ul {
    padding-left: 19px;
}

.marketplace-project-section__body li + li {
    margin-top: 6px;
}

@container main-content (max-width: 1039px) {
    .st-key-marketplace_grid [data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}

@container main-content (max-width: 699px) {
    .st-key-marketplace_toolbar > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"],
    .st-key-marketplace_grid [data-testid="stHorizontalBlock"] {
        grid-template-columns: minmax(0, 1fr) !important;
    }

    .marketplace-project-meta,
    .marketplace-project-section-grid {
        grid-template-columns: minmax(0, 1fr);
    }

    .marketplace-project-carousel__preview {
        display: none;
    }

    .marketplace-project-carousel__current {
        width: calc(100% - 84px);
    }
}

@media (max-width: 1409px) {
    .st-key-marketplace_grid [data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}

@media (max-width: 1069px) {
    .st-key-marketplace_toolbar > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"],
    .st-key-marketplace_grid [data-testid="stHorizontalBlock"] {
        grid-template-columns: minmax(0, 1fr) !important;
    }

    .marketplace-project-meta,
    .marketplace-project-section-grid {
        grid-template-columns: minmax(0, 1fr);
    }

    .marketplace-project-carousel__preview {
        display: none;
    }

    .marketplace-project-carousel__current {
        width: calc(100% - 84px);
    }
}

section[data-testid="stSidebar"] .st-key-previous_concepts [class*="st-key-open_concept_"] button [data-testid="stMarkdownContainer"]::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 7h7l2 2h9v10H3V7ZM3 7V5h7l2 2'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 7h7l2 2h9v10H3V7ZM3 7V5h7l2 2'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-previous_concepts [class*="st-key-delete_concept_"] button [data-testid="stMarkdownContainer"]::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 7h16M9 3h6l1 4H8l1-4ZM6 7l1 14h10l1-14M10 11v6M14 11v6'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 7h16M9 3h6l1 4H8l1-4ZM6 7l1 14h10l1-14M10 11v6M14 11v6'/%3E%3C/svg%3E") !important;
}

/* ---------- Generated Concept image panel ---------- */

.st-key-generated_concept_panel .concept-empty-image-box {
    position: relative !important;
    width: 100% !important;
    max-width: 100% !important;
    height: auto !important;
    min-height: 0 !important;
    aspect-ratio: 8 / 1;
    container-type: inline-size;
    display: grid !important;
    grid-template-columns: minmax(0, 58cqw) minmax(0, 42cqw);
    align-items: center;
    border: 1px solid rgba(217,168,79,0.42) !important;
    border-radius: 16px !important;
    margin-bottom: 1.35rem !important;
    overflow: hidden !important;
    background: #06111f !important;
    box-shadow: inset 0 0 28px rgba(217,168,79,0.08), 0 8px 24px rgba(0,0,0,0.24) !important;
}

.st-key-generated_concept_panel .concept-empty-image {
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    max-width: none !important;
    object-fit: cover !important;
    object-position: center !important;
    z-index: 0 !important;
}

.st-key-generated_concept_panel .concept-empty-image-box::after {
    content: "" !important;
    position: absolute !important;
    inset: 0 !important;
    background: linear-gradient(
        90deg,
        rgba(3, 11, 21, 0.96) 0%,
        rgba(4, 14, 26, 0.90) 36%,
        rgba(5, 17, 31, 0.56) 54%,
        rgba(5, 17, 31, 0.08) 82%,
        transparent 100%
    ) !important;
    z-index: 1 !important;
}

.st-key-generated_concept_panel .concept-empty-text {
    position: relative !important;
    z-index: 2 !important;
    grid-column: 1;
    width: 58cqw;
    max-width: none !important;
    padding: 1.5cqw 2.4cqw !important;
    box-sizing: border-box;
}

.st-key-generated_concept_panel .concept-panel-line {
    max-width: none !important;
    color: #f4d28a !important;
    font-family: "Cinzel", Georgia, serif !important;
    font-size: 1.55cqw !important;
    font-weight: 600 !important;
    line-height: 1.25 !important;
    text-align: left !important;
    white-space: nowrap !important;
    margin: 0 !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.75) !important;
}

/* ---------- Feature cards ---------- */

.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    column-gap: 6px;
    row-gap: 8px;
    align-items: stretch;
    margin-bottom: 22px;
}

.feature-card {
    min-height: 58px !important;
    height: auto !important;
    line-height: 1.3 !important;
    padding: 8px 12px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    margin-bottom: 0 !important;

    background: linear-gradient(
        180deg,
        rgba(14, 32, 49, 0.88) 0%,
        rgba(10, 25, 40, 0.88) 58%,
        rgba(7, 20, 34, 0.88) 100%
    ) !important;
    border: 1px solid rgba(217,168,79,0.22) !important;
    border-radius: 13px !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 235, 190, 0.035),
        inset 0 -1px 0 rgba(0, 0, 0, 0.16) !important;
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
    color: #ead7a4 !important;
}

.feature-icon svg {
    width: 23px !important;
    height: 23px !important;
    display: block !important;
    fill: none !important;
    stroke: currentColor !important;
    stroke-width: 1.8 !important;
    stroke-linecap: round !important;
    stroke-linejoin: round !important;
}

.feature-text {
    margin-top: 0 !important;
    line-height: 1.25 !important;
    color: #a8b3c3 !important;
    font-size: 12px !important;
    min-width: 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Viewport fallback for the home feature grid. */
@media (max-width: 1409px) {
    .feature-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 1129px) {
    .feature-grid {
        grid-template-columns: minmax(0, 1fr);
    }
}

/* Main content-box thresholds keep three-column cards above roughly 323px
   and two-column cards above roughly 352px before reflowing. */
@container main-content (max-width: 999px) {
    .st-key-generated_concept_panel .concept-empty-image-box::after {
        background: linear-gradient(
            90deg,
            rgba(3, 11, 21, 0.98) 0%,
            rgba(4, 14, 26, 0.94) 50%,
            rgba(5, 17, 31, 0.62) 72%,
            rgba(5, 17, 31, 0.24) 100%
        ) !important;
    }

    .feature-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@container main-content (max-width: 719px) {
    .st-key-generated_concept_panel .concept-empty-image-box::after {
        background: linear-gradient(
            90deg,
            rgba(3, 11, 21, 0.99) 0%,
            rgba(4, 14, 26, 0.96) 56%,
            rgba(5, 17, 31, 0.76) 78%,
            rgba(5, 17, 31, 0.52) 100%
        ) !important;
    }

    .feature-grid {
        grid-template-columns: minmax(0, 1fr);
    }
}

/* ---------- Generated-result sections ---------- */

.st-key-previous_concepts [data-testid="stHorizontalBlock"] {
    width: 100% !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-top: 10px !important;
}

.st-key-previous_concepts [class*="st-key-open_concept_"] button,
.st-key-previous_concepts [class*="st-key-favorite_concept_"] button,
.st-key-previous_concepts [class*="st-key-delete_concept_"] button {
    width: 74% !important;
    min-height: 32px !important;
    height: 32px !important;
    padding: 2px 6px !important;
    font-size: 0.8rem !important;
    line-height: 1 !important;
    color: #f3e7c4 !important;
    border-color: rgba(217,168,79,0.34) !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

.st-key-previous_concepts [class*="st-key-open_concept_"] button:hover,
.st-key-previous_concepts [class*="st-key-favorite_concept_"] button:hover,
.st-key-previous_concepts [class*="st-key-delete_concept_"] button:hover {
    transform: none !important;
    background: var(--control-hover-background) !important;
    border-color: rgba(234, 215, 164, 0.52) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 235, 190, 0.08),
        inset 0 -1px 0 rgba(0, 0, 0, 0.24) !important;
}

.st-key-previous_concepts [class*="st-key-open_concept_"] button {
    margin-left: 0 !important;
}

.st-key-previous_concepts [class*="st-key-delete_concept_"] button {
    margin-right: 0 !important;
}

.st-key-previous_concepts [class*="st-key-open_concept_"] button [data-testid="stMarkdownContainer"],
.st-key-previous_concepts [class*="st-key-favorite_concept_"] button [data-testid="stMarkdownContainer"],
.st-key-previous_concepts [class*="st-key-delete_concept_"] button [data-testid="stMarkdownContainer"] {
    font-size: 0.64rem !important;
    line-height: 1 !important;
}

.st-key-leonardo_section,
.st-key-modern_section {
    position: relative !important;
    isolation: isolate !important;
    width: 100% !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    border-radius: 20px !important;
    padding: 26px 28px 28px !important;
}

.st-key-leonardo_section {
    margin-top: 26px !important;
    margin-bottom: 0 !important;
    color: #F2E4C6 !important;
    background:
        radial-gradient(circle at 18% 0%, rgba(200,154,82,0.12), transparent 34%),
        linear-gradient(145deg, #2A1C12 0%, #20140D 56%, #17100A 100%) !important;
    border: 1px solid rgba(200,154,82,0.55) !important;
    box-shadow:
        inset 0 0 32px rgba(200,154,82,0.045),
        0 14px 34px rgba(0,0,0,0.24) !important;
}

.st-key-leonardo_section::before,
.st-key-modern_section::before {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
}

.st-key-leonardo_section::before {
    opacity: 0.24;
    background-image:
        radial-gradient(rgba(242,228,198,0.09) 0.65px, transparent 0.65px),
        linear-gradient(110deg, transparent 0%, rgba(200,154,82,0.055) 48%, transparent 74%);
    background-size: 7px 7px, 100% 100%;
}

.st-key-leonardo_section > *,
.st-key-modern_section > * {
    position: relative;
    z-index: 1;
}

.st-key-leonardo_section h2 {
    color: #E2B86F !important;
    font-family: "Cinzel", Georgia, serif !important;
    letter-spacing: 0.025em !important;
    margin-top: 0 !important;
    margin-bottom: 10px !important;
}

.st-key-leonardo_section .leonardo-section-heading {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

.st-key-leonardo_section .leonardo-section-heading__icon {
    display: inline-flex;
    width: 29px;
    height: 29px;
    flex: 0 0 29px;
    color: #ead7a4;
}

.st-key-leonardo_section .leonardo-section-heading__icon svg,
.st-key-leonardo_section .result-title-icon svg {
    display: block;
    width: 100%;
    height: 100%;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.st-key-leonardo_section [data-testid="stCaptionContainer"],
.st-key-leonardo_section [data-testid="stCaptionContainer"] p {
    color: #CDBB98 !important;
    margin-bottom: 6px !important;
}

.st-key-leonardo_section [data-testid="stHorizontalBlock"],
.st-key-modern_section [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 350px)) !important;
    justify-content: center !important;
    align-items: start !important;
    gap: 16px !important;
    margin-top: 18px !important;
    margin-bottom: 22px !important;
}

.st-key-leonardo_section [data-testid="stAlert"] {
    color: #EAD9B7 !important;
    background: rgba(80,51,29,0.58) !important;
    border: 1px solid rgba(200,154,82,0.34) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 0 18px rgba(200,154,82,0.035) !important;
}

.st-key-leonardo_section [data-testid="stAlert"] p {
    color: #EAD9B7 !important;
}

.st-key-leonardo_section .result-box {
    margin: 16px 0 !important;
    padding: 18px 20px !important;
    color: #F2E4C6 !important;
    background: linear-gradient(
        180deg,
        rgba(77,43,25,0.96) 0%,
        rgba(58,31,19,0.98) 100%
    ) !important;
    border: 1px solid rgba(200,154,82,0.46) !important;
    border-radius: 14px !important;
    box-shadow:
        inset 0 1px 0 rgba(255,238,201,0.035),
        0 8px 20px rgba(0,0,0,0.18) !important;
}

.st-key-leonardo_section .result-title {
    color: #DDB36A !important;
    display: flex;
    align-items: center;
    gap: 8px;
}

.st-key-leonardo_section .result-title-icon {
    display: inline-flex;
    width: 19px;
    height: 19px;
    flex: 0 0 19px;
    color: #ead7a4;
}

.st-key-leonardo_section .result-text,
.st-key-leonardo_section .result-text p,
.st-key-leonardo_section .result-text li {
    color: #F5E9CE !important;
}

.st-key-modern_section {
    margin-top: 28px !important;
    margin-bottom: 30px !important;
    color: #EEF6FF !important;
    background:
        radial-gradient(circle at 82% 0%, rgba(79,168,255,0.10), transparent 34%),
        linear-gradient(145deg, #0C1E31 0%, #091726 56%, #06121D 100%) !important;
    border: 1px solid rgba(79,168,255,0.40) !important;
    box-shadow:
        inset 0 0 34px rgba(79,168,255,0.035),
        0 14px 34px rgba(0,0,0,0.25) !important;
}

.st-key-modern_section::before {
    opacity: 0.18;
    background-image:
        linear-gradient(rgba(79,168,255,0.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(79,168,255,0.12) 1px, transparent 1px);
    background-size: 36px 36px;
}

.st-key-modern_section h2 {
    margin-top: 12px !important;
    margin-bottom: 10px !important;
}

.st-key-modern_section .modern-section-heading {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

.st-key-modern_section .modern-section-heading__icon {
    display: inline-flex;
    width: 29px;
    height: 29px;
    flex: 0 0 29px;
    color: #82BEF8;
}

.st-key-modern_section .modern-section-heading__icon svg,
.st-key-modern_section .result-title-icon svg {
    display: block;
    width: 100%;
    height: 100%;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.st-key-modern_section [data-testid="stCaptionContainer"],
.st-key-modern_section [data-testid="stCaptionContainer"] p {
    color: #A9BED3 !important;
    margin-bottom: 6px !important;
}

.st-key-leonardo_section [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-modern_section [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: 100% !important;
    min-width: 0 !important;
    max-width: 350px !important;
    flex: none !important;
}

.st-key-leonardo_section [data-testid="stMarkdownContainer"]:has(.concept-image-slot),
.st-key-modern_section [data-testid="stMarkdownContainer"]:has(.concept-image-slot) {
    margin-bottom: 0 !important;
}

.st-key-leonardo_section .concept-image-slot,
.st-key-modern_section .concept-image-slot {
    width: 100%;
    max-width: 350px;
    aspect-ratio: 1 / 1;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16px;
    overflow: hidden;
    border-radius: 12px;
    text-align: center;
    margin-left: auto;
    margin-right: auto;
}

.st-key-leonardo_section .concept-image-slot > img,
.st-key-modern_section .concept-image-slot > img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.st-key-leonardo_section .concept-image-slot {
    color: #EAD9B7;
    background: rgba(80,51,29,0.58);
    border: 1px solid rgba(214,168,75,0.55);
    box-shadow:
        inset 0 1px 0 rgba(255,235,190,0.10),
        0 5px 14px rgba(0,0,0,0.28);
}

.st-key-modern_section .concept-image-slot {
    color: #DCEEFF;
    background: rgba(12,35,56,0.76);
    border: 1px solid rgba(79,170,235,0.50);
    box-shadow:
        inset 0 1px 0 rgba(190,225,255,0.09),
        0 5px 14px rgba(0,0,0,0.25);
}

.st-key-modern_section [data-testid="stAlert"] {
    color: #DCEEFF !important;
    background: rgba(12,35,56,0.76) !important;
    border: 1px solid rgba(79,168,255,0.30) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 0 18px rgba(79,168,255,0.035) !important;
}

.st-key-modern_section [data-testid="stAlert"] p {
    color: #DCEEFF !important;
}

.st-key-modern_section .result-box {
    margin: 16px 0 !important;
    padding: 18px 20px !important;
    color: #EEF6FF !important;
    background: linear-gradient(
        180deg,
        rgba(13,38,60,0.96) 0%,
        rgba(7,25,42,0.98) 100%
    ) !important;
    border: 1px solid rgba(79,168,255,0.36) !important;
    border-radius: 14px !important;
    box-shadow:
        inset 0 1px 0 rgba(207,234,255,0.035),
        0 8px 20px rgba(0,0,0,0.20),
        0 0 18px rgba(79,168,255,0.025) !important;
}

.st-key-modern_section .result-title {
    color: #75B8F5 !important;
    display: flex;
    align-items: center;
    gap: 8px;
}

.st-key-modern_section .result-title-icon {
    display: inline-flex;
    width: 19px;
    height: 19px;
    flex: 0 0 19px;
    color: #82BEF8;
}

.st-key-modern_section .result-text,
.st-key-modern_section .result-text p,
.st-key-modern_section .result-text li {
    color: #F2EADB !important;
}

/* ---------- Main visual grid responsive geometry ---------- */

/* Viewport fallback for browsers without container queries. */
@media (max-width: 1549px) {
    .st-key-leonardo_section [data-testid="stHorizontalBlock"],
    .st-key-modern_section [data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(2, minmax(0, 350px)) !important;
    }
}

@media (max-width: 1183px) {
    .st-key-leonardo_section [data-testid="stHorizontalBlock"],
    .st-key-modern_section [data-testid="stHorizontalBlock"] {
        grid-template-columns: minmax(0, min(350px, 100%)) !important;
    }
}

/* The main content-box thresholds include each section's 28px side padding,
   1px borders, and the 16px gaps between 350px image cards. */
@container main-content (max-width: 1139px) {
    .st-key-leonardo_section [data-testid="stHorizontalBlock"],
    .st-key-modern_section [data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(2, minmax(0, 350px)) !important;
    }
}

@container main-content (max-width: 773px) {
    .st-key-leonardo_section [data-testid="stHorizontalBlock"],
    .st-key-modern_section [data-testid="stHorizontalBlock"] {
        grid-template-columns: minmax(0, min(350px, 100%)) !important;
    }
}

</style>
"""


def apply_global_styles():
    st.markdown(
        GLOBAL_CSS,
        unsafe_allow_html=True,
    )
