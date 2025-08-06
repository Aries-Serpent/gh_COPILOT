from importlib import import_module

MODULES = [
    ("scripts.wlc_session_manager", "main"),
    ("scripts.docker_healthcheck", "main"),
    ("scripts.automation.autonomous_database_health_optimizer", "main"),
    ("scripts.database.maintenance_scheduler", "main"),
    ("scripts.database.unified_database_initializer", "main"),
    ("scripts.setup_environment", "main"),
    ("scripts.placeholder_cleanup", "main"),
    ("scripts.cleanup", "main"),
    ("scripts.validate_docs_metrics", "main"),
]

def test_required_modules_are_decorated():
    for module_name, func_name in MODULES:
        module = import_module(module_name)
        func = getattr(module, func_name)
        assert hasattr(func, "__wrapped__"), f"{module_name}.{func_name} missing anti_recursion_guard"
