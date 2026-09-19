import re
from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ProvenanceType = Literal["engineering_parameter", "concept_data"]
QuantityType = Literal["length", "mass"]
NormalizedUnit = Literal["mm", "kg"]
ViewType = Literal["top", "front", "side"]

_NUMBER_PATTERN = re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$")
_ENVELOPE_PART_PATTERN = re.compile(
    r"^(length|width|height)\s*=\s*(-?(?:0|[1-9]\d*)(?:\.\d+)?)$",
    re.IGNORECASE,
)
_UNIT_DEFINITIONS = {
    "mm": ("length", Decimal("1"), "mm"),
    "cm": ("length", Decimal("10"), "mm"),
    "m": ("length", Decimal("1000"), "mm"),
    "g": ("mass", Decimal("0.001"), "kg"),
    "kg": ("mass", Decimal("1"), "kg"),
}
SUPPORTED_LENGTH_UNITS = ("mm", "cm", "m")


class _StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


class ValueProvenance(_StrictModel):
    source_type: ProvenanceType
    source_key: str = Field(min_length=1)


class NormalizedValue(_StrictModel):
    value: Decimal
    unit: NormalizedUnit
    quantity: QuantityType
    raw_value: str = Field(min_length=1)
    raw_unit: str = Field(min_length=1)
    provenance: ValueProvenance


class Dimensions(_StrictModel):
    length: NormalizedValue | None = None
    width: NormalizedValue | None = None
    height: NormalizedValue | None = None


class Position(_StrictModel):
    x: NormalizedValue | None = None
    y: NormalizedValue | None = None
    z: NormalizedValue | None = None


class GeneralArrangementComponent(_StrictModel):
    key: str = Field(min_length=1)
    name: str = Field(min_length=1)
    dimensions: Dimensions = Field(default_factory=Dimensions)
    position: Position | None = None


class GeneralArrangementUnits(_StrictModel):
    length: Literal["mm"] = "mm"
    mass: Literal["kg"] = "kg"


class RawSourceValue(_StrictModel):
    raw_value: str = Field(min_length=1)
    raw_unit: str | None = None
    provenance: ValueProvenance


class GeneralArrangement(_StrictModel):
    units: GeneralArrangementUnits = Field(default_factory=GeneralArrangementUnits)
    overall_envelope: Dimensions = Field(default_factory=Dimensions)
    components: tuple[GeneralArrangementComponent, ...] = ()
    raw_inputs: tuple[RawSourceValue, ...] = ()


class EnvelopeView(_StrictModel):
    key: ViewType
    horizontal_axis: Literal["length", "width"]
    vertical_axis: Literal["width", "height"]
    horizontal: NormalizedValue | None = None
    vertical: NormalizedValue | None = None


class DisplayRectangle(_StrictModel):
    width: Decimal
    height: Decimal
    scale: Decimal


def normalize_known_value(
    raw_value,
    raw_unit,
    *,
    source_type: ProvenanceType,
    source_key: str,
):
    """Normalize only an unambiguous scalar with an explicitly supported unit."""
    if isinstance(raw_value, bool) or raw_value is None or raw_unit is None:
        return None

    value_text = str(raw_value).strip()
    unit_text = str(raw_unit).strip().casefold()
    if not value_text or not _NUMBER_PATTERN.fullmatch(value_text):
        return None

    unit_definition = _UNIT_DEFINITIONS.get(unit_text)
    if unit_definition is None:
        return None

    quantity, factor, normalized_unit = unit_definition
    try:
        normalized_value = Decimal(value_text) * factor
    except InvalidOperation:
        return None

    return NormalizedValue(
        value=normalized_value,
        unit=normalized_unit,
        quantity=quantity,
        raw_value=value_text,
        raw_unit=str(raw_unit).strip(),
        provenance=ValueProvenance(
            source_type=source_type,
            source_key=source_key,
        ),
    )


def _normalize_length(raw_value, raw_unit, source_type, source_key):
    value = normalize_known_value(
        raw_value,
        raw_unit,
        source_type=source_type,
        source_key=source_key,
    )
    if value is None or value.quantity != "length" or value.value <= 0:
        return None
    return value


def normalize_length_value(
    raw_value,
    raw_unit,
    *,
    source_type: ProvenanceType,
    source_key: str,
):
    return _normalize_length(raw_value, raw_unit, source_type, source_key)


def _parse_labelled_envelope(raw_value, raw_unit, source_key):
    """Accept only explicitly labelled axes with one shared unit."""
    parts = [part.strip() for part in str(raw_value).split(";")]
    if not 1 <= len(parts) <= 3:
        return None

    values = {}
    for part in parts:
        match = _ENVELOPE_PART_PATTERN.fullmatch(part)
        if match is None:
            return None
        axis, axis_value = match.groups()
        axis = axis.casefold()
        if axis in values:
            return None
        normalized = _normalize_length(
            axis_value,
            raw_unit,
            "engineering_parameter",
            source_key,
        )
        if normalized is None:
            return None
        values[axis] = normalized

    return Dimensions(**values)


def _component_key(value, index, used_keys):
    candidate = re.sub(r"[^a-z0-9]+", "_", str(value or "").casefold()).strip("_")
    base = candidate or f"component_{index}"
    candidate = base
    suffix = 2
    while candidate in used_keys:
        candidate = f"{base}_{suffix}"
        suffix += 1
    used_keys.add(candidate)
    return candidate


def _structured_measurement(value, axis, component_key, group_name):
    if not isinstance(value, dict) or set(value) != {"value", "unit"}:
        return None
    normalized = normalize_known_value(
        value["value"],
        value["unit"],
        source_type="concept_data",
        source_key=f"system_components.{component_key}.{group_name}.{axis}",
    )
    if normalized is None or normalized.quantity != "length":
        return None
    if group_name == "dimensions" and normalized.value <= 0:
        return None
    return normalized


def _structured_dimensions(value, component_key):
    if not isinstance(value, dict):
        return Dimensions()
    return Dimensions(
        **{
            axis: _structured_measurement(
                value.get(axis),
                axis,
                component_key,
                "dimensions",
            )
            for axis in ("length", "width", "height")
        }
    )


def _structured_position(value, component_key):
    if not isinstance(value, dict):
        return None
    coordinates = {
        axis: _structured_measurement(
            value.get(axis),
            axis,
            component_key,
            "position",
        )
        for axis in ("x", "y", "z")
    }
    if not any(coordinates.values()):
        return None
    return Position(**coordinates)


def _build_components(concept_data):
    raw_components = concept_data.get("system_components", [])
    if not isinstance(raw_components, list):
        return ()

    components = []
    used_keys = set()
    for index, item in enumerate(raw_components, start=1):
        if isinstance(item, str):
            name = " ".join(item.split())
            if not name:
                continue
            key = _component_key(name, index, used_keys)
            components.append(GeneralArrangementComponent(key=key, name=name))
            continue

        if not isinstance(item, dict):
            continue
        name = " ".join(str(item.get("name") or "").split())
        if not name:
            continue
        key = _component_key(item.get("key") or name, index, used_keys)
        components.append(
            GeneralArrangementComponent(
                key=key,
                name=name,
                dimensions=_structured_dimensions(item.get("dimensions"), key),
                position=_structured_position(item.get("position"), key),
            )
        )
    return tuple(components)


def build_general_arrangement(concept_data, parameter_set):
    """Build deterministic GA source data without inferring missing geometry."""
    if not isinstance(concept_data, dict):
        raise ValueError("Concept data must be a JSON object")
    if not isinstance(parameter_set, dict):
        raise ValueError("Engineering parameter set must be a JSON object")

    envelope = Dimensions()
    raw_inputs = []
    for group_name in ("universal", "project_specific"):
        parameters = parameter_set.get(group_name, [])
        if not isinstance(parameters, list):
            raise ValueError("Engineering parameter groups must be arrays")
        for parameter in parameters:
            if not isinstance(parameter, dict):
                continue
            raw_value = parameter.get("value")
            value_text = " ".join(str(raw_value or "").split())
            if not value_text:
                continue

            key = str(parameter.get("key") or "").strip()
            source_key = f"{group_name}.{key}"
            parsed_envelope = None
            if (
                group_name == "universal"
                and key == "overall_dimensions_envelope"
                and parameter.get("source") != "ai"
            ):
                parsed_envelope = _parse_labelled_envelope(
                    value_text,
                    parameter.get("unit"),
                    source_key,
                )
            if parsed_envelope is not None:
                envelope = parsed_envelope
                continue

            raw_unit = parameter.get("unit")
            raw_inputs.append(
                RawSourceValue(
                    raw_value=value_text,
                    raw_unit=str(raw_unit).strip() if raw_unit else None,
                    provenance=ValueProvenance(
                        source_type="engineering_parameter",
                        source_key=source_key,
                    ),
                )
            )

    return GeneralArrangement(
        overall_envelope=envelope,
        components=_build_components(concept_data),
        raw_inputs=tuple(raw_inputs),
    )


def build_envelope_views(arrangement):
    envelope = arrangement.overall_envelope
    return (
        EnvelopeView(
            key="top",
            horizontal_axis="length",
            vertical_axis="width",
            horizontal=envelope.length,
            vertical=envelope.width,
        ),
        EnvelopeView(
            key="front",
            horizontal_axis="width",
            vertical_axis="height",
            horizontal=envelope.width,
            vertical=envelope.height,
        ),
        EnvelopeView(
            key="side",
            horizontal_axis="length",
            vertical_axis="height",
            horizontal=envelope.length,
            vertical=envelope.height,
        ),
    )


def calculate_display_rectangle(view, max_width=220, max_height=130):
    """Scale known real dimensions into a fixed display area without mutation."""
    if view.horizontal is None or view.vertical is None:
        return None
    width_limit = Decimal(str(max_width))
    height_limit = Decimal(str(max_height))
    scale = min(
        width_limit / view.horizontal.value,
        height_limit / view.vertical.value,
    )
    return DisplayRectangle(
        width=view.horizontal.value * scale,
        height=view.vertical.value * scale,
        scale=scale,
    )


def has_prepared_geometry(arrangement):
    envelope = arrangement.overall_envelope
    if not all((envelope.length, envelope.width, envelope.height)):
        return False
    if not arrangement.components:
        return False
    return all(
        all(
            (
                component.dimensions.length,
                component.dimensions.width,
                component.dimensions.height,
                component.position,
                component.position and component.position.x,
                component.position and component.position.y,
                component.position and component.position.z,
            )
        )
        for component in arrangement.components
    )
