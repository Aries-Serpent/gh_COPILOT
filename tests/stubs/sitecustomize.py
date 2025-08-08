import sys
import types

scripts_pkg = types.ModuleType("scripts")
run_migrations = types.ModuleType("scripts.run_migrations")
run_migrations.ensure_migrations_applied = lambda: None
scripts_pkg.run_migrations = run_migrations
sys.modules.setdefault("scripts", scripts_pkg)
sys.modules.setdefault("scripts.run_migrations", run_migrations)

utils_pkg = types.ModuleType("utils")
validation_utils = types.ModuleType("utils.validation_utils")
validation_utils.run_dual_copilot_validation = lambda *a, **k: None
utils_pkg.validation_utils = validation_utils
sys.modules.setdefault("utils", utils_pkg)
sys.modules.setdefault("utils.validation_utils", validation_utils)
