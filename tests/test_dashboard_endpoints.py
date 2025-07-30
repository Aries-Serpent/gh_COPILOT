#!/usr/bin/env python3
from web_gui.scripts.flask_apps.enterprise_dashboard import app


def test_index_endpoint():
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Compliance Dashboard' in resp.data


def test_metrics_endpoint():
    client = app.test_client()
    resp = client.get('/metrics')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)


def test_compliance_endpoint():
    client = app.test_client()
    resp = client.get('/compliance')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), dict)


def test_dashboard_compliance_endpoint():
    client = app.test_client()
    resp = client.get('/dashboard/compliance')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), dict)


def test_rollback_alerts_endpoint():
    client = app.test_client()
    resp = client.get('/rollback_alerts')
    assert resp.status_code == 200


def test_dashboard_info_endpoint():
    client = app.test_client()
    resp = client.get('/dashboard_info')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), dict)


def test_health_endpoint():
    client = app.test_client()
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ok'


def test_reports_endpoint():
    client = app.test_client()
    resp = client.get('/reports')
    assert resp.status_code == 200


def test_realtime_metrics_endpoint():
    client = app.test_client()
    resp = client.get('/realtime_metrics')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'metrics' in data
    assert 'corrections' in data


def test_correction_history_endpoint():
    client = app.test_client()
    resp = client.get('/correction_history')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
