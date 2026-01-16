from typing import Optional
from src.database.repositories import BaseRepository
import src.database.models as models



class UserRepository(BaseRepository[models.UserConfig]):
    model = models.UserConfig
    collection_name = 'users'

    async def get_by_client_id(self, client: str) -> Optional[models.UserConfig]:
        result = await self._crud.select({"client_id": client})
        return result

    async def create(self, user: models.UserConfig) -> models.UserConfig:
        result = await self._crud.create(**user.model_dump(exclude_none=True))
        return result





