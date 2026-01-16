import logging

from src.core.settings import LOG_LEVEL, PROJECT_NAME, PROJECT_VERSION, LOGGING_FORMAT, DATETIME_FORMAT

logging.basicConfig(level=LOG_LEVEL, format=LOGGING_FORMAT, datefmt=DATETIME_FORMAT)

logger = logging.getLogger(PROJECT_NAME)