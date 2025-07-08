#!/usr/bin/env python3
"""
Unified Legacy Cleanup System.

Coordinates removal of obsolete files and maintains audit logging.
"""
import os
import sys
import sqlite3
import shutil
import logging
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

# Logging configuration
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'unified_legacy_cleanup.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

LOCK_FILE = Path('.unified_legacy_cleanup.lock')

@dataclass
class CleanupConfig:
    workspace_root: Path = Path('e:/gh_COPILOT')
    archive_root: Path = Path('backup/legacy_cleanup')
    staging_db_path: Path = Path('E:/gh_COPILOT/databases')
    local_db_path: Path = Path('databases')
    db_path: Path = Path('databases/cleanup_actions.db')
    dry_run: bool = False
    require_confirmation: bool = True

@dataclass
class CleanupResult:
    actions: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class UnifiedLegacyCleanupSystem:
    def __init__(self, config: CleanupConfig):
        self.config = config
        self.conn = sqlite3.connect(self.config.db_path)
        self._init_db()
        logger.info('Unified legacy cleanup system initialized')

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cleanup_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                target_path TEXT NOT NULL,
                action_result TEXT NOT NULL,
                files_affected INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def _record_action(self, action_type: str, target_path: Path, result: str, files: int = 1) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO cleanup_actions (action_type, target_path, action_result, files_affected, timestamp) VALUES (?,?,?,?,?)",
            (action_type, str(target_path), result, files, datetime.now().isoformat())
        )
        self.conn.commit()

    # Anti-recursion lock handling
    def _acquire_lock(self) -> bool:
        if LOCK_FILE.exists():
            logger.error('Another cleanup process appears to be running')
            return False
        LOCK_FILE.write_text(str(os.getpid()))
        return True

    def _release_lock(self) -> None:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()

    def _calculate_checksum(self, path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    # Legacy orchestrator cleanup
    def _legacy_orchestrator_patterns(self) -> List[str]:
        return [
            '**/enterprise_gh_copilot_deployment_orchestrator.py',
            '**/enterprise_gh_copilot_deployment_orchestrator_windows.py',
            '**/integrated_deployment_orchestrator.py',
            '**/production_deployment_orchestrator.py',
            '**/comprehensive_deployment_manager.py',
            '**/FINAL_STAGING_DEPLOYMENT_ORCHESTRATOR.py',
            '**/final_enterprise_deployment_executor.py'
        ]

    def identify_legacy_orchestrators(self) -> List[Path]:
        workspace = Path(self.config.workspace_root)
        files: List[Path] = []
        for pattern in self._legacy_orchestrator_patterns():
            files.extend(workspace.glob(pattern))
        return [f for f in files if f.is_file() and f.name != Path(__file__).name]

    def archive_and_remove(self, file_path: Path) -> None:
        relative = file_path.relative_to(Path(self.config.workspace_root))
        archive_dest = Path(self.config.archive_root) / relative
        archive_dest.parent.mkdir(parents=True, exist_ok=True)
        if not self.config.dry_run:
            shutil.copy2(file_path, archive_dest)
            if self._calculate_checksum(file_path) == self._calculate_checksum(archive_dest):
                file_path.unlink()
                self._record_action('archive_remove', file_path, 'archived')
                logger.info(f'Archived and removed {file_path}')
            else:
                self._record_action('archive_remove', file_path, 'checksum_mismatch', 0)
                logger.error(f'Checksum mismatch for {file_path}')
        else:
            logger.info(f'[DRY RUN] Would archive and remove {file_path}')

    # Zero-byte file cleanup
    def remove_zero_byte_files(self, root_path: Path) -> int:
        count = 0
        for file in root_path.rglob('*'):
            if file.is_file() and file.stat().st_size == 0:
                if not self.config.dry_run:
                    file.unlink()
                count += 1
                self._record_action('remove_zero_byte', file, 'removed')
                logger.info(f'Removed zero-byte file {file}')
        return count

    # C:\Temp violation fixes
    def fix_c_temp_violations(self, root_path: Path) -> int:
        count = 0
        patterns = ['C:/Temp', 'C:\\Temp']
        for file in root_path.glob('*.py'):
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if any(p.lower() in content.lower() for p in patterns):
                fixed = content
                for p in patterns:
                    fixed = fixed.replace(p, str(self.config.workspace_root / 'temp'))
                if not self.config.dry_run:
                    backup = file.with_suffix('.backup')
                    if not backup.exists():
                        with open(backup, 'w', encoding='utf-8') as b:
                            b.write(content)
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(fixed)
                count += 1
                self._record_action('fix_c_temp', file, 'fixed')
                logger.info(f'Fixed C:Temp violation in {file}')
        return count

    # Database file cleanup
    def cleanup_redundant_databases(self) -> int:
        removed = 0
        staging = Path(self.config.staging_db_path)
        local = Path(self.config.local_db_path)
        if not staging.exists() or not local.exists():
            return 0
        for db_file in staging.glob('*.db'):
            local_file = local / db_file.name
            if local_file.exists() and self._calculate_checksum(db_file) == self._calculate_checksum(local_file):
                if not self.config.dry_run:
                    db_file.unlink()
                removed += 1
                self._record_action('remove_redundant_db', db_file, 'removed')
                logger.info(f'Removed redundant DB {db_file}')
        return removed

    def cleanup_after_session(self) -> None:
        """Run cleanup tasks after each session."""
        workspace = Path(self.config.workspace_root)
        self.remove_zero_byte_files(workspace)
        self.fix_c_temp_violations(workspace)
        self.cleanup_redundant_databases()

    def execute_cleanup(self) -> CleanupResult:
        result = CleanupResult()
        if not self._acquire_lock():
            result.errors.append('Lock acquisition failed')
            return result
        try:
            # Confirm
            if self.config.require_confirmation and not self.config.dry_run:
                answer = input('Proceed with unified legacy cleanup? (yes/no): ').strip().lower()
                if answer != 'yes':
                    logger.info('Cleanup aborted by user')
                    return result
            # Legacy orchestrators
            for f in self.identify_legacy_orchestrators():
                self.archive_and_remove(f)
            # Zero-byte files
            self.remove_zero_byte_files(Path(self.config.workspace_root))
            # C:Temp fixes
            self.fix_c_temp_violations(Path(self.config.workspace_root))
            # Redundant DBs
            self.cleanup_redundant_databases()
            # Accumulate actions performed during cleanup
        except Exception as e:
            logger.error(f'Cleanup failed: {e}')
            result.errors.append(str(e))
        finally:
            self._release_lock()
            self.conn.close()
        return result

def main() -> bool:
    config = CleanupConfig()
    cleaner = UnifiedLegacyCleanupSystem(config)
    res = cleaner.execute_cleanup()
    logger.info('Cleanup errors: %s', res.errors)
    return len(res.errors) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
