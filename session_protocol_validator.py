"""CLI wrapper for :mod:`validation.protocols.session`."""
from validation.protocols.session import SessionProtocolValidator

__all__ = ["SessionProtocolValidator", "main"]


def main() -> int:
    """Delegate to :class:`~validation.protocols.session.SessionProtocolValidator`."""
    return SessionProtocolValidator.main()


if __name__ == "__main__":
    raise SystemExit(main())
