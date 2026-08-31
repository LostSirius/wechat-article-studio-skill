# Research notes and provenance

Research snapshot: 2026-08-31.

This project is independently implemented. Public references informed problem framing,
workflow decomposition, and evaluation questions; no third-party code, theme template,
or proprietary visual asset is included.

## Public references

- [isjiamu/gzh-design-skill](https://github.com/isjiamu/gzh-design-skill) — theme libraries,
  progressive disclosure, validation, and preview workflows. Upstream is AGPL-3.0;
  this repository contains none of its code or theme templates.
- [zjp1997720/wechat-styler](https://github.com/zjp1997720/wechat-styler) — structured
  rendering and output-contract ideas. Licensed MIT; implementation here is independent.
- [dengqikuang/wechat-article-skills](https://github.com/dengqikuang/wechat-article-skills) —
  separation of writing, formatting, and publishing responsibilities.
- [xiaohuailabs/xiaohu-wechat-format](https://github.com/xiaohuailabs/xiaohu-wechat-format) —
  content-shaped components and density rhythm.
- [geekjourneyx/md2wechat-skill](https://github.com/geekjourneyx/md2wechat-skill) —
  readiness checks and image/cover pipeline concepts.
- [limin112/min-skill](https://github.com/limin112/min-skill) — narrow skill triggers,
  reusable blocks, and explicit manual handoff.
- [larashero3-dotcom/lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone)
  and [hongcha1101/de-aigc-ch](https://github.com/hongcha1101/de-aigc-ch) — discourse-level
  editing signals. Heuristics are not authorship detectors.

## Design boundary

The public claim is a reproducible local editorial workflow, not state of the art.
Static scores cover only rules encoded in the auditor. A meaningful comparative claim
would need a shared corpus, blinded human review, editor paste tests across versions,
and published comparator results.
