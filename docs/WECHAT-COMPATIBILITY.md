# WeChat compatibility

The repository uses an intentionally conservative browser-to-editor profile. It is an
engineering baseline, not an official Tencent or WeChat specification.

## Clean fragment

Allowed tags are `section`, `p`, `span`, `table`, `tbody`, `tr`, `td`, `img`, and `br`.
The fragment uses inline styles only, no classes, IDs, event handlers, scripts, external
fonts, flex/grid, positioning, gradients, transforms, filters, or CSS variables.

## Preview boundary

`article.preview.html` has copy buttons (with image links, and without images), HTML
download buttons, and a clipboard fallback. This code must remain outside the article root and
is never part of `article.fragment.html`, `article.noimage.html`, or `article.import.html`.

## Publication checklist

1. Open the preview in Chrome or Edge and read the image-source notice.
2. Pick the route that matches the image state: copy with image links when every image has an
   HTTPS URL; copy without images when they only exist locally, then insert each image into
   its numbered slot from the material library; or download the HTML for 135编辑器 code mode
   (秀米 imports through a WeChat draft link instead).
3. Paste or import into a new WeChat editor draft.
4. Transfer or re-upload all non-material-library images and remove any leftover slot text.
5. Confirm final image delivery uses the official material library or `mmbiz.qpic.cn`.
6. Inspect a phone preview, including dark mode when relevant.
7. Verify GIF dimensions, timing, file size, and playback.

A strict compatibility score of 100 means only that the local allowlist passed. Editor
behavior can change and must still be tested before publication.
