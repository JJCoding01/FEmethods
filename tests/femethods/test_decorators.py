# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

import pytest

from femethods import validation as dec


@pytest.fixture()
def numeric():
    class Temp:
        def __init__(self, prop=0):
            self.prop = prop

        @property
        def prop(self):
            return self.__value

        @prop.setter
        @dec.is_numeric
        def prop(self, value):
            self.__value = value

    return Temp()


@pytest.fixture()
def positive():
    class Temp:
        def __init__(self, prop=1):
            self.prop = prop

        @property
        def prop(self):
            return self.__value

        @prop.setter
        @dec.positive
        def prop(self, value):
            self.__value = value

    return Temp()


@pytest.fixture()
def non_positive():
    class Temp:
        def __init__(self, prop=-1):
            self.prop = prop

        @property
        def prop(self):
            return self.__value

        @prop.setter
        @dec.non_positive
        def prop(self, value):
            self.__value = value

    return Temp()


@pytest.fixture()
def negative():
    class Temp:
        def __init__(self, prop=-1):
            self.prop = prop

        @property
        def prop(self):
            return self.__value

        @prop.setter
        @dec.negative
        def prop(self, value):
            self.__value = value

    return Temp()


@pytest.fixture()
def non_negative():
    class Temp:
        def __init__(self, prop=1):
            self.prop = prop

        @property
        def prop(self):
            return self.__value

        @prop.setter
        @dec.non_negative
        def prop(self, value):
            self.__value = value

    return Temp()


@pytest.mark.parametrize("value", [-2, -1.5, 0, 1.5, 2])
def test_is_numeric_valid(value, numeric):
    numeric.prop = value
    assert numeric.prop == value


@pytest.mark.parametrize("value", ["string", (1,), [], None])
def test_is_numeric_invalid(value, numeric):
    with pytest.raises(TypeError):
        numeric.prop = value


@pytest.mark.parametrize("value", [1.5, 2])
def test_positive_valid(value, positive):
    positive.prop = value
    assert positive.prop == value


@pytest.mark.parametrize("value", [-2, -1.5, 0])
def test_positive_invalid(value, positive):
    with pytest.raises(ValueError):
        positive.prop = value


@pytest.mark.parametrize("value", [-2, -1.5])
def test_negative_valid(value, negative):
    negative.prop = value
    assert negative.prop == value


@pytest.mark.parametrize("value", [0, 1.5, 2])
def test_negative_invalid(value, negative):
    with pytest.raises(ValueError):
        negative.prop = value


@pytest.mark.parametrize("value", [-2, -1.5, 0])
def test_non_positive_valid(value, non_positive):
    non_positive.prop = value
    assert non_positive.prop == value


@pytest.mark.parametrize("value", [1.5, 2])
def test_non_positive_invalid(value, non_positive):
    with pytest.raises(ValueError):
        non_positive.prop = value


@pytest.mark.parametrize("value", [0, 1.5, 2])
def test_non_negative_valid(value, non_negative):
    non_negative.prop = value
    assert non_negative.prop == value


@pytest.mark.parametrize("value", [-2, -1.5])
def test_non_negative_invalid(value, non_negative):
    with pytest.raises(ValueError):
        non_negative.prop = value
