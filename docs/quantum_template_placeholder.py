"""Quantum-Integrated Documentation Template Generator.

Generate documentation templates using database-first logic and optional
quantum-inspired scoring. Templates and patterns are loaded from
``production.db`` and ranked before output.
"""

from pathlib import Path
from typing import Any, List, Tuple

from template_engine.auto_generator import TemplateAutoGenerator

try:
    from quantum.orchestration.executor import QuantumExecutor
except Exception:  # pragma: no cover - optional quantum deps
    QuantumExecutor = None


def _score(executor: Any | None, text: str) -> float:
    """Return a quantum-inspired score for ``text``."""
    if executor:
        try:
            return float(executor.score_text(text))
        except Exception:
            pass
    return float(len(text))


def generate_default_templates(db_path: Path = Path("databases/production.db")) -> List[str]:
    """Generate scored documentation templates.

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
    executor = QuantumExecutor() if QuantumExecutor else None
    scored: List[Tuple[str, float]] = [(rep, _score(executor, rep)) for rep in reps]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [template for template, _ in scored]


if __name__ == "__main__":  # pragma: no cover
    for tmpl in generate_default_templates():
        print(tmpl)
