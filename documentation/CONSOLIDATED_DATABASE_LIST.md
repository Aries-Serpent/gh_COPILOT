# Consolidated Database Inventory

The following SQLite databases remain after consolidation:

- **enterprise_assets.db**: Contains data related to enterprise assets. This database is synchronized daily with the central asset management system. Migration history: Created in 2020, last schema update in 2023. Size constraint: Limited to 2GB due to SQLite limitations.
- **archive.db**: Stores archived records for long-term storage. This database is independent and not synchronized with others. Migration history: Created in 2018, last schema update in 2022. Size constraint: No specific limit, but typically remains under 5GB.
- **development.db**: Used for development and testing purposes. This database is reset frequently and is not synchronized with production. Migration history: Created dynamically as needed. Size constraint: Typically under 500MB.
- **staging.db**: Mirrors the production database for pre-deployment testing. Synchronized with production weekly. Migration history: Created in 2021, last schema update in 2023. Size constraint: Matches production size, typically under 10GB.
- **testing.db**: Used for automated testing. This database is reset after each test cycle and is not synchronized with production. Migration history: Created dynamically as needed. Size constraint: Typically under 1GB.
- **production.db**: The primary database for live operations. Synchronized in real-time with backup systems. Migration history: Created in 2015, last schema update in 2023. Size constraint: Limited to 10GB due to operational requirements.
