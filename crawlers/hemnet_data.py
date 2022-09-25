from dataclasses import dataclass


@dataclass
class FeatureAnalysisConfig:
    balcony_bias: float
    patio_bias: float

    highest_floor_bias: float
    nth_floor_bias: float
    preferred_floor: str
    lowest_floor_bias: float

    elevator_bias: float