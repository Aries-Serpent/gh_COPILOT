"""Template engine package."""

from .auto_generator import (
    TemplateAutoGenerator,
    DEFAULT_ANALYTICS_DB,
    DEFAULT_COMPLETION_DB,
)
from .template_synchronizer import synchronize_templates
from .pattern_clustering_sync import PatternClusteringSync
from .workflow_enhancer import TemplateWorkflowEnhancer
from .placeholder_utils import (
    find_placeholders,
    replace_placeholders,
    DEFAULT_PRODUCTION_DB as PLACEHOLDER_PRODUCTION_DB,
    DEFAULT_TEMPLATE_DOC_DB as PLACEHOLDER_TEMPLATE_DOC_DB,
    DEFAULT_ANALYTICS_DB as PLACEHOLDER_ANALYTICS_DB,
)
from .pattern_mining_engine import extract_patterns, mine_patterns
from .objective_similarity_scorer import (
    compute_objective_similarity,
    validate_similarity,
)
from .template_placeholder_remover import remove_placeholders, validate_removals

__all__ = [
    "TemplateAutoGenerator",
    "synchronize_templates",
    "DEFAULT_ANALYTICS_DB",
    "DEFAULT_COMPLETION_DB",
    "PatternClusteringSync",
    "TemplateWorkflowEnhancer",
    "find_placeholders",
    "replace_placeholders",
    "PLACEHOLDER_PRODUCTION_DB",
    "PLACEHOLDER_TEMPLATE_DOC_DB",
    "PLACEHOLDER_ANALYTICS_DB",
    "extract_patterns",
    "mine_patterns",
    "compute_objective_similarity",
    "validate_similarity",
    "remove_placeholders",
    "validate_removals",
]
