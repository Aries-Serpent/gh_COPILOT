"""Flask dashboard application with compliance export routes."""

from __future__ import annotations

import csv
import io
import subprocess
from flask import Response

from .enterprise_dashboard import app
from .routes import register_routes
from scripts.compliance.update_compliance_metrics import fetch_recent_compliance


GIT_SHA = (
    subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
)


@app.context_processor
def inject_git_sha() -> dict[str, str]:
    """Expose current Git SHA to all templates."""
    return {"git_sha": GIT_SHA}


# Register additional blueprint routes such as compliance page
register_routes(app)


@app.route("/api/compliance_scores.csv")
def compliance_scores_csv() -> Response:
    """Return recent compliance metrics as CSV for download."""
    rows = fetch_recent_compliance(limit=20)
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "timestamp",
            "composite",
            "lint_score",
            "test_score",
            "placeholder_score",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)
    return Response(output.getvalue(), mimetype="text/csv")


__all__ = ["app"]
