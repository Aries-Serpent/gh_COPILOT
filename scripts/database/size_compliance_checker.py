#!/usr/bin/env python3
"""
Size Compliance Checker with enterprise logging.

Databases larger than 99.9 MB are considered non-compliant by default.
"""

from pathlib import Path

from utils.enterprise_logging import EnterpriseLoggingManager

logger = None


def setup_logging() -> None:
    """Configure the module logger on first use."""
    global logger
    if logger is None:
        logger = EnterpriseLoggingManager.setup_module_logging(
            module_name="size_compliance_checker",
            log_file="logs/size_compliance_checker.log",
        )


def check_database_sizes(databases_dir: Path, threshold_mb: float = 99.9) -> bool:
    """Check sizes of ``.db`` files in ``databases_dir``.

    Returns ``True`` if all databases are within ``threshold_mb`` megabytes,
    otherwise ``False``.
    """
    setup_logging()
    if not databases_dir.exists():
        logger.error(f"Database directory not found: {databases_dir}")
        return True

    exceeded = False
    for db_file in databases_dir.rglob("*.db"):
        size_mb = db_file.stat().st_size / (1024 * 1024)
        if size_mb > threshold_mb:
            logger.warning(f"⚠️ {db_file.name}: {size_mb:.2f} MB > {threshold_mb} MB")
            exceeded = True
        else:
            logger.info(f"✅ {db_file.name}: {size_mb:.2f} MB")
    return not exceeded


def main(databases_dir: Path | None = None) -> bool:
    """Run a size check on ``databases_dir`` or ``<workspace>/databases``."""
    EnterpriseLoggingManager.setup_logging(
        log_file="logs/size_compliance_main.log",
        console_output=True,
    )
    if databases_dir is None:
        workspace_path = Path.cwd()
        databases_dir = workspace_path / "databases"
    return check_database_sizes(databases_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check database size compliance")
    parser.add_argument("--path", type=Path, help="Optional path to the databases directory")
    args = parser.parse_args()
    main(args.path)
