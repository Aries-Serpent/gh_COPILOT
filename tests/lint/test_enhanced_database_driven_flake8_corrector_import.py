"""Ensure the enhanced corrector module imports without errors."""

import importlib


def test_import() -> None:
    importlib.import_module("enhanced_database_driven_flake8_corrector")
