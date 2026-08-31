# Benchmark and evaluation boundary

## Public regression corpus

The repository contains three anonymous synthetic manuscripts:

- chronological institutional reporting (`academy`);
- dense academic news with facts, table, callout, and quote (`minimal`);
- profile/interview narrative with attributed fictional quotes (`editorial`).

The suite verifies rendering, strict auditing, preview/fragment separation, invalid HTML
rejection, image ICC and JPEG 4:4:4 behavior, slideshow dimensions/frame count, and
repository hygiene. All files are generated in an operating-system temporary directory.

## Current public baseline

Local clean-environment run on 2026-08-31 with Python 3.12:

- 3/3 fixtures: `strict_compatibility=100`, `editorial_heuristic=100`;
- 0 fatal issues and 0 warnings across the synthetic fixtures;
- invalid HTML and missing image alt text rejected;
- 1200×600 test JPEG retained sRGB ICC and 4:4:4 sampling;
- 540×720 two-frame GIF matched expected dimensions and frame count;
- repository hygiene scan returned zero findings.

## Interpreting scores

`strict_compatibility` measures only encoded HTML/CSS rules. `editorial_heuristic` counts
selected discourse signals in non-quote body paragraphs. Neither score verifies facts,
human authorship, visual quality, editor paste behavior, or publication success.

Therefore:

- 100 is not official WeChat certification;
- the public synthetic suite is not evidence of SOTA;
- a real article still needs source checking, editor paste testing, CDN transfer, and
  phone preview.

## Future comparative protocol

A credible comparison should publish a shared anonymized corpus, comparator versions and
dates, blinded editorial ratings, mobile render review, WeChat paste outcomes, and all
failure cases. Until that exists, this project reports only deterministic regression data.
