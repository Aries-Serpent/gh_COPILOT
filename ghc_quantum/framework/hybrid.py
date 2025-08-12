"""Utility helpers for running quantum routines with classical fallbacks.

These helpers complement :mod:`quantum.framework.executor` by providing a
lightweight way to execute a circuit-building callable and transparently fall
back to a classical implementation when quantum execution fails.
"""

from __future__ import annotations

from typing import Any, Callable

from .executor import QuantumExecutor


def run_with_fallback(
    circuit_builder: Callable[[], Any],
    classical_fallback: Callable[[], Any],
    *,
    executor: QuantumExecutor | None = None,
    **kwargs: Any,
) -> Any:
    """Execute a quantum routine and fall back to ``classical_fallback``.

    Parameters
    ----------
    circuit_builder:
        Callable returning a circuit representation consumable by
        :class:`QuantumExecutor`.
    classical_fallback:
        Callable returning a classical approximation used when quantum
        execution fails.
    executor:
        Optional :class:`QuantumExecutor` instance. A new executor is created
        when omitted.
    **kwargs:
        Additional keyword arguments forwarded to
        :meth:`QuantumExecutor.run`.

    Returns
    -------
    Any
        Result from ghc_quantum execution or classical fallback.
    """

    exec_ = executor or QuantumExecutor()
    try:
        circuit = circuit_builder()
        return exec_.run(circuit, **kwargs)
    except Exception:
        return classical_fallback()


__all__ = ["run_with_fallback"]

