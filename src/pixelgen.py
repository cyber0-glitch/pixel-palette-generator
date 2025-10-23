"""Command line interface for the pixel palette generator."""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from .image_writer import generate_image
from .palettes import PaletteError, build_palette, parse_colors, parse_size

LARGE_IMAGE_THRESHOLD = 50_000_000


def _infer_format(outfile: str, explicit_format: Optional[str]) -> str:
    if explicit_format:
        fmt = explicit_format.upper()
    else:
        ext = os.path.splitext(outfile)[1]
        fmt = ext[1:].upper() if ext else "PNG"
    if fmt == "JPG":
        fmt = "JPEG"
    if fmt not in {"PNG", "JPEG", "JPE", "BMP", "GIF"}:
        raise ValueError(f"Unsupported output format: {fmt}")
    return fmt


def _confirm_large_image(total_pixels: int) -> bool:
    prompt = input(
        f"The requested image contains {total_pixels:,} pixels which may consume significant\n"
        "time and memory. Continue? [y/N] "
    )
    return prompt.strip().lower() in {"y", "yes"}


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate images filled with colors from random or custom palettes.",
    )

    parser.add_argument("--mode", choices=["random", "custom"], required=True)
    parser.add_argument("--size", required=True, help="Image dimensions in WIDTHxHEIGHT format")
    parser.add_argument(
        "--palette",
        choices=["bw", "grayscale", "all"],
        help="Named palette to use in random mode",
    )
    parser.add_argument(
        "--colors",
        help="Comma-separated list of hex colors (e.g. '#000,#fff,#123456')",
    )
    parser.add_argument("--seed", type=int, help="Seed for deterministic output")
    parser.add_argument("--outfile", default="output.png", help="Output image path")
    parser.add_argument(
        "--format",
        help="Optional output format (PNG, JPG, BMP). Inferred from --outfile if omitted.",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Print progress updates as rows are rendered.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Automatically confirm generation of very large images.",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        width, height = parse_size(args.size)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        explicit_colors = parse_colors(args.colors)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        palette = build_palette(args.mode, args.palette, explicit_colors)
    except PaletteError as exc:
        parser.error(str(exc))

    total_pixels = width * height
    if total_pixels > LARGE_IMAGE_THRESHOLD and not args.yes:
        if not _confirm_large_image(total_pixels):
            print("Generation cancelled by user.")
            return 1

    try:
        image_format = _infer_format(args.outfile, args.format)
    except ValueError as exc:
        parser.error(str(exc))

    progress_every = max(1, height // 20)

    def _progress_callback(row: int, total: int, elapsed: float) -> None:
        if not args.progress:
            return
        if row == total or row % progress_every == 0:
            print(f"Row {row} / {total} ({elapsed:.1f}s elapsed)")

    try:
        image = generate_image(
            width,
            height,
            palette,
            seed=args.seed,
            progress_callback=_progress_callback if args.progress else None,
        )
    except RuntimeError as exc:
        parser.error(str(exc))

    try:
        image.save(args.outfile, format=image_format)
    except (ValueError, OSError) as exc:
        parser.error(f"Failed to save image: {exc}")

    print(f"Saved image to {args.outfile} ({width}x{height}, format {image_format})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
