#!/usr/bin/env python3
"""Create EXIF-corrected, color-normalized web copies without touching originals."""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from PIL import Image, ImageCms, ImageOps


STILL_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
ANIMATED_EXTENSIONS = {".gif"}
SRGB_ICC = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def to_srgb(im: Image.Image) -> Image.Image:
    icc = im.info.get("icc_profile")
    if icc:
        try:
            source = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            target = ImageCms.createProfile("sRGB")
            return ImageCms.profileToProfile(im, source, target, outputMode="RGB")
        except Exception:
            pass
    return im.convert("RGB")


def resize(im: Image.Image, max_long_edge: int) -> Image.Image:
    width, height = im.size
    long_edge = max(width, height)
    if long_edge <= max_long_edge:
        return im
    scale = max_long_edge / long_edge
    return im.resize(
        (max(1, round(width * scale)), max(1, round(height * scale))),
        Image.Resampling.LANCZOS,
    )


def process(source: Path, destination: Path, max_long_edge: int, quality: int) -> dict:
    with Image.open(source) as opened:
        original_size = list(opened.size)
        corrected = ImageOps.exif_transpose(opened)
        corrected_size = list(corrected.size)
        alpha = corrected.getchannel("A") if "A" in corrected.getbands() else None
        output = resize(to_srgb(corrected), max_long_edge)
        if alpha is not None:
            alpha = alpha.resize(output.size, Image.Resampling.LANCZOS)
            output.putalpha(alpha)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() == ".png" and alpha is not None:
            output.save(
                destination.with_suffix(".png"),
                "PNG",
                optimize=True,
                icc_profile=SRGB_ICC,
            )
            actual = destination.with_suffix(".png")
        else:
            actual = destination.with_suffix(".jpg")
            output.convert("RGB").save(
                actual,
                "JPEG",
                quality=quality,
                subsampling=0,
                optimize=True,
                progressive=True,
                icc_profile=SRGB_ICC,
            )
        with Image.open(actual) as saved:
            output_size = list(saved.size)
        return {
            "source": str(source),
            "output": str(actual),
            "original_size": original_size,
            "exif_corrected_size": corrected_size,
            "output_size": output_size,
            "output_bytes": actual.stat().st_size,
            "low_resolution_warning": max(corrected_size) < 1080,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--max-long-edge", type=int, default=1600)
    parser.add_argument("--quality", type=int, default=88)
    args = parser.parse_args()
    source_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    if source_dir == output_dir:
        raise ValueError("input_dir and output_dir must differ; originals are never overwritten")
    if not 1 <= args.quality <= 95:
        raise ValueError("quality must be between 1 and 95")
    if args.max_long_edge < 640:
        raise ValueError("max-long-edge below 640 px is unsuitable for article images")

    records = []
    skipped = []
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        suffix = source.suffix.lower()
        relative = source.relative_to(source_dir)
        if suffix in STILL_EXTENSIONS:
            destination = output_dir / relative
            records.append(process(source, destination, args.max_long_edge, args.quality))
        elif suffix in ANIMATED_EXTENSIONS:
            skipped.append({"source": str(source), "reason": "animated GIF requires slideshow or explicit copy decision"})
        else:
            skipped.append({"source": str(source), "reason": "unsupported extension"})

    report = {
        "input_dir": str(source_dir),
        "output_dir": str(output_dir),
        "max_long_edge": args.max_long_edge,
        "quality": args.quality,
        "processed": records,
        "skipped": skipped,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "image-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"processed={len(records)} skipped={len(skipped)}")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

