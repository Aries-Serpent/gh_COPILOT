# Compliance History

This log records composite compliance scores.

| Date       | Score |
|------------|-------|
| 2025-08-20 | 0.0   |

## Updating

After each compliance run:
1. Get the current UTC date:
   ```bash
   date -u +%Y-%m-%d
   ```
2. Retrieve the latest score:
   ```bash
   python -m scripts.compliance_score_cli
   ```
3. Append a new row to the table above with the date and score, keeping the newest entry at the top.
4. Commit the updated file.

