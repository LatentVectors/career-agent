import pytest


def test_setup() -> None:
    assert True


def test_setup_fail() -> None:
    with pytest.raises(Exception):
        assert False
