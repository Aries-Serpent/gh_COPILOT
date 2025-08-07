# Migration Scripts

This directory contains SQL scripts for evolving the application databases.

## Execution Order

1. `v1_to_v2_migration.sql` – upgrade existing web tables to the v2 schema.
2. `enterprise_auth_setup.sql` – create enterprise role and user tables.
3. `quantum_preparation.sql` – introduce tables required for quantum features.

Run each script against `production.db` using:

```bash
sqlite3 production.db < path/to/script.sql
```

## Rollback Guidance

SQLite supports transactional execution for most data changes. For safety:

1. **Backup** the database before running migrations.
2. Wrap manual runs in a transaction so failures can be rolled back:
   ```sql
   BEGIN TRANSACTION;
   -- migration statements
   COMMIT; -- or ROLLBACK; on failure
   ```
3. To undo migrations after they succeed, restore the backup or drop added objects:
   ```sql
   DROP TABLE IF EXISTS enterprise_roles;
   DROP TABLE IF EXISTS enterprise_users;
   DROP TABLE IF EXISTS quantum_jobs;
   -- Columns added by migrations require restoring the backup.
   ```

Follow this order and rollback strategy to maintain database integrity.
