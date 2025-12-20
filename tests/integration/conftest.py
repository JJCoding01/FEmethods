import pytest


@pytest.fixture(params=(100, 120, 130))
def beam_length(request):
    return request.param


@pytest.fixture(params=(-1000, -500, 500))
def load(request):
    return request.param


@pytest.fixture(scope="session", autouse=True)
def E():
    """
    # psi, Young's modulus
    """
    return 29e6


@pytest.fixture(scope="session", autouse=True)
def I():
    """
    # in^4 area moment of inertia of beam
    """
    return 350


@pytest.fixture(scope="session", autouse=True)
def EI(E, I):
    """common constant"""
    return E * I


@pytest.fixture(scope="session", autouse=True)
def TOL():
    return 1e-1
