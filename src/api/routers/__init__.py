from fastapi import APIRouter, FastAPI
from src.api.routers.user import user_router


router = APIRouter()
router.include_router(user_router)


def setup_routers(app: FastAPI):
    app.include_router(router)