import pytest

from tests.factories import ConstantDistributedLoadFactory


@pytest.mark.skip(reason="equivalent_loads function not functional yet")
def test_const_distributed_load_loads():
    dload = ConstantDistributedLoadFactory(start=0, stop=20)
    nodes = dload.equivalent_loads(nodes=(0, 10, 20))
    print(nodes)

    # em = dload.equivalent_magnitude(nodes=(0, 10, 20))
    # print(em)

    print("")

    assert False
