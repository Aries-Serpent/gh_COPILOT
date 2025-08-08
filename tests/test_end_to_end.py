from pathlib import Path
import sqlite3

from web_gui.scripts.flask_apps.quantum_enhanced_framework import (
    QuantumEnhancedFramework,
)


def test_end_to_end_flow() -> None:
    """Basic end-to-end workflow touches database and quantum layer."""
    db_path = Path("databases/production.db")
    with sqlite3.connect(db_path) as conn:
        conn.execute("SELECT 1")
    framework = QuantumEnhancedFramework()
    result = framework.run_algorithm("noop")
    assert isinstance(result, dict)


def test_algorithms_list_not_none() -> None:
    """Quantum framework should provide an algorithm list."""
    framework = QuantumEnhancedFramework()
    assert isinstance(framework.available_algorithms(), list)

