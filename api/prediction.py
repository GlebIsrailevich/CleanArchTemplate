from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.entities.auth_schema import Payload
from core.entities.prediction_schema import (
    PredictionBatchInfo,
    PredictionFeatures,
    PredictionInfo,
    PredictionRequest,
    PredictionTarget,
)
from core.entities.predictor_schema import PredictorInfo
from infra.container import Container
from infra.dependencies import get_current_user_payload
from infra.exceptions.exceptions import PredictionError, ValidationError
from infra.logger import LOGGER
from service.billing_service import BillingService
from service.prediction_service import PredictionService
from service.predictor_service import PredictorService
from utils.date import get_now

router = APIRouter(
    prefix="/prediction",
    tags=["prediction"],
)

security = HTTPBearer()


@router.get("/", response_model=List[PredictorInfo])
@inject
async def init_available_predictors(
    predictor_service: PredictorService = Depends(Provide[Container.predictor_service]),
):
    available_models = predictor_service.init_predictors()
    return available_models


@router.get("/models", response_model=List[PredictorInfo])
@inject
async def get_available_models(
    predictor_service: PredictorService = Depends(Provide[Container.predictor_service]),
):
    available_models = predictor_service.get_available_models()
    return available_models


@router.get("/history", response_model=List[PredictionBatchInfo])
@inject
async def get_prediction_history(
    current_user_payload: Payload = Depends(get_current_user_payload),
    prediction_service: PredictionService = Depends(
        Provide[Container.prediction_service]
    ),
):
    prediction_history = prediction_service.get_prediction_history(
        current_user_payload.id
    )
    return prediction_history


@router.post("/make", response_model=PredictionBatchInfo)
@inject
async def make_predictions(
    prediction_request: PredictionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user_payload: Payload = Depends(get_current_user_payload),
    prediction_service: PredictionService = Depends(
        Provide[Container.prediction_service]
    ),
    predictor_service: PredictorService = Depends(Provide[Container.predictor_service]),
    billing_service: BillingService = Depends(Provide[Container.billing_service]),
):
    if len(prediction_request.features) == 0:
        raise ValidationError("No features provided")
    model_cost_per_prediction = predictor_service.get_model_cost(
        prediction_request.model_name
    )
    total_cost = model_cost_per_prediction * len(prediction_request.features)
    if not billing_service.reserve_funds(current_user_payload.id, total_cost):
        raise PredictionError(detail="Insufficient funds for prediction batch.")

    try:
        LOGGER.error("Prediction request: %s", prediction_request.features)
        # print(prediction_request.features)
        batch_requests = [
            {
                "app_id": single_request.app_id,
                "amnt": single_request.amnt,
                "currency": single_request.currency,
                "operation_kind": single_request.operation_kind,
                "card_type": single_request.card_type,
                "operation_type": single_request.operation_type,
                "operation_type_group": single_request.operation_type_group,
                "ecommerce_flag": single_request.ecommerce_flag,
                "payment_system": single_request.payment_system,
                "income_flag": single_request.income_flag,
                "mcc": single_request.mcc,
                "country": single_request.country,
                "city": single_request.city,
                "mcc_category": single_request.mcc_category,
                "day_of_week": single_request.day_of_week,
                "hour": single_request.hour,
                "days_before": single_request.days_before,
                "weekofyear": single_request.weekofyear,
                "hour_diff": single_request.hour_diff,
                "transaction_number": single_request.transaction_number,
                "product": single_request.product,
            }
            for single_request in prediction_request.features
        ]
        batch_result = prediction_service.make_batch_prediction(
            prediction_request.model_name, batch_requests
        )
        prediction_results = batch_result.get(timeout=30)  # loop inside

        predictions = []
        for i, result in enumerate(prediction_results):
            predictions.append(
                PredictionInfo(
                    features=PredictionFeatures(**batch_requests[i]),
                    target=PredictionTarget(answer=result),
                )
            )
    except ValueError as e:
        billing_service.cancel_reservation(current_user_payload.id, total_cost)
        raise PredictionError(detail=str(e))
    except Exception as e:
        billing_service.cancel_reservation(current_user_payload.id, total_cost)
        raise PredictionError(detail="An error occurred during prediction: " + str(e))
    try:
        transaction = billing_service.finalize_transaction(
            current_user_payload.id, total_cost
        )
        batch = prediction_service.save_batch_prediction(
            user_id=current_user_payload.id,
            model_name=prediction_request.model_name,
            transaction_id=transaction.id,
            batch_requests=batch_requests,
            prediction_results=prediction_results,
        )

        return PredictionBatchInfo(
            id=batch.id,
            model_name=prediction_request.model_name,
            predictions=predictions,
            timestamp=get_now(),
            cost=total_cost,
        )
    except Exception as e:
        raise PredictionError(detail=str(e))
