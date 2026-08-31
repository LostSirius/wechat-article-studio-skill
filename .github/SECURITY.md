# Security policy

Report suspected vulnerabilities privately through the repository host's security advisory
feature when available. Do not open a public issue containing secrets, unpublished articles,
personal data, local paths, or account screenshots.

Supported security work focuses on the current default branch. Reports should include impact,
minimal reproduction steps, affected script, and a redacted sample. The maintainers will
acknowledge and triage reports as capacity allows; no fixed response SLA is promised.

## Security boundaries

- This is a local preparation tool. It does not sign in to WeChat or publish articles.
- `audit.py` checks this project's WeChat fragment contract; it is not a general-purpose
  HTML sanitizer. Never treat audited output as safe for an unrelated execution context.
- The preview page contains local copy-to-clipboard JavaScript and may request externally
  hosted images. The publishable fragment must never contain scripts, event handlers, raw
  manuscript HTML, or external font dependencies.
- Images, fonts, manuscripts, and slideshow manifests are untrusted input. Malformed media
  can target Pillow, FFmpeg, or a preview browser. Apply file-size and pixel-count limits,
  keep these tools patched, and process unknown files in a sandbox.
- `slideshow.py --force` can replace the output path named by a manifest. Use only trusted
  manifests and keep outputs inside a dedicated build directory.
- Browser and FFmpeg paths cause local executables to run. Prefer trusted absolute paths and
  do not accept executable locations from an untrusted manuscript.
- Generated HTML, reports, and screenshots may preserve article text, personal information,
  image URLs, and local paths. Do not commit them without review.

Pillow and `imageio-ffmpeg` are Python dependencies. Chrome/Edge and system FFmpeg are optional
external tools and are not distributed by this repository. See
[../docs/legal/THIRD_PARTY_NOTICES.md](../docs/legal/THIRD_PARTY_NOTICES.md).

Security checks do not establish copyright, portrait consent, QR-code destination safety, or
the final behavior of the WeChat editor. Verify those separately before publication.
