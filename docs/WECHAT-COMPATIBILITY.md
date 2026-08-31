# WeChat compatibility

The repository uses an intentionally conservative browser-to-editor profile. It is an
engineering baseline, not an official Tencent or WeChat specification.

## Clean fragment

Allowed tags are `section`, `p`, `span`, `table`, `tbody`, `tr`, `td`, `img`, and `br`.
The fragment uses inline styles only, no classes, IDs, event handlers, scripts, external
fonts, flex/grid, positioning, gradients, transforms, filters, or CSS variables.

## Preview boundary

`article.preview.html` has a copy button and clipboard fallback. This code must remain
outside the article root and is never part of `article.fragment.html`.

## Publication checklist

1. Open the preview in Chrome or Edge and wait for every image.
2. Copy the article root and paste it into a new WeChat editor draft.
3. Transfer or re-upload all non-material-library images.
4. Confirm final image delivery uses the official material library or `mmbiz.qpic.cn`.
5. Inspect a phone preview, including dark mode when relevant.
6. Verify GIF dimensions, timing, file size, and playback.

A strict compatibility score of 100 means only that the local allowlist passed. Editor
behavior can change and must still be tested before publication.
