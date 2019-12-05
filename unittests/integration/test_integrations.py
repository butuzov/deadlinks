import pytest


@pytest.mark.slow
def test_data_1(interface):
    print("uno", interface.cmd)


@pytest.mark.slow
def test_data_2(interface):
    print("dos", interface.cmd)
