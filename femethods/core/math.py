def derivative(func, x0, n=1, method="forward"):
    """
    Calculate the nth derivative of function f at x0

     Calculate the 1st or 2nd order derivative of a function using
     the forward or backward method.

     Parameters:
         func: callable: function to get the derivative of
         x0: float: location where derivative is calculated
         n: int: derivative order (must be either 1 for first derivative or 2 for
            second derivative)
        method: str: derivative method, either "forward" (default) or "backward"

    Returns:
        float: returns the derivative of func at x0
    """

    # validate input for n (order) and method
    if n not in (1, 2):
        raise ValueError("n must be 1 or 2")

    if method not in ("forward", "backward"):
        raise ValueError(f'invalid method parameter "{method}"')

    # for second order derivatives, return the 1st derivative of the derivative
    # function. This will result in the 2nd derivative of the original function
    if n == 2:
        return derivative(
            lambda x: derivative(func, x, n=1, method=method),
            x0,
            n=1,
            method=method,
        )

    dx = 1e-4

    if method == "forward":
        return (func(x0 + dx) - func(x0)) / dx
    assert method == "backward"
    return (func(x0) - func(x0 - dx)) / dx
