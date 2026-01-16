from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import TypeAlias, Any
from collections.abc import AsyncIterable


MongoClientType: TypeAlias = AsyncIOMotorClient


def async_mongo_client(uri: str, **kwargs: Any) -> MongoClientType:
    """
    Create an asynchronous MongoDB client with connection pooling.

    Args:
        uri (str): The MongoDB connection URL.
        **kwargs: Additional keyword arguments to pass to AsyncIOMotorClient.

    Returns:
        MongoClientType: An asynchronous MongoDB client.
    """
    # Default connection pooling parameters
    default_kwargs = {
        'maxPoolSize': 20,
        'minPoolSize': 5,
        'maxIdleTimeMS': 60000,
        'serverSelectionTimeoutMS': 5000,
    }
    # Merge with user parameters (user parameters take precedence)
    merged_kwargs = {**default_kwargs, **kwargs}
    
    return AsyncIOMotorClient(host=uri, **merged_kwargs)


async def async_mongo_db(
    client: MongoClientType, db_name: str
) -> AsyncIterable[AsyncIOMotorDatabase]:
    """
    Create an asynchronous MongoDB database context.

    Args:
        client (MongoClientType): An asynchronous MongoDB client.
        db_name (str): The name of the database.

    Yields:
        AsyncIOMotorDatabase: An asynchronous MongoDB database.
    """
    async with client:
        db = client[db_name]
        yield db



