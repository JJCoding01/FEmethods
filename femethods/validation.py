"""
Misc validation decorators that are used for validation of class properties
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

# value type: allow int-only OR float-only (and preserve it)
N = TypeVar("N", int, float)

# Assumes decorated function is called like: func(self, value, *args, **kwargs)
ValidatedFunc = Callable[Concatenate[Any, N, P], R]


def is_numeric(func: ValidatedFunc[N, P, R]) -> ValidatedFunc[N, P, R]:
    """
    Validate property is numeric

    Raises:
        TypeError: when input value is non-numeric
    """

    @wraps(func)
    def wrapper(self: Any, value: N, /, *args: P.args, **kwargs: P.kwargs) -> R:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{func.__name__} must be a number, not {value}")
        return func(self, value, *args, **kwargs)

    return wrapper


def positive(func: ValidatedFunc[N, P, R]) -> ValidatedFunc[N, P, R]:
    """
    Validate property is positive (excluding ``0``)

    Raises:
        ValueError: when input value is negative or ``0``
    """

    @wraps(func)
    def wrapper(self: Any, value: N, /, *args: P.args, **kwargs: P.kwargs) -> R:
        if value <= 0:
            raise ValueError(f"{func.__name__} must be a positive number, not {value}")
        return func(self, value, *args, **kwargs)

    return wrapper


def non_positive(func: ValidatedFunc[N, P, R]) -> ValidatedFunc[N, P, R]:
    """
    Validate property is non_positive (negative or ``0``)

    Raises:
        ValueError: when value is positive
    """

    @wraps(func)
    def wrapper(self: Any, value: N, /, *args: P.args, **kwargs: P.kwargs) -> R:
        if value > 0:
            raise ValueError(f"{func.__name__} must be a negative or 0, not {value}")
        return func(self, value, *args, **kwargs)

    return wrapper


def negative(func: ValidatedFunc[N, P, R]) -> ValidatedFunc[N, P, R]:
    """
    Validate property is negative (excluding ``0``)

    Raises:
        ValueError: when value is ``0`` or positive
    """

    @wraps(func)
    def wrapper(self: Any, value: N, /, *args: P.args, **kwargs: P.kwargs) -> R:
        if value >= 0:
            raise ValueError(f"{func.__name__} must be a negative number, not {value}")
        return func(self, value, *args, **kwargs)

    return wrapper


def non_negative(func: ValidatedFunc[N, P, R]) -> ValidatedFunc[N, P, R]:
    """
    Validate property is non_negative (must be ``0`` or positive)

    Raises:
        ValueError: when value is negative
    """

    @wraps(func)
    def wrapper(self: Any, value: N, /, *args: P.args, **kwargs: P.kwargs) -> R:
        if value < 0:
            raise ValueError(
                f"{func.__name__} must be a positive or 0 number, not {value}"
            )
        return func(self, value, *args, **kwargs)

    return wrapper
