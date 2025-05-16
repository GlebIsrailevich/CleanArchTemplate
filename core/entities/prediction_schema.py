from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from utils.date import get_now


class PredictionFeatures(BaseModel):
    app_id: int = Field(...)
    amnt: float = Field(...)
    currency: int = Field(...)
    operation_kind: int = Field(...)
    card_type: int = Field(...)
    operation_type: int = Field(...)
    operation_type_group: int = Field(...)
    ecommerce_flag: int = Field(...)
    payment_system: int = Field(...)
    income_flag: int = Field(...)
    mcc: int = Field(...)
    country: int = Field(...)
    city: int = Field(...)
    mcc_category: int = Field(...)
    day_of_week: int = Field(...)
    hour: int = Field(...)
    days_before: int = Field(...)
    weekofyear: int = Field(...)
    hour_diff: int = Field(...)
    transaction_number: int = Field(...)
    product: int = Field(...)


class PredictionTarget(BaseModel):
    answer: int = Field(...)


class PredictionInfo(BaseModel):
    features: PredictionFeatures
    target: PredictionTarget


class PredictionRequest(BaseModel):
    model_name: str = Field(
        ..., example="RandomForest", description="Name of the prediction model to use."
    )
    features: List[PredictionFeatures] = Field(
        ..., description="List of predictions to make."
    )


class PredictionBatchInfo(BaseModel):
    id: int
    model_name: str
    predictions: List[PredictionInfo]
    timestamp: datetime = Field(
        default_factory=get_now(), description="Timestamp of the prediction batch."
    )
    cost: int = Field(..., description="Total cost of this batch of predictions.")


class PredictionsReport(BaseModel):
    model_name: str = Field(..., description="Name of the prediction model.")
    total_prediction_batches: int = Field(
        ..., description="Total number of prediction batches made using this model."
    )
