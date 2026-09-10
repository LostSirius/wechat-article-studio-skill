# Benchmark and evaluation boundary

## Public regression corpus

The repository contains four anonymous synthetic manuscripts:

- chronological institutional reporting (`academy`);
- dense academic news with facts, table, callout, and quote (`minimal`);
- profile/interview narrative with attributed fictional quotes (`editorial`);
- club activity recap using the `campus` preset with `style` overrides.

A style matrix additionally renders one manuscript through every preset, every component
variant, and one combined override set, auditing both the image-bearing and the no-image
fragment for each case.

The suite verifies rendering, strict auditing, preview/fragment separation, invalid HTML and
invalid style rejection, gallery generation, image ICC and JPEG 4:4:4 behavior, slideshow
dimensions/frame count, and repository hygiene. All files are generated in an
operating-system temporary directory.

## Current public baseline

Local run on 2026-09-10 with Python 3.12:

- 4/4 fixtures: `strict_compatibility=100`, `editorial_heuristic=100`;
- 0 fatal issues and 0 warnings across the synthetic fixtures;
- 27 style-matrix cases (8 presets, 18 variants, 1 combined override) with 0 fatal issues;
- invalid HTML, missing image alt text, and invalid style values rejected;
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
