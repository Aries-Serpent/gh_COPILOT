"""Compatibility shim for the unified enterprise dashboard.

This module exposes the Flask ``app`` defined in
``dashboard.enterprise_dashboard`` so existing imports of
``web_gui.dashboard_actionable_gui`` continue to work after the
dashboard consolidation.
"""

from dashboard.enterprise_dashboard import app

__all__ = ["app"]

