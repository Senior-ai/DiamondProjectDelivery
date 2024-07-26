from enum import Enum


class Clarity(Enum):
    FL = "FL"
    IF = "IF"
    VVS1 = "VVS1"
    VVS2 = "VVS2"
    VS1 = "VS1"
    VS2 = "VS2"
    SI1 = "SI1"
    SI2 = "SI2"
    SI3 = "SI3"
    I1 = "I1"
    I2 = "I2"
    I3 = "I3"


clarity_aliases = {
    "FL": Clarity.FL,
    "IF": Clarity.IF,
    "VVS": Clarity.VVS1, # Mapping of general VVS to VVS1
    "VVS1": Clarity.VVS1,
    "VVS2": Clarity.VVS2,
    "VS": Clarity.VS1, # Mapping of general VS to VS1
    "VS1": Clarity.VS1,
    "VS2": Clarity.VS2,
    "SI": Clarity.SI1, # Mapping of general SI to average SI2
    "SI1": Clarity.SI1,
    "SI2": Clarity.SI2,
    "SI3": Clarity.SI3,
    "I": Clarity.I1, # Mapping of general I to average I2
    "I1": Clarity.I1,
    "I2": Clarity.I2,
    "I3": Clarity.I3,
}
