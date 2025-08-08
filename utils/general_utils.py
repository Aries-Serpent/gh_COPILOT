"""General utility functions for script entrypoints."""

from pathlib import Path
import shlex
import subprocess
from typing import Any, Callable


BUFFER_SCRIPT = Path(__file__).resolve().parent.parent / "tools" / "shell_buffer_manager.sh"


def operations_main(main_func: Callable[..., Any]) -> None:
    """Execute ``main_func`` and print its result if not ``None``."""
    result = main_func()
    if result is not None:
        print(result)


def safe_shell_execute(command: str) -> str:
    """Run ``command`` with 4 KB line cutoff and overflow logging.

    Output beyond 4 KB per line is redirected to files under
    ``/tmp/gh_copilot_sessions``. A summary of overflow locations is printed
    after execution. The truncated standard output is returned.
    """

    cmd = f"bash -c {shlex.quote(command)} | {BUFFER_SCRIPT}"
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    overflow_files = [line.split(":", 1)[1] for line in proc.stderr.splitlines() if line.startswith("OVERFLOW:")]
    if overflow_files:
        print("overflow logged to:")
        for path in overflow_files:
            print(f"  - {path}")
    return proc.stdout
