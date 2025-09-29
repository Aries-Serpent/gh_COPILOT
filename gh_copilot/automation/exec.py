from __future__ import annotations

"""Subprocess execution helper with local-only safeguards."""

import shlex
import subprocess
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

    argv = _flatten_cmd(cmd)
    _deny_network_tools(argv)

    proc = subprocess.run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    result = {
        "code": int(proc.returncode),
        "out": proc.stdout or "",
        "err": proc.stderr or "",
    }
    if proc.returncode != 0 and not allow_fail:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(argv)}\n{proc.stderr or ''}"
        )
    return result

