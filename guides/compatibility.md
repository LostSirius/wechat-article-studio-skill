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

`article.preview.html` may contain:

- document shell;
- responsive preview frame;
- copy button;
- JavaScript that copies the article root.

Preview-only code must stay outside the article root.

## Copy workflow

1. Open `article.preview.html` in Chrome or Edge.
2. Wait until all images finish loading.
3. Click “复制到公众号”.
4. Paste into a new WeChat article.
5. Transfer/re-upload every external image to the WeChat material library.
6. Confirm image URLs resolve from `mmbiz.qpic.cn`.
7. Preview on at least one phone before publication.

An image appearing in the desktop editor does not prove it will appear in public preview.

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

