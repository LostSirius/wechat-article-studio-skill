#!/usr/bin/env python3
"""Render one manuscript across several style presets so a user can pick a direction.

The gallery exists because visual direction belongs to the user. Instead of
arguing about adjectives, render the same copy in every candidate preset, open
``index.html``, and let the user point at the column they want. The chosen preset
name (plus any ``style`` overrides) then goes back into the manuscript.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:  # installed as a package
    from . import render as render_module
except ImportError:  # run as a plain script
    import render as render_module  # type: ignore[no-redef]

SCRIPTS = Path(__file__).resolve().parent
PRESETS = render_module.PRESETS


def run(command: list[str]) -> None:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", errors="replace", env=environment
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}\n{result.stderr}"
        )


def index_document(title: str, entries: list[dict[str, str]], width: int) -> str:
    cards = []
    for entry in entries:
        cards.append(
            '<div class="card">'
            f'<div class="head"><b>{render_module.esc(entry["name"])}</b>'
            f'<span>{render_module.esc(entry["label"])}</span></div>'
            f'<p class="brief">{render_module.esc(entry["brief"])}</p>'
            f'<iframe src="{render_module.esc(entry["preview"])}" loading="lazy"></iframe>'
            "</div>"
        )
    return (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\" />\n"
        f"<title>{render_module.esc(title)} · 风格对比</title>\n"
        "<style>\n"
        "body{margin:0;padding:18px;background:#e5e7eb;font-family:Arial,sans-serif;color:#111827}\n"
        "h1{font-size:18px;margin:0 0 6px 0}\n"
        ".tip{font-size:13px;color:#4b5563;margin:0 0 16px 0;line-height:1.6}\n"
        ".grid{display:flex;gap:16px;overflow-x:auto;padding-bottom:12px}\n"
        f".card{{flex:0 0 {width + 2}px;background:#fff;border:1px solid #d1d5db;border-radius:8px;overflow:hidden}}\n"
        ".head{display:flex;justify-content:space-between;align-items:baseline;padding:10px 12px 4px 12px;font-size:14px}\n"
        ".head span{font-size:12px;color:#6b7280}\n"
        ".brief{margin:0;padding:0 12px 10px 12px;font-size:12px;line-height:1.6;color:#4b5563;min-height:56px}\n"
        f"iframe{{display:block;width:{width}px;height:820px;border:0;border-top:1px solid #e5e7eb}}\n"
        "</style>\n</head>\n<body>\n"
        f"<h1>{render_module.esc(title)} · 风格对比</h1>\n"
        "<p class=\"tip\">同一份稿件、不同视觉方向。横向滚动比较，把想要的预设名写回稿件 <code>theme</code>；"
        "细节（配色、章节样式、图注、引语、段落缩进、密度）可再用 <code>style</code> 覆盖。</p>\n"
        '<div class="grid">' + "".join(cards) + "</div>\n</body>\n</html>\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manuscript", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("gallery"))
    parser.add_argument(
        "--presets",
        default=",".join(PRESETS),
        help="comma-separated preset names (default: all)",
    )
    parser.add_argument("--cdn-map", type=Path)
    parser.add_argument(
        "--keep-style",
        action="store_true",
        help="keep the manuscript style overrides instead of showing pure presets",
    )
    parser.add_argument("--width", type=int, default=390, help="iframe width in CSS pixels")
    args = parser.parse_args()

    names = [name.strip() for name in args.presets.split(",") if name.strip()]
    unknown = [name for name in names if name not in PRESETS]
    if unknown:
        raise SystemExit(f"Unknown presets: {', '.join(unknown)}. Available: {', '.join(PRESETS)}")
    if not names:
        raise SystemExit("No presets selected")

    data = json.loads(args.manuscript.read_text(encoding="utf-8"))
    if not args.keep_style:
        data.pop("style", None)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, str]] = []
    for name in names:
        variant = dict(data)
        variant["theme"] = name
        target = output / name
        target.mkdir(parents=True, exist_ok=True)
        manuscript_path = target / "manuscript.json"
        manuscript_path.write_text(json.dumps(variant, ensure_ascii=False, indent=2), encoding="utf-8")
        command = [sys.executable, str(SCRIPTS / "render.py"), str(manuscript_path), "--output-dir", str(target)]
        if args.cdn_map:
            command.extend(["--cdn-map", str(args.cdn_map.resolve())])
        run(command)
        entries.append(
            {
                "name": name,
                "label": PRESETS[name]["label"],
                "brief": PRESETS[name]["brief"],
                "preview": f"{name}/article.preview.html",
            }
        )

    index_path = output / "index.html"
    index_path.write_text(
        index_document(str(data.get("title", "公众号文章")), entries, args.width), encoding="utf-8"
    )
    summary = {
        "index": str(index_path),
        "presets": [entry["name"] for entry in entries],
        "previews": {entry["name"]: str(output / entry["preview"]) for entry in entries},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
