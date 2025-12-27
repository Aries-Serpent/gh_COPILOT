from __future__ import annotations

"""Core orchestration primitives for phased automation.

Only Python stdlib is used.

Examples:
    Build a small three-phase run in dry-run mode::

        def prep(dry_run: bool = True) -> None:
            pass

        def analyze() -> None:
            pass

        def finalize(dry_run: bool = True) -> None:
            pass

        phases = [
            StepCtx(name="Prepare", desc="init", fn=prep),
            StepCtx(name="Analyze", desc="scan", fn=analyze),
            StepCtx(name="Finalize", desc="wrap", fn=finalize),
        ]
        result = run_phases(phases, dry_run=True)
        assert result.ok

Notes:
- Aligns with snapshot guardrails: dry-run by default; never modifies
  `.github/workflows`; safe to import without optional heavy dependencies.
"""

import inspect
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence


@dataclass
class StepCtx:
    """A single step/phase context for orchestration.

    Attributes:
        name: Human-readable step name.
        desc: Short description of the step.
        fn:   Callable to execute for this step. If the callable accepts a
              ``dry_run`` keyword parameter, it will be passed the current
              dry-run flag.
        weight: Relative weight for progress accounting (not enforced here).
        enabled: If False, the step is skipped.
        dry_run_ok: If False and in dry-run mode, the step is skipped.
    """

    name: str
    desc: str
    fn: Callable[..., Any]
    weight: int = 1
    enabled: bool = True
    dry_run_ok: bool = True


@dataclass
class ExecutionResult:
    """Result of running a sequence of phases."""

    phases_completed: int
    ok: bool
    logs: List[Dict[str, Any]]
    messages: List[str] = field(default_factory=list)


@dataclass
class RunArtifacts:
    """Paths to artifacts produced by a run (if any)."""

    ndjson_log: str
    reports: List[str]


def _supports_kw(fn: Callable[..., Any], kw_name: str) -> bool:
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return False
    for p in sig.parameters.values():
        if p.kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD) and p.name == kw_name:
            return True
        if p.kind == p.VAR_KEYWORD:
            return True
    return False


def run_phases(phases: List[StepCtx], dry_run: bool = True) -> ExecutionResult:
    """Run the provided phases in order, respecting dry-run.

    Each phase is executed if ``enabled`` and if either not dry-run or the step
    allows dry-run via ``dry_run_ok``. If the phase function accepts a
    ``dry_run`` keyword parameter, it is passed the current ``dry_run`` value.

    All timings and basic results are collected into the logs. Exceptions are
    captured and logged; execution proceeds to subsequent steps to maximize
    coverage in dry-run simulations.
    """

    logs: List[Dict[str, Any]] = []
    messages: List[str] = []
    phases_completed = 0
    overall_ok = True

    for step in phases:
        start = time.time()
        entry: Dict[str, Any] = {
            "name": step.name,
            "desc": step.desc,
            "enabled": step.enabled,
            "dry_run": dry_run,
            "dry_run_ok": step.dry_run_ok,
            "ok": False,
            "error": None,
            "started_at": start,
            "ended_at": None,
            "duration_sec": None,
        }

        if not step.enabled:
            entry["ok"] = True
            entry["skipped"] = True
            end = time.time()
            entry["ended_at"] = end
            entry["duration_sec"] = round(end - start, 6)
            logs.append(entry)
            messages.append(f"skip:{step.name}:disabled")
            continue

        if dry_run and not step.dry_run_ok:
            entry["ok"] = True
            entry["skipped_due_to_dry_run"] = True
            end = time.time()
            entry["ended_at"] = end
            entry["duration_sec"] = round(end - start, 6)
            logs.append(entry)
            messages.append(f"skip:{step.name}:dry_run_blocked")
            phases_completed += 1
            continue

        try:
            if _supports_kw(step.fn, "dry_run"):
                step.fn(dry_run=dry_run)
            else:
                step.fn()
            entry["ok"] = True
            outcome = "done"
        except Exception as exc:  # noqa: BLE001
            entry["ok"] = False
            entry["error"] = f"{type(exc).__name__}: {exc}"
            overall_ok = False
            outcome = "error"
        finally:
            end = time.time()
            entry["ended_at"] = end
            entry["duration_sec"] = round(end - start, 6)
            logs.append(entry)
            phases_completed += 1
            mode = "dry_run" if dry_run else "apply"
            messages.append(f"{outcome}:{step.name}:{mode}")

    return ExecutionResult(phases_completed=phases_completed, ok=overall_ok, logs=logs, messages=messages)



def persist_messages_to_compliance(
    result: ExecutionResult,
    *,
    workspace: Optional[str | Path] = None,
    db_path: Optional[Path] = None,
    row_id: Optional[int] = None,
    limit: int = 50,
) -> None:
    """Persist run phase messages into compliance metrics history."""

    if not result.messages:
        return

    workspace_arg = workspace
    if isinstance(workspace_arg, Path):
        workspace_arg = str(workspace_arg)

    try:
        from scripts.compliance.update_compliance_metrics import append_run_phase_messages
    except ModuleNotFoundError:
        return
    except Exception:  # noqa: BLE001
        import warnings

        warnings.warn(
            "Failed to import append_run_phase_messages; automation messages not recorded.",
            RuntimeWarning,
            stacklevel=2,
        )
        return

    try:
        append_run_phase_messages(
            result.messages,
            workspace=workspace_arg,
            db_path=db_path,
            row_id=row_id,
            limit=limit,
        )
    except Exception:  # noqa: BLE001
        import warnings

        warnings.warn(
            "Failed to persist automation messages to compliance metrics.",
            RuntimeWarning,
            stacklevel=2,
        )


