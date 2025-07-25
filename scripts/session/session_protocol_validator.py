"""CLI wrapper for :mod:`session_protocol_validator`."""

from session_protocol_validator import SessionProtocolValidator, main

__all__ = ["SessionProtocolValidator", "main"]


if __name__ == "__main__":
    raise SystemExit(main())

