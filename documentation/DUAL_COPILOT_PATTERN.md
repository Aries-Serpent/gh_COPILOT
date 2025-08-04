# Dual Copilot Pattern

The dual copilot pattern pairs a primary action with a secondary validator to
provide an extra layer of assurance for critical workflows. The secondary step
runs even if the primary fails and any exceptions are aggregated.

Use `secondary_copilot_validator.run_dual_copilot_validation` to coordinate
these checks:

```python
from secondary_copilot_validator import run_dual_copilot_validation

def primary():
    ...

def secondary():
    ...

run_dual_copilot_validation(primary, secondary)
```

### Behavior

* Validations run in order: the primary function executes before the
  secondary.
* The secondary validation always runs, even if the primary raises an
  exception.
* Exceptions from both steps are aggregated and reported in the order they
  occurred.
* The helper returns `True` only when **both** validations succeed; otherwise it
  returns `False` or raises a combined `RuntimeError`.

Recent orchestrators such as
`scripts/orchestrators/unified_wrapup_orchestrator.py` delegate their primary
and secondary checks through this helper, ensuring a unified validation
workflow across the toolkit.
