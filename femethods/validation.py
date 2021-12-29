"""
Misc validation decorators that are used for validation of class properties
"""


def is_numeric(func):
    """
    Validate property is numeric

    Raises:
        TypeError: when input value is non-numeric
    """

    def wrapper(*args, **kwargs):
        if not isinstance(args[1], (int, float)):
            raise TypeError(f"{func.__name__} must be a number, not {args[1]}")
        func(*args, **kwargs)

    return wrapper


def positive(func):
    """
    Validate property is positive (excluding ``0``)

    Raises:
        ValueError: when input value is negative or ``0``
    """

    def wrapper(*args, **kwargs):
        if args[1] <= 0:
            raise ValueError(
                f"{func.__name__} must be a positive number, not {args[1]}"
            )
        func(*args, **kwargs)

    return wrapper


def non_positive(func):
    """
    Validate property is non_positive (negative or ``0``)

    Raises:
        ValueError: when value is positive
    """

    def wrapper(*args, **kwargs):
        if args[1] > 0:
            raise ValueError(f"{func.__name__} must be a negative or 0, not {args[1]}")
        func(*args, **kwargs)

    return wrapper


def negative(func):
    """
    Validate property is negative (excluding ``0``)

    Raises:
        ValueError: when value is ``0`` or positive
    """

    def wrapper(*args, **kwargs):
        if args[1] >= 0:
            raise ValueError(
                f"{func.__name__} must be a negative number, not {args[1]}"
            )
        func(*args, **kwargs)

    return wrapper


def non_negative(func):
    """
    Validate property is non_negative (must be ``0`` or positive)

    Raises:
        ValueError: when value is ``0`` or positive
    """

    def wrapper(*args, **kwargs):
        if args[1] < 0:
            raise ValueError(
                f"{func.__name__} must be a positive or 0 number, not {args[1]}"
            )
        func(*args, **kwargs)

    return wrapper
