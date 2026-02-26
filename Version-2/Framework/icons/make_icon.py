"""Generate app icons with rounded corners using ImageMagick.

Usage:
    python make_icon.py INPUT.png [OUTPUT.png]

If OUTPUT is omitted, defaults to ICON_<input_stem>.png in the current directory.
"""

import argparse
import subprocess
import sys
from pathlib import Path

CORNER_RADIUS = 90
INNER_SIZE = 432
OUTPUT_SIZE = 512

SCRIPT_DIR = Path(__file__).resolve().parent


def get_image_dimensions(image_path: Path) -> tuple[int, int]:
    """Return (width, height) of an image using ImageMagick identify."""
    result = subprocess.run(
        ["magick", "identify", "-format", "%w %h", str(image_path)],
        capture_output=True, text=True, check=True,
    )
    w, h = result.stdout.strip().split()
    return int(w), int(h)


def ensure_mask(width: int, height: int) -> Path:
    """Return path to a mask.png that matches the given dimensions, creating it if needed."""
    mask_path = SCRIPT_DIR / "mask.png"

    if mask_path.exists():
        mw, mh = get_image_dimensions(mask_path)
        if mw == width and mh == height:
            return mask_path

    subprocess.run(
        [
            "magick", "-size", f"{width}x{height}", "xc:black",
            "-fill", "white",
            "-draw", f"roundrectangle 0,0 {width - 1},{height - 1} {CORNER_RADIUS},{CORNER_RADIUS}",
            str(mask_path),
        ],
        check=True,
    )
    print(f"Generated mask: {mask_path} ({width}x{height}, radius {CORNER_RADIUS})")
    return mask_path


def make_icon(input_path: Path, output_path: Path) -> None:
    """Generate a 512x512 icon with rounded corners from input_path."""
    if not input_path.exists():
        sys.exit(f"Error: input file not found: {input_path}")

    width, height = get_image_dimensions(input_path)
    mask_path = ensure_mask(width, height)

    rounded_path = input_path.with_name(input_path.stem + "-rnd.png")

    # Apply rounded-corner mask
    subprocess.run(
        [
            "magick", str(input_path),
            "-alpha", "off",
            str(mask_path),
            "-compose", "CopyOpacity",
            "-composite",
            str(rounded_path),
        ],
        check=True,
    )

    # Resize and center on transparent 512x512 canvas
    subprocess.run(
        [
            "magick", str(rounded_path),
            "-resize", f"{INNER_SIZE}x{INNER_SIZE}",
            "-gravity", "center",
            "-background", "none",
            "-extent", f"{OUTPUT_SIZE}x{OUTPUT_SIZE}",
            str(output_path),
        ],
        check=True,
    )

    rounded_path.unlink()
    print(f"Created icon: {output_path} ({OUTPUT_SIZE}x{OUTPUT_SIZE})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate app icon with rounded corners.")
    parser.add_argument("input", type=Path, help="Source PNG image")
    parser.add_argument("output", type=Path, nargs="?", default=None, help="Output PNG (default: ICON_<input_stem>.png)")
    args = parser.parse_args()

    output = args.output or Path(f"ICON_{args.input.stem}.png")
    make_icon(args.input, output)


if __name__ == "__main__":
    main()
