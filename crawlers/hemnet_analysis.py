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


def get_price_index(price, fee, price_mul, fee_mul) -> float:
    return (price * price_mul) + (fee * fee_mul)


def get_size_index(size, rooms, size_mul, rooms_mul) -> float:
    return (size * size_mul) + (rooms * rooms_mul)


def get_features_index(balcony, patio, floor, has_elevator, settings: FeatureAnalysisConfig) -> float:
    features_index = 0

    if balcony == "Ja":
        features_index += settings.balcony_bias

    if patio == "Ja":
        features_index += settings.patio_bias

    if floor[0:1] == floor[5:6]:
        features_index += settings.highest_floor_bias

    if floor[0:1] in ("0", "1", "-"):
        features_index += settings.lowest_floor_bias

    if len(floor) > 1 and floor[0:floor.index(" ")] == settings.preferred_floor:
        features_index += settings.nth_floor_bias

    if has_elevator:
        features_index += settings.elevator_bias

    return features_index