"""Compliance validation module for security policies.

Provides a central interface for environment checks, policy enforcement and
event logging used across operational modules.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List

from enterprise_modules.compliance import _log_rollback, validate_enterprise_operation
from enterprise_modules.utility_utils import (
    setup_enterprise_logging,
    validate_environment_compliance,
)


class ComplianceError(RuntimeError):
    """Raised when compliance thresholds are exceeded."""


class ComplianceChecker:
    """Validate runtime environment and operational policies."""

    def __init__(
        self,
        policy_path: str | Path = Path("security/enterprise_security_policy.json"),
        *,
        threshold: int = 0,
    ) -> None:
        self.policy_path = Path(policy_path)
        self.threshold = threshold
        self.rules: List[Callable[[], bool]] = []
        self.logger = setup_enterprise_logging(__name__, console_output=False)
        self.policy = self._load_policy()
        self.events: List[str] = []

    def _load_policy(self) -> Dict[str, Any]:
        """Load security policy definitions from JSON."""
        try:
            with open(self.policy_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            self.logger.warning("Security policy not found or invalid")
            return {}

    def register_rule(self, rule: Callable[[], bool]) -> None:
        """Register an additional boolean rule."""
        self.rules.append(rule)

    def log_event(self, message: str) -> None:
        """Record a compliance event."""
        self.events.append(message)
        self.logger.info(message)

    def validate_environment(self) -> Dict[str, Any]:
        """Validate current environment configuration."""
        result = validate_environment_compliance()
        if result.get("compliance_status") != "FULL":
            self.log_event("environment_non_compliant")
        return result

    def validate_operation(self, *, path: str | None = None, command: str | None = None) -> bool:
        """Validate an operation prior to execution."""
        ok = validate_enterprise_operation(target_path=path, command=command)
        if not ok:
            self.log_event("operation_policy_violation")
        return ok

    def run_checks(self) -> bool:
        """Run all checks and enforce violation thresholds."""
        violations = 0
        env = self.validate_environment()
        if env.get("compliance_status") != "FULL":
            violations += 1

        for rule in self.rules:
            try:
                if not rule():
                    violations += 1
                    self.log_event(f"rule_failed:{rule.__name__}")
            except Exception as exc:  # pragma: no cover - defensive log
                violations += 1
                self.log_event(f"rule_error:{rule.__name__}:{exc}")

        if violations > self.threshold:
            self._trigger_compliance_backup()
            raise ComplianceError(f"Compliance threshold exceeded: {violations} > {self.threshold}")
        return violations == 0

    # --- integration helpers -------------------------------------------------

    def _trigger_compliance_backup(self) -> None:
        """Schedule a backup and log rollback details on violations.

        This method integrates the compliance checker with the session
        management and disaster recovery modules to provide a unified security
        posture. It performs a zero-byte file check, triggers a backup, logs a
        rollback record, and emits a compliance event for dashboard
        visualization.
        """

        from unified_disaster_recovery_system import (
            UnifiedDisasterRecoverySystem,
            log_backup_event,
        )
        from unified_session_management_system import ensure_no_zero_byte_files

        workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
        system = UnifiedDisasterRecoverySystem(str(workspace))
        try:
            with ensure_no_zero_byte_files(workspace):
                backup_file = system.schedule_backups()
        except RuntimeError:
            backup_file = system.schedule_backups()
        _log_rollback(str(workspace), str(backup_file))
        log_backup_event("compliance_violation", {"backup": str(backup_file)})


__all__ = ["ComplianceChecker", "ComplianceError"]
