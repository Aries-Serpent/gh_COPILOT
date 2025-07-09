#!/usr/bin/env python3
"""
Script Generation Consolidation Executor
DUAL COPILOT PATTERN - Autonomous File Management
Anti-Recursion Protected Enterprise Consolidation System

This script consolidates all script generation-related files into a single,
enterprise-compliant unified system with:
- DUAL COPILOT PATTERN compliance
- Visual processing indicators
- Anti-recursion protection
- Quantum optimization
- Phase 4/5 integration
- Enterprise compliance certification

AUTONOMOUS_FILE_MANAGEMENT:
- Database-driven file discovery and tracking
- Automated backup and archival
- Legacy script cleanup and validation
- Canonical system preservation
"""

import hashlib
import json
import logging
import sqlite3
import sys
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from base_consolidation_executor import BaseConsolidationExecutor

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(]
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers = [
            LOG_DIR / 'script_generation_consolidation.log', encoding = 'utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ScriptGenerationConsolidationExecutor(BaseConsolidationExecutor):
    """Autonomous script generation consolidation system"""

    def __init__(self, workspace_path: str = r"e:\gh_COPILOT"):
        super().__init__(]
        )
        self.workspace_path = Path(workspace_path)
        self.backup_dir = self.archive_dir

        # Initialize database
        self.db_path = self.workspace_path / "databases" / "consolidation_tracking.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()

        # Define canonical system
        self.canonical_system = "unified_script_generation_system.py"

        # Define script generation patterns
        self.script_generation_patterns = [
        ]

        logger.info(f"🎯 Script Generation Consolidation Executor initialized")
        logger.info(f"📁 Workspace: {self.workspace_path}")
        logger.info(f"🔒 Backup: {self.backup_dir}")

    def _init_database(self):
        """Initialize consolidation tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                )
            ''')

            cursor.execute(
                )
            ''')

            conn.commit()

    def discover_script_generation_files(self) -> List[Dict[str, Any]]:
        """Discover all script generation-related files using database-driven approach"""
        logger.info("🔍 [DISCOVERY] Discovering script generation files...")

        discovered_files = [

        files = self.discover_files(]
                                    self.canonical_system])
        for file_path in files:
            if file_path.suffix != '.py':
                continue
            if 'consolidation' in file_path.name.lower():
                logger.info(
                    f"⚡ [PRESERVE] Consolidation executor preserved: {file_path}")
                continue

            file_hash = self._calculate_file_hash(file_path)
            discovered_files.append(]
                'size': file_path.stat().st_size,
                'hash': file_hash,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'relative_path': file_path.relative_to(self.workspace_path)
            })

        logger.info(
            f"📊 [DISCOVERY] Found {len(discovered_files)} script generation files")
        return discovered_files

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception as e:
            logger.error(
                f"❌ [ERROR] Hash calculation failed for {file_path}: {e}")
            return "error"

    def archive_legacy_files(]
            self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Archive legacy script generation files"""
        logger.info(f"📦 [ARCHIVE] Archiving {len(files)} legacy files...")

        archive_dir = self.archive_dir

        archived_files = [
        failed_files = [

        for file_info in files:
            try:
                source_path = file_info['path']
                relative_path = file_info['relative_path']

                result = self.archive_files([source_path])
                if result:
                    _, backup_path = result[0]
                    # Store in database
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            (file_path, file_hash, backup_path, consolidation_timestamp, status)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (]
                            str(source_path),
                            file_info['hash'],
                            str(backup_path),
                            self.timestamp,
                            'archived'
                        ))
                        conn.commit()

                    archived_files.append(]
                        'source': str(source_path),
                        'backup': str(backup_path),
                        'hash': file_info['hash'],
                        'size': file_info['size']})

                    logger.info(f"✅ [ARCHIVED] {relative_path}")
                else:
                    raise Exception("Backup failed")

            except Exception as e:
                logger.error(
                    f"❌ [ERROR] Archive failed for {file_info['path']}: {e}")
                failed_files.append(]
                    'file': str(file_info['path']),
                    'error': str(e)
                })

        return {]
            'archived_count': len(archived_files),
            'failed_count': len(failed_files),
            'archived_files': archived_files,
            'failed_files': failed_files,
            'archive_directory': str(archive_dir)
        }

    def remove_legacy_files(]
            self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Remove legacy files from workspace after archiving"""
        logger.info(f"🗑️ [CLEANUP] Removing {len(files)} legacy files...")

        removed_files = [
        failed_removals = [

        for file_info in files:
            try:
                source_path = file_info['path']

                # Verify file is archived
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        SELECT COUNT(*) FROM script_generation_consolidation
                        WHERE file_path = ? AND status = 'archived'
                    ''', (str(source_path),))

                    if cursor.fetchone()[0] == 0:
                        raise Exception("File not confirmed as archived")

                # Remove file
                if source_path.exists():
                    source_path.unlink()

                    # Update database
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                        ''', (str(source_path),))
                        conn.commit()

                    removed_files.append(str(source_path))
                    logger.info(f"🗑️ [REMOVED] {file_info['relative_path']}")

            except Exception as e:
                logger.error(
                    f"❌ [ERROR] Removal failed for {file_info['path']}: {e}")
                failed_removals.append(]
                    'file': str(file_info['path']),
                    'error': str(e)
                })

        return {]
            'removed_count': len(removed_files),
            'failed_count': len(failed_removals),
            'removed_files': removed_files,
            'failed_removals': failed_removals
        }

    def validate_consolidation(self) -> Dict[str, Any]:
        """Validate consolidation results"""
        logger.info("🔍 [VALIDATION] Validating consolidation results...")

        # Check canonical system exists
        canonical_path = self.workspace_path / self.canonical_system
        canonical_exists = canonical_path.exists()

        # Check for remaining legacy files
        remaining_files = [
        for pattern in self.script_generation_patterns:
            try:
                files = list(self.workspace_path.rglob(pattern))
                for file_path in files:
                    if file_path.is_file() and file_path.suffix == '.py':
                        if file_path.name != self.canonical_system and 'consolidation' not in file_path.name.lower():
                            remaining_files.append(str(file_path))
            except Exception as e:
                logger.error(
                    f"❌ [ERROR] Validation pattern search failed: {e}")

        # Get database statistics
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT COUNT(*) FROM script_generation_consolidation WHERE status = "removed"')
            removed_count = cursor.fetchone()[0]

            cursor.execute(
                'SELECT COUNT(*) FROM script_generation_consolidation WHERE status = "archived"')
            archived_count = cursor.fetchone()[0]

        validation_results = {
            'canonical_system_path': str(canonical_path) if canonical_exists else None,
            'remaining_legacy_files': remaining_files,
            'remaining_count': len(remaining_files),
            'archived_count': archived_count,
            'removed_count': removed_count,
            'consolidation_successful': canonical_exists and len(remaining_files) == 0
        }

        if validation_results['consolidation_successful']:
            logger.info(
                "✅ [SUCCESS] Script generation consolidation completed successfully")
        else:
            logger.warning(
                "⚠️ [WARNING] Consolidation validation found issues")

        return validation_results

    def generate_consolidation_manifest(]
                                        discovered_files: List[Dict[str, Any]],
                                        archive_results: Dict[str, Any],
                                        removal_results: Dict[str, Any],
                                        validation_results: Dict[str, Any]) -> str:
        """Generate consolidation manifest"""
        logger.info("📋 [MANIFEST] Generating consolidation manifest...")

        consolidation_id = str(uuid.uuid4())

        manifest = {
                'workspace': str(self.workspace_path)
            },
            'canonical_system': {]
                'path': str(self.workspace_path / self.canonical_system),
                'exists': validation_results['canonical_system_exists']
            },
            'discovery_results': {]
                'total_files_discovered': len(discovered_files),
                'search_patterns': self.script_generation_patterns,
                'files': discovered_files
            },
            'archival_results': archive_results,
            'removal_results': removal_results,
            'validation_results': validation_results,
            'file_categories': self._categorize_files(discovered_files),
            'consolidation_summary': {]
                'total_processed': len(discovered_files),
                'successfully_archived': archive_results['archived_count'],
                'successfully_removed': removal_results['removed_count'],
                'failed_operations': archive_results['failed_count'] + removal_results['failed_count'],
                'consolidation_successful': validation_results['consolidation_successful']
            }
        }

        manifest_file = Path(self.generate_manifest(manifest))

        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                 archived_files, manifest_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (]
                len(discovered_files),
                archive_results['archived_count'],
                json.dumps(manifest, default=str)
            ))
            conn.commit()

        logger.info(f"📋 [MANIFEST] Saved: {manifest_file}")
        return str(manifest_file)

    def _categorize_files(]
            self, files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize files by type"""
        categories = defaultdict(list)

        for file_info in files:
            file_name = file_info['name'].lower()

            if 'platform' in file_name:
                categories['platforms'].append(file_info['name'])
            elif 'framework' in file_name:
                categories['frameworks'].append(file_info['name'])
            elif 'engine' in file_name:
                categories['engines'].append(file_info['name'])
            elif 'demo' in file_name:
                categories['demos'].append(file_info['name'])
            elif 'implementation' in file_name:
                categories['implementations'].append(file_info['name'])
            elif 'integration' in file_name:
                categories['integrations'].append(file_info['name'])
            elif 'analyzer' in file_name:
                categories['analyzers'].append(file_info['name'])
            elif 'enhancer' in file_name:
                categories['enhancers'].append(file_info['name'])
            else:
                categories['other'].append(file_info['name'])

        return dict(categories)

    def execute_consolidation(self) -> Dict[str, Any]:
        """Execute complete script generation consolidation"""
        logger.info("🚀 [EXECUTE] Starting script generation consolidation...")

        try:
            # Phase 1: Discovery
            discovered_files = self.discover_script_generation_files()

            if not discovered_files:
                logger.info(
                    "ℹ️ [INFO] No script generation files found to consolidate")
                return {]
                    'consolidation_id': str(uuid.uuid4()),
                    'timestamp': self.timestamp
                }

            # Phase 2: Archive
            archive_results = self.archive_legacy_files(discovered_files)

            # Phase 3: Remove
            removal_results = self.remove_legacy_files(discovered_files)

            # Phase 4: Validate
            validation_results = self.validate_consolidation()

            # Phase 5: Generate manifest
            manifest_file = self.generate_consolidation_manifest(]
            )

            # Generate summary
            summary = {
                'success': validation_results['consolidation_successful'],
                'consolidation_id': str(uuid.uuid4()),
                'timestamp': self.timestamp,
                'workspace': str(self.workspace_path),
                'canonical_system': self.canonical_system,
                'statistics': {]
                    'files_discovered': len(discovered_files),
                    'files_archived': archive_results['archived_count'],
                    'files_removed': removal_results['removed_count'],
                    'files_failed': archive_results['failed_count'] + removal_results['failed_count'],
                    'remaining_legacy': validation_results['remaining_count']
                },
                'manifest_file': manifest_file,
                'archive_directory': archive_results['archive_directory']
            }

            logger.info(
                "✅ [SUCCESS] Script generation consolidation completed")
            return summary

        except Exception as e:
            logger.error(f"❌ [ERROR] Consolidation execution failed: {e}")
            return {]
                'error': str(e),
                'timestamp': self.timestamp
            }


def main():
    """Main execution function"""
    logger.info("🎯 Starting Script Generation Consolidation Executor")

    try:
        executor = ScriptGenerationConsolidationExecutor()
        results = executor.execute_consolidation()

        if results['success']:
            logger.info(
                "🎉 [COMPLETE] Script generation consolidation successful!")
            logger.info(f"📊 Statistics: {results['statistics']}")
            logger.info(f"📋 Manifest: {results['manifest_file']}")
            logger.info(f"📁 Archive: {results['archive_directory']}")
            return 0
        else:
            logger.error(
                f"❌ [FAILED] Consolidation failed: {results.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        logger.error(f"❌ [FATAL] Execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
