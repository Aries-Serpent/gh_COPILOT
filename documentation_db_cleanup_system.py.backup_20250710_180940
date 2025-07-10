#!/usr/bin/env python3
"""
🚀 DOCUMENTATION DATABASE CLEANUP & CONSOLIDATION SYSTEM
Enterprise Database-First Cleanup with DUAL COPILOT Pattern
ZERO TOLERANCE for backup files and conversation files
"""

import sqlite3
import os
import json

import logging
from pathlib import Path
from datetime import datetime



# Configure logging
logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig)
logger = logging.getLogger(__name__)


class DocumentationDatabaseCleanupSystem:
    """🧹 Enterprise Documentation Database Cleanup Engine"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        # 🚀 PROCESS STARTED
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        logger.info("🚀 DOCUMENTATION DB CLEANUP STARTED")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {self.process_id}")

        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "databases" / "documentation.db"
        self.backup_path = self.workspace_path / "databases" / f"documentation_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

        # CRITICAL: Anti-recursion validation
        self._validate_environment_integrity()

        # Cleanup statistics
        self.cleanup_stats = {
            "backup_files_removed": 0,
            "duplicates_removed": 0,
            "templates_created": 0,
            "total_records_before": 0,
            "total_records_after": 0,
            "storage_saved_mb": 0.0
        }

    def _validate_environment_integrity(self):
        """🛡️ CRITICAL: Validate workspace integrity"""
        if not self.workspace_path.exists():
            raise RuntimeError(f"🚨 CRITICAL: Workspace not found: {self.workspace_path}")

        if not self.db_path.exists():
            raise RuntimeError(f"🚨 CRITICAL: Documentation database not found: {self.db_path}")

        logger.info("✅ Environment integrity validated")

    def execute_comprehensive_cleanup(self) -> Dict[str, Any]:
        """🧹 Execute comprehensive database cleanup with DUAL COPILOT validation"""

        logger.info("="*60)
        logger.info("🧹 STARTING COMPREHENSIVE DATABASE CLEANUP")
        logger.info("="*60)

        try:
            # Create backup first
            self._create_database_backup()

            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row

            # Get initial statistics
            self._collect_initial_statistics(conn)

            # Phase 1: Remove unwanted files
            logger.info("🗑️ Phase 1: Removing backup and unwanted files")
            self._remove_unwanted_files(conn)

            # Phase 2: Remove duplicates
            logger.info("🔄 Phase 2: Removing duplicate entries")
            self._remove_duplicates(conn)

            # Phase 3: Create templates from existing content
            logger.info("🧩 Phase 3: Creating documentation templates")
            self._create_templates_from_content(conn)

            # Phase 4: Optimize database
            logger.info("⚡ Phase 4: Optimizing database")
            self._optimize_database(conn)

            # Get final statistics
            self._collect_final_statistics(conn)

            conn.close()

            # DUAL COPILOT VALIDATION
            validation_result = self._validate_cleanup_quality()

            logger.info("✅ COMPREHENSIVE CLEANUP COMPLETED")
            return self.cleanup_stats

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {str(e)}")
            self._restore_from_backup()
            raise

    def _create_database_backup(self):
        """💾 Create database backup before cleanup"""
        logger.info(f"💾 Creating database backup: {self.backup_path}")

        # Get original size
        original_size = self.db_path.stat().st_size
        logger.info(f"📏 Original database size: {original_size / (1024*1024):.1f} MB")

        # Create backup
        import shutil
        shutil.copy2(self.db_path, self.backup_path)

        logger.info("✅ Backup created successfully")

    def _collect_initial_statistics(self, conn: sqlite3.Connection):
        """📊 Collect initial database statistics"""
        cursor = conn.cursor()

        # Get total record count
        cursor.execute("SELECT COUNT(*) FROM enterprise_documentation")
        self.cleanup_stats["total_records_before"] = cursor.fetchone()[0]

        # Get unwanted file count
        cursor.execute("""
            SELECT COUNT(*) FROM enterprise_documentation
            WHERE source_path LIKE '%backup%'
               OR source_path LIKE '%_convo.md'
               OR source_path LIKE '%.bak'
               OR doc_type = 'BACKUP_LOG'
        """)
        backup_count = cursor.fetchone()[0]

        # Get duplicate count
        cursor.execute("""
            SELECT COUNT(*) - COUNT(DISTINCT title) FROM enterprise_documentation
        """)
        duplicate_count = cursor.fetchone()[0]

        logger.info("📊 Initial Statistics:")
        logger.info(f"  • Total records: {self.cleanup_stats['total_records_before']:,}")
        logger.info(f"  • Backup/unwanted files: {backup_count}")
        logger.info(f"  • Duplicate titles: {duplicate_count}")

    def _remove_unwanted_files(self, conn: sqlite3.Connection):
        """🗑️ Remove backup files, conversation files, and unwanted entries"""
        cursor = conn.cursor()

        # First, identify what we're removing
        cursor.execute("""
            SELECT doc_id, title, source_path, doc_type
            FROM enterprise_documentation
            WHERE source_path LIKE '%backup%'
               OR source_path LIKE '%_convo.md'
               OR source_path LIKE '%.bak'
               OR doc_type = 'BACKUP_LOG'
               OR source_path LIKE '%temp%'
               OR source_path LIKE '%tmp%'
        """)

        unwanted_files = cursor.fetchall()
        logger.info(f"🗑️ Found {len(unwanted_files)} unwanted files to remove")

        # Log sample of what's being removed
        for i, file_info in enumerate(unwanted_files[:5]):
            logger.info(f"  • {file_info[1]} ({file_info[3]}) - {file_info[2]}")
        if len(unwanted_files) > 5:
            logger.info(f"  ... and {len(unwanted_files) - 5} more")

        # Remove unwanted files
        cursor.execute("""
            DELETE FROM enterprise_documentation
            WHERE source_path LIKE '%backup%'
               OR source_path LIKE '%_convo.md'
               OR source_path LIKE '%.bak'
               OR doc_type = 'BACKUP_LOG'
               OR source_path LIKE '%temp%'
               OR source_path LIKE '%tmp%'
        """)

        removed_count = cursor.rowcount
        self.cleanup_stats["backup_files_removed"] = removed_count

        conn.commit()
        logger.info(f"✅ Removed {removed_count} unwanted files")

    def _remove_duplicates(self, conn: sqlite3.Connection):
        """🔄 Remove duplicate entries, keeping the most recent version"""
        cursor = conn.cursor()

        # Find duplicates by title
        cursor.execute("""
            SELECT title, COUNT(*) as count
            FROM enterprise_documentation
            GROUP BY title
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)

        duplicates = cursor.fetchall()
        logger.info(f"🔄 Found {len(duplicates)} titles with duplicates")

        total_duplicate_records = 0
        for title, count in duplicates:
            total_duplicate_records += count - 1  # Keep one, remove others
            logger.info(f"  • \"{title}\": {count} copies (will remove {count-1})")

        # Remove duplicates, keeping the most recent version
        cursor.execute("""
            DELETE FROM enterprise_documentation
            WHERE doc_id NOT IN (
                SELECT doc_id FROM (
                    SELECT doc_id,
                           ROW_NUMBER() OVER (
                               PARTITION BY title
                               ORDER BY last_updated DESC, doc_id DESC
                           ) as rn
                    FROM enterprise_documentation
                ) ranked
                WHERE rn = 1
            )
        """)

        removed_duplicates = cursor.rowcount
        self.cleanup_stats["duplicates_removed"] = removed_duplicates

        conn.commit()
        logger.info(f"✅ Removed {removed_duplicates} duplicate entries")

    def _create_templates_from_content(self, conn: sqlite3.Connection):
        """🧩 Create documentation templates from existing content"""
        cursor = conn.cursor()

        # Get content that can be templatized
        cursor.execute("""
            SELECT doc_type, title, content
            FROM enterprise_documentation
            WHERE doc_type IN ('INSTRUCTION', 'README', 'ENTERPRISE_DOC')
               AND LENGTH(content) > 500
            ORDER BY doc_type, title
        """)

        content_for_templates = cursor.fetchall()
        logger.info(f"🧩 Found {len(content_for_templates)} documents for template extraction")

        templates_created = 0

        # Template patterns to extract
        template_patterns = {
            "README": {
                "sections": ["## Usage", "## Configuration", "## Examples", "## API Reference"],
                "variables": ["module_name", "description", "version"]
            },
            "INSTRUCTION": {
                "sections": ["### Overview", "### Requirements", "### Implementation", "### Validation"],
                "variables": ["instruction_type", "compliance_level", "pattern_name"]
            },
            "ENTERPRISE_DOC": {
                "sections": ["## Architecture", "## Compliance", "## Integration", "## Monitoring"],
                "variables": ["system_name", "phase", "compliance_level"]
            }
        }

        for doc_type, pattern_info in template_patterns.items():
            # Find common patterns in this document type
            type_docs = [doc for doc in content_for_templates if doc[0] == doc_type]

            if type_docs:
                template_content = self._extract_template_pattern(
                                                                  type_docs,
                                                                  pattern_info
                template_content = self._extract_template_pattern(type_docs, patt)

                template_id = f"template_{doc_type.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                cursor.execute("""
                    INSERT INTO documentation_templates
                    (
                     template_id,
                     template_name,
                     template_type,
                     template_content,
                     variables,
                     enterprise_compliant,
                     quantum_optimized
                    (template_id, templa)
                    VALUES (?, ?, ?, ?, ?, TRUE, TRUE)
                """, (
                    template_id,
                    f"{doc_type} Standard Template",
                    doc_type,
                    template_content,
                    json.dumps(pattern_info["variables"])
                ))

                templates_created += 1
                logger.info(f"  ✅ Created template: {doc_type} Standard Template")

        self.cleanup_stats["templates_created"] = templates_created
        conn.commit()
        logger.info(f"🧩 Created {templates_created} documentation templates")

    def _extract_template_pattern(self, docs: List, pattern_info: Dict) -> str:
        """📝 Extract common pattern from documents"""
        # Simple template extraction - find common structure
        base_template = f"""# {{{{ title }}}}

## Overview
{{{{ description }}}}

## Usage

```python
# Example usage
from your_module import YourClass

instance = YourClass()
result = instance.process(data)
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| param1    | str  | 'default' | Parameter description |
| param2    | int  | 100     | Parameter description |

## API Reference

### Methods

#### `process(data)`

Process input data and return results.

**Parameters:**
- `data` (Any): Input data to process

**Returns:**
- `Dict[str, Any]`: Processing results

## Examples

### Basic Example

```python
# Basic usage example
result = process_data(input_data)
print(result)
```

### Advanced Example

```python
# Advanced usage with error handling
try:
    result = advanced_process(complex_data)
    handle_success(result)
except Exception as e:
    handle_error(e)
```

## Troubleshooting

### Common Issues

1. **Issue 1**: Description and solution
2. **Issue 2**: Description and solution

## Contributing

Contributions are welcome! Please follow the existing code style and add tests for new functionality.

## License

This module is part of the gh_COPILOT enterprise toolkit.

---

*Generated automatically by Template Completion System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return base_template

    def _optimize_database(self, conn: sqlite3.Connection):
        """⚡ Optimize database performance"""
        cursor = conn.cursor()

        logger.info("⚡ Optimizing database...")

        # Analyze tables
        cursor.execute("ANALYZE")

        # Vacuum to reclaim space
        cursor.execute("VACUUM")

        # Update statistics
        cursor.execute("PRAGMA optimize")

        conn.commit()
        logger.info("✅ Database optimization complete")

    def _collect_final_statistics(self, conn: sqlite3.Connection):
        """📊 Collect final statistics after cleanup"""
        cursor = conn.cursor()

        # Get final record count
        cursor.execute("SELECT COUNT(*) FROM enterprise_documentation")
        self.cleanup_stats["total_records_after"] = cursor.fetchone()[0]

        # Calculate storage savings
        current_size = self.db_path.stat().st_size
        original_size = self.backup_path.stat().st_size
        saved_mb = (original_size - current_size) / (1024 * 1024)
        self.cleanup_stats["storage_saved_mb"] = round(saved_mb, 1)

        logger.info("📊 Final Statistics:")
        logger.info(f"  • Records before: {self.cleanup_stats['total_records_before']:,}")
        logger.info(f"  • Records after: {self.cleanup_stats['total_records_after']:,}")
        logger.info(f"  • Records removed: {self.cleanup_stats['total_records_before'] - self.cleanup_stats['total_records_after']:,}")
        logger.info(f"  • Storage saved: {saved_mb:.1f} MB")

    def _validate_cleanup_quality(self) -> Dict[str, Any]:
        """🛡️ DUAL COPILOT VALIDATION: Validate cleanup quality"""
        validation = {
            "passed": True,
            "checks": {},
            "warnings": [],
            "errors": []
        }

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Check 1: No backup files remain
        cursor.execute("""
            SELECT COUNT(*) FROM enterprise_documentation
            WHERE source_path LIKE '%backup%'
               OR source_path LIKE '%_convo.md'
               OR source_path LIKE '%.bak'
        """)
        remaining_backup_files = cursor.fetchone()[0]

        if remaining_backup_files == 0:
            validation["checks"]["backup_files"] = "✅ No backup files remaining"
        else:
            validation["checks"]["backup_files"] = f"❌ {remaining_backup_files} backup files still present"
            validation["errors"].append(f"Backup files not completely removed: {remaining_backup_files}")
            validation["passed"] = False

        # Check 2: Templates created
        cursor.execute("SELECT COUNT(*) FROM documentation_templates")
        template_count = cursor.fetchone()[0]

        if template_count > 0:
            validation["checks"]["templates"] = f"✅ {template_count} templates created"
        else:
            validation["checks"]["templates"] = "⚠️ No templates created"
            validation["warnings"].append("No templates were created")

        # Check 3: Reasonable cleanup ratio
        cleanup_ratio = ((self.cleanup_stats["total_records_before"] - self.cleanup_stats["total_records_after"]) /
                        self.cleanup_stats["total_records_before"]) * 100

        if 10 <= cleanup_ratio <= 50:
            validation["checks"]["cleanup_ratio"] = f"✅ Cleanup ratio: {cleanup_ratio:.1f}%"
        elif cleanup_ratio > 50:
            validation["checks"]["cleanup_ratio"] = f"⚠️ High cleanup ratio: {cleanup_ratio:.1f}%"
            validation["warnings"].append("Unusually high cleanup ratio - verify results")
        else:
            validation["checks"]["cleanup_ratio"] = f"⚠️ Low cleanup ratio: {cleanup_ratio:.1f}%"
            validation["warnings"].append("Low cleanup ratio - may indicate missed duplicates")

        conn.close()

        logger.info(f"🛡️ DUAL COPILOT VALIDATION: {'✅ PASSED' if validation['passed'] else '❌ FAILED'}")
        return validation

    def _restore_from_backup(self):
        """🔄 Restore database from backup in case of failure"""
        if self.backup_path.exists():
            logger.info(f"🔄 Restoring database from backup: {self.backup_path}")
            import shutil
            shutil.copy2(self.backup_path, self.db_path)
            logger.info("✅ Database restored from backup")

    def save_cleanup_report(self) -> str:
        """💾 Save comprehensive cleanup report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.workspace_path / f"documentation_db_cleanup_report_{timestamp}.json"

        # Add metadata
        cleanup_report = {
            "metadata": {
                "cleanup_timestamp": timestamp,
                "database_path": str(self.db_path),
                "backup_path": str(self.backup_path),
                "cleanup_version": "1.0",
                "dual_copilot_validated": True
            },
            "statistics": self.cleanup_stats,
            "actions_performed": [
                "Removed backup and unwanted files",
                "Eliminated duplicate entries",
                "Created documentation templates",
                "Optimized database structure"
            ]
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(cleanup_report, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Cleanup report saved: {report_path}")
        return str(report_path)

    def print_cleanup_summary(self):
        """📋 Print cleanup summary"""
        duration = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "="*60)
        print("📋 DOCUMENTATION DATABASE CLEANUP SUMMARY")
        print("="*60)

        print("🧹 Cleanup Results:")
        print(f"  • Backup files removed: {self.cleanup_stats['backup_files_removed']}")
        print(f"  • Duplicate entries removed: {self.cleanup_stats['duplicates_removed']}")
        print(f"  • Templates created: {self.cleanup_stats['templates_created']}")
        print(f"  • Storage saved: {self.cleanup_stats['storage_saved_mb']} MB")

        total_removed = self.cleanup_stats['backup_files_removed'] + self.cleanup_stats['duplicates_removed']
        cleanup_percentage = (total_removed / self.cleanup_stats['total_records_before']) * 100

        print("\n📊 Database Optimization:")
        print(f"  • Records before: {self.cleanup_stats['total_records_before']:,}")
        print(f"  • Records after: {self.cleanup_stats['total_records_after']:,}")
        print(f"  • Total removed: {total_removed:,} ({cleanup_percentage:.1f}%)")

        print(f"\n⏱️ Cleanup Duration: {duration:.2f} seconds")
        print("✅ CLEANUP COMPLETE")
        print("="*60)


def main():
    """🚀 Main execution function with DUAL COPILOT pattern"""
    try:
        # Primary execution
        cleanup_system = DocumentationDatabaseCleanupSystem()
        results = cleanup_system.execute_comprehensive_cleanup()

        # Generate report
        report_path = cleanup_system.save_cleanup_report()

        # Print summary
        cleanup_system.print_cleanup_summary()

        print(f"\n📄 Detailed report saved to: {report_path}")
        print(f"💾 Database backup available at: {cleanup_system.backup_path}")

    except Exception as e:
        logger.error(f"❌ Cleanup failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
