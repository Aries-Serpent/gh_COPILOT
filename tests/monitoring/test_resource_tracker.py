from scripts.monitoring.resource_tracker import collect_resource_snapshot


def test_collect_resource_snapshot(tmp_path) -> None:
    snap = collect_resource_snapshot(str(tmp_path))
    assert 0 <= snap["disk_usage_percent"] <= 100
    assert "net_bytes_sent" in snap
    assert "net_bytes_recv" in snap

