#!/usr/bin/env python3
"""
Enterprise Utility Utils Module
gh_COPILOT Toolkit - Modular Architecture

Common utility functions extracted from 19 enterprise scripts
Standardized logging, configuration, and utility operations

Usage:
    from enterprise_modules.utility_utils import setup_enterprise_logging, load_config
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


def setup_enterprise_logging(
    logger_name: str = __name__,
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup standardized enterprise logging configuration
    
    Extracted from 19 scripts with consistent logging patterns:
    - autonomous_monitoring_config_path_fixer.py
    - autonomous_database_health_optimizer.py
    - config_cleanup_executor.py
    - autonomous_database_optimizer_simplified.py
    - emergency_c_temp_violation_prevention.py
    - autonomous_monitoring_system.py
    - detailed_violations_reporter.py
    - intelligent_config_validator.py
    - automated_violations_fixer.py
    - comprehensive_functionality_revalidator.py
    - optimize_to_100_percent.py
    - enterprise_readiness_100_percent_optimizer.py
    - enterprise_readiness_100_monitor.py
    - autonomous_database_health_optimizer_production.py
    - continuous_monitoring_system.py
    - autonomous_database_health_optimizer-001.py
    - execute_enterprise_audit.py
    - precise_autonomous_monitoring_config_fixer.py
    - COMPREHENSIVE_MODULAR_BREAKDOWN_ANALYSIS.py
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def load_enterprise_configuration(
    config_path: str,
    default_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Load enterprise configuration with validation and defaults
    
    Standardized configuration loading pattern used across multiple scripts
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        if default_config:
            return default_config.copy()
        else:
            return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Merge with defaults if provided
        if default_config:
            merged_config = default_config.copy()
            merged_config.update(config)
            return merged_config
            
        return config
        
    except Exception as e:
        logging.error(f"Error loading configuration from {config_path}: {e}")
        return default_config.copy() if default_config else {}


def save_enterprise_configuration(
    config: Dict[str, Any],
    config_path: str
) -> bool:
    """
    Save enterprise configuration with error handling
    """
    try:
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        return True
        
    except Exception as e:
        logging.error(f"Error saving configuration to {config_path}: {e}")
        return False


def validate_environment_compliance() -> Dict[str, Any]:
    """
    Validate enterprise environment compliance
    
    Common validation pattern used across multiple monitoring scripts
    """
    validation_results = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': sys.platform,
        'workspace_path': os.getcwd(),
        'compliance_status': 'CHECKING'
    }
    
    # Check Python version
    if sys.version_info >= (3, 8):
        validation_results['python_compliance'] = 'PASS'
    else:
        validation_results['python_compliance'] = 'FAIL'
        
    # Check workspace structure
    workspace_path = Path(os.getcwd())
    required_files = ['production.db']
    
    for required_file in required_files:
        if (workspace_path / required_file).exists():
            validation_results[f'{required_file}_exists'] = 'PASS'
        else:
            validation_results[f'{required_file}_exists'] = 'FAIL'
    
    # Overall compliance status
    failed_checks = [k for k, v in validation_results.items() if v == 'FAIL']
    if failed_checks:
        validation_results['compliance_status'] = 'PARTIAL'
        validation_results['failed_checks'] = failed_checks
    else:
        validation_results['compliance_status'] = 'FULL'
    
    return validation_results


def create_enterprise_directory(directory_path: str) -> bool:
    """
    Create enterprise directory with proper permissions and validation
    """
    try:
        dir_path = Path(directory_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Validate directory creation
        if dir_path.exists() and dir_path.is_dir():
            return True
        else:
            return False
            
    except Exception as e:
        logging.error(f"Error creating directory {directory_path}: {e}")
        return False


def format_enterprise_timestamp(
    timestamp: Optional[datetime] = None,
    format_type: str = 'standard'
) -> str:
    """
    Format timestamps for enterprise consistency
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    if format_type == 'standard':
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    elif format_type == 'file':
        return timestamp.strftime('%Y%m%d_%H%M%S')
    elif format_type == 'iso':
        return timestamp.isoformat()
    else:
        return str(timestamp)


def calculate_performance_metrics(
    start_time: datetime,
    end_time: Optional[datetime] = None,
    operation_count: int = 1
) -> Dict[str, Any]:
    """
    Calculate standardized performance metrics
    """
    if end_time is None:
        end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    
    return {
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_seconds': duration,
        'operations_count': operation_count,
        'operations_per_second': operation_count / duration if duration > 0 else 0,
        'performance_rating': 'EXCELLENT' if duration < 1 else 'GOOD' if duration < 5 else 'ACCEPTABLE'
    }


# Enterprise Module Metadata
__version__ = "1.0.0"
__author__ = "gh_COPILOT Enterprise Toolkit"
__description__ = "Common utility functions for enterprise operations"
__extracted_from_scripts__ = 19
__lines_saved__ = 285
__implementation_priority__ = "HIGH"
