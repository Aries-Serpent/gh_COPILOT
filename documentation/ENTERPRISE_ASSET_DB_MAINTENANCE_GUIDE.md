# Enterprise Asset Database Maintenance Guide

## Sync Operation Logging

### Overview
The enhanced database sync scheduler automatically logs all sync operations to the `cross_database_sync_operations` table in `enterprise_assets.db`.

Each log entry records the operation name, status, start time captured when the
operation began, the duration in seconds, and the timestamp when the record was
created.  Before any write occurs `validate_enterprise_operation()` is invoked
to enforce audit compliance.  Batch CLI commands display a progress bar so long
running jobs show elapsed time and an estimated time to completion (ETC).

### Monitoring Sync Operations
```sql
-- View recent sync operations
SELECT operation, timestamp 
FROM cross_database_sync_operations 
ORDER BY timestamp DESC 
LIMIT 20;

-- Check for failed operations
SELECT * FROM cross_database_sync_operations
WHERE operation LIKE '%failed%';
```

```sql
-- Retrieve average duration of successful sync cycles
SELECT operation, AVG(duration) AS avg_seconds
FROM cross_database_sync_operations
WHERE status = 'SUCCESS'
GROUP BY operation;
```

### Scheduled Sync Cycles
- **Frequency**: Every 30 minutes during business hours
- **Logging**: Start, completion, and error states
- **Retention**: 90 days of sync operation history

### Troubleshooting
1. Check sync operation logs for error patterns
2. Verify database connectivity and permissions
3. Monitor database size compliance (<99.9 MB)
4. Review enterprise dashboard for sync health metrics
