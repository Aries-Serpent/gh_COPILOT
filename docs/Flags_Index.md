Flags Index
===========

HAR Ingestion
- `HAR_PREVIEW_PAGES` (default 1): DRY_RUN pages preview JSONL to `.codex/har_pages_preview.ndjson`.
- `HAR_PAGES_JSONL` (default 1 in APPLY): write pages JSONL to `HAR_PAGES_JSONL_PATH` (default `databases/har_pages.ndjson`).
- `HAR_PAGES_CHUNK_SIZE` (default 1000): pagination chunk size for pages JSONL/SQLite.
- `HAR_ENTRIES_JSONL` (default 0): write entries JSONL to `HAR_ENTRIES_JSONL_PATH` (default `databases/har_entries.ndjson`).
- `HAR_ENTRIES_BATCH` (default 1000): batch size for entries DB insert and entries JSONL chunk.
- `HAR_STRICT_SCHEMA` (default 0): enforce `log.creator` and `log.browser` presence and fields.
- `HAR_EMIT_META` (default 0): include creator/browser metadata in NDJSON metrics.
- `HAR_REDACT_HEADERS`, `HAR_REDACT_BODIES` (default 0): redact header values and body text when enabled.

Logging
- `NDJSON_MAX_BYTES` (default 0): optional file rotation threshold (single backup `<path>.1`).
- `NDJSON_SUMMARY` (default 1): include summary metrics and status histogram in metrics.
- `NDJSON_STATUS_BINS` (default `200,300,400,500`): histogram bin bounds.

Guardrails
- `GUARD_DENYLIST` (optional): comma/semicolon-separated absolute path prefixes to block writes (always in effect).
- `GUARD_ALLOWLIST` (optional): absolute prefixes that take precedence over denylist.

