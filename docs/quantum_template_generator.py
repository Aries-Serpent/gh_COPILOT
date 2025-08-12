"""Quantum-enabled documentation template generator.

This module loads templates from ``production.db`` and ranks them using
quantum-inspired scoring. If the optional :class:`~quantum.orchestration.executor.QuantumExecutor`
is present, its algorithms are used for ranking. Otherwise a classical fallback
score is applied. The API exposes :func:`generate_default_templates` for
automated template creation.
"""

from pathlib import Path
from typing import List, Tuple

from template_engine.auto_generator import TemplateAutoGenerator

try:
    from ghc_quantum.orchestration.executor import QuantumExecutor
except Exception:  # pragma: no cover - optional quantum deps
    QuantumExecutor = None


def generate_default_templates(db_path: Path = Path("databases/production.db")) -> List[Tuple[str, float]]:
    """Return scored documentation templates using quantum-inspired ranking.

    Parameters
    ----------
    db_path : Path
        Path to the production database. The function queries existing
        templates and patterns from this database to create default
        documentation templates. If quantum modules are available,
        quantum-inspired scoring will be applied to select templates.
    """
    generator = TemplateAutoGenerator(db_path, db_path)
    reps = generator.get_cluster_representatives()
    if not reps:
        return []

    scored: List[Tuple[str, float]] = []
    if QuantumExecutor:
        executor = QuantumExecutor()
        for rep in reps:
            try:
                result = executor.execute_algorithm("quantum_similarity_score", text=rep)
                score = float(result.get("stats", {}).get("score", 0))
            except Exception:
                score = generator._quantum_score(rep)
            scored.append((rep, score))
    else:
        scored = [(rep, generator._quantum_score(rep)) for rep in reps]

    scored.sort(key=lambda s: s[1], reverse=True)
    return scored


if __name__ == "__main__":  # pragma: no cover
    for text, score in generate_default_templates():
        print(f"{score:.4f}: {text}")
