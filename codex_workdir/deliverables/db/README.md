# Database Utilities

This package contains minimal database helpers, including a small
synchronization engine for SQLite.

## Schema examples

The accompanying tests create `users` and `orders` tables joined by
`orders.user_id`.

## Performance tips

For join-heavy queries, add indexes on the key columns (e.g., `users.id`
and `orders.user_id`) to avoid full table scans.
