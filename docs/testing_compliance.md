# Testing Compliance Procedures

This guide summarizes the compliance-focused testing steps.

1. **Run Tests**
   - Execute the validation package tests and capture output:
     ```bash
     mkdir -p logs/compliance_monitoring
     pytest tests/test_validation_package.py | tee logs/compliance_monitoring/pytest.log
     ```
   - Review `logs/compliance_monitoring/pytest.log` for any failures.

2. **Placeholder Audit Integration**
   - The test suite invokes `scripts.code_placeholder_audit` in simulation mode to ensure the placeholder audit module integrates with the validation framework.

3. **Rollback Path Verification**
   - Tests assert that rollback utilities exist at:
     - `scripts/database/add_rollback_logs.py`
     - `databases/migrations/add_rollback_logs.sql`

4. **Linting**
   - Validate style with Ruff:
     ```bash
     ruff tests/test_validation_package.py docs/testing_compliance.md
     ```
