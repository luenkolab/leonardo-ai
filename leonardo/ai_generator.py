import json
import os
from openai import OpenAI


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


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


def generate_leonardo_concept(category: str, user_prompt_text: str, creativity: str, audience: str) -> dict:
    client = _get_client()
    system_prompt = f"""
    You are a professional engineering innovation consultant.

    Generate a professional product concept inspired by Leonardo da Vinci thinking,
    but focused on modern implementation, engineering feasibility, and business value.

    Return response strictly as JSON.

    Required JSON structure:

    {{
    "title": "...",

    "leonardo_concept": "...",
    "leonardo_sketch_description": "...",

    "modern_product_name": "...",
    "modern_category": "...",
    "executive_summary": "...",

    "problem_statement": "...",
    "target_users": ["...", "..."],
    "industries": ["...", "..."],
    "use_cases": ["...", "..."],

    "modern_principle": "...",
    "system_components": ["...", "..."],
    "materials": ["...", "..."],
    "technical_requirements": ["...", "..."],
    "modern_sketch_description": "...",

    "implementation_roadmap": {{
        "prototype": "...",
        "mvp": "...",
        "pilot": "...",
        "production": "..."
    }},

    "implementation_guides": {{
        "prototype": {{
            "execution_plan": {{
                "goal": "...",
                "steps": ["...", "...", "..."],
                "specialists": ["...", "..."],
                "technologies": ["...", "..."],
                "estimated_budget": "...",
                "stage_risks": ["...", "..."],
                "readiness_criteria": ["...", "..."],
                "expected_output": "..."
            }},
            "technical_architecture": {{
                "system_schema": "...",
                "module_interaction": "...",
                "process_flow": "...",
                "deployment_logic": "..."
            }},
            "resources_budget": {{
                "team": ["...", "..."],
                "stack": ["...", "..."],
                "materials": ["...", "..."],
                "cost_notes": "..."
            }},
            "validation": {{
                "tests": ["...", "..."],
                "kpi": ["...", "..."],
                "success_criteria": ["...", "..."]
            }}
        }},

        "mvp": {{
            "execution_plan": {{
                "goal": "...",
                "steps": ["...", "...", "..."],
                "specialists": ["...", "..."],
                "technologies": ["...", "..."],
                "estimated_budget": "...",
                "stage_risks": ["...", "..."],
                "readiness_criteria": ["...", "..."],
                "expected_output": "..."
            }},
            "technical_architecture": {{
                "system_schema": "...",
                "module_interaction": "...",
                "process_flow": "...",
                "deployment_logic": "..."
            }},
            "resources_budget": {{
                "team": ["...", "..."],
                "stack": ["...", "..."],
                "materials": ["...", "..."],
                "cost_notes": "..."
            }},
            "validation": {{
                "tests": ["...", "..."],
                "kpi": ["...", "..."],
                "success_criteria": ["...", "..."]
            }}
        }},

        "pilot": {{
            "execution_plan": {{
                "goal": "...",
                "steps": ["...", "...", "..."],
                "specialists": ["...", "..."],
                "technologies": ["...", "..."],
                "estimated_budget": "...",
                "stage_risks": ["...", "..."],
                "readiness_criteria": ["...", "..."],
                "expected_output": "..."
            }},
            "technical_architecture": {{
                "system_schema": "...",
                "module_interaction": "...",
                "process_flow": "...",
                "deployment_logic": "..."
            }},
            "resources_budget": {{
                "team": ["...", "..."],
                "stack": ["...", "..."],
                "materials": ["...", "..."],
                "cost_notes": "..."
            }},
            "validation": {{
                "tests": ["...", "..."],
                "kpi": ["...", "..."],
                "success_criteria": ["...", "..."]
            }}
        }},

        "production": {{
            "execution_plan": {{
                "goal": "...",
                "steps": ["...", "...", "..."],
                "specialists": ["...", "..."],
                "technologies": ["...", "..."],
                "estimated_budget": "...",
                "stage_risks": ["...", "..."],
                "readiness_criteria": ["...", "..."],
                "expected_output": "..."
            }},
            "technical_architecture": {{
                "system_schema": "...",
                "module_interaction": "...",
                "process_flow": "...",
                "deployment_logic": "..."
            }},
            "resources_budget": {{
                "team": ["...", "..."],
                "stack": ["...", "..."],
                "materials": ["...", "..."],
                "cost_notes": "..."
            }},
            "validation": {{
                "tests": ["...", "..."],
                "kpi": ["...", "..."],
                "success_criteria": ["...", "..."]
            }}
        }}
    }},
    
    "deployment_strategy": "...",

    "risks": ["...", "..."],
    "constraints": ["...", "..."],

    "market_demand": "...",
    "startup_cost": "...",
    "roi": "...",
    "investor_summary": "...",

    "difficulty": "...",
    "modern_difficulty": "...",
    "dev_time": "..."
    }}

    Category: {category}
    User prompt: {user_prompt_text}
    Creativity level: {creativity}
    Audience: {audience}

    Important:
    - Leonardo section must be short
    - Modern section must be detailed and professional
    - Avoid fantasy concepts
    - Focus on real-world implementation
    - implementation_guides must be detailed and practical
    - each roadmap stage must include execution_plan, technical_architecture, resources_budget, and validation
    - use professional engineering and project planning language
    - avoid generic filler text
    - modern_sketch_description must describe a clean engineering blueprint, not an artistic sketch
    - modern_sketch_description must explicitly avoid Renaissance, sepia, hand-drawn, or notebook aesthetics
    - modern_sketch_description must include orthographic views, labels, dimensions, arrows, and technical annotations
    - modern_sketch_description must feel like a CAD or product engineering presentation
    """

    user_prompt = f"""
    Category: {category}
    Creativity mode: {creativity}
    Target audience: {audience}
    User prompt: {user_prompt_text}

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

    return data