# WeChat compatibility

## Conservative article profile

Use this profile by default because rendered browser HTML is copied into the WeChat editor:

### Allowed tags

`section`, `p`, `span`, `table`, `tbody`, `tr`, `td`, `img`, `br`

### Allowed structural attributes

- `style`
- `src`, `alt`
- `cellpadding`, `cellspacing`
- `data-no-dark` only when an existing workflow demonstrably uses it

### Safe style set

- text: `font-size`, `font-family`, `font-weight`, `color`, `line-height`, `letter-spacing`, `text-align`, `text-indent`, `text-decoration`
- box: `margin`, `padding`, `width`, `max-width`, `height`, `max-height`, `border`, `border-top`, `border-right`, `border-bottom`, `border-left`, `border-collapse`, `background-color`, `box-sizing`
- basic display: `display:block`, `display:inline`, `display:inline-block`, `vertical-align`

Use hex colors. Keep the copied fragment functional even if optional properties are stripped.

### Do not use in the clean fragment

- `style`, `script`, `link`, `iframe`, `video`, `canvas`, `svg`;
- `class`, `id`, inline event handlers;
- `position`, `float`, `grid`, flex layout in strict mode;
- transforms, filters, transitions, CSS animations;
- gradients, CSS variables, media queries, keyframes;
- external fonts;
- semantic heading tags when paragraph headings suffice;
- JavaScript-dependent interactions.

## Clean fragment versus preview

`article.fragment.html` contains only the copied article root `<section>`.

`article.noimage.html` is the same fragment with every image replaced by a numbered dashed
slot that shows the alt text and file name. `article.import.html` wraps the fragment in a
minimal HTML document for editors that import files.

`article.preview.html` may contain:

- document shell;
- responsive preview frame;
- copy and download buttons;
- JavaScript that copies the article root or the no-image version.

Preview-only code must stay outside the article root.

## Critical image handoff rule

The copy button copies HTML and image URL strings. It does **not** place local JPG, PNG, or
GIF binary data on the clipboard.

Consequences:

- `file://`, relative, `blob:`, and `data:` sources may look correct in the local browser but
  cannot be treated as WeChat-ready;
- ordinary HTTPS images may paste temporarily, but they remain externally hosted and must be
  transferred or re-uploaded in the WeChat editor;
- only a verified WeChat material-library URL on `mmbiz.qpic.cn` can be
  treated as publication-ready, and it still requires a phone preview.

The generated preview disables the image-bearing copy button while unresolved local/relative
images remain, but it always offers the no-image copy and the HTML downloads. Do not remove
the guard merely to make the workflow appear one-click; route the user to the path below
that matches their image state.

## Three delivery routes

Tell the user which route applies. All three end with a phone preview.

### Route A — copy with image links

Use when every image already has an HTTPS URL (WeChat CDN, or an approved host plus
`cdn_map.json`).

1. Open `article.preview.html` in Chrome or Edge and read the image-source notice.
2. Click “复制排版（含图片链接）”; this copies layout, text, and image URLs—not files.
3. Paste into a new WeChat article.
4. Transfer/re-upload every non-WeChat image inside the editor and confirm the final URLs
   resolve from `mmbiz.qpic.cn`.

### Route B — copy without images, insert from the material library

Use when the images only exist on the user's computer and no upload host is available. This
is the default answer to “图片粘贴不过去”.

1. Upload the prepared web images to the WeChat material library first, in article order.
2. Click “复制无图版本”. Every image becomes a dashed slot reading “图 N · 此处插入图片”
   with its alt text and file name; captions stay attached below the slot.
3. Paste into the WeChat editor.
4. Place the cursor in each slot, insert the matching library image, then delete the slot text.
5. Check that captions still sit under the right images.

`article.noimage.html` on disk is the same content for users who prefer a file.

### Route C — import HTML into a third-party editor

Use when the user works in 135编辑器 or 秀米 rather than the native editor. Click
“下载 HTML” (or “下载无图 HTML”) or use `article.import.html` from the build folder.

- **135编辑器**: open the toolbar 【HTML】 button to enter code mode, paste the body of the
  file (the root `<section>`), then click 【HTML】 again to return to the visual editor. The
  “导入文章” panel can also accept an HTML file in current versions. Images still need to
  be replaced by editor-hosted or WeChat-hosted copies.
- **秀米**: there is no stable whole-article HTML import. Reliable paths are (1) paste the
  layout into a WeChat draft first, save it, then use 秀米's “导入公众号图文” with the draft
  or article link; or (2) place the fragment into 秀米's “插入HTML代码” component and verify
  the result. Treat either as a starting point that the user finishes inside 秀米.

Editor menus change; state that the names above reflect the versions checked when this
guide was written, and ask the user to confirm the button exists before relying on it.

An image appearing in the desktop editor does not prove it will appear in public preview.

### Optional CDN map

Use a JSON object whose keys are original sources or filenames and whose values are approved
HTTPS URLs:

```json
{
  "photo.jpg": "https://example.org/photo.jpg"
}
```

```bash
python scripts/build.py manuscript.json --output-dir output --cdn-map cdn_map.json
```

The map makes clipboard HTML reference the mapped URL. It does not transfer that URL into
WeChat; a non-`mmbiz.qpic.cn` value still requires editor-side transfer/re-upload.

## Image source states

- `mmbiz.qpic.cn`: publication-ready, still preview.
- HTTPS external image: previewable but must be transferred.
- relative/local image: useful only for local preview; must be uploaded.
- expiring host: urgent transfer; record expiry when known.
- missing/empty `src`: fatal.

Do not tell the user that WeChat “automatically saved” an external image unless verified in the editor/material library.

## Links

External article links may be stripped or disabled. Preserve visible source names and, when appropriate, move URLs to a reference section or the “原文链接” field. Do not rely on arbitrary anchor behavior.

## GIF constraints

GIF is the most portable way to achieve automatic image switching inside article content.

- every frame must have identical dimensions;
- stay within the account/editor upload limit;
- GIF supports only 256 colors, so gradients and blue skies may band;
- preview the actual animation, not only frame 1;
- transfer the final GIF to the WeChat CDN.

## Dark mode

Do not depend on pure white text over a background that may be stripped. For dark blocks:

- set background and text colors inline on the same or nested elements;
- keep a readable border/fallback;
- use dark blocks sparingly;
- inspect a pasted phone preview.

## Audit expectations

The audit script is intentionally stricter than every current WeChat editor variant. A stricter profile trades some novelty for reproducible copy/paste behavior.

When a user explicitly requests a modern effect:

1. keep a conservative fallback;
2. isolate the risky component;
3. state which property may be filtered;
4. test paste behavior before delivery.

