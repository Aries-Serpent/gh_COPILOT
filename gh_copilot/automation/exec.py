from __future__ import annotations

"""Subprocess execution helper with local-only safeguards."""

import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def _flatten_cmd(cmd: Union[str, List[str]]) -> List[str]:
    if isinstance(cmd, str):
        return shlex.split(cmd)
    return list(cmd)


def _deny_network_tools(argv: List[str]) -> None:
    lowered = [a.lower() for a in argv]
    banned = {"curl", "wget", "invoke-webrequest", "iwr"}
    for a in lowered:
        token = a.split("/")[-1].split("\\")[-1]
        if token in banned:
            raise RuntimeError(f"Networked tool invocation is not allowed: {token}")


def run_cmd(
    cmd: Union[str, List[str]],
    cwd: Optional[str] = None,
    allow_fail: bool = False,
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Run a command locally and capture output.

    Args:
        cmd: Command as string or argv list.
        cwd: Optional working directory.
        allow_fail: If False, non-zero exit codes raise ``RuntimeError``.
        timeout: Optional timeout in seconds.

    Returns:
        Dict with keys ``code`` (int), ``out`` (str), ``err`` (str).
    """

    if not cmd:
        raise ValueError("Command must not be empty")

    argv = _flatten_cmd(cmd)
    _deny_network_tools(argv)

    workdir = Path(cwd).resolve() if cwd else Path.cwd()
    env = os.environ.copy()
    env.setdefault("NO_NETWORK_EXEC", "1")

    proc = subprocess.run(
        argv,
        cwd=str(workdir),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        env=env,
    )
    result = {
        "code": int(proc.returncode),
        "out": proc.stdout or "",
        "err": proc.stderr or "",
        "cmd": " ".join(shlex.quote(part) for part in argv),
        "cwd": str(workdir),
    }
    if proc.returncode != 0 and not allow_fail:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(argv)}\n{proc.stderr or ''}"
        )
    return result

