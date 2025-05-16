from fastapi import APIRouter

from api.admin import router as admin_router
from api.auth import router as auth_router
from api.billing import router as billing_router
from api.prediction import router as predicting_router

routers = APIRouter(prefix="/api")


@routers.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "I am alive"


router_list = [admin_router, auth_router, billing_router, predicting_router]

for router in router_list:
    # router.tags = routers.tags.append("v1")
    routers.include_router(router)
