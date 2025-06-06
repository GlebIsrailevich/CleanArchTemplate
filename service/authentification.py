# from datetime import timedelta

# # from config import settings  # OK
# from config.settings import settings
# from core.entities.auth_schema import (  # OK
#     Payload,
#     Session,
#     SignInRequest,
#     SignUpRequest,
# )
# from core.entities.user import User
# from core.entities.user_schema import BaseUser
# from core.repositories.user_repository import UserRepository  # OK
# from infra.exceptions.exceptions import AuthError  # OK
# from infra.security.security_entity import (  # OK
#     create_access_token,
#     get_password_hash,
#     verify_password,
# )
# from service.base_service import BaseService


# class AuthService(BaseService):
#     def __init__(self, user_repository: UserRepository):
#         self.user_repository = user_repository
#         super().__init__(user_repository)

#     def sign_in(self, sign_in_info: SignInRequest):
#         found_user = self.user_repository.read_by_email(sign_in_info.email)
#         if not found_user or not verify_password(
#             sign_in_info.password, found_user.password
#         ):
#             raise AuthError(detail="Incorrect email or password")

#         if not verify_password(sign_in_info.password, found_user.password):
#             raise AuthError(detail="Incorrect email or password")

#         payload = Payload(
#             id=found_user.id,
#             email=found_user.email,
#             name=found_user.name,
#             is_superuser=found_user.is_superuser,
#         )
#         token_lifespan = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token, expiration_datetime = create_access_token(
#             payload.dict(), token_lifespan
#         )

#         session = Session(access_token=access_token, expiration=expiration_datetime)

#         base_user = BaseUser(
#             payload=payload,
#             session=session,
#         )

#         return base_user

#     def sign_up(self, user_info: SignUpRequest):
#         user = User(**user_info.dict(exclude_none=True), is_superuser=False)
#         user.password = get_password_hash(user_info.password)
#         created_user = self.user_repository.create_prediction(user)

#         payload = Payload(
#             id=created_user.id,
#             email=created_user.email,
#             name=created_user.name,
#             is_superuser=created_user.is_superuser,
#         )
#         token_lifespan = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token, expiration_datetime = create_access_token(
#             payload.dict(), token_lifespan
#         )

#         session = Session(access_token=access_token, expiration=expiration_datetime)

#         base_user = BaseUser(
#             payload=payload,
#             session=session,
#         )

#         return base_user
from datetime import timedelta

from config.settings import settings
from core.entities.auth_schema import Payload, Session, SignInRequest, SignUpRequest
from core.entities.user import User
from core.entities.user_schema import BaseUser
from core.repositories.user_repository import UserRepository
from infra.exceptions.exceptions import AuthError
from infra.security.security_entity import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from service.base_service import BaseService


class AuthService(BaseService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        super().__init__(user_repository)

    def sign_in(self, sign_in_info: SignInRequest):
        found_user = self.user_repository.read_by_email(sign_in_info.email)
        if not found_user or not verify_password(
            sign_in_info.password, found_user.password
        ):
            raise AuthError(detail="Incorrect email or password")

        if not verify_password(sign_in_info.password, found_user.password):
            raise AuthError(detail="Incorrect email or password")

        payload = Payload(
            id=found_user.id,
            email=found_user.email,
            name=found_user.name,
            is_superuser=found_user.is_superuser,
        )
        token_lifespan = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, expiration_datetime = create_access_token(
            payload.dict(), token_lifespan
        )

        session = Session(access_token=access_token, expiration=expiration_datetime)

        base_user = BaseUser(
            payload=payload,
            session=session,
        )

        return base_user

    def sign_up(self, user_info: SignUpRequest):
        user = User(**user_info.dict(exclude_none=True), is_superuser=False)
        user.password = get_password_hash(user_info.password)
        created_user = self.user_repository.create(
            user
        )  # Changed from create_prediction to create

        payload = Payload(
            id=created_user.id,
            email=created_user.email,
            name=created_user.name,
            is_superuser=created_user.is_superuser,
        )
        token_lifespan = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, expiration_datetime = create_access_token(
            payload.dict(), token_lifespan
        )

        session = Session(access_token=access_token, expiration=expiration_datetime)

        base_user = BaseUser(
            payload=payload,
            session=session,
        )

        return base_user
