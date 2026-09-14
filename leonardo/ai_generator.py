import json

from categories import require_category_key
from i18n import ai_language_name, category_display_name
from services.openai_client import get_text_client


_get_client = get_text_client


def generate_system_name(category: str) -> str:
    category = require_category_key(category)
    names = {
        "emergency_rescue": "SlopeSafe System",
        "water": "AquaLift System",
        "aerospace_space": "AeroGlide System",
        "construction_architecture": "StoneBridge System",
        "transport_mobility": "CargoFlow System",
        "manufacturing_industry": "ForgeFlow System",
        "energy": "PowerCore System",
        "agriculture_food": "AgroLift System",
        "health_biotech": "LifeAssist System",
        "robotics_automation": "AutoMechanica System",
        "defense_security": "Fortress System",
    }
    return names.get(category, "Leonardo System")


def generate_leonardo_concept(
    category: str,
    user_prompt_text: str,
    creativity: str,
    audience: str,
    language: str = "en",
) -> dict:
    category_key = require_category_key(category)
    category = category_display_name(category_key, language)
    client = _get_client()
    response_language = ai_language_name(language)
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
    - Write every user-facing JSON value in {response_language}
    - Keep all JSON property names exactly as specified in English
    - Leonardo section must be short
    - Modern section must be detailed and professional
    - Avoid fantasy concepts
    - Focus on real-world implementation
    - implementation_guides must be detailed and practical
    - each roadmap stage must include execution_plan, technical_architecture, resources_budget, and validation
    - implementation_roadmap and implementation_guides must form one strict Prototype → MVP → Pilot → Production lifecycle: Prototype validates the key technical hypothesis; MVP builds on that evidence as the minimum usable real-world version; Pilot validates the MVP in a limited real environment with actual users or operators and measurable criteria; Production is scalable and operationally ready
    - Each lifecycle stage must depend on evidence and outputs from the preceding stage and must not skip maturity levels
    - Keep every guide's execution_plan, technical_architecture, resources_budget, and validation appropriate to that stage; do not place production-scale work in Prototype or unexplained early experimental validation in Production
    - Every implementation_guides item must explain why that action, specialist, technology, resource, or validation is necessary for this specific concept at this specific lifecycle stage; rewrite content that could apply unchanged to almost any startup
    - In execution_plan, derive concrete product-specific actions from the User prompt and system_components; do not use generic steps such as develop a prototype, perform testing, or collect feedback without naming what is built, tested, measured, or learned
    - In technical_architecture, describe only the concept-relevant hardware, software, sensing, materials, interfaces, power, communications, manufacturing, and deployment dependencies, and show their stage-specific relationships rather than using a universal architecture template
    - In specialists, technologies, team, stack, materials, and cost_notes, justify each resource through a concrete task or dependency of that stage; use an explicitly labelled estimate or range with principal cost drivers when a budget cannot be calculated, never unsupported precision
    - In validation, define measurable stage-exit tests, KPI, success criteria, readiness criteria, and expected evidence that prove the stage is ready to advance; keep them consistent with technical_requirements and avoid vague outcomes such as successful testing, positive feedback, or works correctly without a specific acceptance criterion
    - Any timing stated in implementation_roadmap or implementation_guides must be sequential, realistic for the concept's complexity, and consistent with technical_requirements, risks, constraints, and dev_time
    - Before returning JSON, cross-check roadmap, guides, and dev_time for temporal contradictions; dev_time must name its target maturity milestone, and later stages must not finish within the same or a shorter horizon unless the schedule explicitly and credibly explains the overlap
    - use professional engineering and project planning language
    - avoid generic filler text
    - problem_statement must preserve every material problem driver, operating context, failure situation, and required reason for use that the User prompt explicitly states
    - If the User prompt lists multiple materially distinct problem-context conditions, include all of them explicitly or consolidate them without losing any condition; do not silently drop an item that changes the intended use
    - Keep problem_statement concise and synthesized rather than copying the User prompt verbatim or retelling the full concept, and keep it consistent with target_users, use_cases, executive_summary, and mandatory capabilities
    - Every technical_requirements item must be a concept-specific system requirement that is measurable, verifiable, or operationally defined; where supported, state a quantity, time, operating condition, load, accuracy, range, service life, frequency, limiting condition, or verification method
    - Do not write technical_requirements as vague qualities or marketing benefits such as rapid, reliable, efficient, simple, or robust without stating the operational criterion by which that quality is evaluated
    - Do not invent unsupported numerical precision; when the brief and concept do not justify a number, give a testable criterion tied to the operating envelope, resource budget, acceptance test, or full working cycle without fabricating a threshold
    - Derive technical_requirements from the User prompt and keep them consistent with modern_principle, system_components, materials, mandatory capabilities, risks, and constraints
    - Before writing risks and constraints, treat mandatory capabilities in the User prompt and the capabilities already stated in executive_summary, modern_principle, technical_requirements, use_cases, and other concept fields as invariants
    - Risks must describe conditional failure modes, uncertainties, dependencies, or boundary conditions that could degrade an outcome; never state or imply that a mandatory or already-stated capability is simply absent
    - When a risk concerns a required capability, frame it as a specific performance boundary, triggering condition, validation need, or mitigation dependency rather than negating the capability
    - Constraints must be specific to this concept and state what is limited, why it is limited, and which implementation or operating area is affected; avoid generic constraints unless they are concretely tied to the concept
    - Before returning JSON, check every risk and constraint against the User prompt and all generated concept fields and rewrite any direct contradiction
    - In market_demand, identify concept-specific customer segments, demand drivers, the problem customers would pay to solve, and the conditions or markets where demand is plausible; do not invent market size, TAM, SAM, SOM, CAGR, growth statistics, or generic high-potential claims without verifiable support
    - In startup_cost, do not give a single precise monetary amount without sufficient basis; when an exact calculation is unavailable, label the value as a preliminary estimate or range and name the main concept-specific cost drivers such as development, hardware, manufacturing, testing, certification, infrastructure, or other applicable work
    - Do not choose a currency arbitrarily or automatically convert the user's currency, and do not create false financial precision
    - In roi, do not state an exact return percentage or payback period without explicit assumptions; when data is insufficient, identify the relevant dependencies such as pricing, unit economics, sales volume, development or production cost, operating cost, adoption rate, and other concept-specific factors
    - If roi includes a number, state the assumptions that produce it; never invent a precise financial result merely to fill the field
    - investor_summary must agree with market_demand, startup_cost, roi, implementation_roadmap, risks, and constraints; do not promise fast payback, guaranteed returns, low investment risk, or high profitability unless the other concept fields substantiate the claim
    - investor_summary must concisely state the commercial opportunity, conditions for success, and material uncertainty or dependency where present
    - Across all four commercial fields, distinguish facts known or derived from the concept from estimates, assumptions, and unknowns that require validation, and keep them consistent with the User prompt, target_users, industries, use_cases, implementation roadmap, technical complexity, risks, and constraints
    - difficulty must begin with an explicit score from 1–10 in the form N/10 and briefly explain the concept-specific factors behind that score, considering applicable subsystem complexity, physical production, software, automation, certification, testing, supply chain, infrastructure, and other real engineering dependencies
    - modern_difficulty must use the same 1–10 scale but assess the present-day implementation specifically rather than repeat difficulty; explain how contemporary technology, hardware and software integration, automation, manufacturing, deployment, regulatory burden, and operational dependencies make it easier or harder than the underlying concept where applicable
    - dev_time must state the product maturity being estimated and remain logically consistent with implementation_roadmap, implementation_guides, both complexity metrics, risks, and constraints
    - When dev_time cannot be justified precisely, use a realistic time range and briefly name the schedule drivers instead of inventing an exact duration; do not claim a prototype, MVP, pilot, or production milestone on a timeline inconsistent with the roadmap sequence
    - Treat difficulty, modern_difficulty, and dev_time as mutually consistent implementation metrics, not marketing descriptions
    - modern_sketch_description must describe a clean engineering blueprint, not an artistic sketch
    - modern_sketch_description must identify and preserve every mandatory capability from the User prompt that can be represented visually, including concept-specific assembly methods, transport or deployment workflow, sensing or monitoring elements, automation mechanisms, and interactions between major subsystems
    - Describe how those visually representable capabilities appear in the system or operating scene, not merely as abstract claims, and do not omit them in favor of a generic product render
    - Do not invent visual features that are not supported by the User prompt or the generated concept
    - modern_sketch_description must explicitly avoid Renaissance, sepia, hand-drawn, or notebook aesthetics
    - modern_sketch_description must include orthographic views, labels, dimensions, arrows, and technical annotations
    - modern_sketch_description must feel like a CAD or product engineering presentation
    """

    user_prompt = f"""
    Category: {category}
    Creativity mode: {creativity}
    Target audience: {audience}
    User prompt: {user_prompt_text}
    Response language: {response_language}

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
    data["modern_category"] = category

    return data
