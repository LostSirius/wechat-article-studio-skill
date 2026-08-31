# Third-party notices

This repository does not vendor third-party source or binaries. A normal installation
downloads these Python packages under their own licenses:

- [Pillow](https://github.com/python-pillow/Pillow) — MIT-CMU.
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) — BSD-2-Clause;
  optional slideshow support.

The exact installed versions are recorded in
[requirements.txt](../../requirements.txt). Their complete license texts are available in
the installed distributions and linked source repositories.

The workflow can optionally invoke a user-installed Chrome/Edge browser or FFmpeg executable.
Those programs are not bundled, and their licenses depend on the product and FFmpeg build
selected by the user. Installing this project does not install or relicense them.

Conceptual research references are documented separately in [NOTICE.md](../../NOTICE.md).
