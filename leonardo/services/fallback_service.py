from categories import require_category_key
from config import DIFFICULTY, MATERIALS, USE_CASES
from i18n import category_display_name
from services.fallback_translations import (
    build_localized_fallback_concept,
    normalize_fallback_language,
)


_DEFAULT_PROMPT = "a practical idea that requires a clearer user brief"
_DEFAULT_AUDIENCE = "prospective users"
_DEFAULT_CATEGORY = "ai_software"


_IDEA_LENSES = (
    {
        "keywords": (
            "кормуш",
            "животн",
            "pet feeder",
            "animal feeder",
        ),
        "value": (
            "a controllable feeding routine with visible status, manual override, "
            "and straightforward cleaning"
        ),
        "problem": (
            "The hypothesis to test is whether feeding routines need more predictable "
            "dispensing, clearer refill status, and easier exception handling."
        ),
        "solution": (
            "Use a food-safe storage and measured-dispensing path controlled by an explicit "
            "schedule or manual action, with status feedback and a safe recovery path."
        ),
        "core_assumption": (
            "a controlled dispensing workflow is more useful than a simple reminder"
        ),
        "components": [
            "Food-safe storage and refill access",
            "Measured dispensing mechanism with manual override",
            "Schedule and status controls",
            "Cleaning, blockage detection, and safe recovery path",
        ],
        "materials": [
            "Washable food-contact prototype containers",
            "Replaceable dispensing mock-up components",
            "Low-voltage controls selected after safety review",
        ],
        "use_cases": [
            "Testing scheduled and manual feeding workflows",
            "Evaluating refill, cleaning, and blocked-dispensing scenarios",
        ],
        "risk": (
            "Food handling, cleaning, dispensing reliability, and animal-safe operation "
            "require specialist review and controlled testing."
        ),
    },
    {
        "keywords": (
            "шведск",
            "язык",
            "language learning",
            "learn swedish",
        ),
        "value": (
            "a repeatable practice loop connecting short Swedish-language exercises, "
            "recall, feedback, and learner-controlled review"
        ),
        "problem": (
            "The hypothesis to test is whether learners need a clearer progression from "
            "recognition to recall and practical language use without an overwhelming interface."
        ),
        "solution": (
            "Organize short practice units around a learner-selected goal, collect responses, "
            "offer explainable feedback, and let the learner choose what to review next."
        ),
        "core_assumption": (
            "a transparent practice-and-review loop helps users maintain useful learning habits"
        ),
        "components": [
            "Goal and proficiency self-assessment",
            "Swedish practice-unit library",
            "Response, feedback, and review workflow",
            "Learner-controlled progress and accessibility settings",
        ],
        "materials": [
            "Interface prototype and representative lesson samples",
            "Audio or text samples with documented usage rights",
            "Accessibility and usability test materials",
        ],
        "use_cases": [
            "Practising vocabulary and short real-life language tasks",
            "Reviewing difficult material through a learner-controlled queue",
        ],
        "risk": (
            "Lesson quality, accessibility, feedback clarity, and content rights must be "
            "reviewed before broader use."
        ),
    },
    {
        "keywords": (
            "прогноз",
            "спрос",
            "demand forecast",
            "retail forecast",
        ),
        "value": (
            "an explainable demand-planning workflow that combines available store data, "
            "visible uncertainty, and human review"
        ),
        "problem": (
            "The hypothesis to test is whether planning decisions are hindered by fragmented "
            "sales inputs, unclear assumptions, and no consistent way to review forecast errors."
        ),
        "solution": (
            "Create a traceable pipeline that checks available data, produces a simple baseline, "
            "shows assumptions and uncertainty, and records human adjustments for later review."
        ),
        "core_assumption": (
            "an explainable baseline with human review is more useful than an opaque prediction"
        ),
        "components": [
            "Store-data import and quality checks",
            "Baseline forecast and uncertainty view",
            "Human adjustment and reason log",
            "Outcome comparison and error-review workflow",
        ],
        "materials": [
            "Anonymized or synthetic store-data samples",
            "Data-quality and assumption checklist",
            "Dashboard and decision-log prototype",
        ],
        "use_cases": [
            "Reviewing replenishment hypotheses for selected products",
            "Comparing baseline forecasts with later observed outcomes",
        ],
        "risk": (
            "Incomplete data, changing store conditions, and misunderstood uncertainty can "
            "produce misleading planning recommendations."
        ),
    },
)


_CREATIVITY_PROFILES = {
    "low": {
        "label": "focused",
        "novelty": "a focused adaptation of established product and engineering patterns",
        "complexity": "Keep the first version deliberately narrow and easy to test.",
        "technology_risk": "The main risk is choosing the wrong core assumption before speaking with users.",
        "optional_features": [
            "A configurable workflow that can be enabled only after the core use case is validated",
        ],
        "roadmap": {
            "prototype": "Build the smallest representation that can test the central assumption",
            "mvp": "Keep only the essential workflow and remove unvalidated additions",
            "pilot": "Run a limited, closely observed evaluation with the intended audience",
            "production": "Standardize only the parts supported by reliable test evidence",
        },
    },
    "medium": {
        "label": "balanced",
        "novelty": "a distinctive combination of proven patterns with one clearly testable differentiator",
        "complexity": "Balance a clear core workflow with a small number of optional modules.",
        "technology_risk": "Integration and user-comprehension risks must be tested before expanding scope.",
        "optional_features": [
            "An optional feedback module tailored to the intended audience",
            "A configurable reporting or guidance view for different operating contexts",
        ],
        "roadmap": {
            "prototype": "Compare the core workflow with one differentiated alternative",
            "mvp": "Integrate the strongest tested path with limited modular extensions",
            "pilot": "Evaluate usefulness, usability, and operational fit with the intended audience",
            "production": "Scale the validated configuration while retaining rollback paths",
        },
    },
    "high": {
        "label": "exploratory",
        "novelty": "an ambitious but physically plausible exploration of several prototype approaches",
        "complexity": "Explore multiple approaches, but isolate them so each can be tested or removed independently.",
        "technology_risk": "Novel interactions and technical assumptions may fail independently and require simpler alternatives.",
        "optional_features": [
            "A modular alternative interaction path for comparison during testing",
            "An optional adaptive workflow governed by explicit user controls",
            "A simulation or sandbox mode for evaluating risky assumptions safely",
        ],
        "roadmap": {
            "prototype": "Test several physically plausible approaches as separate experiments",
            "mvp": "Select the most credible approach and retain alternatives only as optional modules",
            "pilot": "Stress-test the selected approach and its simpler fallback with the intended audience",
            "production": "Scale only validated modules and preserve conservative operating limits",
        },
    },
}


_STAGE_PLANS = {
    "prototype": {
        "label": "prototype",
        "goal": "turn the user brief into a testable representation of its core assumption",
        "steps": [
            "Write the problem, intended outcome, and unsafe assumptions as testable statements",
            "Build a low-fidelity representation of the essential workflow",
            "Observe representative users completing the core task and record failure points",
        ],
        "specialists": [
            "Product or service designer",
            "Domain specialist appropriate to the selected category",
            "Prototype and test facilitator",
        ],
        "technologies": [
            "Low-fidelity prototyping tools",
            "Requirements and decision log",
            "Test observation and feedback tools",
        ],
    },
    "mvp": {
        "label": "minimum viable version",
        "goal": "implement the smallest dependable workflow that demonstrates practical user value",
        "steps": [
            "Convert validated prototype findings into a limited functional specification",
            "Implement the core workflow with observable failure handling",
            "Evaluate accessibility, maintainability, and task completion with intended users",
        ],
        "specialists": [
            "Product engineer",
            "User-experience specialist",
            "Quality and safety reviewer",
        ],
        "technologies": [
            "Implementation tools suitable for the selected category",
            "Basic monitoring and issue tracking",
            "Repeatable test environment",
        ],
    },
    "pilot": {
        "label": "pilot",
        "goal": "evaluate the concept in a limited realistic setting without assuming broad demand",
        "steps": [
            "Define a reversible pilot with clear operating boundaries",
            "Train participants and document support needs",
            "Collect qualitative feedback and operational evidence before deciding whether to expand",
        ],
        "specialists": [
            "Pilot coordinator",
            "Domain or field specialist",
            "User support and evaluation lead",
        ],
        "technologies": [
            "Pilot monitoring tools",
            "Feedback and incident log",
            "Configuration and rollback controls",
        ],
    },
    "production": {
        "label": "production candidate",
        "goal": "prepare only validated capabilities for repeatable delivery and support",
        "steps": [
            "Document the validated configuration and operating limits",
            "Define quality, support, and maintenance responsibilities",
            "Review evidence, costs, and unresolved risks before any wider rollout",
        ],
        "specialists": [
            "Delivery or production lead",
            "Quality assurance specialist",
            "Operations and support owner",
        ],
        "technologies": [
            "Versioned production tooling",
            "Quality and monitoring systems",
            "Support documentation and issue management",
        ],
    },
}


def _normalize_text(value, default):
    normalized = " ".join(str(value or "").split())
    return normalized or default


def _resolve_creativity_mode(creativity_mode):
    normalized = _normalize_text(creativity_mode, "").casefold()
    if normalized in {"classic", "low", "minimal", "minimum"}:
        return "low"
    if normalized in {"experimental", "high", "maximum", "max"}:
        return "high"
    return "medium"


def _title_fragment(prompt_text, word_limit=9):
    words = prompt_text.split()
    fragment = " ".join(words[:word_limit])
    if len(words) > word_limit:
        fragment += "…"
    return fragment[0].upper() + fragment[1:]


def _select_idea_lens(prompt_text, category):
    normalized_prompt = prompt_text.casefold()
    for lens in _IDEA_LENSES:
        if any(keyword in normalized_prompt for keyword in lens["keywords"]):
            return lens

    return {
        "value": (
            f"a testable workflow for the task described as '{prompt_text}', with explicit "
            "inputs, observable outcomes, and user feedback"
        ),
        "problem": (
            f"The hypothesis to test is whether the current approach to '{prompt_text}' "
            "creates a meaningful problem for the intended audience."
        ),
        "solution": (
            f"Represent '{prompt_text}' as a sequence of explicit user actions, a minimal "
            "core function, an observable outcome, and a reversible recovery path."
        ),
        "core_assumption": (
            f"a structured workflow can improve the task described as '{prompt_text}'"
        ),
        "components": [
            f"Input and task-definition module for '{prompt_text}'",
            "Minimal core-function prototype",
            "Outcome, feedback, and recovery workflow",
        ],
        "materials": generate_materials(category),
        "use_cases": generate_use_cases(category)[:2],
        "risk": (
            "The generic fallback interpretation may overlook domain-specific safety, "
            "accessibility, or feasibility requirements."
        ),
    }


def generate_difficulty(category, creativity_mode):
    category_key = require_category_key(category)
    base = DIFFICULTY.get(category_key, "High")
    if _resolve_creativity_mode(creativity_mode) == "high" and base == "Medium":
        return "High"
    return base


def generate_modern_difficulty(category):
    category_key = require_category_key(category)
    return DIFFICULTY.get(category_key, "High")


def generate_materials(category):
    category_key = require_category_key(category)
    return list(
        MATERIALS.get(
            category_key,
            [
                "Replaceable off-the-shelf prototype components",
                "Low-fidelity mock-up materials",
                "Test fixtures selected after the operating context is clarified",
            ],
        )
    )


def generate_use_cases(category):
    category_key = require_category_key(category)
    return list(
        USE_CASES.get(
            category_key,
            [
                "User workflow validation",
                "Controlled concept demonstration",
                "Operational feasibility testing",
            ],
        )
    )


def _build_implementation_guide(
    stage,
    prompt_text,
    audience,
    profile,
    lens,
    materials,
):
    plan = _STAGE_PLANS[stage]
    optional_features = "; ".join(profile["optional_features"])

    return {
        "execution_plan": {
            "goal": (
                f"For '{prompt_text}', {plan['goal']} for {audience} by testing whether "
                f"{lens['core_assumption']}."
            ),
            "steps": [
                *plan["steps"],
                f"Review the domain assumption: {lens['core_assumption']}",
                f"Review whether the {profile['label']} creativity scope remains appropriate for {audience}",
            ],
            "specialists": list(plan["specialists"]),
            "technologies": list(plan["technologies"]),
            "estimated_budget": (
                "Not estimated in fallback mode; prepare a bottom-up budget after scope, "
                "suppliers, and validation needs are known."
            ),
            "stage_risks": [
                profile["technology_risk"],
                lens["risk"],
                f"The interpretation of '{prompt_text}' may not match the priorities of {audience}.",
            ],
            "readiness_criteria": [
                f"Evidence shows that the {plan['label']} addresses the stated user brief",
                f"Feedback from {audience} is documented, including negative findings",
                "Unresolved safety, feasibility, and support questions are recorded",
            ],
            "expected_output": (
                f"A {plan['label']} decision package for '{prompt_text}' with evidence, "
                "limitations, and a clear next-step recommendation."
            ),
        },
        "technical_architecture": {
            "system_schema": (
                f"A modular representation of the core workflow for '{prompt_text}', "
                f"separating required functions from optional features. {lens['solution']}"
            ),
            "module_interaction": (
                f"Core modules support the primary task for {audience}; optional modules "
                f"remain independently testable: {optional_features}."
            ),
            "process_flow": (
                "User need → explicit input → core workflow → observable outcome → "
                "feedback and revision."
            ),
            "deployment_logic": (
                f"Use a reversible {plan['label']} deployment with documented limits "
                "and a simpler fallback path."
            ),
        },
        "resources_budget": {
            "team": list(plan["specialists"]),
            "stack": list(plan["technologies"]),
            "materials": list(materials),
            "cost_notes": (
                "Costs are unknown in fallback mode and depend on validated scope, "
                "implementation choices, testing, and support requirements."
            ),
        },
        "validation": {
            "tests": [
                f"Task walkthrough for '{prompt_text}'",
                f"Core-assumption review: {lens['core_assumption']}",
                f"Usability and comprehension review with {audience}",
                "Failure, recovery, and boundary-condition review",
            ],
            "kpi": [
                "Traceability to the original user brief",
                f"Quality of feedback from {audience}",
                "Observed task completion and documented failure modes",
            ],
            "success_criteria": [
                "The core value hypothesis is supported by observed evidence",
                "Critical risks have owners and a realistic validation path",
                "The next-stage decision can be explained without unsupported claims",
            ],
        },
    }


def build_fallback_concept(
    category,
    prompt_text,
    creativity_mode,
    audience,
    language="en",
):
    category_key = require_category_key(category)
    normalized_language = normalize_fallback_language(language)
    if normalized_language != "en":
        return build_localized_fallback_concept(
            language=normalized_language,
            category=category_key,
            prompt_text=prompt_text,
            creativity_mode=creativity_mode,
            audience=audience,
            mode=_resolve_creativity_mode(creativity_mode),
            difficulty=generate_difficulty(category_key, creativity_mode),
            modern_difficulty=generate_modern_difficulty(category_key),
        )

    prompt = _normalize_text(prompt_text, _DEFAULT_PROMPT)
    audience_text = _normalize_text(audience, _DEFAULT_AUDIENCE)
    category_text = category_display_name(category_key, "en")
    mode = _resolve_creativity_mode(creativity_mode)
    profile = _CREATIVITY_PROFILES[mode]

    title_fragment = _title_fragment(prompt)
    lens = _select_idea_lens(prompt, category_key)
    materials = list(lens["materials"])
    category_use_cases = list(lens["use_cases"])
    optional_features = profile["optional_features"]
    difficulty = generate_difficulty(category_key, creativity_mode)
    modern_difficulty = generate_modern_difficulty(category_key)

    implementation_roadmap = {
        stage: (
            f"{instruction} for '{prompt}', using feedback from {audience_text}."
        )
        for stage, instruction in profile["roadmap"].items()
    }
    implementation_guides = {
        stage: _build_implementation_guide(
            stage,
            prompt,
            audience_text,
            profile,
            lens,
            materials,
        )
        for stage in _STAGE_PLANS
    }

    return {
        "title": f"{title_fragment} — {profile['label'].title()} Concept",
        "leonardo_concept": (
            f"A preliminary fallback interpretation of '{prompt}' based on observable "
            "needs, simple mechanisms, and ideas that can be tested before expansion."
        ),
        "leonardo_sketch_description": (
            f"A Renaissance notebook study of '{prompt}', showing the primary user task, "
            "separate functional elements, motion or information flow, and handwritten "
            "questions marking assumptions that still require testing."
        ),
        "modern_product_name": f"{title_fragment} Pilot",
        "modern_category": category_text,
        "executive_summary": (
            f"This local fallback concept treats '{prompt}' as the central user brief for "
            f"{audience_text}. It proposes {lens['value']} through {profile['novelty']} and "
            "keeps market, cost, and feasibility statements as hypotheses that require validation."
        ),
        "problem_statement": (
            f"The stated challenge is '{prompt}'. {lens['problem']} The actual priorities "
            f"and constraints of {audience_text} must be confirmed before selecting a solution."
        ),
        "target_users": [
            audience_text,
            f"People who currently handle the task described as '{prompt}'",
            "Teams responsible for evaluating feasibility, safety, and delivery",
        ],
        "industries": [
            category_text,
            "User-centered product development",
            "Prototype and operational validation",
        ],
        "use_cases": [
            f"Primary use case: {prompt}",
            *category_use_cases[:2],
        ],
        "modern_principle": (
            f"For {audience_text}, {lens['solution']} {profile['complexity']} Each optional "
            "capability remains removable until evidence supports it."
        ),
        "system_components": [
            *lens["components"],
            f"Audience interaction and feedback module for {audience_text}",
            "Monitoring, failure reporting, and safe recovery controls",
            *optional_features,
        ],
        "materials": materials,
        "technical_requirements": [
            f"A documented interpretation of the user brief: {prompt}",
            f"Accessibility and usability checks appropriate to {audience_text}",
            "Replaceable modules with observable inputs, outputs, and failure states",
            f"Risk controls appropriate to the {profile['label']} creativity scope",
        ],
        "modern_sketch_description": (
            f"A modern concept blueprint for '{prompt}' with the core workflow highlighted, "
            f"optional {profile['label']} modules visually separated, audience touchpoints "
            "labeled, and unverified assumptions marked for testing."
        ),
        "implementation_roadmap": implementation_roadmap,
        "implementation_guides": implementation_guides,
        "deployment_strategy": (
            f"Start with a reversible evaluation of '{prompt}' for {audience_text}; expand "
            "only when user evidence, technical testing, operating limits, and support needs "
            "are documented."
        ),
        "risks": [
            profile["technology_risk"],
            lens["risk"],
            f"The proposed interpretation of '{prompt}' may miss the real user problem.",
            f"The needs of {audience_text} may differ from the initial brief.",
            "Feasibility, accessibility, safety, and operating costs remain unverified.",
        ],
        "constraints": [
            "Fallback mode cannot establish market demand or technical feasibility.",
            "Scope depends on user interviews, prototype evidence, and category-specific review.",
            "Cost and delivery planning depend on implementation choices that are not yet known.",
        ],
        "market_demand": (
            f"Demand for a solution to '{prompt}' among {audience_text} is a preliminary "
            "hypothesis. Validate it through direct user conversations and observed workflows "
            "before making commercial claims."
        ),
        "startup_cost": (
            "No fixed startup cost is asserted in fallback mode. Prepare a bottom-up estimate "
            "after scope, materials, specialist effort, validation, and support are defined."
        ),
        "roi": (
            "Return on investment is undetermined. Evaluate it using verified user value, "
            "measured operating outcomes, total delivery cost, and realistic adoption evidence."
        ),
        "investor_summary": (
            f"'{prompt}' is presented as a preliminary {profile['label']} concept for "
            f"{audience_text}, not as a proven opportunity. Commercial potential depends on "
            "user validation, technical feasibility, delivery economics, and evidence from a "
            "limited pilot."
        ),
        "difficulty": difficulty,
        "modern_difficulty": modern_difficulty,
        "dev_time": (
            "Timeline is undetermined in fallback mode; estimate it after the core assumption, "
            "implementation path, testing obligations, and delivery resources are defined."
        ),
    }
