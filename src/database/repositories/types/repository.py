from typing import  Protocol, TypeVar, Any, Type

RepositoryType = TypeVar("RepositoryType", bound="Repository")


class Repository(Protocol):
    """
    A protocol representing a MongoDB Repository.

    This protocol defines the basic contract for all MongoDB repositories implementations.
    The exact type of the database core is not specified in the protocol,
    allowing for flexibility in the underlying database library used (e.g., motor, pymongo).
    """
    model: Type[Any]
    collection_name: str

