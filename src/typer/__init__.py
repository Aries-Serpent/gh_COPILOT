"""Minimal Typer stub used for testing.

This lightweight implementation provides just enough features of the
`typer` package for the project's test suite. It defines a small command
registry, basic option and argument helpers, and a simple ``echo``
function. The real Typer package offers a far richer feature set; this
module is only intended as a local stand-in when the external dependency
is unavailable.
"""

from __future__ import annotations

import sys
from typing import Any, Callable, Dict


class Exit(Exception):
    """Signal an exit from a command with a status code."""

    def __init__(self, code: int = 0) -> None:
        self.code = code


class BadParameter(Exception):
    """Raised when command line arguments are invalid."""


def Option(default: Any = None, *args: Any, **_: Any) -> Any:
    """Return the default value for a CLI option."""

    return default


def Argument(default: Any = ..., **_: Any) -> Any:
    """Return the default value for a CLI argument."""

    return default


def echo(message: str, err: bool = False) -> None:
    """Write *message* to standard output or error."""

    stream = sys.stderr if err else sys.stdout
    print(message, file=stream)


class Typer:
    """Very small command registry compatible with ``CliRunner``."""

    def __init__(self, *, help: str | None = None, **_: Any) -> None:  # noqa: D401
        self.help = help
        self.commands: Dict[str, Callable[..., Any]] = {}

    def command(self, name: str | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator registering *func* under *name* as a command."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            cmd_name = name or func.__name__
            self.commands[cmd_name] = func
            return func

        return decorator


from .testing import CliRunner, Result  # noqa: E402  (re-export convenience)

__all__ = [
    "Argument",
    "BadParameter",
    "CliRunner",
    "Exit",
    "Option",
    "Result",
    "Typer",
    "echo",
]
