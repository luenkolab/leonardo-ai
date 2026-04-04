import streamlit as st
from project import validate_category, generate_invention


st.set_page_config(
    page_title="Leonardo AI",
    page_icon="🎨",
    layout="wide"
)

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
        index=1
    )

if "history" not in st.session_state:
    st.session_state.history = []

display_categories = [
    "flight",
    "water",
    "war",
    "transport",
    "energy",
    "medicine",
    "architecture",
    "agriculture",
    "robotics",
    "space"
]


def build_fallback_concept(category, prompt_text):
    title = f"Leonardo Concept for {category.title()}: {prompt_text[:60]}"
    principle = (
        f"This invention applies Renaissance engineering logic to {category}. "
        f"It combines mechanical motion, structural balance, and practical design "
        f"to solve the problem described by the user prompt: '{prompt_text}'."
    )
    modern_version = (
        f"A modern implementation could combine AI, sensors, lightweight materials, "
        f"automation, and data analysis to transform this {category} concept into a real product."
    )
    demand = (
        f"Potential demand is moderate to high in the {category} sector, especially if "
        f"the solution improves efficiency, safety, or cost reduction."
    )
    roi = (
        "Estimated ROI: 50% to 85% within 2-4 years depending on prototype quality, "
        "market fit, and production cost."
    )
    return title, principle, modern_version, demand, roi


def generate_difficulty(category, creativity_mode):
    base = {
        "flight": "High",
        "water": "High",
        "war": "Extreme",
        "transport": "Medium",
        "energy": "High",
        "medicine": "Extreme",
        "architecture": "High",
        "agriculture": "Medium",
        "robotics": "High",
        "space": "Extreme"
    }.get(category, "High")

    if creativity_mode == "Experimental" and base == "Medium":
        return "High"
    return base


def generate_modern_difficulty(category):
    mapping = {
        "flight": "High",
        "water": "High",
        "war": "Extreme",
        "transport": "Medium",
        "energy": "High",
        "medicine": "Extreme",
        "architecture": "High",
        "agriculture": "Medium",
        "robotics": "High",
        "space": "Extreme"
    }
    return mapping.get(category, "High")


def generate_materials(category):
    materials_map = {
        "flight": ["carbon fiber frame", "servo motors", "flight controller", "stabilizing sensors"],
        "water": ["sealed pressure shell", "marine turbine", "waterproof sensors", "composite tubing"],
        "war": ["reinforced alloy shell", "shock-resistant frame", "remote navigation system", "targeting module"],
        "transport": ["electric motor", "battery pack", "wheel control system", "lightweight chassis"],
        "energy": ["battery cells", "smart grid controller", "thermal insulation", "power conversion module"],
        "medicine": ["biocompatible housing", "diagnostic sensors", "microcontroller", "sterile casing"],
        "architecture": ["load-bearing frame", "adaptive joints", "smart materials", "support modules"],
        "agriculture": ["soil sensors", "mechanical cultivator", "smart irrigation unit", "navigation controller"],
        "robotics": ["robotic joints", "camera module", "AI control board", "precision actuators"],
        "space": ["heat-resistant composite", "guidance sensors", "autonomous control unit", "sealed energy module"]
    }
    return materials_map.get(category, ["modular frame", "sensors", "AI controller", "lightweight materials"])


def generate_use_cases(category):
    use_cases_map = {
        "flight": ["rescue missions", "aerial mapping", "surveillance", "scientific observation"],
        "water": ["marine exploration", "underwater inspection", "rescue operations", "environmental research"],
        "war": ["defense support", "remote tactical operations", "simulation systems", "protective engineering"],
        "transport": ["urban delivery", "smart mobility", "industrial logistics", "campus transport"],
        "energy": ["smart power systems", "green infrastructure", "remote energy delivery", "industrial optimization"],
        "medicine": ["diagnostics", "remote monitoring", "hospital support systems", "medical training"],
        "architecture": ["rapid deployment structures", "emergency shelters", "adaptive buildings", "civil engineering demos"],
        "agriculture": ["precision farming", "soil monitoring", "crop management", "automated harvesting"],
        "robotics": ["industrial automation", "education", "inspection", "research and development"],
        "space": ["orbital maintenance", "planetary exploration", "autonomous research", "space logistics"]
    }
    return use_cases_map.get(category, ["education", "engineering demos", "research", "commercial prototypes"])


def generate_dev_time(difficulty):
    mapping = {
        "Medium": "Prototype: 2-4 months • MVP: 6-8 months • Product: 1 year",
        "High": "Prototype: 4-6 months • MVP: 8-12 months • Product: 1-2 years",
        "Extreme": "Prototype: 6-10 months • MVP: 12-18 months • Product: 2+ years"
    }
    return mapping.get(difficulty, "Prototype: 3-6 months • MVP: 8-12 months • Product: 1-2 years")


def generate_investor_summary(title, category, demand, roi):
    return (
        f"{title} is a {category} innovation concept inspired by Leonardo da Vinci. "
        f"It targets practical engineering value, visual uniqueness, and product potential. "
        f"{demand} {roi}"
    )


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
        display_categories
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
        placeholder="Example: Create an invention for agriculture, rescue missions, smart transport, underwater exploration, or medical diagnostics...",
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
        '<div class="small-note">For CS50 submission, core logic remains in project.py.</div>',
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
        "and product presentation for your final project."
    )

    st.markdown("## System Status")
    st.markdown('<div class="status-good">✅ Core Logic: Active</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-good">✅ Interface Layer: Active</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="status-warn">🟡 Voice Prompt Transcription: Demo UI only (speech-to-text not connected yet)</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="status-good">✅ Image Module: Concept Ready</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-good">✅ Blueprint Engine: Concept Ready</div>', unsafe_allow_html=True)

    should_generate = generate or regenerate

    if should_generate:
        prompt_text = user_prompt.strip() if user_prompt.strip() else f"an invention in {category}"

        if validate_category(category):
            invention = generate_invention(category)
            title = invention["title"]
            principle = invention["principle"]
            modern_version = invention["modern_version"]
            demand = invention["demand"]
            roi = invention["roi"]
        else:
            title, principle, modern_version, demand, roi = build_fallback_concept(category, prompt_text)

        difficulty = generate_difficulty(category, creativity_mode)
        modern_difficulty = generate_modern_difficulty(category)
        materials = generate_materials(category)
        use_cases = generate_use_cases(category)
        dev_time = generate_dev_time(modern_difficulty)
        investor_summary = generate_investor_summary(title, category, demand, roi)

        leonardo_sketch_description = (
            f"A sepia-toned Renaissance sketch of '{title}', drawn with fine ink lines, "
            f"mechanical annotations, visible gears, cross-sections, and Leonardo-style notes "
            f"around the concept."
        )

        modern_sketch_description = (
            f"A modern engineering sketch of '{title}', showing labeled modules, clean industrial lines, "
            f"smart materials, digital control systems, and a presentation-ready schematic layout."
        )

        if voice_module:
            voice_assistant_concept = (
                f"The voice assistant could explain how '{title}' works, guide the user through "
                f"its modern implementation, answer questions about demand and ROI, and present "
                f"the concept step by step."
            )
        else:
            voice_assistant_concept = "Voice assistant module is currently disabled."

        if image_module:
            image_concept = (
                "Image generation concept enabled: the system can later produce Leonardo-style visual ideas "
                "and modern concept art for the invention."
            )
        else:
            image_concept = "Image generation concept is currently disabled."

        if blueprint_module:
            blueprint_concept = (
                "Blueprint concept enabled: the system can later output technical sketch descriptions "
                "for engineering slides and presentation visuals."
            )
        else:
            blueprint_concept = "Blueprint concept is currently disabled."

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

        record = {
            "title": title,
            "category": category
        }
        st.session_state.history.insert(0, record)
        st.session_state.history = st.session_state.history[:5]

        st.success("Concept generated successfully.")

        if user_prompt.strip():
            st.markdown("### User Prompt")
            st.markdown(
                f"""
                <div class="result-box">
                {user_prompt}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("## 🎨 Leonardo Concept")

        st.markdown("### 📜 Generated Invention")
        st.markdown(
            f"""
            <div class="result-box">
            <b>{title}</b><br><br>
            {extra_note}<br><br>
            {audience_note}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### ⚙️ Principle of Operation")
        st.markdown(
            f'<div class="result-box">{principle}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### ✏️ Leonardo Sketch Description")
        st.markdown(
            f'<div class="result-box">{leonardo_sketch_description}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### 🎯 Leonardo Concept Difficulty")
        st.markdown(
            f'<div class="result-box">{difficulty}</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("## 🚀 Modern Engineering")

        st.markdown("### 🚀 Modern Implementation")
        st.markdown(
            f'<div class="result-box">{modern_version}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### 🧩 Modern Sketch Description")
        st.markdown(
            f'<div class="result-box">{modern_sketch_description}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### 🧱 Materials / Technologies")
        st.markdown(
            f'<div class="result-box">• ' + "<br>• ".join(materials) + "</div>",
            unsafe_allow_html=True
        )

        st.markdown("### 🧭 Use Cases")
        st.markdown(
            f'<div class="result-box">• ' + "<br>• ".join(use_cases) + "</div>",
            unsafe_allow_html=True
        )

        st.markdown("### ⏱ Development Timeline")
        st.markdown(
            f'<div class="result-box">{dev_time}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### 🏗️ Modern Engineering Difficulty")
        st.markdown(
            f'<div class="result-box">{modern_difficulty}</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("## 📈 Market & Business")

        st.markdown("### 📈 Market Demand")
        st.markdown(
            f'<div class="result-box">{demand}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### 💰 ROI Analysis")
        st.markdown(
            f'<div class="result-box">{roi}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### 📊 Investor Summary")
        st.markdown(
            f'<div class="result-box">{investor_summary}</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("## 🧠 AI System Features")

        st.markdown("### 🖼 Image Generation Concept")
        st.markdown(
            f'<div class="result-box">{image_concept}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### 🎤 Voice Assistant Concept")
        st.markdown(
            f'<div class="result-box">{voice_assistant_concept}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### 📐 Blueprint Concept")
        st.markdown(
            f'<div class="result-box">{blueprint_concept}</div>',
            unsafe_allow_html=True
        )

    else:
        st.markdown("## Demo Preview")
        st.write(
            "Choose a category, write your own prompt, select creativity mode, and generate "
            "a full invention concept for your presentation, screenshots, or final project video."
        )

    st.markdown("## Previous Concepts")
    if st.session_state.history:
        for item in st.session_state.history:
            st.markdown(
                f"""
                <div class="mini-card">
                <b>{item['title']}</b><br>
                Category: {item['category']}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div class="mini-card">No previous concepts yet. Generate your first invention.</div>',
            unsafe_allow_html=True
        )