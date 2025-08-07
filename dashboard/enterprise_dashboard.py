"""Enterprise dashboard entrypoint with consolidated views."""

from flask import render_template

from .integrated_dashboard import (
    _load_audit_results,
    _load_metrics,
    _load_sync_events,
    app,
    get_rollback_logs,
    _dashboard as dashboard_bp,
    create_app,
)


# Register view directly on the Flask app because the blueprint is already
# attached during app creation.
@app.get("/overview")
def overview() -> str:
    """Render a unified view of metrics, rollbacks, sync events, and audits."""
    return render_template(
        "dashboard.html",
        metrics=_load_metrics(),
        rollbacks=get_rollback_logs(),
        sync_events=_load_sync_events(),
        audit_results=_load_audit_results(),
    )


__all__ = ["app", "dashboard_bp", "create_app", "overview"]
