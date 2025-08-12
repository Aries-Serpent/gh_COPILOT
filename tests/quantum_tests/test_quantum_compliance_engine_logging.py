import importlib
import logging
import sys


def test_import_has_no_logging_side_effect(tmp_path):
    """Importing the module should not alter existing logging handlers or level."""
    root_logger = logging.getLogger()
    handler = logging.FileHandler(tmp_path / "test.log")
    root_logger.addHandler(handler)
    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level

    module_name = "ghc_quantum.quantum_compliance_engine"
    sys.modules.pop(module_name, None)
    importlib.import_module(module_name)

    assert root_logger.handlers == original_handlers
    assert root_logger.level == original_level

    root_logger.removeHandler(handler)
    handler.close()
