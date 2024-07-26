from enum import Enum


class Shape(Enum):
    ROUND_BRILLIANT = "round brilliant"
    PRINCESS = "princess"
    CUSHION = "cushion"
    OVAL = "oval"
    EMERALD = "emerald"
    PEAR = "pear"
    MARQUISE = "marquise"
    ASSCHER = "asscher"
    RADIANT = "radiant"
    HEART = "heart"
    BAGUETTE = "baguette"
    OLD_EUROPEAN = "old european"
    ROSE = "rose"
    TAPERED_BAGUETTE = "tapered baguette"
    BULLET = "bullet"
    KITE = "kite"
    HALF_MOON = "half moons"
    TRILLION = "trillion"
    HORSE_HEAD = "horse head"
    SHIELD = "shield"
    HEXAGONAL = "hexagonal"
    OLD_MINE = "old mine"
    ROSE_HEAD = "rose head"


shape_aliases = {
    "RB": Shape.ROUND_BRILLIANT,
    "PC": Shape.PRINCESS,
    "PR": Shape.PRINCESS,
    "CC": Shape.CUSHION,
    "CU": Shape.CUSHION,
    "OC": Shape.OVAL,
    "OV": Shape.OVAL,
    "EC": Shape.EMERALD,
    "EM": Shape.EMERALD,
    "PS": Shape.PEAR,
    "MC": Shape.MARQUISE,
    "MQ": Shape.MARQUISE,
    "AC": Shape.ASSCHER,
    "AS": Shape.ASSCHER,
    "RC": Shape.RADIANT,
    "RD": Shape.RADIANT,
    "RA": Shape.RADIANT,
    "HC": Shape.HEART,
    "HT": Shape.HEART,
    "HS": Shape.HEART,
    "BC": Shape.BAGUETTE,
    "BG": Shape.BAGUETTE,
    "OEC": Shape.OLD_EUROPEAN,
    "RS": Shape.ROSE,
    "BR": Shape.ROUND_BRILLIANT,
    "TBC": Shape.TAPERED_BAGUETTE,
    "BUC": Shape.BULLET,
    "BU": Shape.BULLET,
    "KC": Shape.KITE,
    "HMC": Shape.HALF_MOON,
    "HM": Shape.HALF_MOON,
    "TC": Shape.TRILLION,
    "TR": Shape.TRILLION,
    "SC": Shape.SHIELD,
    "HXC": Shape.HEXAGONAL,
    "OM": Shape.OLD_MINE,
    "HH": Shape.HORSE_HEAD,
    "AF": Shape.ASSCHER,
    "PE": Shape.PEAR,
    "HD": Shape.HORSE_HEAD
}
