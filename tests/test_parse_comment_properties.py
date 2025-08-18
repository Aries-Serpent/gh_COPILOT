"""Property-based tests for ``parse_comment`` utility."""

import random
import string

from scripts.database.unified_database_management_system import parse_comment


def _gen_random_string() -> str:
    """Return a random string that may include comment markers."""
    alphabet = string.ascii_letters + string.digits + " #*( )"
    return "".join(random.choice(alphabet) for _ in range(20))


def test_parse_comment_properties() -> None:
    """Randomized property test ensuring comment markers are stripped."""
    random.seed(0)
    for _ in range(100):
        raw = _gen_random_string()
        result = parse_comment(raw)
        expected = raw.split("#", 1)[0]
        expected = expected.split("*(", 1)[0].strip()
        assert result == expected
        assert "#" not in result
        assert "*(" not in result
