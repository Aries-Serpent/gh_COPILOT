from __future__ import annotations

"""Security compliance enforcement utilities."""

from pathlib import Path
import json

from enterprise_modules.compliance import validate_enterprise_operation

DEFAULT_POLICY = Path(__file__).resolve().parent / "enterprise_security_policy.json"


def enforce_security_policies(policy_path: Path | None = None) -> None:
    """Ensure security policies meet enterprise standards.

    The policy file must define ``encryption`` and ``access_control`` keys.
    """
    path = policy_path or DEFAULT_POLICY
    validate_enterprise_operation(str(path.parent))
    if not path.exists():
        raise FileNotFoundError(f"Security policy not found: {path}")
    data = json.loads(path.read_text())
    controls = data.get("security_controls", {})
    has_encryption = "encryption" in data or "data_protection" in controls
    has_access = "access_control" in data or "access_control" in controls
    missing = []
    if not has_encryption:
        missing.append("encryption")
    if not has_access:
        missing.append("access_control")
    if missing:
        raise ValueError(f"Missing required policies: {', '.join(missing)}")


__all__ = ["enforce_security_policies"]
