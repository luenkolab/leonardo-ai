import streamlit as st
from project import choose_category, generate_invention, build_report


st.set_page_config(
    page_title="Leonardo AI",
    page_icon="🎨",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            font-size: 3.2rem;
            font-weight: 800;
            margin-top: 0.5rem;
            margin-bottom: 0.2rem;
            color: #1f2937;
        }

        .subtitle {
            text-align: center;
            font-size: 1.15rem;
            color: #6b7280;
            margin-bottom: 2rem;
        }

        .card {
            background: #f9fafb;
            border-radius: 18px;
            padding: 1.2rem 1.3rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
            border: 1px solid #eceff3;
        }

        .card-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.45rem;
            color: #111827;
        }

        .highlight-card {
            background: linear-gradient(135deg, #f8fafc, #eef2ff);
            border-radius: 20px;
            padding: 1.4rem;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.07);
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }

        .metric-box {
            background: white;
            border-radius: 16px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 3px 12px rgba(0,0,0,0.05);
            border: 1px solid #eceff3;
            margin-bottom: 1rem;
        }

        .metric-label {
            font-size: 0.9rem;
            color: #6b7280;
            margin-bottom: 0.3rem;
        }

        .metric-value {
            font-size: 1.05rem;
            font-weight: 700;
            color: #111827;
        }

        .footer-note {
            text-align: center;
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_impact_statement(report):
    demand = report["Market Demand"]
    difficulty = report["Engineering Difficulty"]
    realization = report["Modern Realization"]

    if demand == "High" and difficulty in ["Medium", "High"]:
        return (
            f"This invention matters because it combines strong real-world demand with a "
            f"clear path toward a modern solution such as {realization}. "
            f"It has the potential to connect Renaissance imagination with practical innovation."
        )

    if demand == "Medium":
        return (
            f"This invention matters because it shows how an old engineering concept can evolve "
            f"into {realization}. Even with moderate demand, it has strong educational and "
            f"demonstration value."
        )

    return (
        f"This invention matters because it represents ambitious creative engineering. "
        f"Even if the market is smaller, the idea demonstrates how historical invention can "
        f"inspire future technology."
    )


def get_drawing_prompt(report):
    return (
        f"Create a Leonardo da Vinci style technical sketch of {report['Generated Invention']}. "
        f"Include mechanical notes, sepia tone, hand-drawn lines, and Renaissance engineering detail. "
        f"Also create a modern blueprint-inspired interpretation based on {report['Modern Realization']}."
    )


def get_voice_summary(report):
    return (
        f"This invention is called {report['Generated Invention']}. "
        f"It is a Renaissance-inspired concept. "
        f"The modern version is {report['Modern Realization']}. "
        f"Overall evaluation: {report['Project Evaluation']}."
    )


def render_card(title, content, icon="📌"):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{icon} {title}</div>
            <div>{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown('<div class="main-title">Leonardo AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Renaissance invention generator with modern engineering analysis, visual ideas, and AI-ready expansion</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Control Panel")

    category_input = st.selectbox(
        "Choose category",
        ["flight", "war", "water", "transport"],
        index=0,
    )

    user_prompt = st.text_area(
        "Prompt / Idea",
        placeholder="Example: Create an invention for agriculture, rescue missions, or smart transport...",
    )

    st.markdown("### 🧠 AI Modules")
    image_mode = st.toggle("Enable image generation concept", value=True)
    blueprint_mode = st.toggle("Enable blueprint concept", value=True)
    voice_mode = st.toggle("Enable voice assistant concept", value=True)

    st.markdown("---")

    generate_button = st.button("✨ Generate Invention", use_container_width=True)
    generate_again_button = st.button("🔄 Generate Again", use_container_width=True)

    st.markdown("---")
    st.caption("For CS50 submission, core logic remains in project.py.")

if "last_report" not in st.session_state:
    st.session_state.last_report = None

if generate_button or generate_again_button:
    try:
        category = choose_category(category_input)
        invention = generate_invention(category)
        report = build_report(invention)
        st.session_state.last_report = report
    except ValueError:
        st.error("Invalid category.")

report = st.session_state.last_report

if report:
    st.success("Invention generated successfully.")

    st.markdown(
        f"""
        <div class="highlight-card">
            <div class="card-title">🏛️ Generated Invention</div>
            <div style="font-size: 1.6rem; font-weight: 800; margin-top: 0.2rem;">
                {report["Generated Invention"]}
            </div>
            <div style="margin-top: 0.8rem; color: #4b5563;">
                A Renaissance concept reimagined through modern engineering logic.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([2.2, 1])

    with left_col:
        render_card("Leonardo Concept", report["Leonardo Concept"], "🪶")
        render_card("How It Works", report["How It Works"], "⚙️")
        render_card("Modern Realization", report["Modern Realization"], "🚀")
        render_card(
            "How the Modern Version Works",
            report["How the Modern Version Works"],
            "🔬",
        )
        render_card(
            "Why This Invention Matters",
            get_impact_statement(report),
            "💡",
        )

    with right_col:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">📈 Market Demand</div>
                <div class="metric-value">{report["Market Demand"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">💰 Return Potential</div>
                <div class="metric-value">{report["Return Potential"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">🛠️ Engineering Difficulty</div>
                <div class="metric-value">{report["Engineering Difficulty"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">🏆 Project Evaluation</div>
                <div class="metric-value">{report["Project Evaluation"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## 🎨 AI Extensions")

    ai_col1, ai_col2, ai_col3 = st.columns(3)

    with ai_col1:
        if image_mode:
            render_card(
                "Image Generation Prompt",
                get_drawing_prompt(report),
                "🖼️",
            )
        else:
            render_card(
                "Image Generation Prompt",
                "Image module is currently disabled.",
                "🖼️",
            )

    with ai_col2:
        if blueprint_mode:
            render_card(
                "Blueprint Concept",
                (
                    "Generate a modern engineering blueprint based on the selected invention. "
                    "The output should focus on structure, materials, moving parts, and practical deployment."
                ),
                "📐",
            )
        else:
            render_card(
                "Blueprint Concept",
                "Blueprint module is currently disabled.",
                "📐",
            )

    with ai_col3:
        if voice_mode:
            render_card(
                "Voice Assistant Summary",
                get_voice_summary(report),
                "🎤",
            )
        else:
            render_card(
                "Voice Assistant Summary",
                "Voice module is currently disabled.",
                "🎤",
            )

    if user_prompt.strip():
        st.info(
            f"User prompt received: {user_prompt.strip()}.\n\n"
            "In the current version, prompt input is displayed as an enhancement path. "
            "The next version can use it to guide invention generation more directly."
        )

else:
    st.markdown("## 👋 Welcome")
    st.write(
        "Use the sidebar to choose a category and generate a Leonardo-style invention. "
        "The interface is designed as a polished demo layer for the core Python project."
    )
    st.write(
        "This version is already prepared for future integration with image generation, "
        "technical sketches, and a voice assistant."
    )

st.markdown(
    '<div class="footer-note">Leonardo AI • CS50 Final Project • Streamlit demo interface</div>',
    unsafe_allow_html=True,
)