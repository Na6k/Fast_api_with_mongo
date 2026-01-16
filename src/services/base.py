from abc import ABC
from typing import Generic, TypeVar
from src.common.interfaces.repository import Repository


TypeRepo = TypeVar("TypeRepo", bound=Repository, covariant=True)


class Service(ABC, Generic[TypeRepo]):
    def __init__(self, repository: TypeRepo) -> None:
        self._repo = repository