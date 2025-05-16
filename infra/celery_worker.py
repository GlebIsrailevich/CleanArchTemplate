# import os

# from celery import Celery

# from config.settings import settings

# celery = Celery("prediction_worker")

# celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", settings.BROKER_URL)
# celery.conf.result_backend = os.environ.get(
#     "CELERY_RESULT_BACKEND", settings.BROKER_RESULT_BACKEND
# )

# celery.conf.update(
#     task_serializer="pickle",
#     result_serializer="pickle",
#     accept_content=["pickle"],
#     worker_send_task_events=True,
#     worker_disable_rate_limits=False,
# )


# @celery.task
# def async_make_batch_predictions(model_name, prediction_requests):
#     import json
#     from io import StringIO

#     import pandas as pd

#     from service.prediction_service import make_prediction
#     from service.predictor_service import load_model

#     model = load_model(model_name)
#     # pipeline = load_pipeline()

#     results = []

#     df = pd.read_json(StringIO(json.dumps(prediction_requests)))

#     results = make_prediction(model, df)

#     return results

import json
from io import StringIO

import pandas as pd
from celery import Celery

from config.settings import settings
from service.predictor_service import load_model, load_pipeline

celery = Celery("prediction_worker")

celery.conf.broker_url = settings.BROKER_URL
celery.conf.result_backend = settings.BROKER_RESULT_BACKEND

celery.conf.update(
    task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["pickle"],
    worker_send_task_events=True,
    worker_disable_rate_limits=False,
)


@celery.task(name="make_batch_predictions")
def async_make_batch_predictions(model_name, prediction_requests):
    """
    Celery task to make batch predictions

    Args:
        model_name (str): Name of the model to use
        prediction_requests (List[dict]): List of feature dictionaries

    Returns:
        List[float]: List of prediction results
    """
    try:
        # Load the model
        model = load_model(model_name)

        # Convert the prediction requests to a DataFrame
        df = pd.read_json(StringIO(json.dumps(prediction_requests)))

        # Make predictions
        results = make_prediction(model, df)

        return results
    except Exception as e:
        # Log the error and re-raise
        import logging

        logging.error(f"Error in prediction task: {str(e)}")
        raise


def make_prediction(model, df):
    """
    Make predictions using the provided model and features

    Args:
        model: The loaded ML model
        df (pd.DataFrame): DataFrame containing features

    Returns:
        List[float]: Prediction results
    """
    try:
        # Try to load pipeline for preprocessing
        try:
            pipeline = load_pipeline()
            # Apply preprocessing if pipeline exists
            transformed_df = pipeline.transform(df)
        except (FileNotFoundError, ImportError, Exception):
            # If pipeline fails, just use the original data
            transformed_df = df

        # Make predictions
        if hasattr(model, "predict_proba"):
            # For probability predictions (for classification)
            predictions = model.predict_proba(transformed_df)
            # Take the probability of the positive class
            if predictions.shape[1] > 1:
                results = predictions[:, 1].tolist()
            else:
                results = predictions.tolist()
        else:
            # For regular predictions
            predictions = model.predict(transformed_df)
            results = predictions.tolist()

        return results
    except Exception as e:
        import logging

        logging.error(f"Prediction error: {str(e)}")
        raise ValueError(f"Failed to make prediction: {str(e)}")
