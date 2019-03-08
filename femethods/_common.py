"""
Base module that contains base classes to be used by other modules
"""


class Validator(object):
    """Decorator class used to validate parameters"""

    @staticmethod
    def positive(param_name='parameter'):
        """Function decorator to handle validating input parameters to ensure
        parameters are positive values.

        The input, param_name, is the parameter name that will show up in the
        call-stack when an invalid parameter is entered.
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                if args[1] <= 0:
                    raise ValueError(param_name + ' must be positive!')
                func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def non_negative(param_name='parameter'):
        """Function decorator to handle validating input parameters to ensure
        parameters are non-negative (positive or zero values).

        The input, param_name, is the parameter name that will show up in the
        call-stack when an invalid parameter is entered.
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                if args[1] < 0:
                    raise ValueError(param_name + ' must be non-negative!')
                func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def islist(param_name='parameter'):
        """Function decorator to handle validating input parameters to ensure
        parameters are a list.

        The input, param_name, is the parameter name that will show up in the
        call-stack when an invalid parameter is entered.
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                if not isinstance(args[1], list):
                    raise TypeError(param_name + ' must be a list!')
                func(*args, **kwargs)
            return wrapper
        return decorator


class Forces(object):
    """Base class for all loads and reactions"""

    def __init__(self, value, location=0):
        self.location = location
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def location(self):
        return self._location

    @location.setter
    @Validator.non_negative('location')
    def location(self, location):
        self._location = location

    def __moment(self):
        return self.value * self.location

    def __repr__(self):
        return (f'{self.__class__.__name__}(value={self.value}, ' +
                f'location={self.location})')

    def __add__(self, force2):
        return self.value + force2.value

    def __sub__(self, load2):
        return self.value - load2.value
