# Changelog

All notable changes will be documented here. The project follows Keep a Changelog structure
and uses semantic versioning for public releases.

## [Unreleased]

### Added

- Third-party dependency and generated-artwork license notices.
- Monthly Dependabot checks for Python packages and GitHub Actions.
- macOS to the Python 3.10/3.12 CI matrix.
- Optional `cdn_map.json` substitution for local image sources during preview copying.
- Five new style presets (`campus`, `festival`, `tech`, `ink`, `magazine`) alongside the
  original three, each with its own palette and default component variants.
- Manuscript `style` overrides for palette tokens, font, masthead/heading/caption/quote/callout
  variants, paragraph metrics, image inset, and spacing density; unknown or unsafe values fail.
- `scripts/gallery.py` renders one manuscript across presets into a side-by-side index page.
- `article.noimage.html` (numbered image slots) and `article.import.html` (document-wrapped
  fragment) outputs; preview buttons for copy without images and HTML download.
- Documentation for the three delivery routes, including 135编辑器 HTML code mode and the
  秀米 path through a WeChat draft.
- A fourth synthetic fixture exercising the `campus` preset with overrides, and a style
  matrix regression that audits every preset and variant with and without images.

### Changed

- The layout guide now states that the user's brief decides the visual direction and maps
  common Chinese mood words to presets and knobs; SKILL.md no longer defaults silently to
  `academy` for non-institutional content.

- Expanded the documented security boundaries for untrusted media, local executables,
  overwrite behavior, previews, and generated reports.
- Pinned clean-environment test dependencies and clarified upstream license observations.
- Reworked the banner and icon with a bilingual WeChat Article Studio wordmark.
- Grouped editorial guidance under `guides/`, repository policies under `.github/`, and
  supplemental legal notes under `docs/legal/`.
- Preview pages now distinguish local, external HTTPS, and WeChat CDN images, disable copying
  for unresolved local sources, and state explicitly that clipboard HTML contains no image
  file bytes.

## [0.1.0] - 2026-08-31

### Added

- Public repository packaging with bilingual documentation.
- Three anonymous synthetic regression fixtures.
- Cross-platform CI for Python 3.10 and newer.
- Repository hygiene scanner for private paths, experiment artifacts, URLs, and secrets.
- Banner and square icon derived from the second-generation project brand source image.

### Security

- Excluded production articles, real names, photographs, QR codes, screenshots, and local
  experiment outputs from the public package.
