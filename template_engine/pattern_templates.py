"""Builtin templates derived from COMPREHENSIVE_LESSONS_LEARNED_IMPLEMENTATION.

These templates embody the core learning patterns documented in
``docs/COMPREHENSIVE_LESSONS_LEARNED_IMPLEMENTATION.md``.
They can be loaded by the template engine or other modules.
"""

from __future__ import annotations

from typing import Dict, List

_DATABASE_FIRST = """
class DatabaseFirstOperator:
    def __init__(self, workspace_path: str = os.getenv('GH_COPILOT_WORKSPACE', str(Path.cwd()))):
        self.production_db = workspace_path + '/databases/production.db'
        self.patterns = self.load_organization_patterns_from_db()

    def categorize_file(self, file_path: str) -> str:
        db_pattern = self.query_database_pattern(file_path)
        if db_pattern:
            return db_pattern
        return self.apply_learned_classification(file_path)
"""

_AUTONOMOUS_ERROR_PREVENTION = """
class AutonomousFileProtection:
    NEVER_MOVE_PATTERNS = [
        '*.py in root directory',
        'COPILOT_NAVIGATION_MAP.json',
        'requirements.txt',
        'main.py',
        '*.exe files',
    ]

    def validate_before_move(self, file_path: str) -> bool:
        if self.is_executable_file(file_path):
            return False
        if self.is_critical_config(file_path):
            return False
        return True
"""

_VISUAL_PROCESSING = """
def enterprise_operation(operation_name: str, total_items: int):
    with tqdm(
        total=total_items,
        desc=f'\ud83d\udd04 {operation_name}',
        unit='items',
        bar_format='{l_bar}{bar}| {n}/{total} [{elapsed}<{remaining}]',
    ) as pbar:
        for item in items:
            process_item(item)
            pbar.update(1)
            pbar.set_description(f'\u2705 Processed: {item.name}')
"""

_SELF_HEALING = """
class SelfHealingSystem:
    def detect_and_heal(self, error_type: str) -> Dict[str, Any]:
        if error_type == 'file_misclassification':
            return self.heal_file_misclassification()
        elif error_type == 'config_dependency_break':
            return self.heal_config_dependencies()
        elif error_type == 'validation_gap':
            return self.heal_validation_gaps()
        return self.apply_general_healing_strategy(error_type)
"""


def get_named_templates() -> Dict[str, str]:
    """Return a mapping of template names to template content."""
    return {
        "database_first_pattern": _DATABASE_FIRST,
        "autonomous_error_prevention_pattern": _AUTONOMOUS_ERROR_PREVENTION,
        "visual_processing_pattern": _VISUAL_PROCESSING,
        "self_healing_pattern": _SELF_HEALING,
    }


def get_pattern_templates() -> List[str]:
    """Return a list of all pattern templates."""
    return list(get_named_templates().values())


async def async_get_pattern_templates() -> List[str]:
    """Asynchronous wrapper returning ``get_pattern_templates`` results."""
    return get_pattern_templates()


__all__ = [
    "get_named_templates",
    "get_pattern_templates",
    "async_get_pattern_templates",
]
