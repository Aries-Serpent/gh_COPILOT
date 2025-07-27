"""Reusable templates embodying core lessons learned patterns.

This module exposes templates that reflect the major enterprise patterns
documented in :mod:`docs.COMPREHENSIVE_LESSONS_LEARNED_IMPLEMENTATION`.
These templates can be inserted into database-driven generators or used
directly by automation scripts.
"""

from __future__ import annotations

from typing import Dict

LESSON_TEMPLATES: Dict[str, str] = {
    "database_first": """
class DatabaseFirstOperator:
    def __init__(self, workspace_path: str = os.getenv('GH_COPILOT_WORKSPACE', str(Path.cwd()))):
        self.production_db = Path(workspace_path) / 'databases' / 'production.db'
        self.patterns = self.load_organization_patterns_from_db()
""",
    "autonomous_error_prevention": """
class AutonomousFileProtection:
    NEVER_MOVE_PATTERNS = [
        '*.py in root directory',
        'COPILOT_NAVIGATION_MAP.json',
        'requirements.txt'
    ]

    def validate_before_move(self, file_path: str) -> bool:
        if self.is_executable_file(file_path):
            return False
        if self.is_critical_config(file_path):
            return False
        return True
""",
    "visual_processing": """
def enterprise_operation(operation_name: str, items: Iterable[str]):
    with tqdm(total=len(items), desc=f'\U0001f504 {operation_name}', unit='item') as bar:
        for item in items:
            process_item(item)
            bar.update(1)
""",
    "autonomous_self_healing": """
class SelfHealingSystem:
    def detect_and_heal(self, error_type: str) -> Dict[str, Any]:
        if error_type == 'file_misclassification':
            return self.heal_file_misclassification()
        if error_type == 'config_dependency_break':
            return self.heal_config_dependencies()
        return self.apply_general_healing_strategy(error_type)
""",
}


def get_lesson_templates() -> Dict[str, str]:
    """Return a copy of the lesson templates dictionary."""
    return LESSON_TEMPLATES.copy()
