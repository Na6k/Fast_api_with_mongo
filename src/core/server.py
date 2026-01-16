import uvicorn
from typing import Any
from src.core.settings import Settings
from src.core.logger import logger, LOG_LEVEL


def run_api_uvicorn(app:Any, config: Settings, **kwargs: Any) -> Any:
    uv_config = uvicorn.Config(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level=LOG_LEVEL.lower(),
        server_header=False,
        **kwargs,
    )
    server = uvicorn.Server(uv_config)
    logger.info("Running uvicorn server")
    server.run()