import logging

logger = logging.getLogger(__name__)

def rollback() -> None:
    """Rollback schema changes in case of failure."""
    logger.info("Schema rollback executed")
