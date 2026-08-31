#!/usr/bin/env python3
"""One-command render, audit, and mobile screenshot pipeline."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent


def run(command: list[str], allow: set[int] = {0}) -> subprocess.CompletedProcess[str]:
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
    if result.returncode not in allow:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result


def browser_path(explicit: str | None) -> str | None:
    candidates = [
        explicit,
        os.environ.get("CHROME_PATH"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("msedge"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def screenshot(browser: str, preview: Path, destination: Path, width: int, height: int) -> None:
    command = [
        browser,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={destination}",
        preview.resolve().as_uri(),
    ]
    run(command)
    if not destination.exists() or destination.stat().st_size == 0:
        raise RuntimeError(f"Browser did not create screenshot: {destination}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manuscript", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--cdn-map", type=Path)
    parser.add_argument("--browser")
    parser.add_argument("--screenshot-height", type=int, default=12000)
    parser.add_argument("--no-screenshots", action="store_true")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    cdn_map_path = args.cdn_map.resolve() if args.cdn_map else output / "cdn_map.json"
    if args.cdn_map and not cdn_map_path.exists():
        raise FileNotFoundError(f"CDN map not found: {cdn_map_path}")

    render_command = [
        sys.executable,
        str(SCRIPTS / "render.py"),
        str(args.manuscript.resolve()),
        "--output-dir",
        str(output),
    ]
    if cdn_map_path.exists():
        render_command.extend(["--cdn-map", str(cdn_map_path)])
    run(render_command)
    fragment = output / "article.fragment.html"
    preview = output / "article.preview.html"
    audit_result = run(
        [
            sys.executable,
            str(SCRIPTS / "audit.py"),
            str(fragment),
            "--manuscript",
            str(args.manuscript.resolve()),
            "--json",
        ],
        allow={0, 1},
    )
    try:
        audit = json.loads(audit_result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Audit did not return valid JSON.\n"
            f"stdout:\n{audit_result.stdout}\n"
            f"stderr:\n{audit_result.stderr}"
        ) from exc
    audit_path = output / "audit.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    screenshots = []
    screenshot_status = "disabled" if args.no_screenshots else "not-run"
    browser = None if args.no_screenshots else browser_path(args.browser)
    if browser:
        for width in (375, 414):
            destination = output / f"mobile-{width}.png"
            screenshot(browser, preview, destination, width, args.screenshot_height)
            screenshots.append(str(destination))
        screenshot_status = "complete"
    elif not args.no_screenshots:
        screenshot_status = "browser-not-found"

    report = {
        "manuscript": str(args.manuscript.resolve()),
        "output_dir": str(output),
        "cdn_map": str(cdn_map_path) if cdn_map_path.exists() else None,
        "fragment": str(fragment),
        "preview": str(preview),
        "audit": str(audit_path),
        "readiness": audit["readiness"],
        "scores": audit["scores"],
        "fatal": len(audit["fatal"]),
        "warnings": len(audit["warnings"]),
        "screenshot_status": screenshot_status,
        "screenshots": screenshots,
        "browser": browser,
    }
    report_path = output / "build-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if audit["fatal"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

