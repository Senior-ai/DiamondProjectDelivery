from enum import Enum
from typing import Optional


class Quality(Enum):
    EXCELLENT = "EXCELLENT"
    VERY_GOOD = "VERY GOOD"
    GOOD = "GOOD"
    POOR = "POOR"


quality_aliases = {
    "EX": Quality.EXCELLENT,
    "VG": Quality.VERY_GOOD,
    "G": Quality.GOOD,
    "P": Quality.POOR
}
