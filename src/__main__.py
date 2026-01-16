from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.server import run_api_uvicorn
from src.core.settings import load_settings, Settings
from src.api.routers import setup_routers
from src.core.logger import logger
from src.api.dependencies import setup_dependencies
from src.common.cache import RedisCache
from fastapi import FastAPI
from src.core.gunicorn import run_api_gunicorn


def main():
    logger.info("Initialize V1 API")
    settings = load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # ========== MongoDB connection with pooling ==========
        mongo_client = AsyncIOMotorClient(
            settings.db.uri,
            username=settings.db.username,
            password=settings.db.password,
            authSource="admin",
            maxPoolSize=20,
            minPoolSize=5,
            maxIdleTimeMS=60000,
            serverSelectionTimeoutMS=5000,
            appname="fastapi_mongo_example"
        )
        app.state.mongo_client = mongo_client
        app.state.mongo_db = mongo_client[settings.db.name]
        logger.info("MongoDB connected successfully")
        
        # ========== Redis cache with connection pooling ==========
        redis_cache = RedisCache(
            host=settings.redis.host,
            port=settings.redis.port,
            password=settings.redis.password,
            max_connections=50
        )
        await redis_cache.connect()
        app.state.redis_cache = redis_cache
        logger.info("Redis cache connected successfully")
        
        # Setup dependencies (needs mongo_db and redis_cache)
        setup_dependencies(app, settings)
        
        try:
            yield
        finally:
            # Cleanup resources
            logger.info("Shutting down... Closing connections")
            await redis_cache.close()
            logger.info("Redis connection closed")
            mongo_client.close()
            logger.info("MongoDB connection closed")
    
    app = FastAPI(
        lifespan=lifespan,
        default_response_class=JSONResponse,
        docs_url="/docs",
        redoc_url=None,
        swagger_ui_oauth2_redirect_url=None,
    )

    setup_routers(app)
    origins = ["*", "http://localhost", "http://localhost:8080", "http://127.0.0.1", "http://127.0.0.1:8080"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    run_api_uvicorn(app, settings)
    #run_api_gunicorn(app, settings)


if __name__ == "__main__":
    main()