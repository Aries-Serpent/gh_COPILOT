DRY_RUN Analysis: semgrep_rules
===============================

Snapshot contents (sample):
- default.yml — basic unsafe patterns (eval/exec, yaml.load)
- python-basic.yml — subprocess shell=True, eval/exec, yaml.load, requests verify=False

Applicability
- These are small, generic security/hygiene rules and can be used locally with
  `semgrep` when available. They introduce no runtime dependency changes.

Recommendation
- Ingest `semgrep_rules/default.yml` and `semgrep_rules/python-basic.yml` into the repo
  to support optional local security scans.

Decision
- Applicable — proceed to APPLY ingestion of these two files only; leave any
  additional rule sets for future DRY_RUN review.

