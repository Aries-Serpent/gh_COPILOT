"""Simulate disaster recovery scenarios using the orchestrator."""

from __future__ import annotations

import argparse

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from disaster_recovery_orchestrator import DisasterRecoveryOrchestrator


def run_complete_failure(orchestrator: DisasterRecoveryOrchestrator) -> bool:
    """Run a simple backup and restore cycle to simulate a failure."""

    backup_file = orchestrator.run_backup_cycle()
    return orchestrator.run_recovery_cycle(backup_file)


def main() -> None:
    parser = argparse.ArgumentParser(description="Disaster recovery simulation")
    parser.add_argument(
        "--scenario",
        default="complete_failure",
        help="Simulation scenario to run",
    )
    args = parser.parse_args()

    orchestrator = DisasterRecoveryOrchestrator()

    if args.scenario == "complete_failure":
        success = run_complete_failure(orchestrator)
        print(f"Complete failure simulation success: {success}")
    else:
        raise ValueError(f"Unknown scenario: {args.scenario}")


if __name__ == "__main__":
    main()
