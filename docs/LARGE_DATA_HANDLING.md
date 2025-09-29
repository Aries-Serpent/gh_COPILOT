Large Data Handling
===================

Overview
- For very large HAR files, prefer JSONL streaming and batched DB inserts. Avoid truncation or summaries: always preserve original JSON.

Recommendations
- Use an external disk/path for JSONL outputs:
  - Pages JSONL: set `HAR_PAGES_JSONL_PATH` to an external location.
  - Entries JSONL: set `HAR_ENTRIES_JSONL=1` and `HAR_ENTRIES_JSONL_PATH` accordingly.
- Tune chunk sizes/batches via:
  - `HAR_PAGES_CHUNK_SIZE` (default 1000)
  - `HAR_ENTRIES_BATCH` (default 1000)
- Keep NDJSON rotation enabled for long runs by setting `NDJSON_MAX_BYTES` (single-backup policy `<path>.1`).

Example
```powershell
$env:DRY_RUN='0'
$env:HAR_PAGES_JSONL='1'
$env:HAR_PAGES_JSONL_PATH='E:\har_outputs\pages.ndjson'
$env:HAR_ENTRIES_JSONL='1'
$env:HAR_ENTRIES_JSONL_PATH='E:\har_outputs\entries.ndjson'
$env:HAR_ENTRIES_BATCH='500'
python scripts/har_ingest.py .\trace.har --db .\databases\har_ingest.db
```

