# Script Database Validation System

## Overview

The Script Database Validation System ensures that all scripts within the repository databases are up-to-date with the current scripts in the codebase. This system provides hash validation, timestamp tracking, and comprehensive synchronization reporting.

## Components

### 1. Core Validator (`script_database_validator.py`)

The primary validation engine that:
- Scans repository for all script files (`.py`, `.ps1`, `.sh`, `.bat`)
- Computes SHA256 hashes for integrity validation
- Compares repository scripts with database entries
- Provides detailed synchronization status reports
- Updates database with current script content and metadata

### 2. Enterprise Synchronizer (`enterprise_script_database_synchronizer_complete.py`)

Enterprise-grade orchestration system that:
- Performs comprehensive synchronization sessions
- Creates database backups before operations
- Generates compliance reports for audit purposes
- Maintains detailed operation logs
- Provides session tracking and recovery

### 3. Test Suite (`tests/test_script_database_validator.py`)

Comprehensive test coverage for:
- Hash calculation accuracy
- Repository script scanning
- Database script retrieval
- Synchronization validation logic
- Database update operations
- Report generation

## Usage

### Basic Validation

```bash
# Generate validation report
python3 script_database_validator.py --report validation_report.md

# Verbose validation with console output
python3 script_database_validator.py --verbose

# Update database with out-of-sync scripts
python3 script_database_validator.py --update --verbose
```

### Enterprise Synchronization

```bash
# Generate compliance report only
python3 enterprise_script_database_synchronizer_complete.py --compliance-report

# Perform validation with backup (no sync)
python3 enterprise_script_database_synchronizer_complete.py

# Full synchronization with backup
python3 enterprise_script_database_synchronizer_complete.py --auto-sync

# Skip backup (faster operation)
python3 enterprise_script_database_synchronizer_complete.py --auto-sync --no-backup
```

### Workspace-Specific Operations

```bash
# Specify custom workspace root
python3 script_database_validator.py --workspace /path/to/workspace --report report.md

# Enterprise sync for specific workspace
python3 enterprise_script_database_synchronizer_complete.py --workspace /path/to/workspace --auto-sync
```

## Key Features

### Hash Validation
- **SHA256 hashing** for secure content integrity validation
- **Comparison logic** between repository files and database content
- **Mismatch detection** for out-of-sync scripts

### Timestamp Tracking
- **Creation timestamps** when scripts are first digested into database
- **Update timestamps** for tracking synchronization operations
- **Modification tracking** from repository file system

### Comprehensive Reporting
- **Sync percentage** calculation for overall system health
- **Detailed breakdowns** of in-sync, out-of-sync, and missing scripts
- **Hash mismatch identification** with specific file details
- **Enterprise compliance** status for audit purposes

### Database Integration
- **Primary database**: `databases/script_generation.db`
- **Schema compatibility** with existing `script_templates` table
- **Unique constraint handling** for template IDs
- **Backup integration** with enterprise archive system

## Database Schema

The system works with the existing `script_templates` table:

```sql
CREATE TABLE script_templates (
    template_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    quantum_hash TEXT,                    -- SHA256 hash for validation
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Expected Outcomes

### Problem Statement Requirements

✅ **Scripts dated when digested**: All database entries include `created_at` and `updated_at` timestamps

✅ **Hash validation**: SHA256 hashes stored in `quantum_hash` field and validated against repository content

✅ **Repository synchronization**: System identifies and can sync all repository scripts to database

✅ **Comprehensive reporting**: Detailed status of synchronization state with actionable information

### Validation Results

Before synchronization:
- **Repository Scripts**: 980
- **Database Scripts**: 3  
- **Synchronization**: 0.00%
- **Status**: REQUIRES ATTENTION

After synchronization (tested with limited scope):
- **Repository Scripts**: 3 (test)
- **Database Scripts**: 3 (test)
- **Synchronization**: 100.00%
- **Status**: COMPLIANT

## Integration Points

### With Existing Systems
- **Enterprise compliance framework**: Generates audit reports
- **Database backup system**: Integrates with archive management
- **Logging infrastructure**: Uses enterprise text indicators
- **Workspace validation**: Respects workspace root and archive exclusions

### With CI/CD Pipeline
- Can be integrated into build processes for continuous validation
- Provides exit codes for automated pipeline decisions
- Generates machine-readable JSON reports for integration

### With Monitoring Systems
- Session tracking with unique identifiers
- Detailed operation logs for debugging
- Performance metrics and timing data

## Configuration

### Environment Variables
- `GH_COPILOT_WORKSPACE`: Workspace root directory (default: current directory)

### File Exclusions
- Hidden directories (starting with `.`)
- Archive directories (`archives/`)
- Build artifacts and temporary files

### Supported Script Types
- Python scripts (`.py`)
- PowerShell scripts (`.ps1`)
- Bash scripts (`.sh`)
- Batch files (`.bat`)

## Security & Compliance

### Data Integrity
- SHA256 cryptographic hashing for tamper detection
- Database transaction safety with rollback on errors
- Backup creation before any modification operations

### Audit Trail
- Complete operation logging with timestamps
- Session tracking for forensic analysis
- Compliance report generation for regulatory requirements

### Enterprise Standards
- Flake8/PEP 8 compliant code
- Text-based indicators (no Unicode emojis)
- Database-first architecture principles
- Anti-recursion protection

## Testing

```bash
# Run focused tests
python3 -m pytest tests/test_script_database_validator.py -v

# Run limited demonstration
python3 test_sync_limited.py

# Full test suite
make test
```

## Troubleshooting

### Common Issues

1. **Database Lock**: Ensure no other processes are accessing the database
2. **Permission Errors**: Verify write access to database and results directories
3. **Large Repository**: Use workspace parameter to limit scope for testing

### Error Recovery

- All operations include database backups for recovery
- Session tracking allows resuming interrupted operations
- Detailed error logging for diagnosis

## Performance Considerations

- **File scanning**: O(n) complexity where n = number of files
- **Hash calculation**: I/O bound, consider SSD for better performance
- **Database operations**: Batch updates for efficiency
- **Memory usage**: Scales with number of scripts in repository

For large repositories (>1000 scripts), consider:
- Running during off-peak hours
- Using workspace filtering to process subsets
- Monitoring system resources during operation