#!/usr/bin/env python3
"""CLI wrapper for :class:`validation.protocols.session.SessionProtocolValidator`."""

from session_protocol_validator import SessionProtocolValidator


def main() -> int:
    """Delegate to :func:`SessionProtocolValidator.main`."""
    return 0 if SessionProtocolValidator.main() else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
