import base64
import json
import re
from decimal import Decimal, InvalidOperation
from typing import get_args

from i18n import ai_language_name
from services.general_arrangement_service import PrimitiveType
from services.openai_client import get_text_client


ENGINEERING_PARAMETERS_MODEL = "gpt-5.6-sol"
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
        "project_specific": _deduplicate_parameters(project_specific, "user"),
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
    """Make one shared-client call for current engineering data."""
    current = validate_parameter_set(parameter_set)
    component_context = [
        {"key": component.key, "name": component.name} for component in components
    ]
    context = {
        "category": category,
        "original_prompt": original_prompt,
        "concept_data": concept_data,
        "engineering_parameters": {
            **current,
            "component_geometry": {
                key: geometry
                for key, geometry in current["component_geometry"].items()
                if geometry.get("source") != "ai"
            },
        },
        "components": component_context,
    }
    required_geometry_keys = {
        component["key"] for component in component_context
    } - set(context["engineering_parameters"]["component_geometry"])
    response_schema = {
        "type": "object",
        "properties": {
            "universal": {"type": "array", "items": {"$ref": "#/$defs/parameter"}},
            "project_specific": {"type": "array", "items": {"$ref": "#/$defs/parameter"}},
            "component_geometry": {
                "type": "object",
                "properties": {
                    key: {"$ref": "#/$defs/geometry"}
                    for key in sorted(required_geometry_keys)
                },
                "required": sorted(required_geometry_keys),
                "additionalProperties": False,
            },
            "connections": {"type": "array", "items": {"$ref": "#/$defs/connection"}},
        },
        "required": ["universal", "project_specific", "component_geometry", "connections"],
        "additionalProperties": False,
        "$defs": {
            "parameter": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "label": {"type": "string"},
                    "value": {"type": ["string", "null"]},
                    "unit": {"type": ["string", "null"]},
                    "status": {"type": "string", "enum": ["missing", "suggested"]},
                    "source": {"type": "string", "enum": ["ai"]},
                    "rationale": {"type": ["string", "null"]},
                },
                "required": ["key", "label", "value", "unit", "status", "source", "rationale"],
                "additionalProperties": False,
            },
            "position": {
                "type": "object",
                "properties": {axis: {"type": "number"} for axis in ("x", "y", "z")},
                "required": ["x", "y", "z"],
                "additionalProperties": False,
            },
            "orientation": {
                "type": "object",
                "properties": {
                    axis: {"type": "number"} for axis in ("roll", "pitch", "yaw")
                },
                "required": ["roll", "pitch", "yaw"],
                "additionalProperties": False,
            },
            "geometry": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "enum": ["ai"]},
                    "primitive": {"type": "string", "enum": list(get_args(PrimitiveType))},
                    "length": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "wall_thickness": {"type": ["number", "null"]},
                    "unit": {"type": "string", "enum": sorted(COMPONENT_GEOMETRY_UNITS)},
                    "position": {"$ref": "#/$defs/position"},
                    "orientation": {"$ref": "#/$defs/orientation"},
                    "features": {"type": "array", "items": {"type": "string"}},
                    "subgeometry": {
                        "type": "array", "items": {"$ref": "#/$defs/subgeometry"}
                    },
                },
                "required": [
                    "source", "primitive", "length", "width", "height",
                    "wall_thickness", "unit", "position", "orientation",
                    "features", "subgeometry",
                ],
                "additionalProperties": False,
            },
            "subgeometry": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "role": {"type": ["string", "null"]},
                    "primitive": {"type": "string", "enum": list(get_args(PrimitiveType))},
                    "length": {"type": ["number", "null"]},
                    "width": {"type": ["number", "null"]},
                    "height": {"type": ["number", "null"]},
                    "diameter": {"type": ["number", "null"]},
                    "wall_thickness": {"type": ["number", "null"]},
                    "unit": {"type": "string", "enum": sorted(COMPONENT_GEOMETRY_UNITS)},
                    "position": {"$ref": "#/$defs/position"},
                    "orientation": {"$ref": "#/$defs/orientation"},
                    "features": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "key", "role", "primitive", "length", "width", "height",
                    "diameter", "wall_thickness", "unit", "position",
                    "orientation", "features",
                ],
                "additionalProperties": False,
            },
            "connection": {
                "type": "object",
                "properties": {
                    "component_a": {"type": "string"},
                    "component_b": {"type": "string"},
                    "connection_type": {"type": "string"},
                    "fastener_type": {"type": ["string", "null"]},
                    "quantity": {"type": ["integer", "null"]},
                    "note": {"type": ["string", "null"]},
                },
                "required": [
                    "component_a", "component_b", "connection_type",
                    "fastener_type", "quantity", "note",
                ],
                "additionalProperties": False,
            },
        },
    }
    system_prompt = f"""
You are the AI Engineer for a physical-product concept. Work in this exact order:
1. Fill missing Universal Core values and refine existing AI-sourced Core
   assumptions when the current engineering model requires it.
2. Generate project-specific engineering characteristics using the Core context.
3. Generate complete replacement records for AI-sourced component geometry.
4. Add only missing connections between supplied stable component keys.

Return exactly one JSON object with these existing contract keys:
universal, project_specific, component_geometry, connections.
Universal and project_specific items use key, label, value, unit, status, source,
rationale. Component geometry fields are source, primitive, length, width, height,
wall_thickness, unit, position, orientation, features, and optional subgeometry.
Each subgeometry item uses key, role, an existing supported primitive, optional
length, width, height, diameter, wall_thickness, unit, parent-relative position,
and orientation. World axes are X = longitudinal / overall length,
Y = transverse / overall width, and Z = vertical / overall height.
Parent position.x/y/z is the component's minimum corner relative to the overall
assembly/envelope origin (0, 0, 0); subgeometry position.x/y/z is relative to its parent
minimum corner, using the same world-axis directions. Orientation uses optional
roll, pitch, yaw angles in degrees. Features is descriptive engineering metadata,
not renderable geometry.
Connection fields are component_a, component_b, connection_type, fastener_type,
quantity, note.

Rules:
- Write labels and rationale in {ai_language_name(language)}.
- Never replace existing user-sourced, concept-sourced, or legacy Core values.
  Fill missing Core values. Existing AI-sourced Core assumptions may be revised,
  recalculated, or explicitly cleared with null when no longer supported by the
  current engineering model; do not preserve obsolete AI assumptions indefinitely.
- Never replace user-sourced or legacy component geometry. A returned geometry
  record for an AI-owned component is its complete current record, not a partial
  patch: omit obsolete fields and subgeometry instead of carrying them forward.
  Previous AI component geometry is omitted from the request because it is a stale
  assumption, not evidence. Do not copy previous AI geometry by default. Re-derive
  AI-owned geometry from canonical ConceptData, protected engineering constraints,
  project function, modern visual references, and engineering reasoning.
- COMPONENT_GEOMETRY IS REQUIRED OUTPUT. Always return a component_geometry object.
  Required AI geometry keys for this request: {json.dumps(sorted(required_geometry_keys))}.
  Return exactly one complete source="ai" component_geometry record for every
  required key, and no replacement records for protected geometry. Do not omit
  required components or return an empty object when required keys are present.
  Each required record must include a supported primitive, physical dimensions and
  unit, position, orientation, features, and subgeometry when structurally needed.
- For each supplied component, infer a primitive and only support these values:
  box, beam, plate, tube, cylinder, shaft, frame, panel, shell, truss, custom.
  Use box when no more specific form is supported. Features describe engineering
  properties but are not drawn. Any physical part needed to show recognizable
  structural form must be represented by the parent primitive or by supported
  subgeometry, not merely named in features. Add meaningful visible or structural
  parts when one primitive cannot convey the component's topology. If the visible
  product topology contains multiple significant structural parts needed to recognize
  a component, return those parts as subgeometry rather than only features text;
  avoid decorative or microscopic detail.
- Rebuild project_specific for the current context on every run. Recalculate records
  whose current source is "ai"; do not replace user, concept, or legacy records.
  Select actual project-specific engineering characteristics such as capacities,
  operating limits, deployment states, range, duration, speed, or throughput when
  relevant to this concept. Do not duplicate individual component dimensions from
  component_geometry as Project-Specific Parameters.
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
  approximate orientation. Images are references for topology, recognizable form,
  the number of visible major elements, spatial arrangement, and placement only.
  For these visual properties they outweigh previous AI geometry assumptions, but
  they are not verified dimensional sources. Never derive or claim verified engineering dimensions
  from image pixels or visual scale. Numeric dimensions must come from existing
  user values, Core or Project-Specific Parameters, or explicit preliminary AI
  engineering assumptions when data is missing.
- Overall Dimensions / Envelope, when proposed, must be labelled axes in the form
  "length=<number>; width=<number>; height=<number>" with one of mm, cm, or m.
- Component geometry may reference only the supplied stable component keys.
  Keep protected geometry unchanged; choose a consistent unit in each complete
  replacement record for AI-owned geometry.
- Infer each component's physical main axis and orient its geometry accordingly in
  the existing world axes. A vertical column or mast must extend mainly along Z
  after orientation; a longitudinal member along X and a transverse member along Y.
  Prefer world-aligned dimensions, such as height for a vertical part, when they
  express the physical form directly. Use supported orientation only when needed;
  do not rely on a renderer transform to repair semantically incorrect dimensions.
- Before returning each component's final record, internally check its dominant
  physical axis, visible parts requiring subgeometry, physical placement, consistency
  with protected overall constraints, and whether it was independently derived
  rather than copied from a previous AI assumption. Return only the corrected
  structured result, not the reasoning.
- Position and dimensions for a component must use the same unit. Check overall
  envelope against component dimensions, positions, orientation, and subgeometry
  extents. For world-aligned components with known fields, require x + length <=
  envelope length, y + width <= envelope width, and z + height <= envelope height.
  If an AI-sourced envelope conflicts with the physical design, revise that AI
  assumption rather than silently shrinking, clamping, moving, or resizing parts.
  Preserve protected envelope values. An intentional deployed/extended geometry
  may exceed a stowed/transport envelope only when existing engineering parameters
  clearly distinguish those states; do not leave an accidental contradiction.
- Dimensions and wall_thickness must be positive numbers. Position coordinates may
  be zero or positive. Orientation angles may be positive, zero, or negative.
- Use structured subgeometry for visually or structurally important parts when one
  primitive is insufficient for recognizable engineering topology, never decorative
  complexity. Subgeometry positions are relative to the parent minimum corner and
  use the same unit and world-axis directions as the parent. For
  renderable orthographic geometry, use axis-aligned orientations in 90-degree
  increments; do not imply a full CAD transform.
- Connections may reference only two different supplied component keys. Quantity is
  a positive integer or null.
- Do not invent unsupported precision, certification, compliance, safety validation,
  performance, geometry, or connections. Use null when a reasonable preliminary
  value cannot be supported by the structured project context.
- Do not return extra top-level keys.

Before returning the structured result, check: X is longitudinal, Y transverse,
Z vertical; each installed component's dominant final extent follows its physical
axis (a vertical mast uses height/Z unless orientation actually rotates it to Z);
visible structural parts needed for recognition are subgeometry, not features text;
reference images guide topology, orientation, arrangement, and visible structure,
never verified dimensions; every required key has one complete replacement record.
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
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "engineering_parameter_set",
                "strict": True,
                "schema": response_schema,
            },
        },
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
    component_geometry = payload.get("component_geometry")
    if not isinstance(component_geometry, dict):
        raise ValueError("AI Engineer response requires component_geometry object")
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
    returned_geometry_keys = set(normalized["component_geometry"])
    if returned_geometry_keys != required_geometry_keys:
        raise ValueError(
            "AI Engineer response has incomplete component_geometry "
            f"(missing={sorted(required_geometry_keys - returned_geometry_keys)}, "
            f"unexpected={sorted(returned_geometry_keys - required_geometry_keys)})"
        )
    for key in required_geometry_keys:
        geometry = normalized["component_geometry"][key]
        if (
            geometry.get("source") != "ai"
            or not geometry.get("primitive")
            or any(geometry.get(field) is None for field in (
                "length", "width", "height", "unit",
            ))
            or any((geometry.get("position") or {}).get(axis) is None
                   for axis in ("x", "y", "z"))
            or any((geometry.get("orientation") or {}).get(axis) is None
                   for axis in ("roll", "pitch", "yaw"))
            or "features" not in geometry
        ):
            raise ValueError(
                f"AI Engineer response has incomplete component_geometry record for {key}"
            )
    return normalized


def merge_ai_engineering_data(parameter_set, suggestions, valid_component_keys):
    """Merge suggestions while protecting user and legacy component geometry."""
    current = validate_parameter_set(parameter_set)
    incoming = validate_parameter_set(suggestions)
    incoming_universal = {item["key"]: item for item in incoming["universal"]}
    for parameter in current["universal"]:
        suggestion = incoming_universal.get(parameter["key"])
        if not suggestion or (
            parameter["value"] is not None and parameter["source"] != "ai"
        ):
            continue
        if (
            parameter["source"] != "ai"
            and suggestion["value"] is not None
            and parameter["unit"]
            and suggestion["unit"]
            and parameter["unit"].casefold() != suggestion["unit"].casefold()
        ):
            continue
        if suggestion["value"] is None and parameter["source"] != "ai":
            continue
        parameter.update(
            {
                "value": suggestion["value"],
                "unit": (
                    suggestion["unit"]
                    if parameter["source"] == "ai"
                    else parameter["unit"] or suggestion["unit"]
                ),
                "status": "missing" if suggestion["value"] is None else "suggested",
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
