from typing import List
from ..database.models.processing_types import ExtractedDiamond


def filter_incomplete_diamonds(diamonds: List[ExtractedDiamond]) -> List[ExtractedDiamond]:
    return [diamond for diamond in diamonds if
            all(getattr(diamond, key) for key in ["shape", "color", "clarity", "carat"])]
