# pylint: disable=missing-function-docstring

import pytest

from tests.factories import PropertyFactory


@pytest.mark.parametrize("length", [1, 29e6, 200e9])
def test_property_length_init(length):
    prop = PropertyFactory(length=length)
    assert prop.length == length


# noinspection PyPep8Naming
@pytest.mark.parametrize("E", [1, 29e6, 200e9])
def test_property_e_init(E):
    prop = PropertyFactory(E=E)
    assert prop.E == E


# noinspection PyPep8Naming
@pytest.mark.parametrize("Ixx", [0.25, 75, 250])
def test_property_ixx_init(Ixx):
    prop = PropertyFactory(Ixx=Ixx)
    assert prop.Ixx == Ixx


@pytest.mark.parametrize("length", [-5, 0])
def test_property_length_invalid_number(length):
    with pytest.raises(ValueError):
        PropertyFactory(length=length)


# noinspection PyPep8Naming
@pytest.mark.parametrize("E", [-15e3, 0])
def test_property_e_invalid_number(E):
    with pytest.raises(ValueError):
        PropertyFactory(E=E)


# noinspection PyPep8Naming
@pytest.mark.parametrize("Ixx", [-1, -0.25, 0])
def test_property_ixx_invalid_number(Ixx):
    with pytest.raises(ValueError):
        PropertyFactory(Ixx=Ixx)


@pytest.mark.parametrize("length", [[], None, "str"])
def test_property_length_invalid_type(length):
    with pytest.raises(TypeError):
        PropertyFactory(length=length)


# noinspection PyPep8Naming
@pytest.mark.parametrize("E", [[], None, "str"])
def test_property_e_invalid_type(E):
    with pytest.raises(TypeError):
        PropertyFactory(E=E)


# noinspection PyPep8Naming
@pytest.mark.parametrize("Ixx", [[], None, "str"])
def test_property_ixx_invalid_type(Ixx):
    with pytest.raises(TypeError):
        PropertyFactory(Ixx=Ixx)
