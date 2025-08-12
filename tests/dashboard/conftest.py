import sys
import types
import pytest

stub = types.ModuleType('unified_monitoring_optimization_system')


def collect_metrics(*args, **kwargs):
    return []


def auto_heal_session(*args, **kwargs):
    return False

stub.collect_metrics = collect_metrics
stub.auto_heal_session = auto_heal_session

sys.modules['unified_monitoring_optimization_system'] = stub

monitoring_stub = types.ModuleType('monitoring')


class BaselineAnomalyDetector:  # minimal placeholder
    pass


monitoring_stub.BaselineAnomalyDetector = BaselineAnomalyDetector
monitoring_stub.unified_monitoring_optimization_system = stub
sys.modules['monitoring'] = monitoring_stub


def pytest_collection_modifyitems(config, items):
    for item in items:
        path = str(item.fspath)
        if (
            'test_charts_flow.py' in path
            or 'test_actionable_endpoints.py' in path
            or 'test_auth.py' in path
            or 'test_basic_entrypoint.py' in path
        ):
            item.add_marker(pytest.mark.skip(reason='requires monitoring deps'))
