# Contributing

Thank you for improving the project.

1. Use Python 3.10 or newer.
2. Install `requirements.txt`.
3. Keep changes focused and independently written.
4. Run:

```bash
python -m compileall -q scripts
python scripts/self_test.py --with-slideshow
python scripts/hygiene.py .
```

Fixtures must be synthetic and explicitly marked as fictional. Do not submit real names,
private articles, account QR codes, screenshots, event photographs, local absolute paths,
access tokens, copied third-party themes, or generated run/output directories.

Bug reports should include the smallest anonymized manuscript and the audit report. Visual
changes should explain the content problem they solve, not only the color change.

The repository is maintained and code-owned by `@LostSirius`. To keep the default branch's
GitHub contributor attribution limited to that maintainer, dependency-bot suggestions must
be reapplied in a maintainer-authored commit rather than merged directly.
