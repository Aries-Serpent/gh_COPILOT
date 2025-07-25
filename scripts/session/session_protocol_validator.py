#!/usr/bin/env python3
"""CLI wrapper for :class:`validation.protocols.session.SessionProtocolValidator`."""
from validation.protocols.session import SessionProtocolValidator

__all__ = ["SessionProtocolValidator"]

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(SessionProtocolValidator.main())
