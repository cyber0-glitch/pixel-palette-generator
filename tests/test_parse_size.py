import pytest

from src.palettes import parse_size


def test_parse_size_valid():
    assert parse_size("10x20") == (10, 20)
    assert parse_size("1x1") == (1, 1)


def test_parse_size_invalid_format():
    with pytest.raises(ValueError):
        parse_size("10")
    with pytest.raises(ValueError):
        parse_size("axb")


def test_parse_size_non_positive():
    with pytest.raises(ValueError):
        parse_size("0x10")
    with pytest.raises(ValueError):
        parse_size("10x0")
