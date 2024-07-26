import json
from enum import Enum
from typing import NamedTuple, Optional, Any, TypeVar

from ..enums import clarity_aliases
from ..enums import color_aliases
from ...models.enums import Color, Clarity, Shape
from .value_range import ValueRange


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, ValueRange):
            return {"from": obj.from_value, "to": obj.to_value}
        elif isinstance(obj, ExtractedDiamond):
            return obj.as_dict()
        return super().default(obj)


enum_type = TypeVar('enum_type', bound=Enum)


class ExtractedDiamond(NamedTuple):
    color: Optional[Color] | ValueRange[Color] | list[Color | ValueRange[Color]]
    clarity: Optional[Clarity] | ValueRange[Clarity] | list[Clarity | ValueRange[Clarity]]
    carat: Optional[float] | ValueRange[float] | list[float | ValueRange[float]]
    shape: Optional[Shape] | ValueRange[Shape] | list[Shape | ValueRange[Shape]]

    @staticmethod
    def get_value_range_by_mapping(data_object: dict[str, Any], mapping: dict[str, enum_type]) \
            -> Optional[ValueRange[enum_type]]:
        from_value, to_value = None, None
        if isinstance(data_object.get("from"), str):
            from_value = mapping.get(data_object["from"].upper())
        if isinstance(data_object.get("to"), str):
            to_value = mapping.get(data_object["to"].upper())
        value_range = ValueRange(from_value, to_value)
        if not value_range.is_valid():
            return None
        return value_range


    @staticmethod
    def get_color_or_none(data: dict[str, Any]) \
            -> Optional[Color] | ValueRange[Color] | list[
                Color | ValueRange[Color]]:
        color = data.get("color")
        if isinstance(color, list):
            return [ExtractedDiamond.get_color_or_none({'color': item}) for item in color if not isinstance(item, list)]
        if isinstance(color, dict):
            value_range = ExtractedDiamond.get_value_range_by_mapping(color, color_aliases)
            return value_range
        if isinstance(color, str) and color:
            color = color_aliases.get(color[0].upper())
            return color
        return None

    @staticmethod
    def get_clarity_or_none(data: dict[str, Any]) \
            -> Optional[Clarity] | ValueRange[Clarity] | list[
                Clarity | ValueRange[Clarity]]:
        clarity = data.get("clarity")
        if isinstance(clarity, list):
            return [ExtractedDiamond.get_clarity_or_none({'clarity': item}) for item in clarity if
                    not isinstance(item, list)]
        if isinstance(clarity, dict):
            value_range = ExtractedDiamond.get_value_range_by_mapping(clarity, clarity_aliases)
            return value_range
        if isinstance(clarity, str) and clarity:
            clarity = clarity_aliases.get(clarity.upper())
            return clarity
        return None

    @staticmethod
    def get_carat_or_none(data: dict[str, Any]) \
            -> Optional[float] | ValueRange[float] | list[float | ValueRange[float]]:
        weight = data.get("carat")
        if isinstance(weight, list):
            return [ExtractedDiamond.get_carat_or_none({'carat': item}) for item in weight if
                    not isinstance(item, list)]
        if isinstance(weight, dict):
            try:
                from_weight = float(weight['from'])
            except (ValueError, KeyError):
                from_weight = None
            try:
                to_weight = float(weight['to'])
            except (ValueError, KeyError):
                to_weight = None
            value_range = ValueRange(from_weight, to_weight)
            if not value_range.is_valid():
                return None
            return value_range
        elif isinstance(weight, (float, int)):
            return float(weight)
        elif isinstance(weight, str):
            try:
                return float(weight)
            except ValueError:
                return None
        return None

    @staticmethod
    def get_shape_or_none(data: dict[str, Any]) \
            -> Optional[Shape] | ValueRange[Shape] | list[Shape | ValueRange[Shape]]:
        shape = data.get("shape")
        if isinstance(shape, list):
            return [ExtractedDiamond.get_shape_or_none({'shape': item}) for item in shape if not isinstance(item, list)]
        if isinstance(shape, dict):
            from_shape = None
            to_shape = None
            if isinstance(shape.get("from"), str) and len(shape) > 0:
                if (value := shape["from"].upper()) in Shape:
                    from_shape = Shape(value)
            if isinstance(shape.get("to"), str) and len(shape) > 0:
                if (value := shape["to"].upper()) in Shape:
                    to_shape = Shape(value)
            value_range = ValueRange(from_shape, to_shape)
            if not value_range.is_valid():
                return None
            return value_range
        if isinstance(shape, str) and shape:
            shape = shape.lower()
            if shape in Shape:
                return Shape(shape)
        return None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ExtractedDiamond":
        return ExtractedDiamond(
            color=ExtractedDiamond.get_color_or_none(data),
            clarity=ExtractedDiamond.get_clarity_or_none(data),
            carat=ExtractedDiamond.get_carat_or_none(data),
            shape=ExtractedDiamond.get_shape_or_none(data),
        )

    def as_dict(self) -> dict:
        return {
            "color": self.color,
            "clarity": self.clarity,
            "carat": self.carat,
            "shape": self.shape,
        }

    def to_user_friendly_string(self, gettext) -> str:
        def format_value(value):
            if isinstance(value, ValueRange):
                return gettext("from_{from_value}_to_{to_value}").format(from_value=format_value(value.from_value),
                                                                         to_value=format_value(value.to_value))
            elif isinstance(value, list):
                return ', '.join([format_value(v) for v in value])
            elif isinstance(value, Enum):
                return value.value
            elif value is None:
                return gettext("not_specified")
            return str(value)

        color_str = format_value(self.color)
        clarity_str = format_value(self.clarity)
        carat_str = format_value(self.carat)
        shape_str = format_value(self.shape)

        parts = [
            gettext("Color: {color}").format(color=color_str) if color_str else None,
            gettext("Clarity: {clarity}").format(clarity=clarity_str) if clarity_str else None,
            gettext("Carat: {carat}").format(carat=carat_str) if carat_str else None,
            gettext("Shape: {shape}").format(shape=shape_str) if shape_str else None,
        ]
        parts = [part for part in parts if part is not None]
        return gettext("Diamond - {details}").format(details=", ".join(parts))
