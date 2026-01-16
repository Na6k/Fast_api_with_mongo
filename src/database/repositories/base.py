from typing import Generic, TypeVar, Type

from src.database.models.base import Base
from src.database.repositories.crud import MongoDBCRUDRepository
from src.database.repositories.types.repository import Repository
from src.database.core.connection import MongoDBConnection
from motor.core import AgnosticDatabase

TypeModel = TypeVar("TypeModel", bound=Base)

class BaseRepository(Repository, Generic[TypeModel]):

    def __init__(self, db: AgnosticDatabase) -> None:
        self._db = db
        self._crud = MongoDBCRUDRepository(self._db, self.collection_name, self.model)
