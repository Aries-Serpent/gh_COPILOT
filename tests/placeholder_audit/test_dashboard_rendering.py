from pathlib import Path
from flask import Flask, render_template


def test_dashboard_template_renders_counts(tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    app = Flask(
        __name__,
        template_folder=str(repo_root / "dashboard" / "templates"),
        static_folder=str(repo_root / "dashboard" / "static"),
    )
    metrics = {
        "placeholder_removal": 0,
        "compliance_score": 1.0,
        "composite_score": 1.0,
        "open_placeholders": 2,
        "resolved_placeholders": 3,
        "progress": 0.6,
        "placeholder_breakdown": {},
        "compliance_trend": [],
        "anomaly": {"threshold": 0},
    }
    with app.test_request_context("/"):
        html = render_template(
            "dashboard.html",
            metrics=metrics,
            rollbacks=[],
            anomaly={"threshold": 0, "count": 0},
            lifecycle={
                "count": 0,
                "avg_duration": 0,
                "success_rate": 0,
                "last_duration": 0,
                "last_status": "",
                "last_zero_byte_violations": 0,
            },
            sync_events=[],
            audit_results=[],
        )
    assert "Open Placeholders:" in html
    assert "Resolved Placeholders:" in html
    assert "Remediation Progress:" in html
    assert "60.0%" in html
