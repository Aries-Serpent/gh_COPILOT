# Session Management Guide

Session finalization now enforces a mandatory zero-byte file scan. The
`finalize_session` routine wraps its log validation with
`ensure_no_zero_byte_files`, which records any findings to `analytics.db` both
before and after completion. If zero-byte artifacts are detected at either
stage they are removed and the session exits with an error.

Integrate `finalize_session` at the end of every session workflow to guarantee
workspace integrity and auditable analytics records.

