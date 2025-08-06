"""Web GUI Integration System launcher.

This module re-exports :class:`WebGUIIntegrationSystem` from
``scripts.utilities.web_gui_integration_system`` and exposes the ``main``
function so the dashboard can be started via ``python web_gui_integration_system.py``.
"""

from scripts.utilities.web_gui_integration_system import (
    WebGUIIntegrationSystem,
    main as _main,
)

__all__ = ["WebGUIIntegrationSystem", "main"]


def main() -> int:
    """Run the Web GUI Integration System."""
    return _main()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
