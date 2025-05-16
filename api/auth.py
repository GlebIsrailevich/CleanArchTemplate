from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from core.entities.auth_schema import SignInRequest, SignUpRequest
from core.entities.user_schema import BaseUser
from infra.container import Container
from infra.dependencies import get_current_user_payload
from service.authentification import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# @router.get(path="/health")
# @inject
# async def health() -> str:
#     return "I am alive"
@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/sign-in", response_model=BaseUser)
@inject
async def sign_in(
    user_info: SignInRequest,
    service: AuthService = Depends(Provide[Container.auth_service]),
):
    return service.sign_in(user_info)


@router.post("/sign-up", response_model=BaseUser)
@inject
async def sign_up(
    user_info: SignUpRequest,
    service: AuthService = Depends(Provide[Container.auth_service]),
):
    return service.sign_up(user_info)


@router.post("/sign-out")
@inject
async def sign_out(
    service: AuthService = Depends(Provide[Container.auth_service]),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    # Log the sign-out by updating last_activity (optional)
    if current_user_payload and "id" in current_user_payload:
        service.update_last_activity(current_user_payload.id)
    return {"message": "Signed out successfully"}
