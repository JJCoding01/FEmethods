import pytest


@pytest.fixture(params=(25, 50, 75))
def overhang_length(request):
    return request.param
