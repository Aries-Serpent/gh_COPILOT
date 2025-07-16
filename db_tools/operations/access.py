"""
Database access layer operations.
Refactored from original database_access_layer.py with enhanced functionality.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.connection import DatabaseConnection
from ..core.exceptions import DatabaseError


# Text-based indicators (NO Unicode emojis)
TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'database': '[DATABASE]',
    'info': '[INFO]'
}


class DatabaseAccessLayer:
    """Enterprise database access layer with enhanced functionality"""

    def __init__(self, database_path: str = "production.db"):
        self.database_path = Path(database_path)
        self.db_connection = DatabaseConnection(self.database_path)
        self.logger = logging.getLogger(__name__)

    def execute_processing(self) -> bool:
        """Execute database processing with enhanced error handling"""
        start_time = datetime.now()
        self.logger.info(f"{TEXT_INDICATORS['start']} Processing started: {start_time}")

        try:
            # Process database operations using unified connection
            success = self.process_operations()

            if success:
                self.logger.info(f"{TEXT_INDICATORS['success']} Database processing completed")
                return True
            else:
                self.logger.error(f"{TEXT_INDICATORS['error']} Database processing failed")
                return False

        except DatabaseError as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Database error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Unexpected error: {e}")
            return False

    def process_operations(self) -> bool:
        """Process database operations using unified connection"""
        try:
            # Example operations - can be extended based on specific needs
            tables_info = self.get_tables_info()
            self.logger.info(f"{TEXT_INDICATORS['info']} Found {len(tables_info)} tables")
            
            return True
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Operation failed: {e}")
            return False
            
    def get_tables_info(self) -> Dict[str, Any]:
        """Get information about all tables in the database"""
        try:
            query = """
                SELECT name, type, sql 
                FROM sqlite_master 
                WHERE type='table'
                ORDER BY name
            """
            results = self.db_connection.execute_query(query)
            return {row['name']: {'type': row['type'], 'sql': row['sql']} for row in results}
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Failed to get tables info: {e}")
            return {}
            
    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a specific table"""
        try:
            if not self.db_connection.table_exists(table_name):
                return 0
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = self.db_connection.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Failed to count rows in {table_name}: {e}")
            return 0


def main():
    """Main execution function - maintains backward compatibility"""
    processor = DatabaseAccessLayer()
    success = processor.execute_processing()

    if success:
        print(f"{TEXT_INDICATORS['success']} Database processing completed")
    else:
        print(f"{TEXT_INDICATORS['error']} Database processing failed")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)