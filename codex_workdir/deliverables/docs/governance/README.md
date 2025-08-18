# Governance Attestations

Policy tests under `policy_tests/` enforce repository controls. Waivers for
temporary exceptions are defined in `policy_tests/waivers.yaml` and evaluated
during test setup.

Run `scripts/generate_attestation.py` to collect results from
`databases/analytics.db` and produce quarterly attestation files in this
folder.


### Installation
```bash
pip install -r requirements.txt
```

> Note: This project requires `PyYAML>=6.0.1`.
