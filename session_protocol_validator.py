"""CLI wrapper for :mod:`validation.protocols.session`."""

from validation.protocols.session import SessionProtocolValidator
from utils.cross_platform_paths import verify_environment_variables
from utils.validation_utils import anti_recursion_guard

__all__ = ["SessionProtocolValidator", "main"]


@anti_recursion_guard
def main() -> int:
    """Delegate to :class:`~validation.protocols.session.SessionProtocolValidator`."""
    verify_environment_variables()
    return SessionProtocolValidator.main()


if __name__ == "__main__":
    raise SystemExit(main())
