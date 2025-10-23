import pytest

from src.palettes import parse_colors


def test_parse_colors_accepts_multiple_formats():
    colors = parse_colors("#fff,#000,#123456,#abc")
    assert colors[0] == (255, 255, 255)
    assert colors[1] == (0, 0, 0)
    assert colors[2] == (18, 52, 86)
    assert colors[3] == (170, 187, 204)


def test_parse_colors_ignores_whitespace():
    colors = parse_colors("  #f00 , #0f0  ,#00f")
    assert colors == [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


def test_parse_colors_empty_raises():
    with pytest.raises(ValueError):
        parse_colors(",,,")
