from pathlib import Path


def test_listener_has_ws_and_sse_fallback():
    content = Path('dashboard/static/js/corrections_ws_listener.js').read_text()
    assert '/ws/corrections' in content
    assert "EventSource('/corrections_stream')" in content


def test_correction_log_appends_updates():
    content = Path('web/dashboard/components/CorrectionLog.vue').read_text()
    assert 'startCorrectionsListener' in content
    assert 'this.logs = this.logs.concat' in content
