"""CLI wrapper for :class:`validation.protocols.session.SessionProtocolValidator`."""
from validation.protocols.session import SessionProtocolValidator

__all__ = ["SessionProtocolValidator", "main"]

def main() -> int:
    """Delegate to :func:`SessionProtocolValidator.main`."""
    return SessionProtocolValidator.main()

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
