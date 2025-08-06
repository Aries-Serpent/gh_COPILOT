# Database Entity-Relationship Diagrams

This directory contains automatically generated diagrams for core SQLite databases. The diagrams visualize table structure and any declared foreign key relationships.

## Generated Diagrams

- **production.db** – see [diagrams/production_er.dot](diagrams/production_er.dot)
- **analytics_collector.db** – see [diagrams/analytics_collector_er.dot](diagrams/analytics_collector_er.dot)
- **monitoring.db** – see [diagrams/monitoring_er.dot](diagrams/monitoring_er.dot)
- **Migration dependencies** – see [diagrams/migration_dependencies.dot](diagrams/migration_dependencies.dot) and [databases/migrations/README.md](../databases/migrations/README.md)

These databases work together to track enterprise scripts, analytics events, and system monitoring data. Tables within `production.db` hold primary configuration and tracking records. `analytics_collector.db` mirrors key events and maintains performance metrics, while `monitoring.db` stores health reports and optimization logs. Data flows from `production.db` into `analytics_collector.db` for reporting, and `monitoring.db` consumes data from both databases to evaluate system status.
