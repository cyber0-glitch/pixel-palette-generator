import os
import subprocess
import sys

import pytest

pytest.importorskip("PIL")
from PIL import Image


def test_cli_smoke(tmp_path):
    output = tmp_path / "test.png"
    cmd = [
        sys.executable,
        "-m",
        "src.pixelgen",
        "--mode",
        "random",
        "--size",
        "8x8",
        "--palette",
        "bw",
        "--seed",
        "123",
        "--outfile",
        str(output),
    ]
    subprocess.check_call(cmd)

    assert output.exists()
    img = Image.open(output)
    try:
        assert img.size == (8, 8)
        pixels = img.getdata()
        allowed = {(0, 0, 0), (255, 255, 255)}
        assert all(pixel in allowed for pixel in pixels)
    finally:
        img.close()
