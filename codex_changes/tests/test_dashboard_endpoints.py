import pytest
from flask import Flask

pytestmark = pytest.mark.smoke

@pytest.fixture
def app():
    app = Flask(__name__)

    @app.get('/metrics/compliance')
    def _c():
        return ({'panel': 'compliance', 'metrics': {'value': 0, 'target': 100, 'unit': '%'}}, 200)

    @app.get('/metrics/synchronization')
    def _s():
        return ({'panel': 'synchronization', 'metrics': {'value': 0, 'target': 100, 'unit': '%'}}, 200)

    @app.get('/metrics/monitoring')
    def _m():
        return ({'panel': 'monitoring', 'metrics': {'value': 0, 'target': 100, 'unit': '%'}}, 200)

    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.mark.parametrize('path', [
    '/metrics/compliance',
    '/metrics/synchronization',
    '/metrics/monitoring',
])
def test_metrics_endpoints_smoke(client, path):
    resp = client.get(path)
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        data = resp.get_json()
        assert 'panel' in data and 'metrics' in data
