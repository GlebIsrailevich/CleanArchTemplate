# from pathlib import Path
# from typing import Dict, List

# import dill
# import joblib

# from core.repositories.predictor_repository import PredictorRepository


# def load_model(model_name):
#     # Грузим 3 модели
#     model_names = {
#         "LogisticRegression": "ml_models/catboost.dill",
#         "SVM": "ml_models/svm.dill",
#         "Catboost": "models/catboost.dill",
#     }
#     model_file = model_names[model_name]
#     # Подстраивает корректный путь для загруженных моделей
#     current_file_path = Path(__file__).resolve()
#     project_root = current_file_path.parents[2]
#     models_directory = project_root / "ml/ml_models"
#     full_model_path = models_directory / model_file

#     if not full_model_path.exists():
#         raise FileNotFoundError(f"Model file not found at {full_model_path}")
#     return joblib.load(full_model_path)


# def load_pipeline():
#     # грузит пайплайн и также подгоняет путь
#     current_file_path = Path(__file__).resolve()
#     project_root = current_file_path.parents[2]
#     models_directory = project_root / "ml/ml_models"

#     with open(models_directory / "preprocessing_pipeline.dill", "rb") as f:
#         return dill.load(f)


# class PredictorService:
#     def __init__(self, predictor_repository: PredictorRepository):
#         self.predictor_repository = predictor_repository

#     def init_predictors(self):
#         predictors = self.predictor_repository.get_all_predictors()
#         if len(predictors) == 0:
#             # Если нет предикторов, то добавляем logreg, svm, catboost
#             self.predictor_repository.create_predictor(
#                 {"name": "LogisticRegression", "cost": 100}
#             )
#             self.predictor_repository.create_predictor({"name": "SVM", "cost": 250})
#             self.predictor_repository.create_predictor(
#                 {"name": "Catboost", "cost": 500}
#             )
#         return self.predictor_repository.get_all_predictors()

#     def get_available_models(self) -> List[Dict[str, str]]:
#         # Получаем доступные модели предсказательные модели
#         available_models = []
#         predictors = self.predictor_repository.get_all_predictors()
#         for predictor in predictors:
#             available_models.append({"name": predictor.name, "cost": predictor.cost})
#         return available_models

#     def get_model_cost(self, model_name: str) -> int:
#         # Получаем поле цена у предиктивной модели
#         predictor = self.predictor_repository.get_predictor_by_name(model_name)
#         if predictor:
#             return predictor.cost
#         raise ValueError(f"Model {model_name} is not available.")


from pathlib import Path
from typing import List

import dill
import joblib

from core.entities.predictor_schema import PredictorInfo
from core.repositories.predictor_repository import PredictorRepository


def load_model(model_name):
    # Fixed model paths to be consistent
    model_names = {
        "LogisticRegression": "ml_models/logreg.dill",
        "SVM": "ml_models/svm.dill",
        "Catboost": "ml_models/catboost.dill",  # Fixed path
    }

    if model_name not in model_names:
        raise ValueError(f"Model {model_name} is not supported")

    model_file = model_names[model_name]

    # Build correct path for loaded models
    current_file_path = Path(__file__).resolve()
    project_root = current_file_path.parents[2]
    models_directory = project_root / "ml/ml_models"
    full_model_path = models_directory / model_file

    if not full_model_path.exists():
        # Try alternative path (without ml prefix)
        models_directory = project_root / "ml_models"
        full_model_path = models_directory / model_file

        if not full_model_path.exists():
            raise FileNotFoundError(f"Model file not found at {full_model_path}")

    try:
        return joblib.load(full_model_path)
    except Exception as e:
        # Try with dill if joblib fails
        try:
            with open(full_model_path, "rb") as f:
                return dill.load(f)
        except Exception as inner_e:
            raise RuntimeError(f"Failed to load model: {str(e)}, then: {str(inner_e)}")


def load_pipeline():
    # Load pipeline with flexible path handling
    current_file_path = Path(__file__).resolve()
    project_root = current_file_path.parents[2]

    # Try multiple possible paths
    possible_paths = [
        project_root / "ml/ml_models/preprocessing_pipeline.dill",
        project_root / "ml_models/preprocessing_pipeline.dill",
        project_root / "ml/models/preprocessing_pipeline.dill",
    ]

    for path in possible_paths:
        if path.exists():
            try:
                with open(path, "rb") as f:
                    return dill.load(f)
            except Exception:
                continue

    raise FileNotFoundError(
        "Preprocessing pipeline not found in any of the expected locations"
    )


class PredictorService:
    def __init__(self, predictor_repository: PredictorRepository):
        self.predictor_repository = predictor_repository
        self.model_descriptions = {
            "LogisticRegression": "Simple linear model",
            "SVM": "Support Vector Machine",
            "Catboost": "Gradient boosting",
            # Add fallback for unknown models
        }

        # Model descriptions for better UI display
        self.model_descriptions = {
            "LogisticRegression": "Simple linear model for classification",
            "SVM": "Support Vector Machine for classification",
            "Catboost": "Gradient boosting on decision trees",
        }

    def init_predictors(self) -> List[PredictorInfo]:
        """Initialize predictors if none exist and return all available predictors"""
        predictors = self.predictor_repository.get_all_predictors()

        if len(predictors) == 0:
            # Create predictors if none exist
            self.predictor_repository.create_predictor(
                {"name": "LogisticRegression", "cost": 100}
            )
            self.predictor_repository.create_predictor({"name": "SVM", "cost": 250})
            self.predictor_repository.create_predictor(
                {"name": "Catboost", "cost": 500}
            )

            # Fetch newly created predictors
            predictors = self.predictor_repository.get_all_predictors()

        # Convert to PredictorInfo objects with additional info
        result = []
        for predictor in predictors:
            # result.append(
            #     PredictorInfo(
            #         id=str(predictor.id),
            #         name=predictor.name,
            #         cost_per_prediction=predictor.cost,
            #         description=self.model_descriptions.get(predictor.name, ""),
            # )
            result.append(
                PredictorInfo(
                    id=str(predictor.id),
                    name=predictor.name,
                    cost_per_prediction=predictor.cost,  # ✅ Match Pydantic model
                    description=str(  # Force string conversion
                        self.model_descriptions.get(predictor.name, "No description")
                    ),
                )
            )

        return result

    def get_available_models(self) -> List[PredictorInfo]:
        """Get all available prediction models with full information"""
        predictors = self.predictor_repository.get_all_predictors()

        result = []
        for predictor in predictors:
            result.append(
                PredictorInfo(
                    id=str(predictor.id),
                    name=predictor.name,
                    cost_per_prediction=predictor.cost,
                    description=self.model_descriptions.get(predictor.name, ""),
                )
            )

        return result

    def get_model_cost(self, model_name: str) -> int:
        """Get the cost of a specific model"""
        predictor = self.predictor_repository.get_predictor_by_name(model_name)
        if predictor:
            return predictor.cost
        raise ValueError(f"Model {model_name} is not available.")

    def check_models_exist(self) -> bool:
        """Verify that model files actually exist on disk"""
        try:
            for model_name in ["LogisticRegression", "SVM", "Catboost"]:
                try:
                    # Just try loading each model to check if it exists
                    load_model(model_name)
                except FileNotFoundError:
                    return False
            return True
        except Exception:
            return False
