import base64
import json
import re
from decimal import Decimal, InvalidOperation
from typing import get_args

from i18n import ai_language_name
from services.general_arrangement_service import PrimitiveType
from services.openai_client import get_text_client


ENGINEERING_PARAMETERS_MODEL = "gpt-4o-mini"
PARAMETER_STATUSES = {
    "missing",
    "suggested",
    "confirmed",
    "not_applicable",
}
PARAMETER_SOURCES = {"user", "ai", "concept"}
COMPONENT_GEOMETRY_UNITS = {"mm", "cm", "m"}
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
        raw_children = raw_geometry.get("subgeometry", [])
        if not isinstance(raw_children, list):
            raise ValueError(f"Component subgeometry must be an array for {key}")
        records = [(key, raw_geometry, False)]
        seen_children = set()
        for raw_child in raw_children:
            if not isinstance(raw_child, dict):
                raise ValueError(f"Component subgeometry must contain objects for {key}")
            child_key = normalize_parameter_key(raw_child.get("key"))
            if child_key not in seen_children:
                seen_children.add(child_key)
                records.append((f"{key}.{child_key}", raw_child, True))

        normalized_records = {}
        parent_unit = _optional_text(raw_geometry.get("unit"))
        for record_key, raw_record, is_child in records:
            fields = (
                ("length", "width", "height", "diameter", "wall_thickness")
                if is_child
                else ("length", "width", "height")
            )
            geometry = {
                field: _optional_text(raw_record.get(field)) for field in fields
            }
            source = _optional_text(raw_record.get("source"))
            if source is not None:
                source = source.casefold()
                if source not in {"ai", "user"}:
                    raise ValueError(f"Unsupported component geometry source for {record_key}")
                geometry["source"] = source
            if not is_child and "wall_thickness" in raw_record:
                geometry["wall_thickness"] = _optional_text(
                    raw_record.get("wall_thickness")
                )

            primitive = _optional_text(raw_record.get("primitive"))
            if primitive is not None:
                primitive = primitive.casefold()
                if primitive not in get_args(PrimitiveType):
                    raise ValueError(f"Unsupported component primitive for {record_key}")
                geometry["primitive"] = primitive
            elif "primitive" in raw_record:
                geometry["primitive"] = None
            if is_child:
                if primitive is None:
                    raise ValueError(
                        f"Unsupported component subgeometry primitive for {record_key}"
                    )
                geometry.update(
                    key=record_key.rsplit(".", 1)[-1],
                    role=_optional_text(raw_record.get("role")),
                )

            raw_position = raw_record.get("position")
            if raw_position is not None and not isinstance(raw_position, dict):
                raise ValueError(f"Component position must be an object for {record_key}")
            position_source = raw_position if raw_position is not None else raw_record
            position = {
                field: _optional_text(position_source.get(field))
                for field in ("x", "y", "z")
            }
            if raw_position is not None:
                if any(position.values()) or "position" in raw_record:
                    geometry["position"] = position
            elif not is_child:
                geometry.update(position)

            raw_orientation = raw_record.get("orientation")
            if raw_orientation is not None and not isinstance(raw_orientation, dict):
                raise ValueError(f"Component orientation must be an object for {record_key}")
            orientation = {
                field: _optional_text((raw_orientation or {}).get(field))
                for field in ("roll", "pitch", "yaw")
            }
            nonzero_angles = []
            for field, raw_angle in orientation.items():
                if raw_angle is None:
                    continue
                try:
                    angle = Decimal(raw_angle)
                except InvalidOperation as exc:
                    raise ValueError(
                        f"Component orientation must be numeric for {record_key}.{field}"
                    ) from exc
                if not angle.is_finite() or angle % 90:
                    raise ValueError(
                        f"Unsupported component orientation for {record_key}.{field}"
                    )
                if angle % 360:
                    nonzero_angles.append(angle)
            if len(nonzero_angles) > 1:
                raise ValueError(f"Unsupported combined orientation for {record_key}")
            if raw_orientation is not None:
                geometry["orientation"] = orientation

            raw_features = raw_record.get("features", [])
            if not isinstance(raw_features, list):
                raise ValueError(f"Component features must be an array for {record_key}")
            if "features" in raw_record:
                geometry["features"] = list(
                    dict.fromkeys(
                        feature
                        for item in raw_features
                        if isinstance(item, str)
                        and (feature := _optional_text(item)) is not None
                    )
                )

            unit = _optional_text(raw_record.get("unit")) or parent_unit
            if unit is not None:
                unit = unit.casefold()
            if any(geometry.get(field) for field in fields) or any(position.values()):
                if unit not in COMPONENT_GEOMETRY_UNITS:
                    raise ValueError(f"Unsupported component geometry unit for {record_key}")
            if unit is not None:
                if unit not in COMPONENT_GEOMETRY_UNITS or (
                    is_child and parent_unit is not None and unit != parent_unit.casefold()
                ):
                    raise ValueError(f"Component subgeometry unit must match parent for {key}")
                geometry["unit"] = unit
            normalized_records[record_key] = geometry

        geometry = normalized_records[key]
        if "subgeometry" in raw_geometry:
            geometry["subgeometry"] = [
                normalized_records[f"{key}.{child_key}"] for child_key in seen_children
            ]
        if any(
            value is not None
            for field, value in geometry.items()
            if field not in {"source", "features", "orientation", "subgeometry"}
        ) or any(field in geometry for field in ("features", "orientation", "subgeometry")):
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
        candidate["source"] = "ai"
        candidate["status"] = (
            "missing" if _optional_text(candidate.get("value")) is None else "suggested"
        )
        parameter = normalize_parameter(candidate, "ai")
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
    modern_images=(),
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
3. Generate or refine AI-sourced component geometry fields.
4. Add only missing connections between supplied stable component keys.

Return exactly one JSON object with these existing contract keys:
universal, project_specific, component_geometry, connections.
Universal and project_specific items use key, label, value, unit, status, source,
rationale. Component geometry fields are source, primitive, length, width, height,
wall_thickness, unit, position, orientation, features, and optional subgeometry.
Each subgeometry item uses key, role, an existing supported primitive, optional
length, width, height, diameter, wall_thickness, unit, parent-relative position,
and orientation. Position uses optional
x, y, z values for the component's minimum corner, measured from the overall
envelope origin (0, 0, 0). Orientation uses optional roll, pitch, yaw angles in
degrees. Features is an array of concise structural-form strings.
Connection fields are component_a, component_b, connection_type, fastener_type,
quantity, note.

Rules:
- Write labels and rationale in {ai_language_name(language)}.
- Never replace user-sourced, concept-sourced, or otherwise protected non-AI Core
  values. Existing AI-sourced Core assumptions may be regenerated or refined when
  new engineering or visual evidence requires it.
- Never replace user-sourced component geometry.
  AI-sourced component geometry may be regenerated or refined.
- For each supplied component, infer a primitive and only support these values:
  box, beam, plate, tube, cylinder, shaft, frame, panel, shell, truss, custom.
  Use features for approximate structural form/topology, and connections for
  component relationships. Use box when no more specific form is supported.
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
  Modern reference images may inform only visible component identity, structural
  form, topology, relative placement, visible subcomponents/features, and
  approximate orientation. Never derive or claim verified engineering dimensions
  from image pixels or visual scale. Numeric dimensions must come from existing
  user values, Core or Project-Specific Parameters, or explicit preliminary AI
  engineering assumptions when data is missing.
- Overall Dimensions / Envelope, when proposed, must be labelled axes in the form
  "length=<number>; width=<number>; height=<number>" with one of mm, cm, or m.
- Component geometry may reference only the supplied stable component keys. Use the
  existing component unit when a partial geometry record already has one.
- Position and dimensions for a component must use the same unit. When the overall
  envelope axes and required component fields are known, require x + length <=
  envelope length, y + width <= envelope width, and z + height <= envelope height.
  If a component intentionally extends outside the stated envelope, do not silently
  move or resize it to fit; leave the contradictory geometry assumption unresolved.
- Dimensions and wall_thickness must be positive numbers. Position coordinates may
  be zero or positive. Orientation angles may be positive, zero, or negative.
- Use structured subgeometry only for justified visible or conceptual structural
  features, never decorative complexity. Subgeometry positions are relative to the
  parent component's minimum corner and use the same unit as the parent. For
  renderable orthographic geometry, use axis-aligned orientations in 90-degree
  increments; do not imply a full CAD transform.
- Connections may reference only two different supplied component keys. Quantity is
  a positive integer or null.
- Do not invent unsupported precision, certification, compliance, safety validation,
  performance, geometry, or connections. Use null when a reasonable preliminary
  value cannot be supported by the structured project context.
- Do not return extra top-level keys.
"""
    user_content = json.dumps(context, ensure_ascii=False)
    if modern_images:
        user_content = [
            {"type": "text", "text": user_content},
            *(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/png;base64,"
                        + base64.b64encode(image_bytes).decode("ascii"),
                        "detail": "low",
                    },
                }
                for _image_type, image_bytes in modern_images
            ),
        ]
    response = get_text_client().chat.completions.create(
        model=ENGINEERING_PARAMETERS_MODEL,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Empty response from OpenAI")
    payload = json.loads(content)
    if not isinstance(payload, dict):
        raise ValueError("AI Engineer response must be a JSON object")
    component_geometry = payload.get("component_geometry", {})
    if isinstance(component_geometry, dict):
        component_geometry = {
            key: (
                {**geometry, "source": "ai"}
                if isinstance(geometry, dict)
                else geometry
            )
            for key, geometry in component_geometry.items()
        }
    normalized = validate_parameter_set(
        {
            "universal": _ai_parameters(payload.get("universal", []), True),
            "project_specific": _ai_parameters(
                payload.get("project_specific", [])
            ),
            "component_geometry": component_geometry,
            "connections": payload.get("connections", []),
        }
    )
    return normalized


def merge_ai_engineering_data(parameter_set, suggestions, valid_component_keys):
    """Merge suggestions while protecting user and legacy component geometry."""
    current = validate_parameter_set(parameter_set)
    incoming = validate_parameter_set(suggestions)
    incoming_universal = {item["key"]: item for item in incoming["universal"]}
    for parameter in current["universal"]:
        suggestion = incoming_universal.get(parameter["key"])
        if (
            (parameter["value"] is not None and parameter["source"] != "ai")
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
        if existing is not None and existing.get("source") != "ai":
            continue
        merged_geometry = {**suggestion, "source": "ai"}
        if any(
            value
            for field, value in merged_geometry.items()
            if field not in {"source", "unit"}
        ):
            current["component_geometry"][component_key] = merged_geometry
        else:
            current["component_geometry"].pop(component_key, None)

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
