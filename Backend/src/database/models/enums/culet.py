from enum import Enum
from typing import Optional


class Culet(Enum):
    NONE = "NONE"
    VERY_SMALL = "VERY SMALL"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    SLIGHTLY_LARGE = "SLIGHTLY LARGE"
    LARGE = "LARGE"
    VERY_LARGE = "VERY LARGE"
    EXTREMELY_LARGE = "EXTREMELY LARGE"


culet_aliases = {
    "NON": Culet.NONE,
    "VSM": Culet.VERY_SMALL,
    "SM": Culet.SMALL,
    "MED": Culet.MEDIUM,
    "SL": Culet.SLIGHTLY_LARGE,
    "LG": Culet.LARGE,
    "VLG": Culet.VERY_LARGE,
    "EXLG": Culet.EXTREMELY_LARGE
}
