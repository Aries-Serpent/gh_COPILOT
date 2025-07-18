# Enterprise Asset Database Maintenance Guide

## Sync Operation Logging

### Overview
The enhanced database sync scheduler automatically logs all sync operations to the `cross_database_sync_operations` table in `enterprise_assets.db`.

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

### Scheduled Sync Cycles
- **Frequency**: Every 30 minutes during business hours
- **Logging**: Start, completion, and error states
- **Retention**: 90 days of sync operation history

### Troubleshooting
1. Check sync operation logs for error patterns
2. Verify database connectivity and permissions
3. Monitor database size compliance (<99.9 MB)
4. Review enterprise dashboard for sync health metrics
