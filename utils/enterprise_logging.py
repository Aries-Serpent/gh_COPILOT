#!/usr/bin/env python3
"""Enterprise Logging Configuration System
Prevents import-time logging conflicts and provides centralized logging management
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class EnterpriseLoggingManager:
    """🎯 Enterprise Logging Management System"""

    _logging_configured = False
    _default_config = {
        'level': logging.INFO,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'date_format': '%Y-%m-%d %H:%M:%S'
    }

    @classmethod
    def setup_logging(
        cls,
        level: Optional[int] = None,
        log_file: Optional[str] = None,
        console_output: bool = True,
        force_reconfigure: bool = False
    ) -> Dict[str, Any]:
        """🎯 Setup enterprise logging configuration"""

        if cls._logging_configured and not force_reconfigure:
            return {
                "status": "ALREADY_CONFIGURED",
                "configuration": cls._default_config
            }

        if force_reconfigure:
            logging.getLogger().handlers.clear()

        log_level = level or cls._default_config['level']

        formatter = logging.Formatter(
            fmt=cls._default_config['format'],
            datefmt=cls._default_config['date_format']
        )

        handlers = []

        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            handlers.append(console_handler)

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)

        logging.basicConfig(level=log_level, handlers=handlers, force=force_reconfigure)

        cls._logging_configured = True

        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("🎯 ENTERPRISE LOGGING CONFIGURED")
        logger.info(f"Level: {logging.getLevelName(log_level)}")
        logger.info(f"Handlers: {len(handlers)}")
        logger.info(f"Console Output: {console_output}")
        logger.info(f"Log File: {log_file or 'None'}")
        logger.info("=" * 60)

        return {
            "status": "CONFIGURED",
            "level": log_level,
            "handlers_count": len(handlers),
            "log_file": log_file,
            "console_output": console_output,
        }

    @classmethod
    def get_module_logger(cls, module_name: str) -> logging.Logger:
        """🎯 Get configured logger for specific module"""
        if not cls._logging_configured:
            cls.setup_logging()
        return logging.getLogger(module_name)

    @classmethod
    def setup_module_logging(
        cls,
        module_name: str,
        log_file: Optional[str] = None
    ) -> logging.Logger:
        """🎯 Setup logging for specific module without conflicts"""

        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"logs/{module_name}_{timestamp}.log"

        if not cls._logging_configured:
            cls.setup_logging(log_file=log_file)

        return cls.get_module_logger(module_name)


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    module_name: Optional[str] = None
) -> logging.Logger:
    """🎯 Setup logging with enterprise compliance"""

    if module_name:
        return EnterpriseLoggingManager.setup_module_logging(module_name, log_file)
    else:
        EnterpriseLoggingManager.setup_logging(level=level, log_file=log_file)
        return logging.getLogger(__name__)
