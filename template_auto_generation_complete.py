#!/usr/bin/env python3
"""TemplateAutoGenerationComplete
================================

Generate and regenerate code templates using stored patterns from the
``template_engine`` databases. Patterns are clustered and the most
representative pattern of each cluster is emitted as a new template.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from tqdm import tqdm

from template_engine.auto_generator import TemplateAutoGenerator

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
    "progress": "[PROGRESS]",
}

logger = logging.getLogger(__name__)


class TemplateSynthesisEngine:
    """Synthesize templates using stored pattern databases."""

    def __init__(self, analytics_db: Path | None = None, completion_db: Path | None = None) -> None:
        self.generator = TemplateAutoGenerator(
            analytics_db or Path("analytics.db"), completion_db or Path(
                "databases/template_completion.db")
        )

    def synthesize_templates(self) -> List[str]:
        """Return regenerated templates from each pattern cluster."""
        templates: List[str] = []
        if not self.generator.patterns:
            return templates
        clusters = self.generator.cluster_model
        if clusters is None or self.generator.pattern_matrix is None:
            return templates
        with tqdm(total=clusters.n_clusters, desc=f"{TEXT_INDICATORS['progress']} synth") as bar:
            for cluster_id in range(clusters.n_clusters):
                indices = [i for i, label in enumerate(clusters.labels_) if label == cluster_id]
                if not indices:
                    bar.update(1)
                    continue
                representative = indices[0]
                templates.append(self.generator.patterns[representative])
                bar.update(1)
        return templates


if __name__ == "__main__":  # pragma: no cover - manual execution
    logging.basicConfig(level=logging.INFO)
    engine = TemplateSynthesisEngine()
    for tmpl in engine.synthesize_templates():
        print(tmpl)
