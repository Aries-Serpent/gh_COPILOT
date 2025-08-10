"""Flask dashboard application with compliance export routes."""

from __future__ import annotations

import csv
import io
from flask import Response

from .enterprise_dashboard import app
from scripts.compliance.update_compliance_metrics import fetch_recent_compliance


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
