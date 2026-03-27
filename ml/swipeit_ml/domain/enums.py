from __future__ import annotations

from enum import Enum


class ModelType(str, Enum):
    HD = "hd"
    DC = "dc"


class GarmentCategory(str, Enum):
    UPPERBODY = "upperbody"
    LOWERBODY = "lowerbody"
    DRESS = "dress"


CATEGORY_TO_MASK_CATEGORY = {
    GarmentCategory.UPPERBODY: "upper_body",
    GarmentCategory.LOWERBODY: "lower_body",
    GarmentCategory.DRESS: "dresses",
}


def coerce_model_type(value: ModelType | str) -> ModelType:
    if isinstance(value, ModelType):
        return value
    return ModelType(value)


def coerce_category(value: GarmentCategory | str) -> GarmentCategory:
    if isinstance(value, GarmentCategory):
        return value
    return GarmentCategory(value)


def category_from_index(index: int) -> GarmentCategory:
    categories = [
        GarmentCategory.UPPERBODY,
        GarmentCategory.LOWERBODY,
        GarmentCategory.DRESS,
    ]
    return categories[index]
