# Database Entity-Relationship Diagrams

This directory contains automatically generated diagrams for core SQLite databases. The diagrams visualize table structure and any declared foreign key relationships.

## Generated Diagrams

- **production.db** – see [diagrams/production_er.png](diagrams/production_er.png)
- **analytics.db** – see [diagrams/analytics_er.png](diagrams/analytics_er.png)
- **monitoring.db** – see [diagrams/monitoring_er.png](diagrams/monitoring_er.png)

These databases work together to track enterprise scripts, analytics events, and system monitoring data. Tables within `production.db` hold primary configuration and tracking records. `analytics.db` mirrors key events and maintains performance metrics, while `monitoring.db` stores health reports and optimization logs. Data flows from `production.db` into `analytics.db` for reporting, and `monitoring.db` consumes data from both databases to evaluate system status.
