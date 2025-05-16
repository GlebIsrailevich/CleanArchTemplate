from typing import List

from core.entities.prediction_schema import (
    PredictionBatchInfo,
    PredictionFeatures,
    PredictionInfo,
    PredictionsReport,
    PredictionTarget,
)
from core.repositories.prediction_repository import PredictionRepository
from infra.celery_worker import async_make_batch_predictions
from service.base_service import BaseService


def make_prediction(model, data):
    answer = model.predict(data)
    return answer.tolist()


class PredictionService(BaseService):
    def __init__(self, prediction_repository: PredictionRepository):
        super().__init__(prediction_repository)
        self.prediction_repository = prediction_repository

    @staticmethod
    def make_batch_prediction(model_name, prediction_requests: List[dict]):
        async_result = async_make_batch_predictions.delay(
            model_name, prediction_requests
        )
        return async_result

    def save_batch_prediction(
        self,
        user_id: int,
        model_name: str,
        transaction_id: int,
        batch_requests: List[dict],
        prediction_results: List[int],
    ):
        batch = self.prediction_repository.create_batch(
            user_id=user_id, predictor_name=model_name, transaction_id=transaction_id
        )

        for i in range(len(prediction_results)):
            prediction_data = batch_requests[i]
            prediction_data["batch_id"] = batch.id
            prediction_data["answer"] = prediction_results[i]
            self.prediction_repository.create_prediction(prediction_data)

        return batch

    def get_prediction_history(self, user_id: int) -> List[PredictionBatchInfo]:
        prediction_batches = self.prediction_repository.get_prediction_history(user_id)
        result = []

        for batch in prediction_batches:
            prediction_infos = []
            for prediction in batch.predictions:
                # category_label = _CATEGORY_LABEL_MAP.get(prediction.category_id, "Unknown Category")

                prediction_info = PredictionInfo(
                    features=PredictionFeatures(
                        app_id=prediction.app_id,
                        amnt=prediction.amnt,
                        currency=prediction.currency,
                        operation_kind=prediction.operation_kind,
                        card_type=prediction.card_type,
                        operation_type=prediction.operation_type,
                        operation_type_group=prediction.operation_type_group,
                        ecommerce_flag=prediction.ecommerce_flag,
                        payment_system=prediction.payment_system,
                        income_flag=prediction.income_flag,
                        mcc=prediction.mcc,
                        country=prediction.country,
                        city=prediction.city,
                        mcc_category=prediction.mcc_category,
                        day_of_week=prediction.day_of_week,
                        hour=prediction.hour,
                        days_before=prediction.days_before,
                        weekofyear=prediction.weekofyear,
                        hour_diff=prediction.hour_diff,
                        transaction_number=prediction.transaction_number,
                        product=prediction.product,
                    ),
                    target=PredictionTarget(
                        answer=prediction.answer,
                    ),
                )
                prediction_infos.append(prediction_info)

            model_name = batch.predictor.name
            transaction_amount = batch.transaction.amount if batch.transaction else 0
            timestamp = batch.created_at

            prediction_batch_info = PredictionBatchInfo(
                id=batch.id,
                predictions=prediction_infos,
                model_name=model_name,
                cost=transaction_amount,
                timestamp=timestamp,
            )
            result.append(prediction_batch_info)

        return result

    def get_predictions_reports(self):
        raw_reports = self.prediction_repository.get_predictions_reports()
        predictions_reports = [
            PredictionsReport(
                model_name=model_name, total_prediction_batches=total_predictions
            )
            for model_name, total_predictions in raw_reports
        ]
        return predictions_reports
