#!/usr/bin/env python3
"""Build a dimensionally consistent slideshow GIF from a JSON manifest."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageColor, ImageOps


def ffmpeg_path() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise RuntimeError("ffmpeg not found; install ffmpeg or imageio-ffmpeg") from exc


def resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def load_rgb(path: Path) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.exif_transpose(source).convert("RGB")


def cover(im: Image.Image, width: int, height: int, focus: tuple[float, float]) -> Image.Image:
    src_w, src_h = im.size
    scale = max(width / src_w, height / src_h)
    resized_w = max(width, int(round(src_w * scale)))
    resized_h = max(height, int(round(src_h * scale)))
    resized = im.resize((resized_w, resized_h), Image.Resampling.LANCZOS)
    fx = min(1.0, max(0.0, focus[0]))
    fy = min(1.0, max(0.0, focus[1]))
    left = int(round((resized_w - width) * fx))
    top = int(round((resized_h - height) * fy))
    return resized.crop((left, top, left + width, top + height))


def contain(im: Image.Image, width: int, height: int, background: str) -> Image.Image:
    scale = min(width / im.size[0], height / im.size[1])
    resized_w = max(1, int(round(im.size[0] * scale)))
    resized_h = max(1, int(round(im.size[1] * scale)))
    resized = im.resize((resized_w, resized_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), ImageColor.getrgb(background))
    canvas.paste(resized, ((width - resized_w) // 2, (height - resized_h) // 2))
    return canvas


def validate_manifest(data: dict[str, Any]) -> None:
    required = {"output", "width", "height", "frames"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing manifest keys: {', '.join(sorted(missing))}")
    if data.get("mode", "cover") not in {"cover", "contain"}:
        raise ValueError("mode must be cover or contain")
    if not isinstance(data["frames"], list) or len(data["frames"]) < 2:
        raise ValueError("frames must contain at least two images")
    if int(data["width"]) <= 0 or int(data["height"]) <= 0:
        raise ValueError("width and height must be positive")


def encode(frames: list[Image.Image], destination: Path, duration_ms: int, dither: str) -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="wechat_slideshow_"))
    try:
        for index, frame in enumerate(frames):
            frame.save(temp_dir / f"frame{index:03d}.png", "PNG")
        filter_graph = (
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=single[p];"
            f"[s1][p]paletteuse=new=1:dither={dither}"
        )
        command = [
            ffmpeg_path(),
            "-y",
            "-framerate",
            f"1000/{duration_ms}",
            "-i",
            str(temp_dir / "frame%03d.png"),
            "-filter_complex",
            filter_graph,
            "-loop",
            "0",
            str(destination),
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode:
            raise RuntimeError(result.stderr[-1600:])
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--force", action="store_true", help="replace an existing output after previews are generated")
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    base = manifest_path.parent
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(data)

    width = int(data["width"])
    height = int(data["height"])
    mode = data.get("mode", "cover")
    background = data.get("background", "#f7f1e8")
    duration_ms = int(data.get("duration_ms", 2300))
    dither = data.get("dither", "none")
    if dither not in {"none", "bayer", "heckbert", "floyd_steinberg", "sierra2", "sierra2_4a"}:
        raise ValueError(f"Unsupported dither mode: {dither}")

    output = resolve(base, data["output"])
    preview_dir = resolve(base, data.get("preview_dir", str(output.with_suffix("")) + "_previews"))
    output.parent.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    frames: list[Image.Image] = []
    report_frames = []
    for index, spec in enumerate(data["frames"]):
        if not isinstance(spec, dict) or not spec.get("src"):
            raise ValueError(f"Frame {index} must contain src")
        source_path = resolve(base, spec["src"])
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        original = load_rgb(source_path)
        focus_value = spec.get("focus", [0.5, 0.5])
        if not isinstance(focus_value, list) or len(focus_value) != 2:
            raise ValueError(f"Frame {index} focus must be [x, y]")
        focus = (float(focus_value[0]), float(focus_value[1]))
        frame = cover(original, width, height, focus) if mode == "cover" else contain(original, width, height, background)
        preview_path = preview_dir / f"{index + 1:02d}_{source_path.stem}.jpg"
        frame.save(preview_path, "JPEG", quality=92, optimize=True)
        frames.append(frame)
        report_frames.append(
            {
                "src": str(source_path),
                "original_size": list(original.size),
                "output_size": [width, height],
                "focus": list(focus),
                "preview": str(preview_path),
            }
        )

    existed_before = output.exists()
    candidate = output.with_name(output.stem + ".candidate.gif") if existed_before else output
    encode(frames, candidate, duration_ms, dither)
    with Image.open(candidate) as result:
        if result.size != (width, height) or result.n_frames != len(frames):
            raise RuntimeError("Encoded GIF dimensions or frame count do not match manifest")
        durations = []
        for index in range(result.n_frames):
            result.seek(index)
            durations.append(result.info.get("duration"))

    replaced = False
    if existed_before:
        if args.force:
            os.replace(candidate, output)
            replaced = True
        else:
            print(f"Existing output preserved. Inspect previews, then rerun with --force: {candidate}")
    final_path = output if replaced or not existed_before else candidate
    report = {
        "output": str(final_path),
        "target_output": str(output),
        "replaced": replaced,
        "mode": mode,
        "size": [width, height],
        "duration_ms": duration_ms,
        "encoded_durations": durations,
        "file_bytes": final_path.stat().st_size,
        "frames": report_frames,
    }
    report_path = final_path.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(final_path)
    print(preview_dir)
    print(report_path)
    return 0 if not existed_before or args.force else 2


if __name__ == "__main__":
    raise SystemExit(main())

