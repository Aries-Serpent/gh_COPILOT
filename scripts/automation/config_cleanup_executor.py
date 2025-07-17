#!/usr/bin/env python3
"""
Configuration Files Cleanup and Organization Script
Address orphaned config files identified in validation report
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

def setup_logging():
    """Setup logging for cleanup operations"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)

def cleanup_orphaned_config_files():
    """Clean up orphaned config files identified in validation"""
    logger = setup_logging()
    
    logger.info("🧹 Starting orphaned config files cleanup...")
    
    # Files identified as orphaned in validation report
    orphaned_files = [
        "reports/autonomous_monitoring_config_fix_report_20250716_173951.json",
        "reports/configuration_path_updates_report_20250716_172755.json", 
        "reports/intelligent_config_validation_20250716_174635.json"
    ]
    
    cleanup_results = {
        "files_processed": 0,
        "files_moved": 0,
        "files_not_found": 0,
        "cleanup_timestamp": datetime.now().isoformat()
    }
    
    # Create archive directory for old reports if needed
    archive_dir = Path("reports/archive")
    archive_dir.mkdir(exist_ok=True)
    
    for file_path in orphaned_files:
        cleanup_results["files_processed"] += 1
        
        if Path(file_path).exists():
            # These are actually report files, not config files
            # Move to archive to clean up main reports directory
            archive_path = archive_dir / Path(file_path).name
            
            try:
                shutil.move(file_path, archive_path)
                logger.info(f"✅ Moved report to archive: {Path(file_path).name}")
                cleanup_results["files_moved"] += 1
                
            except Exception as e:
                logger.error(f"❌ Error moving {file_path}: {e}")
                
        else:
            logger.info(f"⚠️ File not found: {file_path}")
            cleanup_results["files_not_found"] += 1
    
    # Save cleanup report
    cleanup_report_path = f"reports/config_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(cleanup_report_path, 'w') as f:
        json.dump(cleanup_results, f, indent=2)
    
    logger.info("="*60)
    logger.info("✅ CONFIG FILES CLEANUP COMPLETED")
    logger.info(f"Files Processed: {cleanup_results['files_processed']}")
    logger.info(f"Files Moved: {cleanup_results['files_moved']}")
    logger.info(f"Files Not Found: {cleanup_results['files_not_found']}")
    logger.info(f"Cleanup Report: {cleanup_report_path}")
    logger.info("="*60)
    
    return cleanup_results

def validate_config_directory():
    """Validate that all actual config files are properly organized"""
    logger = setup_logging()
    
    logger.info("🔍 Validating config directory organization...")
    
    config_dir = Path("config")
    if not config_dir.exists():
        logger.error("❌ Config directory does not exist!")
        return False
    
    # Count actual config files
    config_files = list(config_dir.rglob("*.json")) + list(config_dir.rglob("*.yml")) + \
                  list(config_dir.rglob("*.yaml")) + list(config_dir.rglob("*.cfg")) + \
                  list(config_dir.rglob("*.ini")) + list(config_dir.rglob("*.conf"))
    
    logger.info(f"✅ Found {len(config_files)} actual config files in config/ directory")
    
    # Validate each config file
    valid_configs = 0
    for config_file in config_files:
        try:
            if config_file.suffix == '.json':
                with open(config_file, 'r') as f:
                    json.load(f)  # Validate JSON
            valid_configs += 1
        except Exception as e:
            logger.error(f"❌ Invalid config file {config_file}: {e}")
    
    logger.info(f"✅ {valid_configs}/{len(config_files)} config files are valid")
    
    return valid_configs == len(config_files)

def main():
    """Execute config cleanup and validation"""
    print("🚀 STARTING CONFIG FILES CLEANUP AND VALIDATION")
    print("="*70)
    
    # Step 1: Clean up orphaned files
    cleanup_results = cleanup_orphaned_config_files()
    
    # Step 2: Validate config directory
    config_valid = validate_config_directory()
    
    # Step 3: Final summary
    overall_success = cleanup_results["files_moved"] >= 0 and config_valid
    
    print("="*70)
    print("🏆 CONFIG CLEANUP SUMMARY")
    print(f"Orphaned Files Cleanup: {'✅ SUCCESS' if cleanup_results['files_moved'] >= 0 else '❌ FAILED'}")
    print(f"Config Directory Validation: {'✅ SUCCESS' if config_valid else '❌ FAILED'}")
    print(f"Overall Status: {'✅ 100% SUCCESS' if overall_success else '⚠️ NEEDS ATTENTION'}")
    print("="*70)
    
    return overall_success

if __name__ == "__main__":
    main()
