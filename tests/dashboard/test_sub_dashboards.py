from web_gui.dashboards.technical_dashboard import get_metrics as tech
from web_gui.dashboards.security_dashboard import get_metrics as sec
from web_gui.dashboards.quantum_dashboard import get_metrics as quant


def test_technical_metrics_include_performance():
    metrics = tech()
    assert "cpu_percent" in metrics and "memory_percent" in metrics


def test_security_metrics_include_compliance():
    metrics = sec()
    assert "compliant" in metrics


def test_quantum_metrics_include_score():
    metrics = quant()
    assert "quantum_score" in metrics
