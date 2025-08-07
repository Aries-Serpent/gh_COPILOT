"""Web GUI Integration System launcher with dashboard routes."""

from scripts.utilities.web_gui_integration_system import (
    WebGUIIntegrationSystem as _BaseSystem,
)
from dashboard.enterprise_dashboard import app as dashboard_app

__all__ = ["WebGUIIntegrationSystem", "main"]


class WebGUIIntegrationSystem(_BaseSystem):
    """Extend base system to expose enterprise dashboard views."""

    def start(self, port: int = 5000) -> None:  # pragma: no cover - thin wrapper
        self.integrator.register_endpoints(dashboard_app)
        self.integrator.initialize()
        self.logger.info("Starting dashboard on port %s", port)
        dashboard_app.run(port=port)


def main() -> int:
    """Run the Web GUI Integration System."""
    system = WebGUIIntegrationSystem()
    system.start()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
