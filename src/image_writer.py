"""Image generation helpers for the pixel palette generator."""

from __future__ import annotations

import random
import time
from typing import Callable, Optional

try:
    from PIL import Image
except ModuleNotFoundError:  # pragma: no cover - exercised in environments without Pillow
    Image = None  # type: ignore

from .palettes import Palette


def generate_image(
    width: int,
    height: int,
    palette: Palette,
    *,
    seed: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int, float], None]] = None,
) -> Image.Image:
    """Generate an image filled row-by-row using the provided palette."""

    if Image is None:
        raise RuntimeError(
            "Pillow is required to generate images. Install it with 'pip install Pillow'."
        )

    rng = random.Random(seed)
    image = Image.new("RGB", (width, height))
    pixels = image.load()

    start_time = time.perf_counter()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = palette.pick(rng)
        if progress_callback:
            progress_callback(y + 1, height, time.perf_counter() - start_time)

    return image


__all__ = ["generate_image"]
