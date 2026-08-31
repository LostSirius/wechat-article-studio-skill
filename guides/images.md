# Image and GIF workflow

## Inventory

For each asset record:

- filename;
- original dimensions;
- corrected EXIF dimensions;
- format and file size;
- visible subject;
- orientation;
- likely article section;
- caption evidence;
- quality problems;
- publication state: local / external / WeChat CDN.

Filenames help locate an image but are not proof of who or what it shows.

## Selection

Use images to carry information and pacing:

- opening: one representative group/venue image;
- lecture: speaker and audience/action;
- travel: landmark or scene;
- presentation: all groups represented fairly;
- reflection: optional quiet scene;
- ending: official QR/footer asset.

Avoid near-duplicates unless they form a deliberate sequence.

## Web copies

When the user supplies a local image folder, create corrected web copies before composing the manuscript:

```bash
python scripts/prepare_images.py original-images web-images
```

This corrects EXIF orientation, converts color to sRGB, embeds an sRGB ICC profile, exports JPEG with 4:4:4 chroma, limits the long edge, and writes a report. It never overwrites originals. Use the web copies in the manuscript; use originals only as the source for a new crop/GIF.

## Clipboard and WeChat delivery

Keep image preparation separate from image delivery:

- a web copy is an optimized local file, not an uploaded WeChat asset;
- seeing a `file://` or relative image in `article.preview.html` proves only that the local
  browser can read the user's disk;
- copying article HTML carries the `<img src="...">` reference, not the file bytes;
- a CDN map can replace local references with HTTPS URLs during copying, but ordinary HTTPS
  URLs still need transfer/re-upload in the WeChat editor;
- final acceptance requires `mmbiz.qpic.cn` (or a confirmed material-library asset) plus a
  phone preview.

If local images remain unresolved, the preview must disable copying and tell the user which
handoff is still required. Never use “图片加载完成” as evidence that the images are paste-ready.

## Caption rules

- State visible person/action/place.
- Use approved names.
- Do not infer emotion, achievement, or identity.
- Keep one sentence.
- Place the caption in the same container as its image.

## Orientation and crop planning

Correct EXIF rotation first. Then choose one target ratio for each sequence.

Common ratios:

- `4:3` (`1080×810`) — landscape events, groups, architecture;
- `3:4` (`1080×1440`) — portrait street scenes, people, vertical architecture;
- source ratio — single photographs when no sequence must match.

For mixed orientations:

1. identify the key subject in every frame;
2. decide whether the sequence reads better as landscape or portrait;
3. record focus as normalized `(x, y)` coordinates from `0.0` to `1.0`;
4. crop preview JPEGs;
5. inspect every preview;
6. only then encode the GIF.

Examples from production:

- portrait 竖幅灯塔 + landscape 横幅海岸建筑: use `4:3`; crop 竖幅灯塔 to retain spire, clock face, and palace roofline;
- two portrait street scenes + one landscape street scene: use `3:4`; crop the landscape frame around the tree/buildings;
- group photos: preserve all people; padding may be safer than cropping.

## Crop versus pad

### Crop to fill

Use when:

- switching orientation causes an obvious jump;
- the subject can survive a crop;
- visual continuity matters.

### Contain with matching background

Use when:

- every person/object must remain;
- cropping would remove context;
- the article background can make padding unobtrusive.

Never use a dark or unrelated letterbox color merely because it matches a heading.

## Slideshow manifest

```json
{
  "output": "fixtures/slideshow/coastline.gif",
  "width": 1080,
  "height": 810,
  "duration_ms": 2300,
  "mode": "cover",
  "background": "#f7f1e8",
  "preview_dir": "fixtures/slideshow/previews",
  "frames": [
    {"src": "fixtures/slideshow/lighthouse.jpg", "focus": [0.42, 0.55]},
    {"src": "fixtures/slideshow/hall.jpg", "focus": [0.48, 0.50]},
    {"src": "fixtures/slideshow/bridge.jpg", "focus": [0.50, 0.48]}
  ]
}
```

Run:

```bash
python scripts/slideshow.py slideshow.json
```

Dependencies:

- Pillow;
- `ffmpeg` on PATH, or `imageio-ffmpeg` installed.

The script creates preview JPEGs and the final GIF. Inspect previews before authorizing overwrite when the output already exists.

## Encoding

Default:

- 2.3 seconds per frame for still-photo slideshows;
- 256-color per-frame palette;
- no dithering for sharp architectural edges and to avoid noisy skies;
- infinite loop.

If smooth gradients band badly, compare `sierra2_4a` dithering, but do not assume it is better. Keep the smaller, cleaner version after visual comparison.

## Still image export

- correct EXIF;
- convert to sRGB/RGB;
- use a practical long edge, usually 1080–1600 px;
- JPEG quality around 82–92 depending on detail;
- export JPEG with 4:4:4 chroma and an sRGB ICC profile;
- retain the untouched original;
- never repeatedly recompress the web export.

## Replacement safety

Before replacing an existing GIF:

1. verify local target path;
2. render to a temporary file;
3. inspect frame count, dimensions, duration, and previews;
4. replace atomically;
5. update the image manifest/CDN mapping;
6. update the article HTML;
7. verify no old URL remains.

Temporary hosting success does not finish the task. The final handoff is transfer to the WeChat material library.

