"""
Convert HEIC files in Planning/YearInPictures to JPEG.

By default writes to public/static/images/year_in_pictures for the website.
Use --dest source to emit .jpg next to each .heic/.HEIC in Planning instead.

Uses pillow-heif + Pillow EXIF transpose only (no manual rotation).

Requires: pip install pillow pillow-heif
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

import pillow_heif

pillow_heif.register_heif_opener()

_ROOT = Path(__file__).resolve().parents[1]
SRC = _ROOT / "Planning" / "YearInPictures"
DST = _ROOT / "public" / "static" / "images" / "year_in_pictures"

HEIC_SUFFIXES = {".heic", ".HEIC"}


def load_heic_fixed(path: Path) -> Image.Image:
    """
    Open HEIC and return pixels in intended display orientation.

    Apply standard EXIF orientation only. Avoid extra guesswork rotations:
    a blanket ±90° correction was wrong for these files (JPEGs like SWDinner /
    SWEntrance from the same album were already correct without it).
    """
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return img


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing files.",
    )
    parser.add_argument(
        "--dest",
        choices=("public", "source", "both"),
        default="public",
        help="public=website static (default); source=Planning/YearInPictures; both=write each.",
    )
    args = parser.parse_args()

    write_public = args.dest in ("public", "both")
    write_source = args.dest in ("source", "both")
    if write_public:
        DST.mkdir(parents=True, exist_ok=True)

    for f in sorted(SRC.iterdir()):
        if f.suffix not in HEIC_SUFFIXES:
            continue
        if args.dry_run:
            if write_public:
                print(f"Would write {DST / (f.stem + '.jpg')} from {f.name}")
            if write_source:
                print(f"Would write {SRC / (f.stem + '.jpg')} from {f.name}")
            continue
        img = load_heic_fixed(f)
        rgb = img.convert("RGB")
        if write_public:
            out_pub = DST / f"{f.stem}.jpg"
            rgb.save(out_pub, "JPEG", quality=88, optimize=True)
            print(f"Wrote {out_pub}")
        if write_source:
            out_src = SRC / f"{f.stem}.jpg"
            rgb.save(out_src, "JPEG", quality=88, optimize=True)
            print(f"Wrote {out_src}")


if __name__ == "__main__":
    main()
