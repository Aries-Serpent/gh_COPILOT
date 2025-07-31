"""General utility functions for script entrypoints."""

from typing import Any, Callable


def operations_main(main_func: Callable[..., Any]) -> None:
    """Execute ``main_func`` and print its result if not ``None``."""
    result = main_func()
    if result is not None:
        print(result)
