from enum import Enum
from typing import Optional


class Fluorescence(Enum):
    NONE = "NONE"
    FAINT = "FAINT"
    MEDIUM = "MEDIUM"
    STRONG = "STRONG"
    VERY_STRONG = "VERY STRONG"

    @classmethod
    def get_range(cls, from_value: Optional["Fluorescence"], to_value: Optional["Fluorescence"]) -> list["Fluorescence"]:
        from_index = from_value.value if from_value is not None else 0
        to_index = to_value.value + 1 if to_value is not None else len(cls)
        return list(cls)[from_index:to_index]


fluorescence_aliases = {
    "NON": Fluorescence.NONE,
    "FNT": Fluorescence.FAINT,
    "MED": Fluorescence.MEDIUM,
    "STG": Fluorescence.STRONG,
    "VST": Fluorescence.VERY_STRONG
}
