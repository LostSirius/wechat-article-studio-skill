#!/usr/bin/env python3
"""Run renderer/auditor regression fixtures and an optional slideshow smoke test."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, JpegImagePlugin


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
EVALS = ROOT / "evals"


def run(command: list[str], expected: set[int] = {0}) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )
    if result.returncode not in expected:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")
    return result


def render_fixtures(temp: Path) -> list[dict]:
    reports = []
    for fixture in sorted(EVALS.glob("*.json")):
        output = temp / fixture.stem
        run(
            [
                sys.executable,
                str(SCRIPTS / "build.py"),
                str(fixture),
                "--output-dir",
                str(output),
                "--no-screenshots",
            ]
        )
        report = json.loads((output / "audit.json").read_text(encoding="utf-8"))
        if report["fatal"]:
            raise AssertionError(f"{fixture.name} has fatal audit issues: {report['fatal']}")
        fragment = (output / "article.fragment.html").read_text(encoding="utf-8")
        preview = (output / "article.preview.html").read_text(encoding="utf-8")
        if "<script" in fragment or "<style" in fragment:
            raise AssertionError(f"{fixture.name} leaked preview code into fragment")
        if "复制排版到公众号" not in preview:
            raise AssertionError(f"{fixture.name} preview has no copy action")
        if "复制 HTML 不会复制图片文件" not in preview:
            raise AssertionError(f"{fixture.name} preview has no local-image warning")
        if "COPY_BUTTON.disabled=true" not in preview:
            raise AssertionError(f"{fixture.name} preview has no unresolved-image guard")
        build_report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
        if build_report["screenshot_status"] != "disabled":
            raise AssertionError(f"{fixture.name} build report has wrong screenshot status")
        reports.append(
            {
                "fixture": fixture.name,
                "readiness": report["readiness"],
                "scores": report["scores"],
                "warnings": len(report["warnings"]),
            }
        )
    return reports


def invalid_fragment_test(temp: Path) -> None:
    invalid = temp / "invalid.html"
    invalid.write_text('<section class="bad"><script>alert(1)</script><p>测试</p></section>', encoding="utf-8")
    result = run(
        [sys.executable, str(SCRIPTS / "audit.py"), str(invalid), "--json"],
        expected={1},
    )
    report = json.loads(result.stdout)
    if not report["fatal"]:
        raise AssertionError("invalid HTML was not rejected")
    missing_alt = temp / "missing-alt.html"
    missing_alt.write_text(
        '<section style="width:100%;"><img src="https://example.invalid/x.jpg" style="width:100%;" /></section>',
        encoding="utf-8",
    )
    result = run(
        [sys.executable, str(SCRIPTS / "audit.py"), str(missing_alt), "--json"],
        expected={1},
    )
    alt_report = json.loads(result.stdout)
    if not any(item["code"] == "missing-alt" for item in alt_report["fatal"]):
        raise AssertionError("missing image alt was not fatal")


def cdn_map_test(temp: Path) -> dict:
    manuscript = json.loads((EVALS / "academic-news.json").read_text(encoding="utf-8"))
    local_src = "file:" + "///C:/article/web-images/photo.jpg"
    mapped_src = "https://example.invalid/photo.jpg"
    manuscript["hero"] = {"src": local_src, "alt": "Synthetic local image"}
    manuscript_path = temp / "cdn-manuscript.json"
    manuscript_path.write_text(
        json.dumps(manuscript, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    cdn_map_path = temp / "cdn_map.json"
    cdn_map_path.write_text(
        json.dumps({local_src: mapped_src}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    output = temp / "cdn-output"
    run(
        [
            sys.executable,
            str(SCRIPTS / "render.py"),
            str(manuscript_path),
            "--output-dir",
            str(output),
            "--cdn-map",
            str(cdn_map_path),
        ]
    )
    fragment = (output / "article.fragment.html").read_text(encoding="utf-8")
    preview = (output / "article.preview.html").read_text(encoding="utf-8")
    if local_src not in fragment:
        raise AssertionError("fragment should preserve the manuscript image source")
    if mapped_src not in preview:
        raise AssertionError("preview did not embed the approved CDN mapping")
    if "classifyAssets" not in preview or "COPY_BUTTON.disabled=true" not in preview:
        raise AssertionError("preview did not embed image-source safeguards")
    return {"mapping_embedded": True, "local_source_preserved": True}


def slideshow_test(temp: Path) -> dict:
    images = temp / "images"
    images.mkdir()
    portrait = Image.new("RGB", (600, 900), "#6c8db3")
    draw = ImageDraw.Draw(portrait)
    draw.rectangle((190, 100, 410, 850), fill="#d7c39a")
    landscape = Image.new("RGB", (1000, 600), "#91b77d")
    draw = ImageDraw.Draw(landscape)
    draw.rectangle((330, 80, 670, 570), fill="#e4d9c5")
    portrait.save(images / "portrait.jpg", quality=95)
    landscape.save(images / "landscape.jpg", quality=95)
    manifest = {
        "output": "result.gif",
        "width": 540,
        "height": 720,
        "duration_ms": 600,
        "mode": "cover",
        "preview_dir": "previews",
        "frames": [
            {"src": "images/portrait.jpg", "focus": [0.5, 0.5]},
            {"src": "images/landscape.jpg", "focus": [0.5, 0.5]},
        ],
    }
    manifest_path = temp / "slideshow.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    run([sys.executable, str(SCRIPTS / "slideshow.py"), str(manifest_path)])
    with Image.open(temp / "result.gif") as gif:
        if gif.size != (540, 720) or gif.n_frames != 2:
            raise AssertionError("slideshow output mismatch")
        return {"size": list(gif.size), "frames": gif.n_frames}


def image_prepare_test(temp: Path) -> dict:
    source = temp / "image-source"
    output = temp / "image-output"
    source.mkdir()
    image = Image.new("RGB", (2400, 1200), "#7f9db8")
    image.save(source / "large.jpg", quality=95)
    run(
        [
            sys.executable,
            str(SCRIPTS / "prepare_images.py"),
            str(source),
            str(output),
            "--max-long-edge",
            "1200",
        ]
    )
    prepared = output / "large.jpg"
    if not prepared.exists():
        raise AssertionError("prepared image was not created")
    with Image.open(prepared) as result:
        if result.size != (1200, 600):
            raise AssertionError(f"prepared image has unexpected size: {result.size}")
        if not result.info.get("icc_profile"):
            raise AssertionError("prepared image has no embedded ICC profile")
        if JpegImagePlugin.get_sampling(result) != 0:
            raise AssertionError("prepared JPEG is not 4:4:4")
        return {
            "size": list(result.size),
            "icc": True,
            "subsampling": "4:4:4",
            "report": (output / "image-report.json").exists(),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-slideshow", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="wechat_skill_test_") as directory:
        temp = Path(directory)
        fixture_reports = render_fixtures(temp)
        invalid_fragment_test(temp)
        hygiene_result = run([sys.executable, str(SCRIPTS / "hygiene.py"), str(ROOT), "--json"])
        hygiene_report = json.loads(hygiene_result.stdout)
        result = {"fixtures": fixture_reports, "invalid_html_rejected": True, "repository_hygiene": hygiene_report["files_clean"]}
        result["cdn_map"] = cdn_map_test(temp)
        result["image_prepare"] = image_prepare_test(temp)
        if args.with_slideshow:
            result["slideshow"] = slideshow_test(temp)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

