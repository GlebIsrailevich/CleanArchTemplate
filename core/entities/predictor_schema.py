# from pydantic import BaseModel, Field


# class PredictorInfo(BaseModel):
#     name: str = Field(..., description="Name of the predictor model.")
#     cost: int = Field(
#         ..., description="Cost associated with using this predictor model."
#     )
# core/entities/predictor_schema.py
from pydantic import BaseModel, Field


class PredictorInfo(BaseModel):
    id: str = Field(
        ..., description="Unique identifier for the predictor model."
    )  # Add this
    name: str = Field(..., description="Name of the predictor model.")
    cost_per_prediction: int = Field(  # Renamed from "cost"
        ..., description="Cost per prediction using this model."
    )
    description: str = Field("", description="Description of the model.")
