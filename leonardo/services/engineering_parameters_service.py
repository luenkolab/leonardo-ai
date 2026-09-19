import json
import re

from i18n import ai_language_name
from services.openai_client import get_text_client


ENGINEERING_PARAMETERS_MODEL = "gpt-4o-mini"
PARAMETER_STATUSES = {
    "missing",
    "suggested",
    "confirmed",
    "not_applicable",
}
PARAMETER_SOURCES = {"user", "ai", "concept"}

UNIVERSAL_PARAMETER_DEFINITIONS = (
    ("unit_system", "Unit System"),
    ("overall_dimensions_envelope", "Overall Dimensions / Envelope"),
    ("mass_weight", "Mass / Weight"),
    ("primary_materials", "Primary Materials"),
    ("design_loads_forces", "Design Loads / Forces"),
    ("tolerances", "Tolerances"),
    ("operating_environment", "Operating Environment"),
    ("safety_design_factors", "Safety / Design Factors"),
    ("interfaces_connections", "Interfaces / Connections"),
    ("manufacturing_constraints", "Manufacturing Constraints"),
    ("applicable_standards", "Applicable Standards"),
    ("service_maintenance_conditions", "Service / Maintenance Conditions"),
)


def normalize_parameter_key(value):
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value or "").casefold()).strip("_")
    if not normalized:
        raise ValueError("Engineering parameter key is required")
    return normalized


def _optional_text(value):
    if value is None:
        return None
    normalized = " ".join(str(value).split())
    return normalized or None


def normalize_parameter(parameter, default_source="user"):
    if not isinstance(parameter, dict):
        raise ValueError("Engineering parameter must be a JSON object")
    key = normalize_parameter_key(parameter.get("key"))
    label = " ".join(str(parameter.get("label") or "").split())
    if not label:
        raise ValueError(f"Engineering parameter label is required for {key}")
    status = parameter.get("status", "missing")
    source = parameter.get("source", default_source)
    if status not in PARAMETER_STATUSES:
        raise ValueError(f"Unsupported engineering parameter status: {status}")
    if source not in PARAMETER_SOURCES:
        raise ValueError(f"Unsupported engineering parameter source: {source}")
    return {
        "key": key,
        "label": label,
        "value": _optional_text(parameter.get("value")),
        "unit": _optional_text(parameter.get("unit")),
        "status": status,
        "source": source,
        "rationale": _optional_text(parameter.get("rationale")),
    }


def build_universal_parameters():
    return [
        {
            "key": key,
            "label": label,
            "value": None,
            "unit": None,
            "status": "missing",
            "source": "user",
            "rationale": None,
        }
        for key, label in UNIVERSAL_PARAMETER_DEFINITIONS
    ]


def build_empty_parameter_set():
    return {
        "universal": build_universal_parameters(),
        "project_specific": [],
    }


def _deduplicate_parameters(parameters, default_source):
    unique = []
    seen_keys = set()
    seen_labels = set()
    for raw_parameter in parameters:
        parameter = normalize_parameter(raw_parameter, default_source)
        label_key = parameter["label"].casefold()
        if parameter["key"] in seen_keys or label_key in seen_labels:
            continue
        seen_keys.add(parameter["key"])
        seen_labels.add(label_key)
        unique.append(parameter)
    return unique


def validate_parameter_set(value):
    if not isinstance(value, dict):
        raise ValueError("Engineering parameter set must be a JSON object")
    universal = value.get("universal")
    project_specific = value.get("project_specific")
    if not isinstance(universal, list) or not isinstance(project_specific, list):
        raise ValueError("Engineering parameter set must contain two arrays")
    return {
        "universal": _deduplicate_parameters(universal, "user"),
        "project_specific": _deduplicate_parameters(project_specific, "ai"),
    }


def merge_project_suggestions(parameter_set, suggestions):
    current = validate_parameter_set(parameter_set)
    universal_keys = {item["key"] for item in current["universal"]}
    universal_labels = {item["label"].casefold() for item in current["universal"]}
    incoming = _deduplicate_parameters(suggestions, "ai")
    incoming = [
        item
        for item in incoming
        if item["key"] not in universal_keys
        and item["label"].casefold() not in universal_labels
    ]

    merged = list(current["project_specific"])
    positions = {item["key"]: index for index, item in enumerate(merged)}
    label_positions = {
        item["label"].casefold(): index for index, item in enumerate(merged)
    }
    for suggestion in incoming:
        position = positions.get(suggestion["key"])
        if position is None:
            position = label_positions.get(suggestion["label"].casefold())
        if position is None:
            positions[suggestion["key"]] = len(merged)
            label_positions[suggestion["label"].casefold()] = len(merged)
            merged.append(suggestion)
            continue
        existing = merged[position]
        if existing["status"] == "confirmed" or existing["source"] == "user":
            continue
        suggestion["key"] = existing["key"]
        merged[position] = suggestion

    return {
        "universal": current["universal"],
        "project_specific": merged,
    }


def suggest_project_parameters(
    concept_data,
    category,
    original_prompt,
    language,
):
    """Make one explicit text-model call for project-specific parameters."""
    context = {
        "title": concept_data.get("title"),
        "category": category,
        "executive_summary": concept_data.get("executive_summary"),
        "technical_requirements": concept_data.get("technical_requirements"),
        "materials": concept_data.get("materials"),
        "system_components": concept_data.get("system_components"),
        "constraints": concept_data.get("constraints"),
        "risks": concept_data.get("risks"),
        "modern_principle": concept_data.get("modern_principle"),
        "problem_statement": concept_data.get("problem_statement"),
        "use_cases": concept_data.get("use_cases"),
        "original_prompt": original_prompt,
    }
    universal = [
        {"key": key, "label": label}
        for key, label in UNIVERSAL_PARAMETER_DEFINITIONS
    ]
    system_prompt = f"""
You propose preliminary, project-specific engineering inputs for a physical product.
Write labels and rationale in {ai_language_name(language)}.

Return exactly one JSON object with a project_specific array. Each item must contain:
key, label, value, unit, status, source, rationale.

Rules:
- Infer parameters from the supplied project context, not from a hardcoded category list.
- Suggest only parameters specific to this project; do not duplicate the Universal Core by key or meaning.
- Use stable lowercase snake_case keys.
- source must be "ai".
- If evidence is insufficient, set value to null and status to "missing".
- If a preliminary value is useful, use a range or clearly stated assumption, set status to "suggested", and explain the assumption briefly.
- Never invent unsupported precision, certification, compliance, dimensions, loads, or performance.
- Do not infer measurements from images; no image data is provided or authoritative.
- Do not claim professional validation, structural safety, legal approval, or certification.
- Keep unit null when no unit is applicable or supported.
- Do not add information unrelated to engineering preparation for this specific project.

Universal Core that must not be duplicated:
{json.dumps(universal, ensure_ascii=False)}
"""
    response = get_text_client().chat.completions.create(
        model=ENGINEERING_PARAMETERS_MODEL,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Empty response from OpenAI")
    payload = json.loads(content)
    suggestions = payload.get("project_specific")
    if not isinstance(suggestions, list):
        raise ValueError("AI response must contain a project_specific array")
    normalized = _deduplicate_parameters(suggestions, "ai")
    for parameter in normalized:
        if not parameter["rationale"]:
            raise ValueError("AI engineering suggestions require a rationale")
        parameter["source"] = "ai"
        parameter["status"] = (
            "missing" if parameter["value"] is None else "suggested"
        )
    return normalized
