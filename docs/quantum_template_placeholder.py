"""Quantum-enabled documentation template generator.

This module loads templates from ``production.db`` and ranks them using
quantum-inspired scoring. If the optional :class:`~quantum.orchestration.executor.QuantumExecutor`
is present, its algorithms are used for ranking. Otherwise a classical fallback
score is applied. The API exposes :func:`generate_default_templates` for
automated template creation.
"""

from pathlib import Path
from typing import Any, List, Tuple

from template_engine.auto_generator import TemplateAutoGenerator

try:
    from quantum.orchestration.executor import QuantumExecutor
except Exception:  # pragma: no cover - optional quantum deps
    QuantumExecutor = None


def generate_default_templates(db_path: Path = Path("databases/production.db")) -> None:
    """Generate documentation templates using quantum-inspired scoring.

    Parameters
    ----------
    db_path : Path
        Path to the production database. The function queries existing
        templates and patterns from this database to create default
        documentation templates. If quantum modules are available,
        quantum-inspired scoring will be applied to select templates.
    """
    generator = TemplateAutoGenerator(db_path, db_path)
    representatives = generator.get_cluster_representatives()
    if not representatives:
        print("No templates found")
        return

    scored = []
    if QuantumExecutor:
        executor = QuantumExecutor()
        for rep in representatives:
            try:
                result = executor.execute_algorithm("quantum_similarity_score", text=rep)
                score = float(result.get("stats", {}).get("score", 0))
            except Exception:
                score = generator._quantum_score(rep)
            scored.append((rep, score))
    else:
        scored = [(rep, generator._quantum_score(rep)) for rep in representatives]

    for rep, score in sorted(scored, key=lambda s: s[1], reverse=True):
        print(f"{score:.4f}: {rep}")


if __name__ == "__main__":  # pragma: no cover
    for tmpl in generate_default_templates():
        print(tmpl)
