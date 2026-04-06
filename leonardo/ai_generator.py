import json
import os
from openai import OpenAI


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


def _modern_difficulty(category: str) -> str:
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
        "space": "Extreme",
    }
    return mapping.get(category, "High")


def _build_modern_sketch(modern_name: str, materials: list[str], use_cases: list[str]) -> str:
    materials_text = ", ".join(materials[:4]) if materials else "advanced structural materials"
    use_cases_text = ", ".join(use_cases[:3]) if use_cases else "urban deployment"

    return (
        f"A clean modern engineering blueprint of '{modern_name}', presented as a realistic "
        f"industrial product with labeled modules, compact structural framing, integrated safety systems, "
        f"digital control architecture, and deployment-ready layout. The concept emphasizes present-day "
        f"engineering clarity, manufacturability, and application in {use_cases_text}. Key materials and "
        f"technologies include {materials_text}."
    )

def generate_system_name(category: str) -> str:
    names = {
        "rescue": "SlopeSafe System",
        "water": "AquaLift System",
        "flight": "AeroGlide System",
        "construction": "StoneBridge System",
        "transport": "CargoFlow System",
        "exploration": "TerraScout System",
        "industrial": "ForgeFlow System",
        "energy": "PowerCore System",
        "architecture": "Archimedes Build System",
        "mechanical": "Mechanica System",
        "agriculture": "AgroLift System",
        "medicine": "LifeAssist System",
        "robotics": "AutoMechanica System",
        "space": "AstroMechanica System",
        "military": "Fortress System"
    }
    return names.get(category, "Leonardo System")


def generate_leonardo_concept(category: str, prompt: str, creativity: str, audience: str) -> dict:
    client = _get_client()
    system_name = generate_system_name(category)
    system_prompt = """
You are Leonardo da Vinci combined with a modern product engineer and startup strategist.

Project Name: {system_name}
Use this name consistently across Leonardo concept, modern implementation, and business analysis.

HISTORICAL ACCURACY RULE:

The Leonardo concept must reflect Renaissance-era environments.

Avoid:
- skyscrapers
- modern cities
- modern infrastructure
- modern terminology
- modern disaster scenarios

Instead use:
- towers
- castles
- fortifications
- ships
- cliffs
- bridges
- medieval cities
- siege scenarios

You must produce TWO CLEARLY SEPARATED layers:

LAYER 1 — LEONARDO CONCEPT
This must be historically believable in the Renaissance.
Allowed:
- wood
- ropes
- pulleys
- gears
- levers
- springs
- counterweights
- iron fittings
- simple wind-driven mechanisms (mills, sails for motion only)
- water power
- hand-powered mechanics
- nature observation

LEONARDO REALISM:

The Leonardo invention must be mechanically simple and plausible for Renaissance technology.

Prefer:
- pulleys
- counterweights
- gears
- winches
- ramps
- carts
- scaffolding
- inclined rails
- sliding platforms

Avoid:
- complex aerodynamic systems
- unstable mechanisms
- overly sophisticated engineering
- multi-stage mechanical systems

Forbidden in Leonardo layer:
- electronics
- AI
- software
- satellites
- sensors
- batteries
- composite materials
- drones
- GPS
- digital systems

HISTORICAL ACCURACY:

The Leonardo concept must use specific Renaissance contexts such as:
- towers
- fortified walls
- castles
- bridges
- ships
- cliffs
- cathedral roofs
- siege structures

In Leonardo sketch descriptions, prefer words like:
- craftsmen
- assistants
- operators
- builders

Avoid modern professional framing such as:
- engineers
- industrial teams
- technical staff

Avoid generic phrases like:
- emergency situations
- elevated structures
- disaster zones
when writing the Leonardo section.

LAYER 2 — MODERN IMPLEMENTATION
This must be a modern engineering product or system.
It must NOT repeat the Leonardo concept in the same physical form.
It must evolve the FUNCTION, not the FORM.

If Leonardo uses wings, bird inspiration, or mechanical lift,
the modern version should transition toward:
- drones
- multirotor systems
- VTOL aircraft
- autonomous emergency systems
- industrial platforms
- scalable modern products

IMPORTANT:
The modern implementation must be:
- practical
- commercial
- industrial
- realistic
- written like a product brief

The modern implementation must avoid exaggerated marketing language.
Use clear engineering language instead of promotional wording.

The modern implementation must directly address the user's environment or scenario.
If the prompt includes Mars, underwater, volcano, etc., the modern version must explicitly reflect it.

MARKET & BUSINESS STYLE:

The Market & Business section must sound like a startup pitch, not a formal report.

Avoid generic corporate phrases like:
- increasing demand
- viable option
- emerging market

Instead:
- describe concrete market drivers
- mention industries
- reference real-world applications
- explain why investors would care

Include 2-3 concrete industries where this product could be used.

Use confident but realistic language.
Avoid hype or exaggerated claims.

Return ONLY valid JSON.
Do not include markdown.
Do not include commentary.

Required JSON keys:
{
  "leonardo_name": "...",
  "leonardo_invention": "...",
  "principle": "...",
  "leonardo_sketch": "...",
  "modern_name": "...",
  "modern_implementation": "...",
  "market_demand": "...",
  "roi_analysis": "...",
  "difficulty_level": "...",
  "development_timeline": "...",
  "materials": ["...", "..."],
  "use_cases": ["...", "..."],
  "investor_summary": "..."
}
"""

    user_prompt = f"""
Category: {category}
Creativity mode: {creativity}
Target audience: {audience}
User prompt: {prompt}

Rules:
- The Leonardo concept must sound like a Renaissance notebook concept.
- The modern implementation must sound like a present-day engineering product brief.
- Do not reuse the same name for both layers.
- Do not let the modern implementation inherit Leonardo-style mechanics.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.8,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Empty response from OpenAI")

    data = json.loads(content)

    leonardo_name = data.get("leonardo_name", "Unnamed Leonardo Concept").strip()
    leonardo_invention = data.get("leonardo_invention", "").strip()
    principle = data.get("principle", "").strip()
    leonardo_sketch = data.get("leonardo_sketch", "").strip()
    modern_name = data.get("modern_name", "Unnamed Modern Product").strip()
    modern_implementation = data.get("modern_implementation", "").strip()
    market_demand = data.get("market_demand", "").strip()
    roi_analysis = data.get("roi_analysis", "").strip()
    difficulty_level = data.get("difficulty_level", "High").strip()
    development_timeline = data.get("development_timeline", "Prototype: 4-6 months • MVP: 8-12 months • Product: 1-2 years").strip()
    investor_summary = data.get("investor_summary", "").strip()

    materials = data.get("materials", [])
    if not isinstance(materials, list):
        materials = [str(materials)]

    use_cases = data.get("use_cases", [])
    if not isinstance(use_cases, list):
        use_cases = [str(use_cases)]

    materials = [str(x).strip() for x in materials if str(x).strip()]
    use_cases = [str(x).strip() for x in use_cases if str(x).strip()]

    modern_sketch = _build_modern_sketch(modern_name, materials, use_cases)

    modern_full = modern_implementation.strip()
    if modern_full.lower().startswith(modern_name.lower()):
        modern_text = modern_full
    else:
        modern_text = f"{modern_name}. {modern_full}" if modern_full else modern_name

    return {
        "title": f"{leonardo_name} — {leonardo_invention}" if leonardo_invention else leonardo_name,
        "principle": principle,
        "leonardo_sketch_description": leonardo_sketch,
        "difficulty": difficulty_level,
        "modern_version": modern_text,
        "modern_sketch_description": modern_sketch,
        "materials": materials,
        "use_cases": use_cases,
        "dev_time": development_timeline,
        "modern_difficulty": _modern_difficulty(category),
        "demand": market_demand,
        "roi": roi_analysis,
        "investor_summary": investor_summary,
        "image_concept": (
            f"Image generation concept enabled: the system can later create a Renaissance sketch for "
            f"'{leonardo_name}' and a separate modern concept illustration for '{modern_name}'."
        ),
        "voice_assistant_concept": (
            f"The voice assistant could explain the historical logic of '{leonardo_name}', then guide the user "
            f"through the modern product strategy of '{modern_name}', including demand, feasibility, and ROI."
        ),
        "blueprint_concept": (
            f"Blueprint concept enabled: the system can later output a Leonardo-style sketch sheet for "
            f"'{leonardo_name}' and a modern engineering blueprint for '{modern_name}'."
        ),
    }