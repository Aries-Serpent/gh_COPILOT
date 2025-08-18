# Executive Guides

Quick references for leadership teams using the enterprise dashboard.

## Key Resources

- [web_gui/scripts/flask_apps/enterprise_dashboard.py](../../web_gui/scripts/flask_apps/enterprise_dashboard.py)
  – launches the executive dashboard
- [web_gui/documentation/user_guides/README.md](../../web_gui/documentation/user_guides/README.md)
  – general user documentation
- [Governance Standards](../GOVERNANCE_STANDARDS.md)
  – compliance policies and scoring rules

## Overview

The executive dashboard surfaces compliance summaries, performance
metrics, and certification status. It displays the composite compliance
score (30% lint, 40% tests, 20% placeholders, 10% session success) and
highlights placeholder audit results. Run the dashboard script and navigate
to the highlighted sections to review system health at a glance.

## Related Modules

- [dashboard/enterprise_dashboard.py](../../dashboard/enterprise_dashboard.py)
  – CLI entry point for the dashboard
- [dashboard/README.md](../../dashboard/README.md)
  – feature overview and configuration details
- [unified_monitoring_optimization_system.py](../../unified_monitoring_optimization_system.py)
  – collects metrics surfaced to executives

## Additional Resources

- [docs/MONITORING_GUIDE.md](../MONITORING_GUIDE.md) – monitoring setup
  and tuning




### Installation
```bash
pip install -r requirements.txt
```

> Note: This project requires `PyYAML>=6.0.1`.
