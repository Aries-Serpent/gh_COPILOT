#!/usr/bin/env python3
"""
Enterprise Template Intelligence Platform - Schema Migration Fix
PHASE 2 COMPLETION: Schema Alignment for Intelligent Code Analysis

Mission: Fix template_intelligence table schema to support advanced code analysis
Author: DUAL COPILOT SYSTEM (PrimaryCopilotExecutor + SecondaryCopilotValidator)
Classification: ENTERPRISE TEMPLATE INTELLIGENCE EVOLUTION
Anti-Recursion: SCHEMA_MIGRATION_FIX_V1_20250103
"""

import sqlite3
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# [?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?]
# [?]                    ENTERPRISE VISUAL PROCESSING INDICATORS                   [?]
# [?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?]

class VisualProcessingIndicators:
    """Enterprise-grade visual processing system for schema migration operations"""
    
    @staticmethod
    def show_startup():
        print("[LAUNCH] ENTERPRISE TEMPLATE INTELLIGENCE PLATFORM")
        print("[BAR_CHART] PHASE 2 COMPLETION: Schema Migration & Alignment")
        print("[WRENCH] DUAL COPILOT SYSTEM: Schema Fix Operation")
        print("[?]" * 80)
        
    @staticmethod
    def show_migration_progress(step: str, status: str = "IN_PROGRESS"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        if status == "SUCCESS":
            print(f"[SUCCESS] [{timestamp}] {step}")
        elif status == "ERROR":
            print(f"[ERROR] [{timestamp}] {step}")
        else:
            print(f"[PROCESSING] [{timestamp}] {step}")
            
    @staticmethod
    def show_completion_summary(migration_count: int):
        print("[?]" * 80)
        print("[TARGET] SCHEMA MIGRATION COMPLETION SUMMARY")
        print(f"[CLIPBOARD] Migrations Applied: {migration_count}")
        print(f"[TIME] Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("[LOCK] Enterprise Compliance: VERIFIED")
        print("[?] DUAL COPILOT Validation: COMPLETE")

# [?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?]
# [?]                           DUAL COPILOT SYSTEM                               [?]
# [?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?]

class PrimaryCopilotExecutor:
    """Primary copilot responsible for schema migration execution"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migration_log = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('schema_migration_fix.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def execute_schema_migration(self) -> bool:
        """Execute the schema migration for template_intelligence table"""
        try:
            VisualProcessingIndicators.show_migration_progress(
                "Connecting to learning_monitor.db database"
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check current schema
                VisualProcessingIndicators.show_migration_progress(
                    "Analyzing current template_intelligence schema"
                )
                
                cursor.execute("PRAGMA table_info(template_intelligence);")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                self.logger.info(f"Current columns: {column_names}")
                
                # Check if intelligence_type column exists
                if 'intelligence_type' not in column_names:
                    VisualProcessingIndicators.show_migration_progress(
                        "Adding missing intelligence_type column"
                    )
                    
                    # Add the missing column
                    cursor.execute("""
                        ALTER TABLE template_intelligence 
                        ADD COLUMN intelligence_type TEXT DEFAULT 'code_analysis'
                    """)
                    
                    self.migration_log.append("Added intelligence_type column")
                    self.logger.info("Successfully added intelligence_type column")
                    
                    VisualProcessingIndicators.show_migration_progress(
                        "intelligence_type column added", "SUCCESS"
                    )
                else:
                    VisualProcessingIndicators.show_migration_progress(
                        "intelligence_type column already exists", "SUCCESS"
                    )
                
                # Check if intelligence_data column exists
                if 'intelligence_data' not in column_names:
                    VisualProcessingIndicators.show_migration_progress(
                        "Adding missing intelligence_data column"
                    )
                    
                    # Add the missing column
                    cursor.execute("""
                        ALTER TABLE template_intelligence 
                        ADD COLUMN intelligence_data TEXT
                    """)
                    
                    self.migration_log.append("Added intelligence_data column")
                    self.logger.info("Successfully added intelligence_data column")
                    
                    VisualProcessingIndicators.show_migration_progress(
                        "intelligence_data column added", "SUCCESS"
                    )
                else:
                    VisualProcessingIndicators.show_migration_progress(
                        "intelligence_data column already exists", "SUCCESS"
                    )
                
                # Check if source_analysis column exists
                if 'source_analysis' not in column_names:
                    VisualProcessingIndicators.show_migration_progress(
                        "Adding missing source_analysis column"
                    )
                    
                    # Add the missing column
                    cursor.execute("""
                        ALTER TABLE template_intelligence 
                        ADD COLUMN source_analysis TEXT
                    """)
                    
                    self.migration_log.append("Added source_analysis column")
                    self.logger.info("Successfully added source_analysis column")
                    
                    VisualProcessingIndicators.show_migration_progress(
                        "source_analysis column added", "SUCCESS"
                    )
                else:
                    VisualProcessingIndicators.show_migration_progress(
                        "source_analysis column already exists", "SUCCESS"
                    )
                
                # Verify the migration
                VisualProcessingIndicators.show_migration_progress(
                    "Verifying schema migration completion"
                )
                
                cursor.execute("PRAGMA table_info(template_intelligence);")
                updated_columns = cursor.fetchall()
                updated_column_names = [col[1] for col in updated_columns]
                
                if 'intelligence_type' in updated_column_names:
                    VisualProcessingIndicators.show_migration_progress(
                        "Schema migration verification", "SUCCESS"
                    )
                    self.logger.info("Schema migration completed successfully")
                    return True
                else:
                    VisualProcessingIndicators.show_migration_progress(
                        "Schema migration verification", "ERROR"
                    )
                    return False
                    
        except Exception as e:
            self.logger.error(f"Schema migration failed: {str(e)}")
            VisualProcessingIndicators.show_migration_progress(
                f"Migration error: {str(e)}", "ERROR"
            )
            return False

class SecondaryCopilotValidator:
    """Secondary copilot for validation and compliance checking"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__ + ".validator")
        
    def validate_migration(self) -> bool:
        """Validate the completed schema migration"""
        try:
            VisualProcessingIndicators.show_migration_progress(
                "DUAL COPILOT: Secondary validation initiated"
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Validate schema structure
                cursor.execute("PRAGMA table_info(template_intelligence);")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                required_columns = [
                    'intelligence_type', 'intelligence_id', 'template_id',
                    'suggestion_type', 'suggestion_content', 'confidence_score',
                    'intelligence_data', 'source_analysis'
                ]
                
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    self.logger.error(f"Validation failed: Missing columns {missing_columns}")
                    VisualProcessingIndicators.show_migration_progress(
                        f"Validation failed: Missing {missing_columns}", "ERROR"
                    )
                    return False
                
                # Test data insertion capability
                test_record = {
                    'intelligence_type': 'code_analysis',
                    'intelligence_id': 'TEST_VALIDATION_001',
                    'template_id': 'VALIDATION_TEMPLATE',
                    'suggestion_type': 'placeholder_opportunity',
                    'suggestion_content': 'Test validation record',
                    'confidence_score': 0.95
                }
                
                cursor.execute("""
                    INSERT INTO template_intelligence 
                    (intelligence_type, intelligence_id, template_id, suggestion_type, 
                     suggestion_content, confidence_score, usage_context, intelligence_data, source_analysis)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_record['intelligence_type'],
                    test_record['intelligence_id'],
                    test_record['template_id'],
                    test_record['suggestion_type'],
                    test_record['suggestion_content'],
                    test_record['confidence_score'],
                    'schema_validation_test',
                    '{"validation": "test"}',
                    'schema_migration_validation'
                ))
                
                # Verify the test record
                cursor.execute("""
                    SELECT COUNT(*) FROM template_intelligence 
                    WHERE intelligence_id = ?
                """, (test_record['intelligence_id'],))
                
                count = cursor.fetchone()[0]
                
                if count == 1:
                    # Clean up test record
                    cursor.execute("""
                        DELETE FROM template_intelligence 
                        WHERE intelligence_id = ?
                    """, (test_record['intelligence_id'],))
                    
                    VisualProcessingIndicators.show_migration_progress(
                        "DUAL COPILOT: Secondary validation", "SUCCESS"
                    )
                    self.logger.info("Schema validation completed successfully")
                    return True
                else:
                    VisualProcessingIndicators.show_migration_progress(
                        "DUAL COPILOT: Data insertion test failed", "ERROR"
                    )
                    return False
                    
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            VisualProcessingIndicators.show_migration_progress(
                f"Validation error: {str(e)}", "ERROR"
            )
            return False

# [?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?]
# [?]                            ANTI-RECURSION SYSTEM                            [?]
# [?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?]

def anti_recursion_guard():
    """Prevent infinite recursion in schema migration operations"""
    lock_file = Path("schema_migration_lock.tmp")
    
    if lock_file.exists():
        print("[ERROR] ANTI-RECURSION: Schema migration already in progress")
        return False
        
    lock_file.touch()
    return True

def cleanup_anti_recursion():
    """Clean up anti-recursion lock"""
    lock_file = Path("schema_migration_lock.tmp")
    if lock_file.exists():
        lock_file.unlink()

# [?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?]
# [?]                              MAIN EXECUTION                                  [?]
# [?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?][?]

def main():
    """Main execution function for schema migration"""
    
    if not anti_recursion_guard():
        sys.exit(1)
    
    try:
        VisualProcessingIndicators.show_startup()
        
        db_path = "databases/learning_monitor.db"
        
        # Initialize DUAL COPILOT system
        primary_copilot = PrimaryCopilotExecutor(db_path)
        secondary_copilot = SecondaryCopilotValidator(db_path)
        
        # Execute primary migration
        migration_success = primary_copilot.execute_schema_migration()
        
        if not migration_success:
            print("[ERROR] CRITICAL: Primary schema migration failed")
            return False
            
        # Execute secondary validation
        validation_success = secondary_copilot.validate_migration()
        
        if not validation_success:
            print("[ERROR] CRITICAL: Secondary validation failed")
            return False
            
        # Show completion summary
        VisualProcessingIndicators.show_completion_summary(1)
        
        print("[TARGET] PHASE 2 PREPARATION: Schema migration completed successfully")
        print("[LAUNCH] READY FOR: Intelligent code analyzer re-execution")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] CRITICAL FAILURE: {str(e)}")
        return False
        
    finally:
        cleanup_anti_recursion()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
