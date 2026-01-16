from fastapi import APIRouter, Depends, status
from src.database.models import UserConfig
from typing import Annotated
from src.services.user import UserService
from src.api.providers import Stub
from pydantic import BaseModel
from src.api.dto import UserDTO


user_router = APIRouter(prefix="/user", tags=["User"])

class UserBody(BaseModel):
    client_id:str


@user_router.get("/{client_id}", response_model=UserConfig, status_code=status.HTTP_200_OK)
async def get_user(
        client_id: str,
        service: Annotated[UserService, Depends(Stub(UserService))],
) -> UserConfig:
    user = await service.get_user(client_id)
    return user


@user_router.post("/create", response_model=UserConfig, status_code=status.HTTP_200_OK)
async def create_user(
        body: UserDTO,
        service: Annotated[UserService, Depends(Stub(UserService))],
) -> UserConfig:
    new_user = await service.create(body)
    return new_user