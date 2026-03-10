from loguru import logger
import os

LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)

logger.add(
    f"{LOG_DIR}/reconciliation.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO"
)

logger.add(
    f"{LOG_DIR}/errors.log",
    rotation="5 MB",
    level="ERROR"
)

logger.add(
    f"{LOG_DIR}/system_upgrade.log",
    rotation="5 MB",
    level="INFO"
)


def get_logger():
    return logger


def log_success(message: str):
    logger.info(f"SUCCESS: {message}")


def log_failure(message: str):
    logger.error(f"FAILURE: {message}")


def log_upgrade(message: str):
    logger.info(f"UPGRADE: {message}")