from typing import List, Optional  # Add this import

from sqlmodel import Field, Relationship, SQLModel


# class Predictor(SQLModel, table=True):
#     name: str = Field(unique=True, primary_key=True)
#     cost: int = Field()
#     prediction_batches: List["PredictionBatch"] = Relationship(
#         back_populates="predictor"
#     )
class Predictor(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True
    )  # Use Optional instead of |
    name: str = Field(unique=True)
    cost: int = Field()
    prediction_batches: List["PredictionBatch"] = Relationship(
        back_populates="predictor"
    )
