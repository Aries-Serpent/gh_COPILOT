from __future__ import annotations

"""Quantum-enhanced utilities for the Flask web GUI.

This module exposes :class:`QuantumEnhancedFramework`, a thin wrapper around
the core quantum toolkit located under the :mod:`quantum` package. It attempts
to import the heavy quantum dependencies at runtime and falls back to safe
placeholders when those libraries are unavailable. The class is intentionally
minimal – it only surfaces a small subset of functionality required by the web
dashboard while keeping import overhead and failure modes contained.

The framework provides two primary capabilities:

``run_algorithm``
    Execute a registered quantum algorithm via
    :class:`quantum.quantum_integration_orchestrator.QuantumIntegrationOrchestrator`.

``score_templates``
    Delegate to :func:`quantum.quantum_optimizer.score_templates` when present
    to rank templates using quantum-informed heuristics.

Both methods return sensible default values when quantum support is missing so
that callers can depend on a stable API regardless of the environment.
"""

import importlib
import logging
from typing import Any, Callable, Dict, Iterable, List, Tuple, TypeVar

from flask import Blueprint, jsonify, request

T = TypeVar("T")

__all__ = ["QuantumEnhancedFramework", "quantum_bp"]


class QuantumEnhancedFramework:
    """Interface layer between the web GUI and quantum modules.

    The class attempts to import ghc_quantum modules lazily. If imports fail (for
    example, when optional quantum libraries such as Qiskit are not installed),
    the class exposes graceful fallbacks that return deterministic placeholder
    values instead of raising ImportError.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._setup_orchestrator()
        self._setup_optimizer()

    # ------------------------------------------------------------------
    # Setup Helpers
    # ------------------------------------------------------------------
    def _setup_orchestrator(self) -> None:
        """Initialize the quantum algorithm orchestrator if available."""

        try:
            orchestrator_mod = importlib.import_module(
                "ghc_quantum.quantum_integration_orchestrator"
            )
            orchestrator_cls = getattr(
                orchestrator_mod, "QuantumIntegrationOrchestrator"
            )
            self.orchestrator = orchestrator_cls()
            self.quantum_enabled = True
            self.logger.debug("Quantum orchestrator initialized")
        except Exception as exc:  # pragma: no cover - import side effects
            self.orchestrator = None
            self.quantum_enabled = False
            self.logger.warning(
                "Quantum modules unavailable, falling back to classical mode: %s",
                exc,
            )

    def _setup_optimizer(self) -> None:
        """Import quantum scoring utilities when present."""

        try:
            optimizer_mod = importlib.import_module("ghc_quantum.quantum_optimizer")
            self._score_templates = getattr(optimizer_mod, "score_templates")
            self.logger.debug("Quantum optimizer utilities loaded")
        except Exception as exc:  # pragma: no cover - import side effects
            self._score_templates = None
            self.logger.warning(
                "Quantum scoring unavailable, using uniform weights: %s", exc
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def available_algorithms(self) -> List[str]:
        """Return algorithms registered with the orchestrator.

        Returns an empty list when quantum support is missing.
        """

        if self.orchestrator is None:
            return []
        return self.orchestrator.available_algorithms()

    def run_algorithm(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a quantum algorithm by name.

        When quantum modules are unavailable a deterministic placeholder result
        is returned so that callers can continue operating without branching.
        """

        if self.orchestrator is None:
            return {
                "status": "unavailable",
                "detail": "Quantum libraries not installed",
            }
        return self.orchestrator.run_algorithm(name, **kwargs)

    def score_templates(self, templates: Iterable[str], tag: str) -> List[Tuple[str, float]]:
        """Rank templates using quantum heuristics if possible.

        Falls back to uniform weights when the quantum optimizer is missing.
        """

        if self._score_templates is None:
            return [(t, 1.0) for t in templates]
        return self._score_templates(list(templates), tag)

    def execute_with_fallback(
        self,
        classical_fn: Callable[..., T],
        quantum_fn: Callable[..., T] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute a quantum function and gracefully fall back.

        Parameters
        ----------
        classical_fn:
            Function to execute when quantum support is unavailable or fails.
        quantum_fn:
            Optional quantum implementation. If ``None`` the ``classical_fn``
            is used directly.

        Returns
        -------
        T
            Result of the successfully executed function.
        """

        chosen = quantum_fn if (quantum_fn and self.quantum_enabled) else None
        if chosen is not None:
            try:
                return chosen(*args, **kwargs)
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning(
                    "Quantum execution failed, falling back to classical: %s",
                    exc,
                )
        return classical_fn(*args, **kwargs)


# ----------------------------------------------------------------------
# Flask Blueprint Endpoints
# ----------------------------------------------------------------------
quantum_bp = Blueprint("quantum", __name__)
framework = QuantumEnhancedFramework()


@quantum_bp.get("/algorithms")
def list_algorithms() -> Any:
    """Expose available quantum algorithms via API."""
    return jsonify({"algorithms": framework.available_algorithms()})


@quantum_bp.post("/run/<name>")
def run_algorithm_endpoint(name: str) -> Any:
    """Run a quantum algorithm with graceful fallback."""
    payload = request.get_json(silent=True) or {}
    return jsonify(framework.run_algorithm(name, **payload))


@quantum_bp.post("/score")
def score_templates_endpoint() -> Any:
    """Score templates using quantum heuristics when available."""
    payload = request.get_json(silent=True) or {}
    templates = payload.get("templates", [])
    tag = payload.get("tag", "")
    scores = framework.score_templates(templates, tag)
    return jsonify({"scores": scores})
