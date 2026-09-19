from threading import Lock

from application.concepts import load_concept
from database import (
    get_engineering_parameter_set,
    get_engineering_parameter_set_source_language,
    get_engineering_parameter_translation,
    save_engineering_parameter_set,
    save_engineering_parameter_translation,
)
from i18n import normalize_language
from services import concept_translation_service
from services.engineering_parameters_service import (
    build_empty_parameter_set,
    normalize_parameter_key,
    validate_parameter_set,
)
from services.general_arrangement_service import (
    SUPPORTED_LENGTH_UNITS,
    build_general_arrangement,
    normalize_known_value,
    normalize_length_value,
)


_TRANSLATION_LOCK = Lock()


def load_engineering_parameters_for_viewer(concept_id, viewer_language):
    """Return canonical or cached viewer-language engineering parameters."""
    original = validate_parameter_set(
        get_engineering_parameter_set(concept_id) or build_empty_parameter_set()
    )
    source_language = get_engineering_parameter_set_source_language(concept_id)
    target_language = normalize_language(viewer_language)
    if (
        source_language is None
        or target_language == source_language
        or not original["project_specific"]
    ):
        return original

    cached = get_engineering_parameter_translation(concept_id, target_language)
    if cached is not None:
        return validate_parameter_set(cached)

    with _TRANSLATION_LOCK:
        cached = get_engineering_parameter_translation(concept_id, target_language)
        if cached is not None:
            return validate_parameter_set(cached)
        translated = concept_translation_service.translate_engineering_parameter_set(
            original,
            source_language,
            target_language,
        )
        save_engineering_parameter_translation(
            concept_id,
            target_language,
            translated,
        )
        return translated


def save_engineering_parameter_values(
    concept_id,
    displayed_parameter_set,
    group_name,
    rendered_values,
):
    """Save edits without persisting translated labels, rationales, or units."""
    canonical = validate_parameter_set(
        get_engineering_parameter_set(concept_id) or build_empty_parameter_set()
    )
    displayed = validate_parameter_set(displayed_parameter_set)
    displayed_by_key = {
        parameter["key"]: parameter for parameter in displayed[group_name]
    }
    for parameter in canonical[group_name]:
        value, unit = rendered_values[parameter["key"]]
        parameter["value"] = value
        if unit != displayed_by_key[parameter["key"]]["unit"]:
            parameter["unit"] = unit
        parameter["status"] = "confirmed" if value else "missing"
    save_engineering_parameter_set(concept_id, canonical)


def save_overall_envelope_values(concept_id, length, width, height, unit):
    """Store explicit envelope axes in the existing core parameter record."""
    normalized_unit = str(unit or "").strip().casefold()
    if normalized_unit not in SUPPORTED_LENGTH_UNITS:
        raise ValueError("Unsupported overall envelope unit")

    values = {}
    source_key = "universal.overall_dimensions_envelope"
    for axis, raw_value in (
        ("length", length),
        ("width", width),
        ("height", height),
    ):
        value_text = str(raw_value or "").strip()
        if not value_text:
            continue
        if normalize_length_value(
            value_text,
            normalized_unit,
            source_type="engineering_parameter",
            source_key=source_key,
        ) is None:
            raise ValueError("Overall envelope values must be positive numbers")
        values[axis] = value_text

    canonical = validate_parameter_set(
        get_engineering_parameter_set(concept_id) or build_empty_parameter_set()
    )
    parameter = next(
        item
        for item in canonical["universal"]
        if item["key"] == "overall_dimensions_envelope"
    )
    parameter["value"] = "; ".join(
        f"{axis}={values[axis]}"
        for axis in ("length", "width", "height")
        if axis in values
    ) or None
    parameter["unit"] = normalized_unit if values else None
    parameter["status"] = "confirmed" if values else "missing"
    parameter["source"] = "user"
    save_engineering_parameter_set(concept_id, canonical)
    return canonical


def save_component_geometry_values(
    concept_id,
    component_key,
    length,
    width,
    height,
    x,
    y,
    z,
    unit,
):
    """Store one component's explicit geometry without replacing its siblings."""
    key = normalize_parameter_key(component_key)
    normalized_unit = str(unit or "").strip().casefold()
    if normalized_unit not in SUPPORTED_LENGTH_UNITS:
        raise ValueError("Unsupported component geometry unit")

    values = {}
    source_prefix = f"component_geometry.{key}"
    for field, raw_value in (
        ("length", length),
        ("width", width),
        ("height", height),
        ("x", x),
        ("y", y),
        ("z", z),
    ):
        value_text = "" if raw_value is None else str(raw_value).strip()
        if not value_text:
            values[field] = None
            continue
        normalized = normalize_known_value(
            value_text,
            normalized_unit,
            source_type="engineering_parameter",
            source_key=f"{source_prefix}.{field}",
        )
        minimum_is_valid = (
            normalized is not None
            and normalized.quantity == "length"
            and (
                normalized.value > 0
                if field in {"length", "width", "height"}
                else normalized.value >= 0
            )
        )
        if not minimum_is_valid:
            raise ValueError("Invalid component geometry value")
        values[field] = value_text

    canonical = validate_parameter_set(
        get_engineering_parameter_set(concept_id) or build_empty_parameter_set()
    )
    if any(values.values()):
        canonical["component_geometry"][key] = {
            **values,
            "unit": normalized_unit,
        }
    else:
        canonical["component_geometry"].pop(key, None)
    save_engineering_parameter_set(concept_id, canonical)
    return canonical


def save_connection_values(
    concept_id,
    component_a,
    component_b,
    connection_type,
    fastener_type=None,
    quantity=None,
    note=None,
):
    """Append one explicit connection between components of the current concept."""
    canonical = validate_parameter_set(
        get_engineering_parameter_set(concept_id) or build_empty_parameter_set()
    )
    concept_data = load_concept(concept_id)
    if concept_data is None:
        raise ValueError("Concept is required")
    valid_keys = {
        component.key
        for component in build_general_arrangement(
            concept_data,
            canonical,
        ).components
    }
    key_a = normalize_parameter_key(component_a)
    key_b = normalize_parameter_key(component_b)
    if key_a not in valid_keys or key_b not in valid_keys:
        raise ValueError("Connection components must belong to the current concept")
    if key_a == key_b:
        raise ValueError("A component cannot connect to itself")

    canonical["connections"].append(
        {
            "component_a": key_a,
            "component_b": key_b,
            "connection_type": connection_type,
            "fastener_type": fastener_type,
            "quantity": quantity,
            "note": note,
        }
    )
    canonical = validate_parameter_set(canonical)
    save_engineering_parameter_set(concept_id, canonical)
    return canonical
