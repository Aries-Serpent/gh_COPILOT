"""Serve compliance metrics page for the dashboard."""

from __future__ import annotations

from pathlib import Path
from flask import Blueprint, render_template

bp = Blueprint(
    "dashboard_compliance",
    __name__,
    template_folder=str(Path(__file__).resolve().parents[1] / "templates"),
)


@bp.route("/compliance")
def compliance_page() -> str:
    """Render the compliance metrics page."""
    return render_template("compliance.html")


__all__ = ["bp"]

