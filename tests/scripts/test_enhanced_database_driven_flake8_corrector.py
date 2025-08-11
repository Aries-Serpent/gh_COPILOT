import importlib


def test_import_module():
    """Smoke test to ensure the corrector module imports without errors."""
    importlib.import_module('scripts.utilities.enhanced_database_driven_flake8_corrector')

