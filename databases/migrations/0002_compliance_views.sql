-- gh_COPILOT: compliance summary read-optimized views
PRAGMA foreign_keys=ON;

-- expects tables score_snapshots and placeholder_tasks exist (see initial migration)
CREATE VIEW IF NOT EXISTS vw_latest_snapshot AS
SELECT s1.*
FROM score_snapshots s1
JOIN (
    SELECT branch, MAX(ts) AS max_ts
    FROM score_snapshots
    GROUP BY branch
) s2 ON s1.branch = s2.branch AND s1.ts = s2.max_ts;

CREATE VIEW IF NOT EXISTS vw_placeholders_open AS
SELECT COUNT(*) AS open_count
FROM placeholder_tasks
WHERE status = 'open';
