# Architecture

## Layers

1. **Editorial guidance** — `SKILL.md` dispatches to six root-level references.
2. **Content contract** — a UTF-8 JSON manuscript stores facts and block order without raw HTML.
3. **Renderer** — `render.py` escapes text, expands only `[[em:...]]`, resolves a style
   (named preset merged with validated manuscript `style` overrides), and emits a strict
   fragment, a no-image fragment with numbered slots, an importable document, and a richer
   preview shell. `gallery.py` runs the renderer across presets for direction review.
4. **Audit** — `audit.py` parses the fragment, enforces allowlists, checks image states, and
   reports editorial signals without rewriting source text.
5. **Assets** — `prepare_images.py` creates non-destructive web copies; `slideshow.py` makes
   dimensionally stable GIFs from explicit focus coordinates.
6. **Orchestration** — `build.py` renders, audits, optionally screenshots, and writes a report.
7. **Regression** — `self_test.py` uses temporary directories and synthetic fixtures;
   `hygiene.py` checks repository contents before publication.

## Trust boundaries

- Manuscript text is untrusted and always HTML-escaped.
- Raw HTML is not a supported manuscript block.
- Preview JavaScript is allowed only outside the copied article root.
- External and local images are never treated as publication-ready.
- Static editorial warnings are prompts for review, not factual or authorship judgments.

## Output contract

The fragment uses a conservative subset of tags, attributes, and inline CSS; every preset and
component variant must pass the same audit, which the style matrix regression enforces. The
preview may use a document shell and JavaScript, but copying targets only the article root or
the embedded no-image fragment. Build reports state whether screenshots actually exist and
which assets still require upload.
