"""Builtin templates implementing core lessons learned patterns.

These reusable snippets provide baseline implementations for the
Database-First, Autonomous Error Prevention, Visual Processing,
Self-Healing and Dual Copilot validation patterns described in
``docs/COMPREHENSIVE_LESSONS_LEARNED_IMPLEMENTATION.md``.
"""

from __future__ import annotations

DATABASE_FIRST_TEMPLATE = """class DatabaseFirstOperator:
    def __init__(self, workspace_path: str = os.getenv('GH_COPILOT_WORKSPACE', str(Path.cwd()))):
        self.production_db = Path(workspace_path) / 'databases' / 'production.db'
        self.patterns = self.load_organization_patterns_from_db()

    def categorize_file(self, file_path: str) -> str:
        # LESSON LEARNED: Query database patterns FIRST
        db_pattern = self.query_database_pattern(file_path)
        if db_pattern:
            return db_pattern
        return self.apply_learned_classification(file_path)
"""


AUTONOMOUS_ERROR_PREVENTION_TEMPLATE = """class AutonomousFileProtection:
    NEVER_MOVE_PATTERNS = [
        '*.py in root directory',
        'COPILOT_NAVIGATION_MAP.json',
        'requirements.txt',
        'main.py',
        '*.exe files',
    ]

    def validate_before_move(self, file_path: str) -> bool:
        # LESSON LEARNED: Prevent executable misclassification
        if self.is_executable_file(file_path):
            return False  # NEVER move executable files
        if self.is_critical_config(file_path):
            return False  # NEVER move critical configs
        return True
"""


COMPREHENSIVE_VISUAL_PROCESSING_TEMPLATE = """def enterprise_operation(operation_name: str, total_items: int, items):
    # LESSON LEARNED: Always provide visual processing indicators
    from tqdm import tqdm

    with tqdm(total=total_items,
              desc=f'\U0001f504 {operation_name}',
              unit='items',
              bar_format='{l_bar}{bar}| {n}/{total} [{elapsed}<{remaining}]') as pbar:
        for item in items:
            process_item(item)
            pbar.update(1)
            pbar.set_description(f'\u2705 Processed: {item.name}')
"""


AUTONOMOUS_SELF_HEALING_TEMPLATE = """class SelfHealingSystem:
    def detect_and_heal(self, error_type: str) -> dict:
        # LESSON LEARNED: Autonomous correction mechanisms
        if error_type == 'file_misclassification':
            return self.heal_file_misclassification()
        elif error_type == 'config_dependency_break':
            return self.heal_config_dependencies()
        elif error_type == 'validation_gap':
            return self.heal_validation_gaps()
        return self.apply_general_healing_strategy(error_type)
"""


DUAL_COPILOT_VALIDATION_TEMPLATE = """def _initialize_copilot_integration(self):
    # LESSON LEARNED: Primary executor + secondary validator
    copilot_config = {
        'autonomous_mode': True,
        'auto_code_generation': True,
        'auto_documentation': True,
        'learning_integration': True,
    }
    # Implements DUAL COPILOT validation pattern
    # Validation results are recorded in copilot_interactions
"""


DEFAULT_TEMPLATES = [
    DATABASE_FIRST_TEMPLATE,
    AUTONOMOUS_ERROR_PREVENTION_TEMPLATE,
    COMPREHENSIVE_VISUAL_PROCESSING_TEMPLATE,
    AUTONOMOUS_SELF_HEALING_TEMPLATE,
    DUAL_COPILOT_VALIDATION_TEMPLATE,
]

__all__ = [
    "DATABASE_FIRST_TEMPLATE",
    "AUTONOMOUS_ERROR_PREVENTION_TEMPLATE",
    "COMPREHENSIVE_VISUAL_PROCESSING_TEMPLATE",
    "AUTONOMOUS_SELF_HEALING_TEMPLATE",
    "DUAL_COPILOT_VALIDATION_TEMPLATE",
    "DEFAULT_TEMPLATES",
    "get_pattern_templates",
    "get_named_templates",
]


def get_pattern_templates() -> list[str]:
    """Return built-in template strings."""
    return DEFAULT_TEMPLATES.copy()


def get_named_templates() -> dict[str, str]:
    """Return templates keyed by descriptive names."""

    return {
        "database_first_pattern": DATABASE_FIRST_TEMPLATE,
        "autonomous_error_prevention": AUTONOMOUS_ERROR_PREVENTION_TEMPLATE,
        "visual_processing": COMPREHENSIVE_VISUAL_PROCESSING_TEMPLATE,
        "self_healing": AUTONOMOUS_SELF_HEALING_TEMPLATE,
        "dual_copilot": DUAL_COPILOT_VALIDATION_TEMPLATE,
    }
