import pytest


@pytest.fixture(params=(-1000, -500, 500))
def load(request):
    return request.param
