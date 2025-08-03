# Dual Copilot Pattern

The **dual copilot** pattern provides an extra layer of assurance for
critical operations. A primary action executes first and a secondary
validator confirms the outcome. Both are executed even when the primary
fails.

## Validation Flow

1. The primary validator runs and returns a boolean indicating success.
   Any exception is captured and treated as a failure.
2. The secondary validator runs regardless of the primary outcome.
3. If either validator raises an exception, the errors are aggregated and
   a `RuntimeError` is raised describing the failures.
4. When both validators return `True`, the overall result is `True`.

Use `utils.validation_utils.run_dual_copilot_validation` to coordinate
this flow in code.
