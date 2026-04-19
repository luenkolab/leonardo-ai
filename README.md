# 🧠 Leonardo AI

**Renaissance-inspired AI system for generating inventions and engineering concepts**

Leonardo AI is a creative engineering platform that combines the imagination of Leonardo da Vinci with modern AI capabilities to generate unique inventions, analyze their feasibility, and visualize their structure.

---

## 🚀 Demo

> (Coming soon — Streamlit deployment)

---

## ⚙️ Features

- 🎨 Generate original invention concepts in Leonardo-style
- 🧠 AI-powered descriptions and explanations
- 🏗 Engineering breakdown of how systems work
- 📊 Modern implementation analysis (materials, tech stack)
- 💰 Market demand and ROI estimation
- 🖼 Concept visualization (sketch + blueprint ideas)
- 🗣 Voice prompt support (concept-ready)

---

## 🛠 Tech Stack

- Python  
- Streamlit  
- OpenAI API (optional integration)  
- SQLite (for history & storage)  

---

## 🧠 How It Works

1. Select a category (transport, robotics, energy, etc.)
2. Enter a custom idea or prompt
3. Choose creativity level (Classic / Bold / Experimental)
4. Generate a full invention concept including:
   - Principle
   - Engineering design
   - Modern implementation
   - Use cases
   - Market analysis

---

## 📦 Project Structure

```bash
project/
│
├── app.py              # Streamlit interface
├── project.py          # Core logic (CS50 requirement)
├── ai_generator.py     # AI-based generation (optional)
├── database.db         # Saved concepts
└── README.md

