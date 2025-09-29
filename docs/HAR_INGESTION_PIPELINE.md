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

Exporting to JSONL
------------------
- Use `scripts/har_export.py` to export DB tables back to JSONL for analysis:
  - `python scripts/har_export.py --db databases/har_ingest.db --out exports`
  - Produces `har_entries.ndjson`, `har_pages.ndjson`, `har_request_headers.ndjson`, `har_response_headers.ndjson`, `har_request_bodies.ndjson`, `har_response_bodies.ndjson` as available.

Output
- SQLite table `har_entries` (created on demand in APPLY mode):
  - started_at, method, url, host, path, status, status_text, mime_type,
    wait_ms, blocked_ms, dns_ms, connect_ms, ssl_ms, send_ms, receive_ms, total_ms
- SQLite table `har_pages` (created when pages are present in APPLY mode):
  - page_index (INTEGER), page_json (TEXT: original page JSON, unmodified)
- SQLite tables for headers/bodies (created when present in APPLY mode):
  - `har_request_headers(entry_index, headers_json)` and `har_response_headers(entry_index, headers_json)` — headers stored as JSON arrays of `{name,value}`; values redacted only when `HAR_REDACT_HEADERS=1`.
  - `har_request_bodies(entry_index, body_text, mime_type)` and `har_response_bodies(entry_index, body_text, mime_type, encoding)` — body text stored as-is; redacted only when `HAR_REDACT_BODIES=1`.
- NDJSON metric appended to `.codex/action_log.ndjson` with counts and run metadata.

Notes
- The pipeline is stdlib-only and local-by-default; networked tooling is not invoked.
- Extend the normalization step to include headers or post bodies if needed (be mindful of PII/secret handling).

Flags Summary
-------------
- DRY_RUN preview (default ON): `HAR_PREVIEW_PAGES=1` writes pages preview JSONL to `.codex/har_pages_preview.ndjson`.
- APPLY JSONL (default ON): `HAR_PAGES_JSONL=1` writes pages JSONL to `databases/har_pages.ndjson` (override with `HAR_PAGES_JSONL_PATH`). Set `HAR_PAGES_JSONL=0` to disable.
- Entries JSONL (default OFF): `HAR_ENTRIES_JSONL=1` writes entries JSONL to `databases/har_entries.ndjson` (override with `HAR_ENTRIES_JSONL_PATH`).
- Pagination: `HAR_PAGES_CHUNK_SIZE` (default 1000) controls chunk size for JSONL/SQLite.
- Entries batch/JSONL chunk: `HAR_ENTRIES_BATCH` (default 1000) controls both entries DB insert batch size and entries JSONL chunk.
- Metadata emission: `HAR_EMIT_META=1` includes creator/browser strings in metrics; default off.
- Redaction flags (scaffolded): `HAR_REDACT_HEADERS`, `HAR_REDACT_BODIES` (default 0; no redaction unless enabled).
- SQLite writes use a small `PRAGMA busy_timeout=3000` to reduce lock contention.
