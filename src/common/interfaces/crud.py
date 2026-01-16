import abc
from collections.abc import Mapping, Sequence
from typing import (
    Any,
    Generic,
    Optional,
    Type,
    TypeVar,
)

from src.common.interfaces.repository import Repository


EntryType = TypeVar("EntryType", bound=Mapping[str, Any])
QueryType = TypeVar("QueryType", bound=Mapping[str, Any])


class AbstractMongoCRUDRepository(Repository, Generic[EntryType, QueryType]):

    model: Type[EntryType]

    def __init__(self, model: Type[EntryType]) -> None:

        self.model = model

    @abc.abstractmethod
    async def create(self, **values: Mapping[str, Any]) -> Optional[EntryType]:

        raise NotImplementedError

    @abc.abstractmethod
    async def create_many(self, data: Sequence[Mapping[str, Any]]) -> Sequence[EntryType]:

        raise NotImplementedError

    @abc.abstractmethod
    async def select(self, query: QueryType) -> Optional[EntryType]:

        raise NotImplementedError

    @abc.abstractmethod
    async def select_many(
        self, query: QueryType, offset: Optional[int], limit: Optional[int]
    ) -> Sequence[EntryType]:

        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, query: QueryType, update: Mapping[str, Any]) -> Sequence[EntryType]:

        raise NotImplementedError

    @abc.abstractmethod
    async def update_many(self, data: Sequence[Mapping[str, Any]]) -> Any:

        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, query: QueryType) -> Sequence[EntryType]:

        raise NotImplementedError

    @abc.abstractmethod
    async def exists(self, query: QueryType) -> bool:

        raise NotImplementedError

    @abc.abstractmethod
    async def count(self, query: QueryType) -> int:

        raise NotImplementedError
