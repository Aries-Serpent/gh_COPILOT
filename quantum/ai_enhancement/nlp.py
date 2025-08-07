"""Natural language processing utilities."""


def count_tokens(text: str) -> int:
    """Very small tokenizer counting whitespace separated tokens."""

    return 0 if not text else len(text.split())


__all__ = ["count_tokens"]

