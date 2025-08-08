from dashboard.integrated_dashboard import create_app


def test_middleware_and_authentication() -> None:
    app = create_app(
        {
            "ENABLE_SECURITY_HEADERS": True,
            "ENABLE_RATE_LIMITING": True,
            "RATE_LIMIT": 2,
            "AUTH_REQUIRED": True,
            "AUTH_TOKEN": "secret",
        }
    )
    client = app.test_client()
    # missing auth
    assert client.get("/metrics").status_code == 401
    # with auth header
    resp = client.get("/metrics", headers={"Authorization": "Bearer secret"})
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.status_code == 200
    # rate limiting kicks in on second authorized request
    assert client.get(
        "/metrics", headers={"Authorization": "Bearer secret"}
    ).status_code == 429
