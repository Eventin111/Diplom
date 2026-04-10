"""Domain layer for the SwipeIt ML module."""

from swipeit_ml.domain.entities import InferenceRequest, InferenceResult
from swipeit_ml.domain.enums import GarmentCategory, ModelType, category_from_index, coerce_category, coerce_model_type

__all__ = [
    "GarmentCategory",
    "InferenceRequest",
    "InferenceResult",
    "ModelType",
    "category_from_index",
    "coerce_category",
    "coerce_model_type",
]
