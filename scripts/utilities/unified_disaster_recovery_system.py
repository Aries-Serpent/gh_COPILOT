#!/usr/bin/env python3
"""UnifiedDisasterRecoverySystem - Enterprise Utility Script."""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from unified_disaster_recovery_system import log_backup_event
from utils import log_utils as enterprise_logging

__all__ = [
    "ComplianceLogger",
    "BackupScheduler",
    "RestoreExecutor",
    "UnifiedDisasterRecoverySystem",
    "main",
]

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
}


class ComplianceLogger:
    """Record compliance events for disaster recovery operations."""

    def log(self, event: str, **details: str) -> None:
        payload = {"module": "disaster_recovery", "event": event, **details}
        enterprise_logging.log_event(payload)
        log_backup_event(event, details)


class BackupScheduler:
    """Handle creation of scheduled backup files."""

    def __init__(self, workspace_path: Path, logger: ComplianceLogger) -> None:
        self.workspace_path = workspace_path
        self.compliance_logger = logger
        self.logger = logging.getLogger(self.__class__.__name__)

    def schedule(self) -> Path:
        backup_root = Path(
            os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups")
        ).resolve()
        workspace = self.workspace_path.resolve()

        if workspace in backup_root.parents or backup_root == workspace:
            msg = f"Backup root {backup_root} resides within workspace {workspace}"
            self.logger.error("%s %s", TEXT_INDICATORS["error"], msg)
            # Record the compliance failure before raising an error to ensure the
            # event is captured even when scheduling aborts early.
            self.compliance_logger.log(
                "backup_failed", path=str(backup_root), reason="recursive"
            )
            raise ValueError(msg)

        backup_root.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_root / f"scheduled_backup_{timestamp}.bak"
        backup_file.write_text("scheduled backup", encoding="utf-8")
        hash_file = backup_file.with_suffix(backup_file.suffix + ".sha256")
        hash_file.write_text(
            hashlib.sha256(backup_file.read_bytes()).hexdigest(), encoding="utf-8"
        )
        self.compliance_logger.log("backup_scheduled", path=str(backup_file))
        return backup_file


class RestoreExecutor:
    """Restore individual backups with integrity checks."""

    def __init__(self, workspace_path: Path, logger: ComplianceLogger) -> None:
        self.workspace_path = workspace_path
        self.compliance_logger = logger
        self.logger = logging.getLogger(self.__class__.__name__)

    def restore(self, path: str | Path) -> bool:
        backup_file = Path(path)
        hash_file = backup_file.with_suffix(backup_file.suffix + ".sha256")

        if not backup_file.exists() or not hash_file.exists():
            self.logger.error(
                "%s Missing backup or checksum for %s",
                TEXT_INDICATORS["error"],
                backup_file,
            )
            self.compliance_logger.log(
                "restore_failed", path=str(backup_file), reason="missing"
            )
            return False

        digest = hashlib.sha256(backup_file.read_bytes()).hexdigest()
        expected = hash_file.read_text().strip()
        if digest != expected:
            self.logger.error(
                "%s Hash mismatch for %s", TEXT_INDICATORS["error"], backup_file
            )
            self.compliance_logger.log(
                "restore_failed", path=str(backup_file), reason="hash_mismatch"
            )
            return False

        destination = self.workspace_path / backup_file.name
        shutil.copy2(backup_file, destination)
        self.compliance_logger.log("restore_success", path=str(backup_file))
        return True


class UnifiedDisasterRecoverySystem:
    """Perform simple disaster recovery from backups."""

    def __init__(self, workspace_path: Optional[str] = None) -> None:
        self.workspace_path = Path(
            workspace_path or os.getenv("GH_COPILOT_WORKSPACE", ".")
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.compliance_logger = ComplianceLogger()
        self.scheduler = BackupScheduler(self.workspace_path, self.compliance_logger)
        self.restore_executor = RestoreExecutor(
            self.workspace_path, self.compliance_logger
        )

    def perform_recovery(self) -> bool:
        """Restore files from ``GH_COPILOT_BACKUP_ROOT``."""
        start_time = datetime.now()
        backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups")).resolve()
        workspace = self.workspace_path.resolve()

        if workspace in backup_root.parents or backup_root == workspace:
            self.logger.error(
                "%s Backup root %s resides within workspace %s",
                TEXT_INDICATORS["error"],
                backup_root,
                workspace,
            )
            return False

        source = backup_root / "production_backup"
        restore_dir = self.workspace_path / "restored"
        restore_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("%s Starting disaster recovery from %s", TEXT_INDICATORS["start"], source)

        if not source.exists():
            self.logger.error("%s Backup source missing: %s", TEXT_INDICATORS["error"], source)
            return False

        for item in source.glob("*"):
            try:
                shutil.copy2(item, restore_dir / item.name)
                self.logger.info("%s Restored %s", TEXT_INDICATORS["info"], item.name)
            except OSError as exc:
                self.logger.error("%s Failed to restore %s: %s", TEXT_INDICATORS["error"], item.name, exc)
                return False

        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info("%s Disaster recovery completed in %.1fs", TEXT_INDICATORS["success"], duration)
        return True

    def schedule_backups(self) -> Path:
        """Create a timestamped backup in ``GH_COPILOT_BACKUP_ROOT``."""
        return self.scheduler.schedule()

    def restore_backup(self, path: str | Path) -> bool:
        """Restore a single backup file with integrity verification."""
        return self.restore_executor.restore(path)


def main() -> int:
    system = UnifiedDisasterRecoverySystem()
    return 0 if system.perform_recovery() else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
