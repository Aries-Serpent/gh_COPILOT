# Logging Policy

This document defines the standard logging practices for the gh_COPILOT toolkit. It covers log file formats, naming conventions, rotation intervals, and retention rules.

## Log File Formats

Log files are written as either plain text (`.log`) or JSON (`.json`) depending on the script. Text logs follow the Python `logging` module format of `"%(asctime)s - %(levelname)s - %(message)s"`. JSON logs store structured data for machine processing, as seen in `logs/session_wrap_up_*`. Markdown logs (`.md`) are used for high-level reports.

## Naming Conventions

All logs reside in the `logs/` directory or the external path `$GH_COPILOT_BACKUP_ROOT/logs/`.

- **Timestamped logs**: `<name>_YYYYMMDD_HHMMSS.log`
- **Session wrap‑up logs**: `session_wrap_up_<ID>.json`
- **Compliance logs**: `compliance_<YYYYMMDD>.log`
- **Audit logs**: `enterprise_audit.log` or `audit_<YYYYMMDD>.log` (structured according to `security/security_audit_framework.json`)
- **Rollback logs**: `rollback_<YYYYMMDD>.log`

## Rotation Schedule

Logs larger than 50 MB or older than 7 days are rotated automatically by maintenance scripts. Rotated logs are compressed into `.7z` archives under `archive/` with the same base filename and a date suffix.

## Retention Policy

- Active logs: keep for 30 days in `logs/`.
- Archived logs: keep for 180 days in `archive/`.
- Quarantined zero‑byte logs are removed after verification.

## Template Log Headers

Include a short header at the start of each log:

### Compliance Log
```text
=== COMPLIANCE SESSION START ===
Timestamp: <ISO-8601>
Compliance Level: <score>
Operator: <user>
===============================
```

### Rollback Log
```text
=== ROLLBACK OPERATION ===
Timestamp: <ISO-8601>
Target: <resource>
Reason: <summary>
========================
```

### Audit Log
```text
=== AUDIT RECORD ===
Timestamp: <ISO-8601>
Auditor: <user>
Scope: <component>
=================
```

## Maintenance Scripts

Run `scripts/maintenance/quarantine_zero_byte_logs.py` periodically to move any empty log files to `_ZERO_BYTE_QUARANTINE/`. Additional cleanup and rotation helpers reside in `scripts/maintenance/`.
