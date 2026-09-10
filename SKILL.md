---
name: wechat-article-studio
description: Creates or revises polished Chinese WeChat Official Account articles from briefs, notes, documents, reference posts, and image folders. Use when the user asks to write, humanize, typeset, beautify, preview, or prepare a 微信公众号/公众号 article; reduce AI-like prose; reproduce an editorial visual direction; process article images or slideshow GIFs; or generate paste-ready inline-style HTML. Covers evidence checking, voice matching, editorial rewriting, layout planning, image preparation, deterministic rendering, WeChat compatibility checks, and iterative quality review.
---

# WeChat Article Studio

Produce an article that reads as edited by a human newsroom and looks intentionally art-directed. Treat writing, layout, and imagery as one editorial system.

## Default behavior

- Work end to end when the user asks to “直接生成 / 一键制作 / 自主优化 / 不用问”.
- Otherwise ask only for a choice that materially changes facts, voice, or destructive image cropping.
- Prefer a project-local output folder. Never publish, push to a draft box, or overwrite source images unless requested.
- Preserve user-approved wording, names, dates, quotation wording, captions, and attribution.
- Never claim “SOTA” from self-scoring alone. Report the benchmark used and remaining subjective limits.

## Load supporting guidance

Read only what the task needs:

- Writing, fact control, and low-AI editing: [guides/editorial.md](guides/editorial.md)
- Style presets, `style` overrides, brief-to-knob mapping, manuscript schema: [guides/layout.md](guides/layout.md)
- WeChat HTML restrictions and the three delivery routes (copy with images, copy without images, HTML import): [guides/compatibility.md](guides/compatibility.md)
- Image selection, cropping, GIFs, and CDN handoff: [guides/images.md](guides/images.md)
- Evaluation rubric and iteration gates: [guides/quality.md](guides/quality.md)
- Research boundaries and provenance: [guides/research.md](guides/research.md)

## Workflow

### 1. Classify the job

Choose one mode:

1. **Create** — notes/assets → article + HTML.
2. **Rewrite** — existing copy → fact-preserving human edit + HTML.
3. **Format only** — approved copy → layout; do not rewrite.
4. **Asset only** — crop/compress/build GIF; do not alter copy.

If the request combines modes, run them in that order.

### 2. Inventory sources before writing

Read all supplied text, schedules, PDFs, reference links, existing HTML, images, and filename metadata.

Create a private evidence ledger with:

- verified fact;
- source and date;
- preferred wording/name;
- conflict or uncertainty;
- publish / omit / ask.

Use the most authoritative and current source. A live schedule outranks an old handbook; a user correction outranks inferred metadata. Reference posts define tone and structure, not facts.

Do not silently turn promotional bios, estimates, or future-tense plans into completed events. Remove or qualify unsupported titles, numbers, awards, superlatives, and causal claims.

### 3. Build a voice fingerprint

When references are available, extract:

- point of view and distance;
- opening pattern;
- sentence-length rhythm;
- paragraph length;
- preferred naming and punctuation;
- heading style;
- caption style;
- amount of evaluation versus observation;
- closing pattern.

If a reference page is blocked, use searchable excerpts, the organization’s other posts, and user-provided sample paragraphs. State internally that the match is approximate; do not invent access.

### 4. Draft or edit the article

Follow [guides/editorial.md](guides/editorial.md).

Core rules:

- Lead with who, when, where, what happened, and why it matters.
- Each paragraph must add a fact, scene, quote, decision, or consequence.
- Prefer concrete nouns and verbs over abstract significance claims.
- Vary sentence and paragraph length naturally; do not manufacture choppiness.
- Keep the voice appropriate to the account. Institutional reportage is usually third person, not forced internet slang.
- Quotes remain quotes only when supplied or sourced.
- Captions are complete factual sentences and name the visible action.
- Titles of talks use the punctuation convention established by the user or account.

Run the low-AI pass after the factual draft, never before. Humanization must not alter facts.

### 5. Plan structure and image rhythm

Before styling, make a compact article plan:

- opening image and lead;
- 3–6 sections;
- one dominant information hierarchy;
- image-to-paragraph mapping;
- at most 3–5 component families;
- ending and credits.

Choose elements because of content shape:

- chronology → date labels or restrained timeline;
- comparison → simple table, maximum four columns;
- quote → quote block with real attribution;
- dense facts → information card;
- travel/reportage → full-width image sequences and factual captions;
- reflection → one quiet quote card per speaker.

Do not add a dashboard, English labels, numbered chapters, callouts, or decorative cards merely because a template contains them. Three consecutive blocks must not share the same visual density.

### 6. Resolve the visual direction from the brief

The user owns the look; this skill owns the execution. Read the brief for mood words,
colors, audience, and references, then map them with the table in
[guides/layout.md](guides/layout.md):

- pick one of the eight presets (`academy`, `editorial`, `minimal`, `campus`, `festival`,
  `tech`, `ink`, `magazine`) as the starting point;
- adjust individual knobs in the manuscript `style` object—palette tokens, masthead,
  heading, caption, quote, callout, paragraph metrics, image inset, density—rather than
  inventing new HTML;
- when the user gives no direction, run `python scripts/gallery.py manuscript.json
  --output-dir gallery`, open `gallery/index.html`, and let them choose a column; do not
  silently default to `academy` for non-institutional content;
- state the chosen preset and overrides in the delivery so the user can redirect with one
  sentence (“更活泼一点” → `pill`/`underline` + `airy`; “更正式” → `frame`/`rule` + indented).

If the user supplies a reference image or post, translate its hierarchy, spacing, palette roles, and component rhythm into the same knobs. Do not copy logos, proprietary illustrations, or distinctive copyrighted artwork.

### 7. Create the manuscript

Write a UTF-8 JSON manuscript following [guides/layout.md](guides/layout.md). Keep prose separate from presentation.

Use `[[em:...]]` only for truly scannable anchors. Usually 0–2 per section. Fixed “1–3 highlights per paragraph” is prohibited.

Build:

```bash
python scripts/build.py manuscript.json --output-dir output
```

When approved HTTPS or WeChat CDN URLs are available for local assets, provide a JSON
source-to-URL map with `--cdn-map cdn_map.json`. The preview may also load
`output/cdn_map.json` automatically.

The build pipeline produces:

- `article.fragment.html` — clean WeChat body fragment;
- `article.noimage.html` — same layout with numbered image slots instead of `<img>`;
- `article.import.html` — fragment wrapped in a minimal document for HTML-importing editors;
- `article.preview.html` — browser preview with copy (with/without images) and download actions;
- `article.render-report.json` — structure, resolved style, and asset report.
- `audit.json` — deterministic compatibility/editorial report;
- `mobile-375.png`, `mobile-414.png` — real browser screenshots when Chrome/Edge is available;
- `build-report.json` — verified artifact paths and screenshot status.

### 8. Prepare images

Follow [guides/images.md](guides/images.md).

- When a local image folder is supplied, generate EXIF-corrected web copies with `scripts/prepare_images.py`; keep originals untouched.
- A browser can render `file://` and relative images from the user's computer, but clipboard
  HTML does not contain those image files. Never describe such a preview as paste-ready.
- Classify each source before delivery: local/relative images require upload; non-WeChat
  HTTPS images require transfer; only verified `mmbiz.qpic.cn` images are publication-ready.
- Correct EXIF rotation before judging orientation.
- Inspect every original, not only the existing GIF.
- Decide a target aspect ratio per image group.
- Crop to the subject with explicit focus; never center-crop blindly.
- For slideshow GIFs, every frame must have identical dimensions.
- Prefer crop-to-fill when orientation jumps are visually disruptive; use matching background padding only when preserving the full frame matters more.
- Preview every frame before replacing the original.

For a slideshow manifest:

```bash
python scripts/slideshow.py slideshow.json
```

### 9. Validate deterministically

`build.py` already runs the audit. Rerun it directly after any manual output change:

```bash
python scripts/audit.py output/article.fragment.html --manuscript manuscript.json
```

Fix every fatal error. Review every warning rather than hiding it.

Required gates:

- no forbidden tags, attributes, or strict-profile CSS;
- no missing image source or broken local path;
- no unresolved local/relative image when the user expects one-click copy/paste delivery;
- all slideshow frames have identical dimensions;
- no unsupported factual placeholder presented as fact;
- all approved source paragraphs represented;
- no obvious boilerplate cluster;
- acceptable paragraph and sentence rhythm;
- captions and credits complete.

### 10. Review the rendered result

Inspect at approximately 375 px and 414 px widths. Check:

- title wraps deliberately;
- text remains 15–16 px and readable;
- no card or decoration overwhelms photographs;
- section transitions are distinguishable without looking mechanical;
- captions stay attached to images;
- dark-mode-sensitive text remains legible;
- animated frames do not jump in size or subject scale.

If screenshots or browser preview are unavailable, say the visual review was structural, not pixel-perfect. Never claim a screenshot review unless the screenshot files exist and are included in the delivery report.

### 11. Iterate

Use the rubric in [guides/quality.md](guides/quality.md). For each failed dimension:

1. identify the exact paragraph, component, or frame;
2. change one cause rather than switching the entire theme;
3. rerender;
4. rerun the audit;
5. compare against the prior version.

Stop only when deterministic gates pass and no rubric dimension is below 4/5, or when a missing fact, inaccessible asset, or user-only preference blocks further improvement.

## Delivery

Give the user:

- final Markdown or manuscript path;
- clean HTML path;
- preview HTML path;
- processed asset paths;
- audit result and what was visually reviewed;
- unresolved placeholders or facts;
- chosen preset and `style` overrides, and how to redirect them;
- explicit image state: local / external HTTPS / WeChat CDN;
- the delivery route that matches that state, from [guides/compatibility.md](guides/compatibility.md):
  - **A** images have HTTPS URLs → “复制排版（含图片链接）” → paste → transfer in the editor;
  - **B** images are local only → upload to the material library → “复制无图版本” → paste →
    insert each image into its numbered slot;
  - **C** the user edits in 135编辑器 or 秀米 → “下载 HTML” / `article.import.html` → 135编辑器
    【HTML】code mode or “导入文章”; 秀米 via a WeChat draft link and “导入公众号图文”;
- in every route: confirm `mmbiz.qpic.cn` → phone preview.

The copy actions copy HTML layout and image URLs, not local image binaries. Do not say
images are safely pasted or published merely because they appear in the browser or desktop
editor. Final public images should resolve from `mmbiz.qpic.cn` or the official material
library.

