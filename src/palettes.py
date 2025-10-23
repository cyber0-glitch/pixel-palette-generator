"""Palette utilities and input parsing for the pixel generator CLI and web app."""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

Color = Tuple[int, int, int]

_HEX_COLOR_RE = re.compile(r"^#?(?P<value>(?:[0-9a-fA-F]{3}){1,2})$")


class PaletteError(ValueError):
    """Raised when invalid palette parameters are encountered."""


@dataclass(frozen=True)
class Palette:
    """Represents a color palette that can sample RGB tuples uniformly."""

    name: str
    colors: Optional[Sequence[Color]]
    sample: Callable[["Palette", "random.Random"], Color]

    def pick(self, rng: "random.Random") -> Color:
        return self.sample(self, rng)


# Built-in palettes for random mode.
_BW_PALETTE: Tuple[Color, ...] = ((0, 0, 0), (255, 255, 255))
_GRAYSCALE_PALETTE: Tuple[Color, ...] = tuple((v, v, v) for v in range(256))


def parse_size(size_str: str) -> Tuple[int, int]:
    """Parse a size string formatted as WIDTHxHEIGHT into integers.

    Args:
        size_str: A string such as "1080x1920".

    Returns:
        A tuple ``(width, height)`` with positive integers.

    Raises:
        ValueError: If the format is invalid or if either dimension is < 1.
    """

    if "x" not in size_str.lower():
        raise ValueError("Size must be in WIDTHxHEIGHT format.")

    try:
        width_str, height_str = size_str.lower().split("x", 1)
        width = int(width_str)
        height = int(height_str)
    except (ValueError, TypeError):
        raise ValueError("Size must contain two integer values separated by 'x'.")

    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive integers.")

    return width, height


def parse_hex_color(color_str: str) -> Color:
    """Parse a single hex color string into an RGB tuple."""

    match = _HEX_COLOR_RE.match(color_str.strip())
    if not match:
        raise ValueError(f"Invalid hex color: {color_str}")

    value = match.group("value")
    if len(value) == 3:
        r, g, b = (int(ch * 2, 16) for ch in value)
    else:
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)

    return r, g, b


def parse_colors(colors: Optional[str]) -> List[Color]:
    """Parse a comma-separated list of hex colors into RGB tuples."""

    if not colors:
        return []

    parsed: List[Color] = []
    for entry in colors.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parsed.append(parse_hex_color(entry))

    if not parsed:
        raise ValueError("No valid colors were provided.")

    return parsed


def _sample_from_list(palette: Palette, rng: "random.Random") -> Color:
    colors = palette.colors
    if not colors:
        raise PaletteError("Palette has no colors to sample from.")
    index = rng.randrange(len(colors))
    return colors[index]


def _sample_all_colors(_: Palette, rng: "random.Random") -> Color:
    return rng.randrange(256), rng.randrange(256), rng.randrange(256)


def build_palette(
    mode: str,
    palette_name: Optional[str],
    explicit_colors: Sequence[Color],
) -> Palette:
    """Construct the palette used for image generation."""

    mode = mode.lower()
    palette_key = (palette_name or "").lower() or None

    if explicit_colors and palette_key:
        warnings.warn(
            "Both a named palette and explicit colors were provided; using the explicit colors.",
            RuntimeWarning,
            stacklevel=2,
        )

    if mode not in {"random", "custom"}:
        raise PaletteError(f"Unsupported mode: {mode}")

    if explicit_colors:
        return Palette(
            name="custom",
            colors=tuple(explicit_colors),
            sample=_sample_from_list,
        )

    if mode == "custom":
        raise PaletteError("Custom mode requires at least one color via --colors.")

    if palette_key is None:
        palette_key = "bw"

    if palette_key == "bw":
        return Palette("bw", _BW_PALETTE, _sample_from_list)
    if palette_key == "grayscale":
        return Palette("grayscale", _GRAYSCALE_PALETTE, _sample_from_list)
    if palette_key == "all":
        return Palette("all", None, _sample_all_colors)

    raise PaletteError(f"Unknown palette name: {palette_name}")


__all__ = [
    "Color",
    "Palette",
    "PaletteError",
    "build_palette",
    "parse_colors",
    "parse_hex_color",
    "parse_size",
]
