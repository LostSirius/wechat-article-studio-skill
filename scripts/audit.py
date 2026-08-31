#!/usr/bin/env python3
"""Strict WeChat HTML and editorial heuristic audit."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


ALLOWED_TAGS = {"section", "p", "span", "table", "tbody", "tr", "td", "img", "br"}
GLOBAL_ATTRS = {"style"}
TAG_ATTRS = {
    "img": {"src", "alt"},
    "table": {"cellpadding", "cellspacing"},
}
ALLOWED_CSS = {
    "font-size", "font-family", "font-weight", "color", "line-height",
    "letter-spacing", "text-align", "text-indent", "text-decoration",
    "margin", "padding", "width", "max-width", "height", "max-height",
    "border", "border-top", "border-right", "border-bottom", "border-left",
    "border-collapse", "background-color", "box-sizing", "display",
    "vertical-align",
}
FORBIDDEN_VALUE = re.compile(
    r"rgba?\s*\(|linear-gradient|radial-gradient|position\s*:|float\s*:|"
    r"display\s*:\s*(flex|grid)|transform\s*:|filter\s*:|var\s*\(|"
    r"@media|@keyframes|url\s*\(",
    re.I,
)
CJK = re.compile(r"[\u3400-\u9fff]")
SENTENCE_SPLIT = re.compile(r"[。！？!?]+")
PLACEHOLDER = re.compile(r"【待补】|\{\{[^}]+\}\}|REPLACE_|TODO|TBD", re.I)

AI_PATTERNS = [
    ("zero-reference", re.compile(r"^(值得注意的是|需要指出的是|不可否认的是|更重要的是)[，,]?")),
    (
        "template-order",
        re.compile(
            r"^(首先|其次|再次|综上所述|由此可见)[，,]?"
            r"|首先.{0,120}其次"
            r"|其次.{0,120}(再次|最后)"
        ),
    ),
    ("empty-symmetry", re.compile(r"不仅.{0,35}(更是|而且|还)|不只是.{0,35}更是")),
    ("corporate-buzz", re.compile(r"赋能|闭环|抓手|颗粒度|注入.{0,8}动能|开启.{0,8}新篇章")),
    ("canned-meaning", re.compile(r"具有.{0,10}重要意义|奠定.{0,10}坚实基础|发挥着.{0,10}重要作用")),
    ("vague-authority", re.compile(r"研究表明|专家认为|业内普遍认为|有观点认为")),
    ("idealized-metaphor", re.compile(r"如同一位.{0,12}(导师|引路人|伙伴)|像一位.{0,12}(导师|引路人|伙伴)")),
]


class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.paragraph_stack: list[list[str]] = []
        self.paragraphs: list[str] = []
        self.tags: list[tuple[str, list[tuple[str, str | None]]]] = []
        self.images: list[dict[str, str]] = []
        self.raw_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(tag)
        self.tags.append((tag, attrs))
        if tag == "p":
            self.paragraph_stack.append([])
        if tag == "img":
            data = {k: v or "" for k, v in attrs}
            self.images.append({"src": data.get("src", ""), "alt": data.get("alt", "")})

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self.paragraph_stack:
            text = "".join(self.paragraph_stack.pop()).strip()
            if text:
                self.paragraphs.append(text)
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.raw_text.append(text)
            if self.paragraph_stack:
                self.paragraph_stack[-1].append(data)


def add(items: list[dict[str, str]], code: str, message: str, sample: str = "") -> None:
    item = {"code": code, "message": message}
    if sample:
        item["sample"] = sample[:100]
    items.append(item)


def parse_css(css: str) -> list[tuple[str, str]]:
    result = []
    for declaration in css.split(";"):
        if not declaration.strip():
            continue
        if ":" not in declaration:
            result.append((declaration.strip().lower(), ""))
            continue
        key, value = declaration.split(":", 1)
        result.append((key.strip().lower(), value.strip()))
    return result


def editorial_audit(paragraphs: list[str]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    sentence_lengths: list[int] = []
    endings: list[str] = []
    for index, paragraph in enumerate(paragraphs, 1):
        clean = re.sub(r"\s+", "", paragraph)
        if len(clean) > 200:
            add(warnings, "long-paragraph", f"第 {index} 段超过 200 字，检查是否需要在语义转折处拆分", clean)
        for name, pattern in AI_PATTERNS:
            if pattern.search(clean):
                add(warnings, name, f"第 {index} 段命中需人工判断的 AI 式结构", clean)
        sentences = [s for s in SENTENCE_SPLIT.split(clean) if s]
        for sentence in sentences:
            length = len(sentence)
            sentence_lengths.append(length)
            if length > 72:
                add(warnings, "long-sentence", f"第 {index} 段有超过 72 字的长句", sentence)
            if length >= 8:
                endings.append(sentence[-6:])

    if len(sentence_lengths) >= 8:
        mean = statistics.mean(sentence_lengths)
        spread = statistics.pstdev(sentence_lengths)
        if mean and spread / mean < 0.25:
            add(warnings, "uniform-cadence", "句长变化偏小，检查是否呈现机械匀速节奏")

    repeated = [(ending, count) for ending, count in Counter(endings).items() if count >= 3]
    for ending, count in repeated[:3]:
        add(warnings, "repeated-ending", f"有 {count} 个句子以相似片段收束", ending)
    return warnings


def audit(path: Path, manuscript: Path | None = None) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8", errors="replace")
    parser = AuditParser()
    parser.feed(source)
    fatals: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    manuscript_data: dict[str, Any] | None = None
    quote_sources: list[str] = []
    if manuscript:
        manuscript_data = json.loads(manuscript.read_text(encoding="utf-8"))
        for section in manuscript_data.get("sections") or []:
            for block in section.get("blocks") or []:
                if isinstance(block, dict) and block.get("type") == "quote":
                    quote_sources.append(re.sub(r"\s+", "", str(block.get("text", ""))))

    if re.search(r"<!doctype|<html[\s>]|<head[\s>]|<body[\s>]", source, re.I):
        add(fatals, "document-shell", "干净正文必须是 section 片段，不能包含文档外壳")
    if re.search(r"<style[\s>]|<script[\s>]|<link[\s>]", source, re.I):
        add(fatals, "active-or-external-code", "正文包含 style/script/link")
    if not source.lstrip().startswith("<section"):
        add(fatals, "root", "正文根节点必须是 section")

    for tag, attrs in parser.tags:
        if tag not in ALLOWED_TAGS:
            add(fatals, "forbidden-tag", f"不允许的标签 <{tag}>")
        allowed_attrs = GLOBAL_ATTRS | TAG_ATTRS.get(tag, set())
        for key, value in attrs:
            key_lower = key.lower()
            if key_lower not in allowed_attrs:
                add(fatals, "forbidden-attribute", f"<{tag}> 使用不允许的属性 {key}")
            if key_lower.startswith("on"):
                add(fatals, "event-handler", f"<{tag}> 包含事件属性 {key}")
            if key_lower == "style":
                if FORBIDDEN_VALUE.search(value or ""):
                    add(fatals, "forbidden-style-value", f"<{tag}> 样式包含严格模式禁用值", value or "")
                for prop, css_value in parse_css(value or ""):
                    if prop not in ALLOWED_CSS:
                        add(fatals, "forbidden-css", f"<{tag}> 使用严格模式之外的 CSS：{prop}", css_value)
                    if prop == "display" and css_value not in {"block", "inline", "inline-block", ""}:
                        add(fatals, "display-mode", f"<{tag}> 使用不允许的 display 值：{css_value}")

    for image in parser.images:
        src = image["src"].strip()
        alt = image["alt"].strip()
        if not src:
            add(fatals, "missing-image-src", "图片 src 为空")
        if not alt:
            add(fatals, "missing-alt", "图片缺少 alt")
        if src.startswith("http://"):
            add(warnings, "insecure-image", "图片使用 HTTP，可能被拦截", src)
        elif src.startswith("https://") and "mmbiz.qpic.cn" not in src:
            add(warnings, "external-image", "外链图片发布前必须转存到微信素材库", src)
        elif src.startswith("file://"):
            add(warnings, "local-image", "file:// 图片只能用于本地预览，发布前必须上传", src)
        elif not src.startswith(("https://", "data:")):
            candidate = (path.parent / src).resolve()
            if not candidate.exists():
                add(fatals, "broken-local-image", "相对图片路径不存在", src)
            else:
                add(warnings, "local-image", "本地图片只能用于预览，发布前必须上传", src)

    full_text = "".join(parser.raw_text)
    if PLACEHOLDER.search(full_text):
        add(warnings, "placeholder", "正文仍有待补或模板占位", PLACEHOLDER.search(full_text).group(0))
    editorial_paragraphs = []
    for paragraph in parser.paragraphs:
        normalized = re.sub(r"\s+", "", paragraph)
        if not CJK.search(paragraph):
            continue
        if any(normalized and normalized in quote for quote in quote_sources):
            continue
        editorial_paragraphs.append(paragraph)
    editorial = editorial_audit(editorial_paragraphs)
    warnings.extend(editorial)
    quote_style_warnings: list[dict[str, str]] = []
    for quote_index, quote in enumerate(quote_sources, 1):
        for item in editorial_audit([quote]):
            quote_style_warnings.append(
                {
                    "code": "verbatim-quote-" + item["code"],
                    "message": f"第 {quote_index} 条来源引语存在风格风险；保留原文，但交付时应说明",
                    "sample": item.get("sample", ""),
                }
            )
    warnings.extend(quote_style_warnings)

    if manuscript_data is not None:
        source_text = json.dumps(manuscript_data, ensure_ascii=False)
        if PLACEHOLDER.search(source_text):
            add(warnings, "manuscript-placeholder", "manuscript 中仍有待补项")
        if len(manuscript_data.get("sections") or []) > 7:
            add(warnings, "many-sections", "章节超过 7 个，检查是否过度拆分")

    emphasis_count = len(re.findall(r"border-bottom\s*:\s*2px", source, re.I))
    body_paragraphs = max(1, len([p for p in parser.paragraphs if len(p) >= 35]))
    if emphasis_count > body_paragraphs:
        add(warnings, "over-emphasis", "强强调数量超过主要正文段数，可能形成模板感")

    compatibility_score = max(0, 100 - len(fatals) * 25 - min(30, len(parser.images) and sum(1 for i in parser.images if i["src"].startswith("http://")) * 2))
    editorial_score = max(0, 100 - min(60, len(editorial) * 4))
    readiness = "fail" if fatals else ("review" if warnings else "pass")
    return {
        "file": str(path),
        "readiness": readiness,
        "scores": {
            "strict_compatibility": compatibility_score,
            "editorial_heuristic": editorial_score,
        },
        "counts": {
            "tags": len(parser.tags),
            "paragraphs": len(parser.paragraphs),
            "images": len(parser.images),
            "emphasis": emphasis_count,
            "fatal": len(fatals),
            "warnings": len(warnings),
            "verbatim_quote_style_warnings": len(quote_style_warnings),
        },
        "fatal": fatals,
        "warnings": warnings,
        "note": "分数只覆盖静态兼容性与非引语正文启发式；来源引语风险单列但不扣分，不能替代事实核验和手机视觉审阅。",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--manuscript", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit(args.html, args.manuscript)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"readiness: {report['readiness']}")
        print(f"scores: {report['scores']}")
        print(f"counts: {report['counts']}")
        for item in report["fatal"]:
            print(f"ERROR {item['code']}: {item['message']} {item.get('sample', '')}")
        for item in report["warnings"]:
            print(f"WARN  {item['code']}: {item['message']} {item.get('sample', '')}")
        print(report["note"])
    return 1 if report["fatal"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

