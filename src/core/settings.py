import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Final, Union
from pydantic import Field
from enum import StrEnum



#def load_env_if_not_docker():
if not os.environ.get("DOCKER_CONTAINER"):
    load_dotenv(find_dotenv(raise_error_if_not_found=True))
    BASE_WEB_HOOK_URL = os.environ.get("BASE_WEB_HOOK_URL")
else:
    BASE_WEB_HOOK_URL = os.getenv("BASE_WEB_HOOK_URL_PROD")

#load_env_if_not_docker()


_PathLike = Union[os.PathLike[str], str, Path]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PROJECT_NAME = os.getenv("PROJECT_NAME", "")
PROJECT_VERSION = os.getenv("PROJECT_VERSION", "")

LOGGING_FORMAT: Final[str] = "%(asctime)s %(name)s %(levelname)s -> %(message)s"
DATETIME_FORMAT: Final[str] = "%Y.%m.%d %H:%M"

def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent


class Environment(StrEnum):
    PROD = "prod"
    DEV = "dev"


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="SERVER_",
        extra="ignore",
    )
    methods: List[str] = ["*"]
    headers: List[str] = ["*"]
    origins: List[str] = ["*"]
    host: str = "127.0.0.1"
    port: int = 8080


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="DB_",
        extra="ignore",
    )

    uri: str = Field(default="")
    name: str = Field(default="")
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_pool_size: int = 10
    connection_max_overflow: int = 90
    connection_pool_pre_ping: bool = True

    @property
    def url(self) -> str:
        if "sqlite" in self.uri:
            return self.uri.format(self.name)
        return self.uri.format(
            self.user,
            self.password,
            self.host,
            self.port,
            self.name,
        )


class RedisSettings(BaseSettings):
    """
    Redis settings for caching.
    
    All parameters are loaded from environment variables with REDIS_ prefix.
    Example: REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
    """
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="REDIS_",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 6379
    password: Optional[str] = None


class Settings(BaseSettings):
    server: ServerSettings
    db: DatabaseSettings
    redis: RedisSettings


def load_settings(
        server: Optional[ServerSettings] = None,
        db: Optional[DatabaseSettings] = None,
        redis: Optional[RedisSettings] = None
) -> Settings:
    return Settings(
        server=server or ServerSettings(),
        db=db or DatabaseSettings(),
        redis=redis or RedisSettings()
    )
