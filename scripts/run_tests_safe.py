from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


def _has_pytest_cov() -> bool:
    return importlib.util.find_spec("pytest_cov") is not None


def _has_json_report() -> bool:
    return importlib.util.find_spec("pytest_jsonreport") is not None


def main() -> int:
    args = list(sys.argv[1:])
    cmd = ["pytest"]
    if _has_json_report():
        cmd.append("--json-report")
    if not _has_pytest_cov():
        addopts = os.environ.get("PYTEST_ADDOPTS", "").split()
        addopts = [opt for opt in addopts if not opt.startswith("--cov")]
        os.environ["PYTEST_ADDOPTS"] = " ".join(addopts)
        if "-q" not in cmd:
            cmd.insert(1, "-q")
    cmd.extend(args)
    proc = subprocess.run(cmd, text=True)
    report = Path(".report.json")
    summary = {"returncode": proc.returncode}
    if report.exists():
        try:
            data = json.loads(report.read_text(encoding="utf-8"))
            summary.update(data.get("summary", {}))
        except Exception:
            pass
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/test_failures_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return proc.returncode


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

