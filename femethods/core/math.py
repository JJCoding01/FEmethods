def derivative(func, x0, n=1, method="forward"):
    """
    Calculate the nth derivative of function f at x0

     Calculate the 1st or 2nd order derivative of a function using
     the forward or backward method.
    """

    if n not in (1, 2):
        raise ValueError("n must be 1 or 2")

    # Note that the value for dx is set manually. This is because the ideal
    # values are not constant based on the method used.
    # TODO determine better method for choosing a more ideal dx value

    if method not in ("forward", "backward"):
        raise ValueError(f'invalid method parameter "{method}"')

    if method == "forward":
        dx = 1e-8
        if n == 1:
            return (func(x0 + dx) - func(x0)) / dx
        assert n == 2
        return (func(x0 + 2 * dx) - 2 * func(x0 + dx) + func(x0)) / dx ** 2

    assert method == "backward"
    dx = 1e-5
    if n == 1:
        return (func(x0) - func(x0 - dx)) / dx
    assert n == 2
    return (func(x0) - 2 * func(x0 - dx) + func(x0 - 2 * dx)) / dx ** 2
