from fastapi import FastAPI, Request
from typing import Type, TypeVar
from collections.abc import Callable
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.services import Service, UserService
from src.services.base import TypeRepo
from src.database.repositories import BaseRepository, UserRepository
from src.database.repositories.base import TypeModel
from src.common.cache import RedisCache
from src.core.settings import Settings

DependencyType = TypeVar("DependencyType")


def singleton(value: DependencyType) -> Callable[[], DependencyType]:
    """
    Create a FastAPI dependency that provides a single, shared instance of a value.

    Args:
        value (DependencyType): The value to be shared as a dependency.

    Returns:
        Callable[[], DependencyType]: A callable function that returns the shared value when called.

    Example:
        shared_dependency = singleton(42)
        app.dependency_overrides[MyDependency] = shared_dependency

    """

    def singleton_factory() -> DependencyType:
        return value

    return singleton_factory


def build_service(
    service: Type[Service[TypeRepo]],
    repo: Type[BaseRepository[TypeModel]],
) -> Service[TypeRepo]:
    return service(repo())


def get_mongo_db(request: Request) -> AsyncIOMotorDatabase:
    """
    Dependency to get MongoDB database from app state.
    
    Usage in endpoint:
        @app.get("/endpoint")
        async def endpoint(db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
            collection = db["my_collection"]
            ...
    """
    return request.app.state.mongo_db


def get_redis_cache(request: Request) -> RedisCache:
    """
    Dependency to get Redis cache from app state.
    
    Usage in endpoint:
        @app.get("/endpoint")
        async def endpoint(cache: RedisCache = Depends(get_redis_cache)):
            await cache.set("key", "value", ttl=3600)
            ...
    """
    return request.app.state.redis_cache


def setup_dependencies(app: FastAPI, settings: Settings) -> None:
    """
    Setup service dependencies.
    
    Note: MongoDB and Redis are initialized in lifespan (see __main__.py)
    """
    # UserService uses MongoDB from app.state.mongo_db
    app.dependency_overrides[UserService] = lambda: UserService(app.state.mongo_db)

