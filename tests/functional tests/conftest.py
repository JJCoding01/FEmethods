import pytest


@pytest.fixture(params=(-1000, -500, 500))
def load(request):
    return request.param


@pytest.fixture(params=(25, 50, 75))
def load_location(request):
    return request.param


@pytest.fixture(params=(100, 120, 130))
def beam_length(request):
    return request.param
