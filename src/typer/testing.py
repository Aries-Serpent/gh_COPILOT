"""Testing helpers for the local Typer stub."""

from __future__ import annotations

import contextlib
import inspect
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from . import Exit


@dataclass
class Result:
    """Result of a CLI invocation."""

    exit_code: int
    stdout: str


class CliRunner:
    """Invoke commands registered on a ``Typer`` instance."""

    def invoke(self, app, args: list[str]) -> Result:
        if not args:
            raise ValueError("no command provided")

        cmd_name, *params = args
        func = app.commands.get(cmd_name)
        if func is None:
            return Result(1, "")

        positional: list[Any] = []
        kwargs: Dict[str, Any] = {}
        it = iter(params)
        for token in it:
            if token.startswith("--"):
                key = token[2:].replace("-", "_")
                try:
                    value = next(it)
                except StopIteration:
                    value = "True"
                kwargs[key] = value
            else:
                positional.append(token)

        sig = inspect.signature(func)
        def _maybe_path(name: str, value: str) -> Any:
            if isinstance(value, str) and (name.endswith("_dir") or name.endswith("_path") or name.endswith("_db") or name in {"workspace", "src_dir", "db", "out_dir", "analytics_db", "source_db"}):
                return Path(value)
            return value

        bound_pos: list[Any] = []
        param_names = list(sig.parameters.keys())
        for i, value in enumerate(positional):
            name = param_names[i]
            bound_pos.append(_maybe_path(name, value))

        converted_kwargs: Dict[str, Any] = {}
        for key, value in kwargs.items():
            converted_kwargs[key] = _maybe_path(key, value)

        buf = io.StringIO()
        exit_code = 0
        try:
            with contextlib.redirect_stdout(buf):
                func(*bound_pos, **converted_kwargs)
        except Exit as exc:  # pragma: no cover - captured as exit code
            exit_code = exc.code

        return Result(exit_code, buf.getvalue())
