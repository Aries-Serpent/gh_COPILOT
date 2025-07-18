import logging
from pathlib import Path

from utils.enterprise_logging import EnterpriseLoggingManager


def test_log_file_not_empty(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    EnterpriseLoggingManager.setup_logging(
        log_file=str(log_file), force_reconfigure=True
    )
    logger = logging.getLogger("test")
    logger.info("hello")
    logging.shutdown()
    assert log_file.exists()
    assert log_file.stat().st_size > 0
