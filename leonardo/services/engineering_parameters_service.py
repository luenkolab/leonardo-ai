import json
import re
from decimal import Decimal

from i18n import ai_language_name
from services.general_arrangement_service import normalize_known_value
from services.openai_client import get_text_client


ENGINEERING_PARAMETERS_MODEL = "gpt-4o-mini"
PARAMETER_STATUSES = {
    "missing",
    "suggested",
    "confirmed",
    "not_applicable",
}
PARAMETER_SOURCES = {"user", "ai", "concept"}
COMPONENT_GEOMETRY_FIELDS = ("length", "width", "height", "x", "y", "z")
COMPONENT_GEOMETRY_UNITS = {"mm", "cm", "m"}
_LENGTH_UNIT_TO_MM = {
    "mm": Decimal("1"),
    "cm": Decimal("10"),
    "m": Decimal("1000"),
}

UNIVERSAL_PARAMETER_DEFINITIONS = (
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
        "component_geometry": {},
        "connections": [],
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
    raw_component_geometry = value.get("component_geometry", {})
    if not isinstance(raw_component_geometry, dict):
        raise ValueError("Component geometry must be a JSON object")
    component_geometry = {}
    for raw_key, raw_geometry in raw_component_geometry.items():
        key = normalize_parameter_key(raw_key)
        if not isinstance(raw_geometry, dict):
            raise ValueError(f"Component geometry must be an object for {key}")
        geometry = {
            field: _optional_text(raw_geometry.get(field))
            for field in COMPONENT_GEOMETRY_FIELDS
        }
        if not any(geometry.values()):
            continue
        unit = _optional_text(raw_geometry.get("unit"))
        if unit is None or unit.casefold() not in COMPONENT_GEOMETRY_UNITS:
            raise ValueError(f"Unsupported component geometry unit for {key}")
        geometry["unit"] = unit.casefold()
        component_geometry[key] = geometry
    raw_connections = value.get("connections", [])
    if not isinstance(raw_connections, list):
        raise ValueError("Connections must be a JSON array")
    connections = []
    for raw_connection in raw_connections:
        if not isinstance(raw_connection, dict):
            raise ValueError("Connection must be a JSON object")
        connection_type = _optional_text(raw_connection.get("connection_type"))
        if connection_type is None:
            raise ValueError("Connection type is required")
        raw_quantity = raw_connection.get("quantity")
        if raw_quantity is None or raw_quantity == "":
            quantity = None
        elif (
            isinstance(raw_quantity, bool)
            or not str(raw_quantity).strip().isdigit()
            or int(raw_quantity) <= 0
        ):
            raise ValueError("Connection quantity must be a positive integer")
        else:
            quantity = int(raw_quantity)
        connections.append(
            {
                "component_a": normalize_parameter_key(
                    raw_connection.get("component_a")
                ),
                "component_b": normalize_parameter_key(
                    raw_connection.get("component_b")
                ),
                "connection_type": connection_type,
                "fastener_type": _optional_text(
                    raw_connection.get("fastener_type")
                ),
                "quantity": quantity,
                "note": _optional_text(raw_connection.get("note")),
            }
        )
    return {
        "universal": _deduplicate_parameters(universal, "user"),
        "project_specific": _deduplicate_parameters(project_specific, "ai"),
        "component_geometry": component_geometry,
        "connections": connections,
    }


def _ai_parameters(parameters, universal=False):
    if not isinstance(parameters, list):
        raise ValueError("AI engineering parameters must be arrays")
    definitions = dict(UNIVERSAL_PARAMETER_DEFINITIONS)
    normalized = []
    for raw_parameter in parameters:
        if not isinstance(raw_parameter, dict):
            continue
        candidate = dict(raw_parameter)
        if universal:
            try:
                key = normalize_parameter_key(candidate.get("key"))
            except ValueError:
                continue
            if key not in definitions:
                continue
            candidate["key"] = key
            candidate["label"] = definitions[key]
        parameter = normalize_parameter(candidate, "ai")
        parameter["source"] = "ai"
        parameter["status"] = (
            "missing" if parameter["value"] is None else "suggested"
        )
        if parameter["value"] is not None and not parameter["rationale"]:
            raise ValueError("AI engineering suggestions require a rationale")
        normalized.append(parameter)
    return _deduplicate_parameters(normalized, "ai")


def suggest_engineering_data(
    concept_data,
    category,
    original_prompt,
    language,
    parameter_set,
    components,
):
    """Make one shared-client call for all missing engineering data."""
    current = validate_parameter_set(parameter_set)
    component_context = [
        {"key": component.key, "name": component.name} for component in components
    ]
    context = {
        "category": category,
        "original_prompt": original_prompt,
        "concept_data": concept_data,
        "engineering_parameters": current,
        "components": component_context,
    }
    system_prompt = f"""
You are the AI Engineer for a physical-product concept. Work in this exact order:
1. Complete only missing Universal Core engineering parameters.
2. Generate project-specific parameters using the completed Core context.
3. Complete only missing component geometry fields.
4. Add only missing connections between supplied stable component keys.

Return exactly one JSON object with these existing contract keys:
universal, project_specific, component_geometry, connections.
Universal and project_specific items use key, label, value, unit, status, source,
rationale. Geometry fields are length, width, height, x, y, z, unit. Connection
fields are component_a, component_b, connection_type, fastener_type, quantity, note.

Rules:
- Write labels and rationale in {ai_language_name(language)}.
- Never replace non-empty Core values or existing component geometry fields.
- Rebuild project_specific for the current context on every run. Recalculate records
  whose current source is "ai"; do not replace records with a non-AI source.
- Keep existing connections and add only genuinely missing component pairs.
- source must be "ai" for parameter records. AI suggestions are preliminary and
  are not verified engineering truth.
- Use realistic physical scale based on purpose and project context: bridges use
  bridge scale, service robots use human/robotic scale, vehicles use vehicle scale,
  wearables use body scale, industrial equipment uses industrial scale, and drones
  use mission/payload scale.
- No image pixels or visual proportions are available as authoritative dimensions.
  Never infer confirmed physical scale from images.
- Overall Dimensions / Envelope, when proposed, must be labelled axes in the form
  "length=<number>; width=<number>; height=<number>" with one of mm, cm, or m.
- Component geometry may reference only the supplied stable component keys. Use the
  existing component unit when a partial geometry record already has one.
- Dimensions must be positive numbers. Coordinates may be zero or positive.
- Connections may reference only two different supplied component keys. Quantity is
  a positive integer or null.
- Do not invent unsupported precision, certification, compliance, safety validation,
  performance, geometry, or connections. Use null when a reasonable preliminary
  value cannot be supported by the structured project context.
- Do not return extra top-level keys.
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
    if not isinstance(payload, dict):
        raise ValueError("AI Engineer response must be a JSON object")
    normalized = validate_parameter_set(
        {
            "universal": _ai_parameters(payload.get("universal", []), True),
            "project_specific": _ai_parameters(
                payload.get("project_specific", [])
            ),
            "component_geometry": payload.get("component_geometry", {}),
            "connections": payload.get("connections", []),
        }
    )
    return normalized


def _converted_geometry_value(value, source_unit, target_unit, field, component_key):
    normalized = normalize_known_value(
        value,
        source_unit,
        source_type="engineering_parameter",
        source_key=f"component_geometry.{component_key}.{field}",
    )
    if normalized is None or normalized.quantity != "length":
        return None
    if field in {"length", "width", "height"} and normalized.value <= 0:
        return None
    if field in {"x", "y", "z"} and normalized.value < 0:
        return None
    converted = normalized.value / _LENGTH_UNIT_TO_MM[target_unit]
    return format(converted.normalize(), "f")


def merge_ai_engineering_data(parameter_set, suggestions, valid_component_keys):
    """Fill missing fields while preserving every existing non-empty value."""
    current = validate_parameter_set(parameter_set)
    incoming = validate_parameter_set(suggestions)
    incoming_universal = {item["key"]: item for item in incoming["universal"]}
    for parameter in current["universal"]:
        suggestion = incoming_universal.get(parameter["key"])
        if (
            parameter["value"] is not None
            or not suggestion
            or suggestion["value"] is None
        ):
            continue
        if (
            parameter["unit"]
            and suggestion["unit"]
            and parameter["unit"].casefold() != suggestion["unit"].casefold()
        ):
            continue
        parameter.update(
            {
                "value": suggestion["value"],
                "unit": parameter["unit"] or suggestion["unit"],
                "status": "suggested",
                "source": "ai",
                "rationale": suggestion["rationale"],
            }
        )

    universal_keys = {item["key"] for item in current["universal"]}
    universal_labels = {item["label"].casefold() for item in current["universal"]}
    merged_project = [
        parameter
        for parameter in current["project_specific"]
        if parameter["source"] != "ai"
    ]
    protected_keys = {item["key"] for item in merged_project}
    protected_labels = {item["label"].casefold() for item in merged_project}
    for suggestion in incoming["project_specific"]:
        if (
            suggestion["key"] in universal_keys
            or suggestion["label"].casefold() in universal_labels
            or suggestion["key"] in protected_keys
            or suggestion["label"].casefold() in protected_labels
        ):
            continue
        merged_project.append(suggestion)
    current["project_specific"] = merged_project

    valid_keys = {normalize_parameter_key(key) for key in valid_component_keys}
    for component_key, suggestion in incoming["component_geometry"].items():
        if component_key not in valid_keys:
            continue
        existing = current["component_geometry"].get(component_key)
        target_unit = existing["unit"] if existing else suggestion["unit"]
        merged_geometry = dict(existing or {"unit": target_unit})
        for field in COMPONENT_GEOMETRY_FIELDS:
            if merged_geometry.get(field) is not None or suggestion.get(field) is None:
                continue
            merged_geometry[field] = _converted_geometry_value(
                suggestion[field],
                suggestion["unit"],
                target_unit,
                field,
                component_key,
            )
        if any(
            merged_geometry.get(field) is not None
            for field in COMPONENT_GEOMETRY_FIELDS
        ):
            current["component_geometry"][component_key] = merged_geometry

    connection_keys = {
        frozenset((item["component_a"], item["component_b"]))
        for item in current["connections"]
    }
    for connection in incoming["connections"]:
        if (
            connection["component_a"] not in valid_keys
            or connection["component_b"] not in valid_keys
            or connection["component_a"] == connection["component_b"]
        ):
            continue
        identity = frozenset((connection["component_a"], connection["component_b"]))
        if identity in connection_keys:
            continue
        current["connections"].append(connection)
        connection_keys.add(identity)
    return validate_parameter_set(current)
