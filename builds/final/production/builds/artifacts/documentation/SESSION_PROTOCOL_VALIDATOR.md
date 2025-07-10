# Session Protocol Validator

The `SessionProtocolValidator` module ensures that sessions managed by
`unified_session_management_system.py` start and end cleanly. It scans the
workspace for zero-byte files before a session begins and again during
shutdown. Detection of zero-byte files causes the validation to fail and the
locations are logged for review.

## Usage

```python
from session_protocol_validator import SessionProtocolValidator

validator = SessionProtocolValidator(workspace_root="/path/to/workspace")
validator.validate_startup()   # returns True or False
validator.validate_shutdown()  # returns True or False
```

The `UnifiedSessionManagementSystem` automatically uses this validator during
`start_session` and `execute_graceful_shutdown`.
