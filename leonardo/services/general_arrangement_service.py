import re
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


ProvenanceType = Literal["engineering_parameter", "concept_data"]
QuantityType = Literal["length", "mass"]
NormalizedUnit = Literal["mm", "kg"]
ViewType = Literal["top", "front", "side"]
PrimitiveType = Literal[
    "box",
    "beam",
    "plate",
    "tube",
    "cylinder",
    "shaft",
    "frame",
    "panel",
    "shell",
    "truss",
    "custom",
]

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


class Orientation(_StrictModel):
    roll: Decimal | None = None
    pitch: Decimal | None = None
    yaw: Decimal | None = None


class GeneralArrangementComponent(_StrictModel):
    key: str = Field(min_length=1)
    name: str = Field(min_length=1)
    primitive: PrimitiveType = "box"
    dimensions: Dimensions = Field(default_factory=Dimensions)
    wall_thickness: NormalizedValue | None = None
    position: Position | None = None
    orientation: Orientation | None = None
    features: tuple[str, ...] = ()
    subgeometry: tuple["GeneralArrangementComponent", ...] = ()


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
    horizontal_min: Decimal = Decimal("0")
    vertical_min: Decimal = Decimal("0")


class ComponentProjection(_StrictModel):
    component_key: str = Field(min_length=1)
    component_name: str = Field(min_length=1)
    primitive: PrimitiveType = "box"
    horizontal_size: NormalizedValue
    vertical_size: NormalizedValue
    horizontal_position: NormalizedValue
    vertical_position: NormalizedValue
    view_axes: tuple[Literal["length", "width", "height"], ...]
    longitudinal_axis: Literal["length", "height"] = "length"
    wall_thickness: NormalizedValue | None = None
    out_of_envelope: bool


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
    if group_name == "position" and normalized.value < 0:
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


def _stored_measurement(value, unit, field, component_key):
    normalized = normalize_known_value(
        value,
        unit,
        source_type="engineering_parameter",
        source_key=f"component_geometry.{component_key}.{field}",
    )
    if normalized is None or normalized.quantity != "length":
        return None
    if field in {"length", "width", "height", "wall_thickness"} and normalized.value <= 0:
        return None
    if field in {"x", "y", "z"} and normalized.value < 0:
        return None
    return normalized


def _stored_geometry(component_geometry, component_key):
    geometry = component_geometry.get(component_key)
    if not isinstance(geometry, dict):
        return None
    unit = geometry.get("unit")
    dimensions = Dimensions(
        **{
            field: _stored_measurement(
                geometry.get(field), unit, field, component_key
            )
            for field in ("length", "width", "height")
        }
    )
    wall_thickness = _stored_measurement(
        geometry.get("wall_thickness"), unit, "wall_thickness", component_key
    )
    raw_position = geometry.get("position")
    position_values = raw_position if isinstance(raw_position, dict) else geometry
    coordinates = {
        field: _stored_measurement(
            position_values.get(field), unit, field, component_key
        )
        for field in ("x", "y", "z")
    }
    position = Position(**coordinates) if any(coordinates.values()) else None
    raw_orientation = geometry.get("orientation")
    try:
        orientation = (
            Orientation.model_validate(raw_orientation, strict=False)
            if isinstance(raw_orientation, dict) and any(raw_orientation.values())
            else None
        )
    except ValidationError:
        orientation = None
    primitive = geometry.get("primitive") or "box"
    features = tuple(geometry.get("features") or ())
    subgeometry = []
    for raw_item in geometry.get("subgeometry") or ():
        if not isinstance(raw_item, dict) or not raw_item.get("key"):
            continue
        child_key = str(raw_item["key"]).strip()
        child_geometry = {**raw_item, "unit": raw_item.get("unit") or unit}
        diameter = child_geometry.get("diameter")
        child_geometry["width"] = child_geometry.get("width") or diameter
        child_geometry["height"] = child_geometry.get("height") or diameter
        stored = _stored_geometry({child_key: child_geometry}, child_key)
        if stored is None:
            continue
        (
            child_dimensions,
            child_position,
            child_primitive,
            child_wall_thickness,
            child_orientation,
            child_features,
            child_subgeometry,
        ) = stored
        if child_position is None or not any(
            (child_dimensions.length, child_dimensions.width, child_dimensions.height)
        ):
            continue
        subgeometry.append(
            GeneralArrangementComponent(
                key=f"{component_key}.{child_key}",
                name=raw_item.get("role") or child_key,
                primitive=child_primitive,
                dimensions=child_dimensions,
                wall_thickness=child_wall_thickness,
                position=child_position,
                orientation=child_orientation,
                features=child_features,
                subgeometry=child_subgeometry,
            )
        )
    return (
        dimensions,
        position,
        primitive,
        wall_thickness,
        orientation,
        features,
        tuple(subgeometry),
    )


def _merge_geometry(concept_dimensions, concept_position, stored):
    (
        stored_dimensions,
        stored_position,
        primitive,
        wall_thickness,
        orientation,
        features,
        subgeometry,
    ) = stored or (Dimensions(), None, "box", None, None, (), ())
    dimensions = Dimensions(
        **{
            field: getattr(stored_dimensions, field)
            or getattr(concept_dimensions, field)
            for field in ("length", "width", "height")
        }
    )
    coordinates = {
        field: (getattr(stored_position, field) if stored_position else None)
        or (getattr(concept_position, field) if concept_position else None)
        for field in ("x", "y", "z")
    }
    position = Position(**coordinates) if any(coordinates.values()) else None
    return (
        dimensions,
        position,
        primitive,
        wall_thickness,
        orientation,
        features,
        subgeometry,
    )


def _build_components(concept_data, component_geometry):
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
            stored = _stored_geometry(component_geometry, key)
            (
                dimensions,
                position,
                primitive,
                wall_thickness,
                orientation,
                features,
                subgeometry,
            ) = _merge_geometry(Dimensions(), None, stored)
            components.append(
                GeneralArrangementComponent(
                    key=key,
                    name=name,
                    primitive=primitive,
                    dimensions=dimensions,
                    wall_thickness=wall_thickness,
                    position=position,
                    orientation=orientation,
                    features=features,
                    subgeometry=subgeometry,
                )
            )
            continue

        if not isinstance(item, dict):
            continue
        name = " ".join(str(item.get("name") or "").split())
        if not name:
            continue
        key = _component_key(item.get("key") or name, index, used_keys)
        stored = _stored_geometry(component_geometry, key)
        (
            dimensions,
            position,
            primitive,
            wall_thickness,
            orientation,
            features,
            subgeometry,
        ) = _merge_geometry(
            _structured_dimensions(item.get("dimensions"), key),
            _structured_position(item.get("position"), key),
            stored,
        )
        components.append(
            GeneralArrangementComponent(
                key=key,
                name=name,
                primitive=primitive,
                dimensions=dimensions,
                wall_thickness=wall_thickness,
                position=position,
                orientation=orientation,
                features=features,
                subgeometry=subgeometry,
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
        components=_build_components(
            concept_data,
            parameter_set.get("component_geometry", {}),
        ),
        raw_inputs=tuple(raw_inputs),
    )


def build_dimension_views(dimensions):
    return (
        EnvelopeView(
            key="top",
            horizontal_axis="length",
            vertical_axis="width",
            horizontal=dimensions.length,
            vertical=dimensions.width,
        ),
        EnvelopeView(
            key="front",
            horizontal_axis="width",
            vertical_axis="height",
            horizontal=dimensions.width,
            vertical=dimensions.height,
        ),
        EnvelopeView(
            key="side",
            horizontal_axis="length",
            vertical_axis="height",
            horizontal=dimensions.length,
            vertical=dimensions.height,
        ),
    )


def build_envelope_views(arrangement):
    return build_dimension_views(arrangement.overall_envelope)


def calculate_display_rectangle(view, max_width=220, max_height=130, projections=()):
    """Scale the envelope and projected geometry into one display area."""
    if view.horizontal is None or view.vertical is None:
        return None
    projections = tuple(projections)
    width_limit = Decimal(str(max_width))
    height_limit = Decimal(str(max_height))
    horizontal_min = min((
        Decimal("0"),
        *(projection.horizontal_position.value for projection in projections),
    ))
    vertical_min = min((
        Decimal("0"),
        *(projection.vertical_position.value for projection in projections),
    ))
    horizontal_max = max((
        view.horizontal.value,
        *(
            projection.horizontal_position.value + projection.horizontal_size.value
            for projection in projections
        ),
    ))
    vertical_max = max((
        view.vertical.value,
        *(
            projection.vertical_position.value + projection.vertical_size.value
            for projection in projections
        ),
    ))
    horizontal_extent = horizontal_max - horizontal_min
    vertical_extent = vertical_max - vertical_min
    scale = min(
        width_limit / horizontal_extent,
        height_limit / vertical_extent,
    )
    return DisplayRectangle(
        width=horizontal_extent * scale,
        height=vertical_extent * scale,
        scale=scale,
        horizontal_min=horizontal_min,
        vertical_min=vertical_min,
    )


_IDENTITY_ROTATION = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
)
_QUARTER_TURN_ROTATIONS = {
    "roll": (
        (1, 0, 0),
        (0, 0, -1),
        (0, 1, 0),
    ),
    "pitch": (
        (0, 0, 1),
        (0, 1, 0),
        (-1, 0, 0),
    ),
    "yaw": (
        (0, -1, 0),
        (1, 0, 0),
        (0, 0, 1),
    ),
}


def _multiply_rotations(left, right):
    return tuple(
        tuple(
            sum(left[row][inner] * right[inner][column] for inner in range(3))
            for column in range(3)
        )
        for row in range(3)
    )


def _orientation_rotation(orientation):
    """Return an exact right-handed signed-axis rotation for stored quarter turns."""
    rotation = _IDENTITY_ROTATION
    if orientation is None:
        return rotation
    for field in ("roll", "pitch", "yaw"):
        angle = getattr(orientation, field) or Decimal("0")
        if angle % 90:
            return _IDENTITY_ROTATION
        for _ in range(int(angle / 90) % 4):
            rotation = _multiply_rotations(
                _QUARTER_TURN_ROTATIONS[field], rotation
            )
    return rotation


def _transform_vector(rotation, vector):
    transformed = []
    for row in rotation:
        value = Decimal("0")
        for coefficient, coordinate in zip(row, vector):
            if coefficient and coordinate is None:
                value = None
                break
            if coefficient:
                value += Decimal(coefficient) * coordinate
        transformed.append(value)
    return tuple(transformed)


def _add_vectors(left, right):
    return tuple(
        first + second if first is not None and second is not None else None
        for first, second in zip(left, right)
    )


def _subtract_vectors(left, right):
    return tuple(
        first - second if first is not None and second is not None else None
        for first, second in zip(left, right)
    )


def _rotated_bounds(values, rotation):
    """Return the AABB of transformed box corners, retaining partial axes."""
    minimums = []
    maximums = []
    for row in rotation:
        minimum = Decimal("0")
        maximum = Decimal("0")
        for coefficient, value in zip(row, values):
            if not coefficient:
                continue
            if value is None:
                minimum = maximum = None
                break
            endpoint = Decimal(coefficient) * value
            minimum += min(Decimal("0"), endpoint)
            maximum += max(Decimal("0"), endpoint)
        minimums.append(minimum)
        maximums.append(maximum)
    return tuple(minimums), tuple(maximums)


def _measurement_with_value(template, value):
    if template is None or value is None:
        return None
    return template.model_copy(update={"value": value})


def _component_dimension_values(component):
    return tuple(
        value.value if value is not None else None
        for value in (
            component.dimensions.length,
            component.dimensions.width,
            component.dimensions.height,
        )
    )


def _component_position_values(component):
    if component.position is None:
        return (None, None, None)
    return tuple(
        value.value if value is not None else None
        for value in (component.position.x, component.position.y, component.position.z)
    )


def _axis_measurement(component, rotation, output_axis, *, position=False):
    source = (
        (component.position.x, component.position.y, component.position.z)
        if position and component.position is not None
        else (
            component.dimensions.length,
            component.dimensions.width,
            component.dimensions.height,
        )
    )
    for coefficient, measurement in zip(rotation[output_axis], source):
        if coefficient and measurement is not None:
            return measurement
    return next((measurement for measurement in source if measurement is not None), None)


def oriented_component_dimensions(component):
    """Return local AABB dimensions after an exact stored quarter turn."""
    rotation = _orientation_rotation(component.orientation)
    minimums, maximums = _rotated_bounds(
        _component_dimension_values(component), rotation
    )
    sizes = tuple(
        maximum - minimum
        if minimum is not None and maximum is not None
        else None
        for minimum, maximum in zip(minimums, maximums)
    )
    return Dimensions(
        length=_measurement_with_value(
            _axis_measurement(component, rotation, 0), sizes[0]
        ),
        width=_measurement_with_value(
            _axis_measurement(component, rotation, 1), sizes[1]
        ),
        height=_measurement_with_value(
            _axis_measurement(component, rotation, 2), sizes[2]
        ),
    )


def build_component_projections(arrangement, view, zero_origin=False):
    """Compose local quarter-turn transforms and project their world AABBs."""
    axis_map = {
        "top": (0, 1),
        "front": (1, 2),
        "side": (0, 2),
    }
    horizontal_axis, vertical_axis = axis_map[view.key]
    normal_axis = 3 - horizontal_axis - vertical_axis
    projections = []
    components = getattr(arrangement, "components", arrangement)
    pending = [
        (component, _IDENTITY_ROTATION, (Decimal("0"),) * 3, zero_origin)
        for component in components
    ]
    while pending:
        component, parent_rotation, parent_offset, use_zero_origin = pending.pop(0)
        local_rotation = _orientation_rotation(component.orientation)
        local_minimums, _local_maximums = _rotated_bounds(
            _component_dimension_values(component), local_rotation
        )
        # Stored position remains the component's minimum corner in its containing
        # frame. Subtracting the rotated local minimum supplies the placement
        # correction required by signed (negative-direction) quarter turns.
        if use_zero_origin:
            local_position = (Decimal("0"),) * 3
        else:
            local_position = _component_position_values(component)
        local_offset = _subtract_vectors(local_position, local_minimums)
        # A child's local rotation and corrected placement are composed through
        # the parent's world transform; no transformed values are stored back.
        world_rotation = _multiply_rotations(parent_rotation, local_rotation)
        world_offset = _add_vectors(
            parent_offset,
            _transform_vector(parent_rotation, local_offset),
        )
        # Projection consumes the world-space 3D AABB, then selects the two axes
        # belonging to the requested technical drawing view.
        world_minimums, world_maximums = _rotated_bounds(
            _component_dimension_values(component), world_rotation
        )
        world_minimums = _add_vectors(world_offset, world_minimums)
        world_maximums = _add_vectors(world_offset, world_maximums)
        projected_bounds = (
            world_minimums[horizontal_axis],
            world_maximums[horizontal_axis],
            world_minimums[vertical_axis],
            world_maximums[vertical_axis],
        )
        if all(value is not None for value in projected_bounds):
            h_minimum, h_maximum, v_minimum, v_maximum = projected_bounds
            h_size_value = h_maximum - h_minimum
            v_size_value = v_maximum - v_minimum
            h_template = _axis_measurement(component, world_rotation, horizontal_axis)
            v_template = _axis_measurement(component, world_rotation, vertical_axis)
            position_template = _axis_measurement(
                component, parent_rotation, horizontal_axis, position=True
            )
            if position_template is None:
                position_template = h_template
            vertical_position_template = _axis_measurement(
                component, parent_rotation, vertical_axis, position=True
            )
            if vertical_position_template is None:
                vertical_position_template = v_template
            h_size = _measurement_with_value(h_template, h_size_value)
            v_size = _measurement_with_value(v_template, v_size_value)
            h_position = _measurement_with_value(position_template, h_minimum)
            v_position = _measurement_with_value(
                vertical_position_template, v_minimum
            )
            if all((h_size, v_size, h_position, v_position)):
                view_axes = tuple(
                    ("length", "width", "height")[
                        next(
                            index
                            for index, coefficient in enumerate(
                                world_rotation[output_axis]
                            )
                            if coefficient
                        )
                    ]
                    for output_axis in (horizontal_axis, vertical_axis, normal_axis)
                )
                out_of_envelope = (
                    view.horizontal is not None
                    and view.vertical is not None
                    and (
                        h_minimum < 0
                        or v_minimum < 0
                        or h_maximum > view.horizontal.value
                        or v_maximum > view.vertical.value
                    )
                )
                projections.append(
                    ComponentProjection(
                        component_key=component.key,
                        component_name=component.name,
                        primitive=component.primitive,
                        horizontal_size=h_size,
                        vertical_size=v_size,
                        horizontal_position=h_position,
                        vertical_position=v_position,
                        view_axes=view_axes,
                        longitudinal_axis=(
                            "height"
                            if component.primitive in {"cylinder", "shaft"}
                            and component.dimensions.length is None
                            else "length"
                        ),
                        wall_thickness=component.wall_thickness,
                        out_of_envelope=out_of_envelope,
                    )
                )
        for child in component.subgeometry:
            if child.position is None:
                continue
            pending.append((child, world_rotation, world_offset, False))
    return tuple(projections)


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
