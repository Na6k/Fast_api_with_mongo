from collections.abc import Mapping, Sequence
from typing import (
    Any,
    Optional,
    Type,
    TypeVar,
)

from motor.core import AgnosticDatabase

from src.common.interfaces import AbstractMongoCRUDRepository


DocumentType = TypeVar("DocumentType", bound=Mapping[str, Any])


class MongoDBCRUDRepository(AbstractMongoCRUDRepository[DocumentType, dict]):

    def __init__(self, db: AgnosticDatabase, collection_name: str, model: Type[DocumentType]) -> None:
        super().__init__(model)
        self._db = db
        self._collection_name = collection_name
        self._collection = self._db[self._collection_name]  # Cache the collection object

    async def create(self, **values: Any) -> Optional[DocumentType]:

        result = await self._collection.insert_one(values)
        if result.inserted_id:
            # Retrieve the newly created document
            document = await self.select({"_id": result.inserted_id})
            document["_id"] = str(document["_id"])
            return document

        return None

    async def create_many(self, data: Sequence[Mapping[str, Any]]) -> Sequence[DocumentType]:

        result = await self._collection.insert_many(data)
        return await self.select_many({"_id": {"$in": result.inserted_ids}})

    async def select(self, query: dict) -> Optional[DocumentType]:
        document = await self._collection.find_one(query)
        if document:
            document["_id"] = str(document["_id"])
            return document
        return None

    async def select_many(
        self, query: dict, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> Sequence[DocumentType]:


        cursor = self._collection.find(query)
        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        documents = await cursor.to_list(length=None) # Fetch all documents within the limit/offset
        return documents

    async def update(self, query: dict, update: dict) -> Sequence[DocumentType]:


        result = await self._collection.update_one(query, {"$set": update})
        return await self.select(query)


    async def update_many(self, data: Sequence[Mapping[str, Any]]) -> Any:

        modified_count = 0
        for item in data:
            query = item.get("query")
            update = item.get("update")
            if query and update:
                result = await self._collection.update_many(query, {"$set": update})
                modified_count += result.modified_count
        return modified_count  # Return the total number of modified documents


    async def delete(self, query: dict) -> Sequence[DocumentType]:


        # MongoDB doesn't directly return the deleted documents. We fetch them before deleting.
        deleted_documents = await self.select_many(query)
        result = await self._collection.delete_many(query)
        return deleted_documents

    async def exists(self, query: dict) -> bool:

        count = await self._collection.count_documents(query, limit=1)
        return count > 0

    async def count(self, query: dict) -> int:

        return await self._collection.count_documents(query)

    def with_query_model(self, model: Type[DocumentType]) -> "MongoDBCRUDRepository[DocumentType]":

        return MongoDBCRUDRepository(self._db, self._collection_name, model)
