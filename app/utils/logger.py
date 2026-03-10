from loguru import logger

logger.add(
    "reconciliation.log",
    rotation="10 MB",
    level="INFO"
)

def get_logger():
    return logger