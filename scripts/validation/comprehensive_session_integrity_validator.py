#!/usr/bin/env python3
"""Comprehensive Session Integrity Validator.

Runs a full suite of session-related checks using the modular
``SessionProtocolValidator`` and emits a JSON report summarizing the
results. The script is referenced in the documentation as a quick way to
verify workspace integrity before starting a Copilot session.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from validation.protocols.session import SessionProtocolValidator

LOGGER = logging.getLogger(__name__)


def run_validation(workspace: Optional[str] = None) -> Tuple[Dict[str, object], bool]:
    """Run comprehensive session validation.

    Parameters
    ----------
    workspace:
        Optional path to the workspace to validate. Defaults to the current
        working directory.

    Returns
    -------
    Tuple[Dict[str, object], bool]
        A tuple containing the report dictionary and a boolean indicating
        success.
    """
    validator = SessionProtocolValidator(workspace)
    result = validator.validate_comprehensive_session()

    report = {
        "timestamp": datetime.now().isoformat(),
        "workspace": str(validator.workspace_path),
        "status": result.status.value,
        "message": result.message,
        "errors": result.errors,
        "warnings": result.warnings,
        "details": result.details,
    }

    return report, result.is_success


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    LOGGER.info("Running comprehensive session integrity validation...")

    report, success = run_validation()

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / f"session_integrity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    if success:
        LOGGER.info("Session integrity validation passed")
    else:
        LOGGER.error("Session integrity validation failed")

    LOGGER.info(f"Report saved to: {report_file}")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
