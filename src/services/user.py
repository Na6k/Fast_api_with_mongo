from src.services import Service
from src.database.repositories.user import UserRepository



class UserService(Service[UserRepository]):

    def __init__(self, db):
        self._repo = UserRepository(db)

    async def get_user(self, user_id):
        result = await self._repo.get_by_client_id(user_id)
        return result

    async def create(self, user):
        result = await self._repo.create(user)
        return result
