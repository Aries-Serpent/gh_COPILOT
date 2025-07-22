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
    assert isinstance(data, list)


def test_compliance_endpoint():
    client = app.test_client()
    resp = client.get('/compliance')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
