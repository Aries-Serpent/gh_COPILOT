HAR Ingestion Pipeline
======================

Overview
- The `scripts/har_ingest.py` pipeline ingests HTTP Archive (HAR) files using the `gh_copilot.automation` primitives with a safe, phased workflow.
- Phases: Validate → JSON schema check → Normalize → Persist (APPLY only) → Emit metrics.

Modes
- DRY_RUN (default): `DRY_RUN=1`
  - Simulates writes, validates structure, normalizes entries in-memory, and appends a concise NDJSON metric to `.codex/action_log.ndjson`.
- APPLY: set `DRY_RUN=0`
  - Enables guardrails and persists normalized entries into SQLite (default `databases/har_ingest.db`).

Guardrails
- Blocks edits to `.github/workflows` during APPLY.
- Forbids writing to `C:/temp` and `E:/temp`.
- Scans for recursive “backup” patterns to avoid storing backups inside the repo.

Usage
- Dry run:
  - `python scripts/har_ingest.py path/to/file.har`
- Apply with custom DB path:
  - PowerShell: `$env:DRY_RUN='0'; python scripts/har_ingest.py trace.har --db databases/har_ingest.db`
  - Bash: `DRY_RUN=0 python scripts/har_ingest.py trace.har --db databases/har_ingest.db`

Output
- SQLite table `har_entries` (created on demand in APPLY mode):
  - started_at, method, url, host, path, status, status_text, mime_type,
    wait_ms, blocked_ms, dns_ms, connect_ms, ssl_ms, send_ms, receive_ms, total_ms
- SQLite table `har_pages` (created when pages are present in APPLY mode):
  - page_index (INTEGER), page_json (TEXT: original page JSON, unmodified)
- NDJSON metric appended to `.codex/action_log.ndjson` with counts and run metadata.

Notes
- The pipeline is stdlib-only and local-by-default; networked tooling is not invoked.
- Extend the normalization step to include headers or post bodies if needed (be mindful of PII/secret handling).
