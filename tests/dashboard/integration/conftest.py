"""Common fixtures and stubs for dashboard integration tests."""

import sys
import types


class _Validator:
    def __init__(self, *_args, **_kwargs):
        pass

    def validate_corrections(self, *_args, **_kwargs):
        return True


sys.modules["secondary_copilot_validator"] = types.SimpleNamespace(
    SecondaryCopilotValidator=_Validator, run_flake8=lambda *_a, **_k: True
)

sys.modules["scripts.validation.secondary_copilot_validator"] = types.SimpleNamespace(
    SecondaryCopilotValidator=_Validator
)

sys.modules["unified_monitoring_optimization_system"] = types.SimpleNamespace(
    get_anomaly_summary=lambda **_: [],
    EnterpriseUtility=type("EnterpriseUtility", (), {}),
    push_metrics=lambda *args, **kwargs: None,
    _update_dashboard=lambda *args, **kwargs: None,
)

sys.modules["scripts.monitoring.unified_monitoring_optimization_system"] = types.SimpleNamespace(
    EnterpriseUtility=type("EnterpriseUtility", (), {}),
    push_metrics=lambda *args, **kwargs: None,
    collect_metrics=lambda *args, **kwargs: {},
)
