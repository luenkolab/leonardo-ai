import streamlit as st


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Noto+Sans:wght@400;500;600;700&display=swap');

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

.result-box.result-box--control-gap {
    margin-bottom: 30px !important;
}

.st-key-voice_pause,
.st-key-voice_resume,
.st-key-voice_stop {
    margin-top: 14px !important;
}

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

.idea-block-leonardo {
    padding: 22px;
    border-radius: 18px;

    background:
        linear-gradient(
            rgba(247,238,215,0.94),
            rgba(234,223,196,0.94)
        ),
        url("https://www.transparenttextures.com/patterns/old-paper.png");

    border: 1px solid rgba(120,90,40,0.25);

    margin-bottom: 22px;

    color:#2b2418;

    box-shadow:
        inset 0 0 30px rgba(0,0,0,0.05),
        0 8px 24px rgba(0,0,0,0.12);
}

.idea-block-modern {

    padding:22px;

    border-radius:18px;

    background:

        linear-gradient(
            rgba(7,17,31,0.95),
            rgba(8,22,38,0.95)
        );

    border:1px solid rgba(59,130,246,0.25);

    margin-bottom:22px;

    box-shadow:
        inset 0 0 40px rgba(59,130,246,0.08),
        0 8px 24px rgba(0,0,0,0.25);
}

/* ---------- Release UI polish: isolated generated-result worlds ---------- */

.st-key-previous_concepts [class*="st-key-open_concept_"] button,
.st-key-previous_concepts [class*="st-key-favorite_concept_"] button,
.st-key-previous_concepts [class*="st-key-delete_concept_"] button {
    width: 74% !important;
    min-height: 32px !important;
    height: 32px !important;
    padding: 2px 6px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    font-size: 0.8rem !important;
    line-height: 1 !important;
}

.st-key-previous_concepts [class*="st-key-open_concept_"] button p,
.st-key-previous_concepts [class*="st-key-favorite_concept_"] button p,
.st-key-previous_concepts [class*="st-key-delete_concept_"] button p {
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

.st-key-leonardo_section::before {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.24;
    background-image:
        radial-gradient(rgba(242,228,198,0.09) 0.65px, transparent 0.65px),
        linear-gradient(110deg, transparent 0%, rgba(200,154,82,0.055) 48%, transparent 74%);
    background-size: 7px 7px, 100% 100%;
}

.st-key-leonardo_section > * {
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

.st-key-leonardo_section [data-testid="stHorizontalBlock"] {
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
    content: "";
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.18;
    background-image:
        linear-gradient(rgba(79,168,255,0.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(79,168,255,0.12) 1px, transparent 1px);
    background-size: 36px 36px;
}

.st-key-modern_section > * {
    position: relative;
    z-index: 1;
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

.st-key-modern_section [data-testid="stHorizontalBlock"] {
    gap: 16px !important;
    margin-top: 18px !important;
    margin-bottom: 22px !important;
}

.st-key-leonardo_section [data-testid="stMarkdownContainer"]:has(.concept-image-slot),
.st-key-modern_section [data-testid="stMarkdownContainer"]:has(.concept-image-slot) {
    margin-bottom: 0 !important;
}

.st-key-leonardo_section .concept-image-slot,
.st-key-modern_section .concept-image-slot {
    width: 100%;
    aspect-ratio: 1 / 1;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16px;
    overflow: hidden;
    border-radius: 12px;
    text-align: center;
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

</style>
"""


def apply_global_styles():
    st.markdown(
        GLOBAL_CSS,
        unsafe_allow_html=True,
    )
