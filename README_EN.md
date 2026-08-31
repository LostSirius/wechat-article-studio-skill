<p align="center">
  <img src="assets/wechat-article-studio-banner.png" alt="WeChat Article Studio banner" width="100%">
</p>

# WeChat Article Studio

A local editorial pipeline for WeChat Official Account articles: evidence control,
Chinese editorial revision, content-shaped layouts, image preparation, conservative
inline HTML, deterministic audits, and explicit publishing handoff.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-2f855a)](LICENSE)
[![CI](https://github.com/LostSirius/wechat-article-studio-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/LostSirius/wechat-article-studio-skill/actions/workflows/ci.yml)

[GitHub](https://github.com/LostSirius/wechat-article-studio-skill) · [中文](README.md) · [Architecture](docs/ARCHITECTURE.md) · [Compatibility](docs/WECHAT-COMPATIBILITY.md) · [Benchmark](docs/BENCHMARK.md)

## What makes it different

This is not a color-swap template. It starts with a source ledger and voice fingerprint,
uses components only when the content needs them, keeps prose separate from presentation,
and treats WeChat paste/CDN/phone preview as required manual delivery steps.

Core capabilities:

- `academy`, `editorial`, and `minimal` editorial recipes;
- structured JSON manuscript to conservative inline-style HTML;
- strict tag, attribute, and CSS auditing;
- EXIF correction, embedded sRGB ICC, and JPEG 4:4:4 export;
- subject-aware cover/contain slideshow GIF generation;
- synthetic regressions on Windows, Ubuntu, and macOS plus repository hygiene scanning;
- seven Python CLIs plus one lightweight version module under `scripts/`.

## Install and test

Clone the repository; no GitHub Release is required:

```bash
git clone https://github.com/LostSirius/wechat-article-studio-skill.git
```

Windows PowerShell:

```powershell
cd wechat-article-studio-skill
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe scripts/self_test.py --with-slideshow
```

macOS / Linux:

```bash
cd wechat-article-studio-skill
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python scripts/self_test.py --with-slideshow
```

For a project-level Cursor installation, copy the repository to
`.cursor/skills/wechat-article-studio`. For a personal installation, copy it to
`$HOME/.cursor/skills/wechat-article-studio`. The root-level `SKILL.md` is directly usable.

Other agents may read the Markdown guidance and call the Python CLIs, but automatic skill
discovery, triggers, permissions, and context loading vary. Only the Cursor layout and local
Python workflow are tested here.

## Quick start

```bash
python3 scripts/build.py examples/manuscript.json --output-dir output --no-screenshots
python3 scripts/audit.py output/article.fragment.html --manuscript examples/manuscript.json
```

The build writes a clean fragment, browser preview, render report, audit report, and build
report. Screenshots are optional when Chrome or Edge is available.

## Important limits

A static score of 100 means only that the encoded audit rules passed. It is not WeChat
certification. The copy button copies HTML layout and image URLs, not local JPG, PNG, or GIF
files. The preview disables copying when unresolved local/relative images remain. An optional
`--cdn-map cdn_map.json` can substitute approved HTTPS URLs, but non-WeChat URLs still require
transfer/re-upload in the editor. Before publishing, confirm final `mmbiz.qpic.cn` delivery
and run a phone preview.
The project does not claim SOTA; public tests are synthetic engineering regressions, not a
blinded editorial benchmark.

## Maintainer

The current maintainer and code owner is [LostSirius](https://github.com/LostSirius).

## Attribution and license

The implementation is independent and MIT-licensed. Public projects that informed ideas
are linked in [NOTICE.md](NOTICE.md) and [guides/research.md](guides/research.md); runtime
dependencies are listed in
[docs/legal/THIRD_PARTY_NOTICES.md](docs/legal/THIRD_PARTY_NOTICES.md), and artwork terms
are in [docs/legal/ASSETS-LICENSE.md](docs/legal/ASSETS-LICENSE.md). No third-party code or
theme template is included. This project is not affiliated with or endorsed by Tencent or
WeChat, and its generated brand artwork contains no official WeChat logo.
