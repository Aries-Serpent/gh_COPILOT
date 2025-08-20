from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, TypeVar, Generic

T = TypeVar("T")


class _TqdmStub(Generic[T]):
    """Minimal stand-in for :func:`tqdm` when the real package is unavailable."""

    def __init__(self, iterable: Iterable[T] | None = None, **_kwargs: Any) -> None:
        self._iterable = iterable if iterable is not None else []

    def __iter__(self) -> Iterator[T]:
        return iter(self._iterable)

    def __enter__(self) -> "_TqdmStub[T]":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any | None,
    ) -> None:
        return None

    def update(self, _n: int = 1) -> None:
        return None

    def set_description(self, _desc: str) -> None:
        return None


def _noop_tqdm(iterable: Iterable[T] | None = None, **_kwargs: Any) -> _TqdmStub[T]:
    return _TqdmStub(iterable, **_kwargs)


def get_tqdm() -> Callable[..., Iterable[Any]]:
    try:
        from tqdm import tqdm  # type: ignore[import]
        return tqdm
    except Exception:
        return _noop_tqdm


# Expose a tqdm-like callable for modules to import directly.
tqdm: Callable[..., Iterable[Any]] = get_tqdm()

