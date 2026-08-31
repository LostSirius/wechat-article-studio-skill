# Changelog

All notable changes will be documented here. The project follows Keep a Changelog structure
and uses semantic versioning for public releases.

## [Unreleased]

### Added

- Third-party dependency and generated-artwork license notices.
- Monthly Dependabot checks for Python packages and GitHub Actions.
- macOS to the Python 3.10/3.12 CI matrix.

### Changed

- Expanded the documented security boundaries for untrusted media, local executables,
  overwrite behavior, previews, and generated reports.
- Pinned clean-environment test dependencies and clarified upstream license observations.
- Reworked the banner and icon with a bilingual WeChat Article Studio wordmark.
- Grouped editorial guidance under `guides/`, repository policies under `.github/`, and
  supplemental legal notes under `docs/legal/`.

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
