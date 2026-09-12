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
body:not(:has(.gallery-page-heading)) [data-testid="stSidebarNav"],
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
    background: rgba(248,250,252,0.96);
    border: 1px solid #dbe3ec;
    margin-top: 12px;
    margin-bottom: 12px;
    color: #111827;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    overflow-wrap: anywhere;
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
    font-weight: 800;
    margin-bottom: 0.4rem;
}

.result-text {
    line-height: 1.6;
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
    border: 1px solid rgba(217,168,79,0.22) !important;
    border-radius: 11px !important;
    background: rgba(5, 13, 24, 0.52) !important;
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
section[data-testid="stSidebar"] .st-key-nav_gallery button {
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 12px !important;
}

section[data-testid="stSidebar"] .st-key-nav_app button p,
section[data-testid="stSidebar"] .st-key-nav_gallery button p {
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    text-align: left !important;
}

section[data-testid="stSidebar"] .st-key-nav_app button > div,
section[data-testid="stSidebar"] .st-key-nav_gallery button > div,
section[data-testid="stSidebar"] .st-key-nav_app button > div > span,
section[data-testid="stSidebar"] .st-key-nav_gallery button > div > span,
section[data-testid="stSidebar"] .st-key-nav_app button [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] .st-key-nav_gallery button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
}

section[data-testid="stSidebar"] .st-key-language div[data-baseweb="select"] > div {
    padding-left: 12px !important;
    align-items: center !important;
}

section[data-testid="stSidebar"] .st-key-language div[data-baseweb="select"] > div > div:first-of-type {
    margin-left: 0 !important;
    padding-left: 0 !important;
}

section[data-testid="stSidebar"] .st-key-language div[data-baseweb="select"] > div::before,
section[data-testid="stSidebar"] .st-key-nav_app button p::before,
section[data-testid="stSidebar"] .st-key-nav_gallery button p::before,
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

section[data-testid="stSidebar"] .st-key-language div[data-baseweb="select"] > div::before {
    margin-right: 10px !important;
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M3 12h18M12 3c2.5 2.5 4 5.5 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.5-4-9s1.5-6.5 4-9Z'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M3 12h18M12 3c2.5 2.5 4 5.5 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.5-4-9s1.5-6.5 4-9Z'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-nav_app button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 11.5 9-7.5 9 7.5M5.5 10v10h13V10M9.5 20v-6h5v6'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 11.5 9-7.5 9 7.5M5.5 10v10h13V10M9.5 20v-6h5v6'/%3E%3C/svg%3E") !important;
}

section[data-testid="stSidebar"] .st-key-nav_gallery button p::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='16' rx='2'/%3E%3Ccircle cx='8.5' cy='9' r='1.5'/%3E%3Cpath d='m3 17 5-5 4 4 3-3 6 6'/%3E%3C/svg%3E") !important;
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='16' rx='2'/%3E%3Ccircle cx='8.5' cy='9' r='1.5'/%3E%3Cpath d='m3 17 5-5 4 4 3-3 6 6'/%3E%3C/svg%3E") !important;
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
section[data-testid="stSidebar"] .st-key-previous_concepts [data-testid="stExpander"] summary p,
section[data-testid="stSidebar"] .st-key-regenerate_idea [data-testid="stButton"] button p,
section[data-testid="stSidebar"] .st-key-voice_prompt [data-testid="stButton"] button p {
    color: #f3e7c4 !important;
}

section[data-testid="stSidebar"] .st-key-language div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] .st-key-nav_app [data-testid="stButton"] > button,
section[data-testid="stSidebar"] .st-key-nav_gallery [data-testid="stButton"] > button,
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

body:has(.gallery-page-heading) [data-testid="stSidebarNav"] {
    display: block !important;
    visibility: visible !important;
    width: 100% !important;
    height: auto !important;
    min-height: 0 !important;
    padding: 12px 22px 0 !important;
    box-sizing: border-box !important;
    overflow: visible !important;
}

body:has(.gallery-page-heading) [data-testid="stSidebarNavItems"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
}

body:has(.gallery-page-heading) [data-testid="stSidebarNavLinkContainer"] {
    border-radius: 11px !important;
}

body:has(.gallery-page-heading) a[data-testid="stSidebarNavLink"] {
    min-height: 38px !important;
    padding: 0 12px !important;
    display: flex !important;
    align-items: center !important;
    color: #f3e7c4 !important;
    background: var(--control-background) !important;
    border: 1px solid rgba(217,168,79,0.30) !important;
    border-radius: 11px !important;
    box-shadow: var(--control-depth) !important;
    text-decoration: none !important;
}

body:has(.gallery-page-heading) a[data-testid="stSidebarNavLink"] p {
    color: #f3e7c4 !important;
    text-transform: capitalize !important;
}

body:has(.gallery-page-heading) a[data-testid="stSidebarNavLink"] svg {
    color: #ead7a4 !important;
    fill: #ead7a4 !important;
}

body:has(.gallery-page-heading) a[data-testid="stSidebarNavLink"][aria-current="page"] {
    color: #ead7a4 !important;
    border-color: rgba(234,215,164,0.52) !important;
    background: var(--control-background) !important;
}

body:has(.gallery-page-heading) a[data-testid="stSidebarNavLink"]:hover {
    color: #f3e7c4 !important;
    border-color: rgba(234,215,164,0.52) !important;
    background: var(--control-hover-background) !important;
}

body:has(.gallery-page-heading) [data-testid="stSidebarNavSeparator"] {
    margin: 12px 0 0 !important;
    background: linear-gradient(90deg, transparent, rgba(217,168,79,0.58), transparent) !important;
}

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
    color: #a8b3c3 !important;
    font-size: 16px !important;
    line-height: 1.55 !important;
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

body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stSelectbox"] label,
body:has(.gallery-page-heading) [data-testid="stMain"] [data-testid="stSelectbox"] label p {
    color: #d6c6a5 !important;
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
    background: rgba(65,40,23,0.78) !important;
    border: 1px solid rgba(200,154,82,0.46) !important;
    border-radius: 14px !important;
    box-shadow:
        inset 0 1px 0 rgba(255,238,201,0.035),
        0 8px 20px rgba(0,0,0,0.18) !important;
}

.st-key-leonardo_section .result-title {
    color: #DDB36A !important;
}

.st-key-leonardo_section .result-text,
.st-key-leonardo_section .result-text p,
.st-key-leonardo_section .result-text li {
    color: #F2E4C6 !important;
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
    color: #82BEF8 !important;
    letter-spacing: 0.015em !important;
    margin-top: 12px !important;
    margin-bottom: 10px !important;
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
    border: 1px solid rgba(200,154,82,0.34);
    box-shadow: inset 0 0 18px rgba(200,154,82,0.035);
}

.st-key-modern_section .concept-image-slot {
    color: #DCEEFF;
    background: rgba(12,35,56,0.76);
    border: 1px solid rgba(79,168,255,0.30);
    box-shadow: inset 0 0 18px rgba(79,168,255,0.035);
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
    background: rgba(8,26,42,0.84) !important;
    border: 1px solid rgba(79,168,255,0.36) !important;
    border-radius: 14px !important;
    box-shadow:
        inset 0 1px 0 rgba(207,234,255,0.035),
        0 8px 20px rgba(0,0,0,0.20),
        0 0 18px rgba(79,168,255,0.025) !important;
}

.st-key-modern_section .result-title {
    color: #75B8F5 !important;
}

.st-key-modern_section .result-text,
.st-key-modern_section .result-text p,
.st-key-modern_section .result-text li {
    color: #EEF6FF !important;
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
