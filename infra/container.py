# from dependency_injector import containers, providers

# from config import settings
# from core.repositories.billing_repository import BillingRepository
# from core.repositories.prediction_repository import PredictionRepository
# from core.repositories.predictor_repository import PredictorRepository
# from core.repositories.user_repository import UserRepository
# from infra.database import Database
# from service.authentification import AuthService
# from service.billing_service import BillingService
# from service.prediction_service import PredictionService
# from service.predictor_service import PredictorService
# from service.user_service import UserService


# class Container(containers.DeclarativeContainer):
#     wiring_config = containers.WiringConfiguration(
#         modules=[
#             "backend.api.v1.endpoints.admin",
#             "backend.api.v1.endpoints.auth",
#             "backend.api.v1.endpoints.billing",
#             "backend.api.v1.endpoints.prediction",
#             "backend.core.dependencies",
#         ]
#     )

#     db = providers.Singleton(Database, db_url=settings.DATABASE_URI)

#     user_repository = providers.Factory(
#         UserRepository, session_factory=db.provided.session
#     )
#     billing_repository = providers.Factory(
#         BillingRepository, session_factory=db.provided.session
#     )
#     prediction_repository = providers.Factory(
#         PredictionRepository, session_factory=db.provided.session
#     )
#     predictor_repository = providers.Factory(
#         PredictorRepository, session_factory=db.provided.session
#     )

#     user_service = providers.Factory(UserService, user_repository=user_repository)
#     auth_service = providers.Factory(AuthService, user_repository=user_repository)
#     billing_service = providers.Factory(
#         BillingService, billing_repository=billing_repository
#     )
#     predictor_service = providers.Factory(
#         PredictorService, predictor_repository=predictor_repository
#     )
#     prediction_service = providers.Factory(
#         PredictionService, prediction_repository=prediction_repository
#     )
from dependency_injector import containers, providers

# from config import settings
from config.settings import settings
from core.repositories.billing_repository import BillingRepository
from core.repositories.prediction_repository import PredictionRepository
from core.repositories.predictor_repository import PredictorRepository
from core.use_cases.user_use_cases import UserUseCases
from infra.database import Database
from infra.db.user_repository_impl import UserRepositoryImpl
from service.authentification import AuthService
from service.billing_service import BillingService
from service.prediction_service import PredictionService
from service.predictor_service import PredictorService
from service.user_service import UserService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "api.admin",
            "api.auth",
            "api.billing",
            "api.prediction",
            "infra.dependencies",
            "infra.web.controllers.user_controller",
            # "infra.web.dependencies",
        ]
    )

    db = providers.Singleton(Database, db_url=settings.DATABASE_URI)

    # Update to use UserRepositoryImpl
    user_repository = providers.Factory(
        UserRepositoryImpl, session_factory=db.provided.session
    )
    billing_repository = providers.Factory(
        BillingRepository, session_factory=db.provided.session
    )
    prediction_repository = providers.Factory(
        PredictionRepository, session_factory=db.provided.session
    )
    predictor_repository = providers.Factory(
        PredictorRepository, session_factory=db.provided.session
    )

    # Add UserUseCases
    user_use_cases = providers.Factory(UserUseCases, user_repository=user_repository)

    user_service = providers.Factory(UserService, user_repository=user_repository)
    auth_service = providers.Factory(AuthService, user_repository=user_repository)
    billing_service = providers.Factory(
        BillingService, billing_repository=billing_repository
    )
    predictor_service = providers.Factory(
        PredictorService, predictor_repository=predictor_repository
    )
    prediction_service = providers.Factory(
        PredictionService, prediction_repository=prediction_repository
    )
