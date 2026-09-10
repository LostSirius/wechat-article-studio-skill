#!/usr/bin/env python3
"""Render a structured manuscript into strict WeChat HTML and a copy preview.

Visual direction is resolved in two layers:

1. a named preset (``theme``) that supplies a palette, a font stack, and default
   component variants;
2. an optional ``style`` object in the manuscript that overrides any palette token,
   the font, individual component variants, paragraph metrics, image inset, and
   spacing density.

The renderer only shapes the layout. Wording comes from the manuscript and the
visual direction comes from the user's brief; presets are starting points, not
the only permitted looks.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote


PALETTE_KEYS = ("paper", "card", "ink", "text", "muted", "accent", "soft", "line")
SANS = "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"

PRESETS: dict[str, dict[str, Any]] = {
    "academy": {
        "label": "学院纪实",
        "brief": "暖纸底、藏青、哑光黄铜；双线报头、编号色块章节。适合高校新闻、游学、学术交流。",
        "palette": {
            "paper": "#f7f3ec", "card": "#ffffff", "ink": "#1a2740", "text": "#3c3834",
            "muted": "#786f66", "accent": "#c4a06a", "soft": "#efe8dc", "line": "#e4d8c5",
        },
        "font": SANS,
        "variants": {"masthead": "frame", "heading": "block", "caption": "strip", "quote": "card", "callout": "soft"},
        "paragraph": {"indent": True, "size": 15, "line_height": "2", "align": "justify"},
    },
    "editorial": {
        "label": "杂志特稿",
        "brief": "米白、炭黑、一点编辑红；上下细线报头、细线章节。适合人物、访谈、品牌故事。",
        "palette": {
            "paper": "#fbfaf7", "card": "#ffffff", "ink": "#26221f", "text": "#38332f",
            "muted": "#7d746c", "accent": "#9d3f35", "soft": "#f1ebe5", "line": "#ded6ce",
        },
        "font": "Optima, Palatino Linotype, PingFang SC, Microsoft YaHei, sans-serif",
        "variants": {"masthead": "rule", "heading": "rule", "caption": "strip", "quote": "card", "callout": "soft"},
        "paragraph": {"indent": True, "size": 15, "line_height": "2", "align": "justify"},
    },
    "minimal": {
        "label": "极简留白",
        "brief": "纯白、近黑、低饱和灰绿；无框报头、最宽留白。适合图片主导的游记或已定稿文字。",
        "palette": {
            "paper": "#ffffff", "card": "#ffffff", "ink": "#242424", "text": "#393939",
            "muted": "#808080", "accent": "#74867f", "soft": "#f4f4f1", "line": "#e6e6e2",
        },
        "font": SANS,
        "variants": {"masthead": "plain", "heading": "rule", "caption": "strip", "quote": "card", "callout": "soft"},
        "paragraph": {"indent": True, "size": 15, "line_height": "2", "align": "justify"},
    },
    "campus": {
        "label": "清新校园",
        "brief": "薄荷白、松绿、明快草绿；左对齐下划线报头、胶囊编号章节、不缩进段落。适合社团、招新、活动回顾。",
        "palette": {
            "paper": "#f6faf7", "card": "#ffffff", "ink": "#1f4d3a", "text": "#33403a",
            "muted": "#7a8a81", "accent": "#3f9d6b", "soft": "#e8f3ec", "line": "#d5e5db",
        },
        "font": SANS,
        "variants": {"masthead": "underline", "heading": "pill", "caption": "plain", "quote": "line", "callout": "soft"},
        "paragraph": {"indent": False, "size": 15, "line_height": "1.9", "align": "left"},
    },
    "festival": {
        "label": "节庆典礼",
        "brief": "暖米底、正红、金色；整块色带报头、居中章节。适合校庆、节日祝福、颁奖、典礼。",
        "palette": {
            "paper": "#fbf3ec", "card": "#ffffff", "ink": "#9b1c1c", "text": "#3b2f2a",
            "muted": "#8a6f66", "accent": "#c9a24d", "soft": "#f7e6dc", "line": "#ead4c6",
        },
        "font": SANS,
        "variants": {"masthead": "band", "heading": "centered", "caption": "strip", "quote": "card", "callout": "outline"},
        "paragraph": {"indent": True, "size": 15, "line_height": "2", "align": "justify"},
    },
    "tech": {
        "label": "科技简报",
        "brief": "冷灰白、深海军蓝、电光蓝；左对齐报头、竖条章节、左对齐不缩进段落。适合科研成果、产品、数据解读。",
        "palette": {
            "paper": "#f4f6fa", "card": "#ffffff", "ink": "#10233f", "text": "#2f3a4a",
            "muted": "#6f7c8f", "accent": "#2f6fed", "soft": "#e7edf8", "line": "#d6deea",
        },
        "font": "-apple-system, PingFang SC, Helvetica Neue, Microsoft YaHei, sans-serif",
        "variants": {"masthead": "underline", "heading": "bar", "caption": "plain", "quote": "line", "callout": "outline"},
        "paragraph": {"indent": False, "size": 15, "line_height": "1.9", "align": "left"},
    },
    "ink": {
        "label": "水墨人文",
        "brief": "宣纸白、墨黑、朱砂；细线报头、居中章节、居中图注、无框引语。适合文化、历史、读书、人文随笔。",
        "palette": {
            "paper": "#f8f6f1", "card": "#fffdf9", "ink": "#1d1d1b", "text": "#35322e",
            "muted": "#7c766d", "accent": "#a8402f", "soft": "#efebe3", "line": "#dcd6cb",
        },
        "font": "Songti SC, STSong, Noto Serif CJK SC, SimSun, serif",
        "variants": {"masthead": "rule", "heading": "centered", "caption": "centered", "quote": "plain", "callout": "soft"},
        "paragraph": {"indent": True, "size": 15, "line_height": "2.1", "align": "justify"},
    },
    "magazine": {
        "label": "暖调生活",
        "brief": "奶油白、深可可、焦橙；左对齐报头、竖条章节、白卡引语。适合生活方式、美食、周末、社区故事。",
        "palette": {
            "paper": "#fffaf4", "card": "#ffffff", "ink": "#2b2320", "text": "#3d3431",
            "muted": "#8b7d75", "accent": "#e07b39", "soft": "#fdeedf", "line": "#efdccb",
        },
        "font": SANS,
        "variants": {"masthead": "underline", "heading": "bar", "caption": "plain", "quote": "card", "callout": "soft"},
        "paragraph": {"indent": False, "size": 15, "line_height": "1.95", "align": "left"},
    },
}

# Backwards-compatible alias used by older tests and scripts.
THEMES = {name: {**preset["palette"], "font": preset["font"]} for name, preset in PRESETS.items()}

VARIANT_OPTIONS: dict[str, tuple[str, ...]] = {
    "masthead": ("frame", "rule", "plain", "band", "underline"),
    "heading": ("block", "rule", "pill", "bar", "centered"),
    "caption": ("strip", "plain", "centered"),
    "quote": ("card", "line", "plain"),
    "callout": ("soft", "outline"),
}
DENSITY = {"compact": 0.8, "normal": 1.0, "airy": 1.3}
STYLE_KEYS = {"palette", "font", "density", "image_inset", "paragraph", *VARIANT_OPTIONS}
PARAGRAPH_KEYS = {"indent", "size", "line_height", "align"}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

ALLOWED_BLOCKS = {"p", "date", "image", "quote", "callout", "table", "rule"}
EM_RE = re.compile(r"\[\[em:(.+?)\]\]")
SENTENCE_RE = re.compile(r".+?[。！？!?](?:[”’])?|.+$", re.S)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def style(**items: str) -> str:
    return ";".join(f"{k.replace('_', '-')}:{v}" for k, v in items.items() if v) + ";"


def quote_chunks(value: Any, target: int = 150) -> list[str]:
    """Split a long quote at sentence boundaries without changing its wording."""
    text = str(value).strip()
    if len(text) <= target:
        return [text] if text else []
    sentences = [match.group(0) for match in SENTENCE_RE.finditer(text)]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) > target:
            chunks.append(current)
            current = sentence
        else:
            current += sentence
    if current:
        chunks.append(current)
    return chunks


def resolve_style(manuscript: dict[str, Any]) -> dict[str, Any]:
    """Merge the named preset with the manuscript ``style`` overrides and validate them."""
    theme = manuscript.get("theme", "academy")
    if theme not in PRESETS:
        raise ValueError(f"Unknown theme: {theme}. Available: {', '.join(PRESETS)}")
    preset = PRESETS[theme]
    override = manuscript.get("style") or {}
    if not isinstance(override, dict):
        raise ValueError("Manuscript style must be an object")
    unknown = set(override) - STYLE_KEYS
    if unknown:
        raise ValueError(f"Unknown style keys: {', '.join(sorted(unknown))}")

    palette = dict(preset["palette"])
    palette_override = override.get("palette") or {}
    if not isinstance(palette_override, dict):
        raise ValueError("style.palette must be an object")
    for key, value in palette_override.items():
        if key not in PALETTE_KEYS:
            raise ValueError(f"Unknown palette token: {key}. Tokens: {', '.join(PALETTE_KEYS)}")
        if not isinstance(value, str) or not HEX_RE.match(value):
            raise ValueError(f"Palette token {key} must be a six-digit hex color")
        palette[key] = value.lower()

    variants = dict(preset["variants"])
    for key, options in VARIANT_OPTIONS.items():
        if key in override:
            value = override[key]
            if value not in options:
                raise ValueError(f"style.{key} must be one of: {', '.join(options)}")
            variants[key] = value

    paragraph = dict(preset["paragraph"])
    paragraph_override = override.get("paragraph") or {}
    if not isinstance(paragraph_override, dict):
        raise ValueError("style.paragraph must be an object")
    unknown = set(paragraph_override) - PARAGRAPH_KEYS
    if unknown:
        raise ValueError(f"Unknown style.paragraph keys: {', '.join(sorted(unknown))}")
    paragraph.update(paragraph_override)
    paragraph["indent"] = bool(paragraph["indent"])
    size = int(paragraph["size"])
    if not 13 <= size <= 18:
        raise ValueError("style.paragraph.size must be between 13 and 18")
    paragraph["size"] = size
    line_height = float(paragraph["line_height"])
    if not 1.5 <= line_height <= 2.4:
        raise ValueError("style.paragraph.line_height must be between 1.5 and 2.4")
    paragraph["line_height"] = f"{line_height:g}"
    if paragraph["align"] not in ("justify", "left"):
        raise ValueError("style.paragraph.align must be justify or left")

    density = override.get("density", "normal")
    if density not in DENSITY:
        raise ValueError(f"style.density must be one of: {', '.join(DENSITY)}")
    image_inset = int(override.get("image_inset", 16))
    if not 0 <= image_inset <= 32:
        raise ValueError("style.image_inset must be between 0 and 32 pixels")
    font = str(override.get("font") or preset["font"])
    if re.search(r"[<>\"';]", font):
        raise ValueError("style.font contains characters that are not allowed in a font stack")

    return {
        "theme": theme,
        "label": preset["label"],
        "palette": palette,
        "font": font,
        "variants": variants,
        "paragraph": paragraph,
        "density": density,
        "image_inset": image_inset,
    }


def asset_name(src: str) -> str:
    cleaned = unquote(src.split("?")[0].split("#")[0])
    return cleaned.replace("\\", "/").rstrip("/").split("/")[-1] or cleaned


class Renderer:
    def __init__(self, manuscript: dict[str, Any]):
        self.m = manuscript
        self.s = resolve_style(manuscript)
        self.name = self.s["theme"]
        self.t = self.s["palette"]
        self.v = self.s["variants"]
        self.p = self.s["paragraph"]
        self.scale = DENSITY[self.s["density"]]
        self.inset = self.s["image_inset"]
        self.placeholder = False
        self.images: list[dict[str, str]] = []
        self.block_counts: dict[str, int] = {}

    # ---------------------------------------------------------------- helpers
    def px(self, value: float) -> str:
        return f"{max(0, round(value * self.scale))}px"

    def box(self, top: float, right: float, bottom: float, left: float) -> str:
        return f"{self.px(top)} {right}px {self.px(bottom)} {left}px"

    def span(self, text: Any, css: str = "") -> str:
        return f'<span style="{css}">{esc(text)}</span>'

    def rich(self, text: Any, base_css: str = "") -> str:
        raw = str(text)
        out: list[str] = []
        cursor = 0
        for match in EM_RE.finditer(raw):
            out.append(self.span(raw[cursor : match.start()], base_css))
            out.append(
                self.span(
                    match.group(1),
                    style(
                        color=self.t["ink"],
                        font_weight="bold",
                        border_bottom=f"2px solid {self.t['accent']}",
                    ),
                )
            )
            cursor = match.end()
        out.append(self.span(raw[cursor:], base_css))
        return "".join(part for part in out if part)

    def accent_rule(self, margin: str, width: int = 36, height: int = 1) -> str:
        return (
            f'<section style="{style(margin=margin, width=f"{width}px", height=f"{height}px", background_color=self.t["accent"], font_size="0", line_height="0")}">&nbsp;</section>'
        )

    def paragraph(self, text: Any, margin: str = "13px 0 0 0") -> str:
        p_style = style(
            margin=margin,
            padding="0",
            font_size=f"{self.p['size']}px",
            line_height=self.p["line_height"],
            text_align=self.p["align"],
            color=self.t["text"],
            text_indent="2em" if self.p["indent"] else "",
        )
        return f'<p style="{p_style}">{self.rich(text, style(color=self.t["text"]))}</p>'

    # --------------------------------------------------------------- masthead
    def masthead(self) -> str:
        title = self.m.get("title", "")
        kicker = self.m.get("kicker")
        subtitle = self.m.get("subtitle")
        date = self.m.get("date")
        if not title:
            raise ValueError("Manuscript title is required")
        variant = self.v["masthead"]
        inverted = variant == "band"
        ink = "#ffffff" if inverted else self.t["ink"]
        muted = self.t["line"] if inverted else self.t["muted"]
        accent = self.t["accent"]
        align = "left" if variant == "underline" else "center"

        lines: list[str] = []
        if kicker:
            lines.append(
                f'<p style="{style(margin="0", padding="0", text_align=align, font_size="12px", letter_spacing="4px", color=accent if variant == "underline" else ink)}">'
                f'{self.span(kicker, style(color=accent if variant == "underline" else ink))}</p>'
            )
        lines.append(
            f'<p style="{style(margin="14px 0 0 0" if kicker else "0", padding="0", text_align=align, font_size="24px", font_weight="bold", line_height="1.5", letter_spacing="1px", color=ink)}">'
            f'{self.span(title, style(color=ink, font_weight="bold"))}</p>'
        )
        if subtitle:
            subtitle_text = str(subtitle) if variant == "underline" else "·" + str(subtitle) + "·"
            lines.append(
                f'<p style="{style(margin="12px 0 0 0", padding="0", text_align=align, font_size="13px", line_height="1.9", color=muted)}">'
                f'{self.span(subtitle_text, style(color=muted))}</p>'
            )
        if date:
            lines.append(
                f'<p style="{style(margin="12px 0 0 0", padding="0", text_align=align, font_size="12px", color=muted)}">'
                f'{self.span(date, style(color=muted))}</p>'
            )
        inner = "".join(lines)

        if variant == "frame":
            return (
                f'<section style="{style(margin=self.box(22, 16, 18, 16), padding="3px", border="1px solid " + self.t["ink"])}">'
                f'<section style="{style(padding="26px 16px 22px 16px", border="1px solid " + accent)}">{inner}</section>'
                "</section>"
            )
        if variant == "rule":
            return (
                f'<section style="{style(margin=self.box(24, 20, 20, 20), padding="24px 0 20px 0", border_top="2px solid " + self.t["ink"], border_bottom="1px solid " + self.t["line"])}">'
                f"{inner}</section>"
            )
        if variant == "band":
            return (
                f'<section style="{style(margin="0 0 " + self.px(18) + " 0", padding="34px 22px 30px 22px", background_color=self.t["ink"], border_bottom="4px solid " + accent)}">'
                f"{inner}</section>"
            )
        if variant == "underline":
            return (
                f'<section style="{style(margin=self.box(28, 20, 18, 20), padding="0")}">{inner}'
                f"{self.accent_rule('18px 0 0 0', width=40, height=3)}</section>"
            )
        return f'<section style="{style(margin=self.box(32, 22, 24, 22), padding="0")}">{inner}</section>'

    # ------------------------------------------------------------------ image
    def caption(self, caption: str) -> str:
        variant = self.v["caption"]
        marker = self.span("▍", style(color=self.t["accent"]))
        if variant == "strip":
            cap_style = style(padding="9px 16px 11px 16px", background_color=self.t["soft"])
            p_style = style(margin="0", padding="0", font_size="12px", line_height="1.7", color=self.t["muted"])
            return (
                f'<section style="{cap_style}"><p style="{p_style}">{marker}'
                f'{self.span(" " + caption, style(color=self.t["muted"]))}</p></section>'
            )
        if variant == "centered":
            p_style = style(margin="0", padding="0", text_align="center", font_size="12px", line_height="1.7", color=self.t["muted"])
            return (
                f'<section style="{style(padding="10px 16px 4px 16px")}"><p style="{p_style}">'
                f'{self.span(caption, style(color=self.t["muted"]))}</p></section>'
            )
        p_style = style(margin="0", padding="0", font_size="12px", line_height="1.7", color=self.t["muted"])
        return (
            f'<section style="{style(padding="9px 16px 4px 16px")}"><p style="{p_style}">{marker}'
            f'{self.span(" " + caption, style(color=self.t["muted"]))}</p></section>'
        )

    def image(self, data: dict[str, Any], hero: bool = False) -> str:
        src = str(data.get("src", "")).strip()
        alt = str(data.get("alt", "")).strip()
        caption = str(data.get("caption", "")).strip()
        full = bool(data.get("full", False))
        self.images.append({"src": src, "alt": alt, "caption": caption})
        index = len(self.images)
        margin = "0" if full or hero else f"{self.px(14)} {self.inset}px 0 {self.inset}px"
        if self.placeholder:
            body = self.image_placeholder(index, src, alt, caption)
        else:
            img_style = style(width="100%", max_width="100%", height="auto", display="block", border="0")
            body = f'<img src="{esc(src)}" alt="{esc(alt)}" style="{img_style}" />'
        result = f'<section style="{style(margin=margin, padding="0")}">{body}'
        if caption:
            result += self.caption(caption)
        return result + "</section>"

    def image_placeholder(self, index: int, src: str, alt: str, caption: str) -> str:
        """A visible slot that survives copy/paste so the editor knows where to insert the image."""
        head = style(margin="0", padding="0", text_align="center", font_size="13px", line_height="1.8", font_weight="bold", color=self.t["ink"])
        meta = style(margin="4px 0 0 0", padding="0", text_align="center", font_size="12px", line_height="1.7", color=self.t["muted"])
        lines = [
            f'<p style="{head}">{self.span(f"图 {index} · 此处插入图片", style(color=self.t["ink"], font_weight="bold"))}</p>'
        ]
        description = alt or caption
        if description:
            lines.append(f'<p style="{meta}">{self.span(description, style(color=self.t["muted"]))}</p>')
        name = asset_name(src)
        if name:
            lines.append(f'<p style="{meta}">{self.span("文件：" + name, style(color=self.t["muted"]))}</p>')
        return (
            f'<section style="{style(margin="0", padding="22px 16px 22px 16px", border="1px dashed " + self.t["accent"], background_color=self.t["soft"])}">'
            + "".join(lines)
            + "</section>"
        )

    # ------------------------------------------------------------------ facts
    def facts(self) -> str:
        facts = self.m.get("facts") or []
        if not facts:
            return ""
        title = str(self.m.get("facts_title") or "项目速览")
        rows = []
        for pair in facts:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ValueError("Each facts item must be [label, value]")
            rows.append(
                "<tr>"
                f'<td style="{style(width="22%", padding="10px 8px 10px 0", border_top="1px solid " + self.t["line"], font_size="13px", color=self.t["accent"], vertical_align="top")}">'
                f'{self.span(pair[0], style(color=self.t["accent"]))}</td>'
                f'<td style="{style(padding="10px 0 10px 8px", border_top="1px solid " + self.t["line"], font_size="13px", line_height="1.75", color=self.t["text"], vertical_align="top")}">'
                f'{self.span(pair[1], style(color=self.t["text"]))}</td>'
                "</tr>"
            )
        return (
            f'<section style="{style(margin=self.box(18, 16, 8, 16), padding="2px", border="1px solid " + self.t["accent"])}">'
            f'<section style="{style(padding="16px 14px 8px 14px", border="1px solid " + self.t["line"], background_color=self.t["card"])}">'
            f'<p style="{style(margin="0 0 8px 0", padding="0", text_align="center", font_size="13px", color=self.t["ink"], letter_spacing="3px")}">'
            f'{self.span(title, style(color=self.t["ink"]))}</p>'
            f'<table cellpadding="0" cellspacing="0" style="{style(width="100%", border_collapse="collapse")}"><tbody>'
            + "".join(rows)
            + "</tbody></table></section></section>"
        )

    # --------------------------------------------------------------- headings
    def section_heading(self, section: dict[str, Any], index: int) -> str:
        number = section.get("number") or str(index).zfill(2)
        title = section.get("title", "")
        note = section.get("note")
        if not title:
            raise ValueError(f"Section {index} has no title")
        variant = self.v["heading"]
        centered = variant == "centered"
        title_p = (
            f'<p style="{style(margin="0", padding="0", text_align="center" if centered else "", font_size="18px", font_weight="bold", line_height="1.5", color=self.t["ink"])}">'
            f'{self.span(title, style(color=self.t["ink"], font_weight="bold"))}</p>'
        )
        note_p = ""
        if note:
            note_p = (
                f'<p style="{style(margin="4px 0 0 0", padding="0", text_align="center" if centered else "", font_size="12px", color=self.t["muted"])}">'
                f'{self.span(note, style(color=self.t["muted"]))}</p>'
            )
        number_text = str(number)

        if variant == "block":
            return (
                f'<section style="{style(margin=self.box(28, 16, 8, 16))}"><table cellpadding="0" cellspacing="0" '
                f'style="{style(width="100%", border_collapse="collapse")}"><tbody><tr>'
                f'<td style="{style(width="52px", background_color=self.t["ink"], text_align="center", vertical_align="middle", padding="14px 0 14px 0")}">'
                f'<p style="{style(margin="0", padding="0", font_size="18px", font_weight="bold", color="#ffffff", line_height="1.2")}">'
                f'{self.span(number_text, style(color="#ffffff", font_weight="bold"))}</p></td>'
                f'<td style="{style(padding="10px 14px 10px 14px", background_color=self.t["card"], border_top="1px solid " + self.t["ink"], border_right="1px solid " + self.t["ink"], border_bottom="1px solid " + self.t["ink"], vertical_align="middle")}">'
                f"{title_p}{note_p}</td></tr></tbody></table></section>"
            )
        if variant == "pill":
            pill = (
                f'<span style="{style(display="inline-block", background_color=self.t["accent"], color="#ffffff", font_size="12px", font_weight="bold", letter_spacing="1px", padding="3px 10px 3px 10px", line_height="1.5")}">'
                f"{esc(number_text)}</span>"
            )
            return (
                f'<section style="{style(margin=self.box(30, 20, 8, 20), padding="0")}">'
                f'<p style="{style(margin="0 0 8px 0", padding="0")}">{pill}</p>{title_p}{note_p}</section>'
            )
        if variant == "bar":
            return (
                f'<section style="{style(margin=self.box(30, 20, 8, 20), padding="2px 0 2px 14px", border_left="4px solid " + self.t["accent"])}">'
                f'<p style="{style(margin="0 0 4px 0", padding="0", font_size="12px", letter_spacing="2px", color=self.t["accent"])}">'
                f'{self.span(number_text, style(color=self.t["accent"]))}</p>{title_p}{note_p}</section>'
            )
        if variant == "centered":
            return (
                f'<section style="{style(margin=self.box(32, 20, 8, 20), padding="0")}">'
                f'<p style="{style(margin="0 0 6px 0", padding="0", text_align="center", font_size="12px", letter_spacing="3px", color=self.t["accent"])}">'
                f'{self.span(number_text, style(color=self.t["accent"]))}</p>{title_p}{note_p}'
                f"{self.accent_rule('12px auto 0 auto', width=28, height=2)}</section>"
            )
        left = f"{number_text.zfill(2)}　" if number_text else ""
        return (
            f'<section style="{style(margin=self.box(30, 20, 8, 20), padding="0 0 10px 0", border_bottom="1px solid " + self.t["accent"])}">'
            f'<p style="{style(margin="0", padding="0", font_size="12px", color=self.t["accent"], letter_spacing="2px")}">'
            f'{self.span(left, style(color=self.t["accent"]))}</p>{title_p}{note_p}</section>'
        )

    # ----------------------------------------------------------------- blocks
    def quote(self, block: dict[str, Any]) -> str:
        variant = self.v["quote"]
        author = block.get("author")
        centered = variant == "plain"
        body = (
            f'<p style="{style(margin="0", padding="0", text_align="center" if centered else "", font_size="28px", line_height="0.9", color=self.t["accent"])}">'
            f'{self.span("“", style(color=self.t["accent"]))}</p>'
        )
        for index, chunk in enumerate(quote_chunks(block.get("text", ""))):
            body += (
                f'<p style="{style(margin="7px 0 0 0" if index == 0 else "10px 0 0 0", padding="0", font_size="14px", line_height="1.95", text_align="center" if centered else "justify", color=self.t["text"], text_indent="" if centered or not self.p["indent"] else "2em")}">'
                f'{self.rich(chunk, style(color=self.t["text"]))}</p>'
            )
        if author:
            body += (
                f'<p style="{style(margin="14px 0 0 0", padding="0", text_align="center" if centered else "right", font_size="13px", color=self.t["ink"])}">'
                f'{self.span("—— " + str(author), style(color=self.t["ink"]))}</p>'
            )
        if variant == "line":
            return f'<section style="{style(margin=self.box(14, 20, 0, 20), padding="6px 0 6px 16px", border_left="3px solid " + self.t["accent"])}">{body}</section>'
        if variant == "plain":
            return f'<section style="{style(margin=self.box(18, 28, 4, 28), padding="0")}">{body}</section>'
        return f'<section style="{style(margin=self.box(14, 16, 0, 16), padding="18px 16px 16px 16px", background_color=self.t["card"], border="1px solid " + self.t["line"])}">{body}</section>'

    def callout(self, block: dict[str, Any]) -> str:
        label = block.get("label")
        label_html = ""
        if label:
            label_html = (
                f'<p style="{style(margin="0 0 8px 0", padding="0", font_size="12px", letter_spacing="2px", color=self.t["accent"])}">'
                f'{self.span(label, style(color=self.t["accent"]))}</p>'
            )
        text_p = (
            f'<p style="{style(margin="0", padding="0", font_size="14px", line_height="1.9", color=self.t["text"])}">'
            f'{self.rich(block.get("text", ""), style(color=self.t["text"]))}</p>'
        )
        if self.v["callout"] == "outline":
            return (
                f'<section style="{style(margin=self.box(16, 20, 8, 20), padding="14px 16px 14px 16px", border="1px solid " + self.t["accent"], background_color=self.t["card"])}">'
                f"{label_html}{text_p}</section>"
            )
        return (
            f'<section style="{style(margin=self.box(16, 20, 8, 20), padding="14px 14px 14px 14px", background_color=self.t["soft"], border_left="3px solid " + self.t["accent"])}">'
            f"{label_html}{text_p}</section>"
        )

    def render_block(self, block: dict[str, Any]) -> str:
        kind = block.get("type")
        if kind not in ALLOWED_BLOCKS:
            raise ValueError(f"Unknown block type: {kind}")
        self.block_counts[kind] = self.block_counts.get(kind, 0) + 1
        if kind == "p":
            return f'<section style="{style(padding=self.box(6, 20, 4, 20))}">{self.paragraph(block.get("text", ""), "8px 0 0 0")}</section>'
        if kind == "date":
            p = (
                f'<p style="{style(margin="0", padding="0")}">'
                f'<span style="{style(display="inline-block", background_color=self.t["ink"], color="#ffffff", font_size="12px", padding="3px 9px 3px 9px")}">'
                f'{esc(block.get("text", ""))}</span></p>'
            )
            return f'<section style="{style(padding=self.box(12, 20, 4, 20))}">{p}</section>'
        if kind == "image":
            return self.image(block)
        if kind == "quote":
            return self.quote(block)
        if kind == "callout":
            return self.callout(block)
        if kind == "table":
            rows = block.get("rows") or []
            if not rows:
                return ""
            width = max(len(row) for row in rows)
            if width > 4:
                raise ValueError("Tables may contain at most four columns")
            trs = []
            for ridx, row in enumerate(rows):
                cells = []
                for cell in row:
                    bg = self.t["ink"] if ridx == 0 else self.t["card"]
                    color = "#ffffff" if ridx == 0 else self.t["text"]
                    cells.append(
                        f'<td style="{style(padding="9px 8px 9px 8px", border="1px solid " + self.t["line"], background_color=bg, color=color, font_size="13px", line_height="1.6", vertical_align="top")}">'
                        f'{self.span(cell, style(color=color, font_weight="bold" if ridx == 0 else ""))}</td>'
                    )
                trs.append("<tr>" + "".join(cells) + "</tr>")
            return (
                f'<section style="{style(margin=self.box(14, 20, 8, 20))}"><table cellpadding="0" cellspacing="0" '
                f'style="{style(width="100%", border_collapse="collapse")}"><tbody>{"".join(trs)}</tbody></table></section>'
            )
        return self.accent_rule(f"{self.px(24)} auto {self.px(20)} auto")

    def credits(self) -> str:
        credits = self.m.get("credits") or []
        if not credits:
            return ""
        lines = []
        for pair in credits:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ValueError("Each credit must be [label, value]")
            lines.append(f"{pair[0]}丨{pair[1]}")
        body = "<br />".join(self.span(line, style(color=self.t["muted"])) for line in lines)
        return (
            f'<section style="{style(padding=self.box(22, 20, 14, 20))}"><p style="{style(margin="0", padding="0", text_align="center", font_size="12px", line_height="2.15", color=self.t["muted"])}">'
            f"{body}</p></section>"
        )

    # ----------------------------------------------------------------- render
    def compose(self, placeholder: bool = False) -> str:
        self.placeholder = placeholder
        self.images = []
        self.block_counts = {}
        sections = self.m.get("sections")
        if not isinstance(sections, list) or not sections:
            raise ValueError("Manuscript sections must be a nonempty list")
        root_style = style(
            width="100%",
            max_width="677px",
            margin="0 auto",
            padding="0",
            background_color=self.t["paper"],
            font_family=self.s["font"],
        )
        parts = [f'<section style="{root_style}">', self.masthead()]
        hero = self.m.get("hero")
        if hero:
            parts.append(self.image(hero, hero=True))
        lead = self.m.get("lead") or []
        if lead:
            parts.append(f'<section style="{style(padding=self.box(16, 20, 6, 20))}">')
            for idx, paragraph in enumerate(lead):
                parts.append(self.paragraph(paragraph, "0" if idx == 0 else "14px 0 0 0"))
            parts.append("</section>")
        parts.append(self.facts())
        for index, section in enumerate(sections, 1):
            parts.append(self.section_heading(section, index))
            blocks = section.get("blocks") or []
            for block in blocks:
                if not isinstance(block, dict):
                    raise ValueError(f"Section {index} contains a non-object block")
                parts.append(self.render_block(block))
        closing = self.m.get("closing") or []
        if closing:
            parts.append(self.accent_rule(f"{self.px(28)} auto 0 auto"))
            parts.append(f'<section style="{style(padding=self.box(18, 20, 8, 20))}">')
            for idx, paragraph in enumerate(closing):
                parts.append(self.paragraph(paragraph, "0" if idx == 0 else "14px 0 0 0"))
            parts.append("</section>")
        parts.append(self.credits())
        footer = self.m.get("footer_image")
        if footer:
            parts.append(self.image({**footer, "full": True}))
        parts.append("</section>")
        return "\n".join(part for part in parts if part)

    def render(self) -> tuple[str, dict[str, Any]]:
        fragment = self.compose(placeholder=False)
        report = {
            "theme": self.name,
            "style": self.s,
            "title": self.m.get("title"),
            "sections": len(self.m.get("sections") or []),
            "blocks": self.block_counts,
            "images": self.images,
            "external_images_need_wechat_transfer": [
                item["src"]
                for item in self.images
                if item["src"].startswith(("http://", "https://"))
                and "mmbiz.qpic.cn" not in item["src"]
            ],
            "assets_requiring_wechat_upload": [
                item["src"]
                for item in self.images
                if item["src"]
                and not item["src"].startswith("data:")
                and "mmbiz.qpic.cn" not in item["src"]
            ],
        }
        return fragment, report

    def render_without_images(self) -> str:
        """Same layout, but every image becomes a numbered insertion slot."""
        return self.compose(placeholder=True)


def load_cdn_map(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("CDN map must be a JSON object of source-to-HTTPS URL pairs")
    return {
        str(key): str(value)
        for key, value in data.items()
        if str(value).startswith("https://")
    }


def import_document(fragment: str, title: str) -> str:
    """A complete HTML document for editors that import files rather than clipboard HTML."""
    return (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\" />\n"
        f"<title>{esc(title)}</title>\n</head>\n<body>\n{fragment}\n</body>\n</html>\n"
    )


def js_json(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>__TITLE__ · 公众号预览</title>
<style>
body{margin:0;background:#e9e6e1;font-family:Arial,sans-serif}
.bar{position:sticky;top:0;z-index:9;padding:10px 14px;text-align:center;background:#1f2937;color:#fff}
.bar button{border:0;border-radius:6px;padding:9px 16px;margin:2px 3px;background:#fff;color:#111;cursor:pointer}
.bar button.secondary{background:#d1d5db}
.bar button:disabled{cursor:not-allowed;opacity:.45}
#article-root{max-width:677px;margin:18px auto;background:#fff}
.hint{display:block;font-size:12px;line-height:1.6;margin-top:6px}
.notice{max-width:649px;margin:12px auto 0;padding:10px 14px;border-radius:6px;font-size:13px;line-height:1.65;box-sizing:border-box}
.notice-danger{color:#7f1d1d;background:#fef2f2;border:1px solid #fecaca}
.notice-warn{color:#78350f;background:#fffbeb;border:1px solid #fde68a}
.notice-ok{color:#14532d;background:#f0fdf4;border:1px solid #bbf7d0}
.routes{max-width:649px;margin:10px auto 0;padding:10px 14px;border-radius:6px;font-size:12px;line-height:1.7;color:#374151;background:#f3f4f6;box-sizing:border-box}
.routes b{color:#111827}
</style>
</head>
<body>
<div class="bar">
<button id="copy-button" onclick="copyArticle()">复制排版（含图片链接）</button>
<button id="copy-noimage-button" class="secondary" onclick="copyWithoutImages()">复制无图版本</button>
<button id="download-button" class="secondary" onclick="downloadHtml(false)">下载 HTML</button>
<button id="download-noimage-button" class="secondary" onclick="downloadHtml(true)">下载无图 HTML</button>
<span class="hint" id="status">正在检查图片来源…</span>
</div>
<div class="notice notice-warn" id="asset-notice">浏览器预览能显示图片，不代表微信编辑器能够接收图片。</div>
<div class="routes"><b>三条交付路径：</b>① 图片已有 HTTPS 链接时用「复制排版（含图片链接）」，粘贴后在微信里转存图片；② 图片只在本机时用「复制无图版本」，每张图会变成编号占位框，粘贴后在编辑器内按编号从素材库插入；③ 「下载 HTML」得到的文件可粘贴进 135编辑器顶部【HTML】代码模式，或用其「导入文章」功能；秀米没有整篇 HTML 导入入口，建议先在公众号后台保存草稿，再用秀米「导入公众号图文」。</div>
<div id="article-root">__FRAGMENT__</div>
<script>
const CDN = __CDN__;
const NOIMAGE_HTML = __NOIMAGE__;
const TITLE = __TITLE_JSON__;
const ROOT = document.getElementById('article-root');
const COPY_BUTTON = document.getElementById('copy-button');
const STATUS = document.getElementById('status');
const NOTICE = document.getElementById('asset-notice');
const WECHAT_CDN = /^https:\\/\\/mmbiz\\.qpic\\.cn\\//i;

function resolveCdn(src){
 if(!src) return '';
 if(CDN[src]) return CDN[src];
 let decoded=src;
 try{decoded=decodeURIComponent(src);}catch(e){}
 if(CDN[decoded]) return CDN[decoded];
 const name=decoded.split('/').pop()||'';
 return CDN[name]||'';
}

function classifyAssets(root){
 const result={local:[],external:[],ready:[],mapped:[]};
 root.querySelectorAll('img').forEach((img)=>{
  const raw=img.getAttribute('src')||'';
  const mapped=resolveCdn(raw)||resolveCdn(img.src);
  const src=mapped||raw;
  const item={src:src,alt:img.getAttribute('alt')||'未命名图片'};
  if(mapped) result.mapped.push(item);
  if(WECHAT_CDN.test(src)) result.ready.push(item);
  else if(/^https?:\\/\\//i.test(src)) result.external.push(item);
  else result.local.push(item);
 });
 return result;
}

function showAssetNotice(){
 const assets=classifyAssets(ROOT);
 NOTICE.className='notice ';
 if(assets.local.length){
  COPY_BUTTON.disabled=true;
  NOTICE.className+='notice-danger';
  NOTICE.textContent=`检测到 ${assets.local.length} 张本地、相对或内嵌图片。复制 HTML 不会复制图片文件；请改用「复制无图版本」后在编辑器内插入素材库图片，或先上传图片并提供 cdn_map.json。`;
  STATUS.textContent='含图复制已禁用；无图版本与 HTML 下载仍可用';
 }else if(assets.external.length){
  COPY_BUTTON.disabled=false;
  NOTICE.className+='notice-warn';
  NOTICE.textContent=`检测到 ${assets.external.length} 张非微信外链图片。可以复制排版，但粘贴后必须在微信编辑器中转存/重传，并确认最终地址来自 mmbiz.qpic.cn。`;
  STATUS.textContent='可复制排版；图片仍需转存到微信素材库';
 }else if(assets.ready.length){
  COPY_BUTTON.disabled=false;
  NOTICE.className+='notice-ok';
  NOTICE.textContent=`检测到 ${assets.ready.length} 张微信 CDN 图片。复制后仍需进行手机预览，确认图片和 GIF 均正常。`;
  STATUS.textContent='图片来源已就绪，可复制排版';
 }else{
  COPY_BUTTON.disabled=false;
  NOTICE.className+='notice-ok';
  NOTICE.textContent='正文不含图片，可以直接复制排版。';
  STATUS.textContent='可复制排版';
 }
}

function mappedClone(){
 const clone=ROOT.cloneNode(true);
 clone.querySelectorAll('img').forEach((img)=>{
  const mapped=resolveCdn(img.getAttribute('src')||'')||resolveCdn(img.src);
  if(mapped) img.setAttribute('src',mapped);
 });
 return clone;
}

async function writeClipboard(html,text,successMessage){
 try{
  await navigator.clipboard.write([new ClipboardItem({
   'text/html':new Blob([html],{type:'text/html'}),
   'text/plain':new Blob([text],{type:'text/plain'})
  })]);
  STATUS.textContent=successMessage;
 }catch(e){
  const holder=document.createElement('div');
  holder.innerHTML=html;
  holder.style.position='fixed';
  holder.style.left='-9999px';
  document.body.appendChild(holder);
  const range=document.createRange();range.selectNodeContents(holder);
  const sel=window.getSelection();sel.removeAllRanges();sel.addRange(range);
  document.execCommand('copy');sel.removeAllRanges();
  holder.remove();
  STATUS.textContent=successMessage+'（兼容模式）';
 }
}

async function copyArticle(){
 const clone=mappedClone();
 const assets=classifyAssets(clone);
 if(assets.local.length){
  STATUS.textContent='复制已阻止：仍有本地图片无法随 HTML 粘贴，请改用无图版本';
  return;
 }
 const message=assets.external.length
  ?`已复制排版；粘贴后必须转存/重传 ${assets.external.length} 张图片`
  :'已复制排版；请在微信中完成手机预览';
 await writeClipboard(clone.innerHTML,ROOT.innerText,message);
}

async function copyWithoutImages(){
 const holder=document.createElement('div');
 holder.innerHTML=NOIMAGE_HTML;
 const text=holder.textContent||ROOT.innerText;
 await writeClipboard(NOIMAGE_HTML,text,'已复制无图版本；粘贴后按「图 N」占位框依次从素材库插入图片，再删除占位框');
}

function downloadHtml(withoutImages){
 const body=withoutImages?NOIMAGE_HTML:mappedClone().innerHTML;
 const doc='<!DOCTYPE html>\\n<html lang="zh-CN">\\n<head>\\n<meta charset="utf-8" />\\n<title>'+TITLE.replace(/[&<>]/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))+'</title>\\n</head>\\n<body>\\n'+body+'\\n</body>\\n</html>\\n';
 const blob=new Blob([doc],{type:'text/html;charset=utf-8'});
 const link=document.createElement('a');
 link.href=URL.createObjectURL(blob);
 link.download=withoutImages?'article.noimage.html':'article.import.html';
 document.body.appendChild(link);
 link.click();
 link.remove();
 setTimeout(()=>URL.revokeObjectURL(link.href),1500);
 STATUS.textContent=withoutImages
  ?'已下载无图 HTML；可导入编辑器后再插入素材库图片'
  :'已下载 HTML；导入编辑器后仍需把图片换成微信素材库地址';
}
window.addEventListener('load',showAssetNotice);
</script>
</body>
</html>
"""


def preview_document(
    fragment: str,
    title: str,
    cdn_map: dict[str, str] | None = None,
    noimage_fragment: str | None = None,
) -> str:
    page = PREVIEW_TEMPLATE
    page = page.replace("__TITLE_JSON__", js_json(title))
    page = page.replace("__TITLE__", esc(title))
    page = page.replace("__CDN__", js_json(cdn_map or {}))
    page = page.replace("__NOIMAGE__", js_json(noimage_fragment or ""))
    return page.replace("__FRAGMENT__", fragment)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manuscript", type=Path, nargs="?")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--cdn-map", type=Path)
    parser.add_argument("--list-presets", action="store_true", help="print the style presets as JSON and exit")
    args = parser.parse_args()
    if args.manuscript is None and not args.list_presets:
        parser.error("manuscript path is required unless --list-presets is given")
    if args.list_presets:
        summary = {
            name: {"label": preset["label"], "brief": preset["brief"], "variants": preset["variants"]}
            for name, preset in PRESETS.items()
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    data = json.loads(args.manuscript.read_text(encoding="utf-8"))
    renderer = Renderer(data)
    fragment, report = renderer.render()
    noimage = renderer.render_without_images()
    title = str(data.get("title", "公众号文章"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fragment_path = args.output_dir / "article.fragment.html"
    noimage_path = args.output_dir / "article.noimage.html"
    import_path = args.output_dir / "article.import.html"
    preview_path = args.output_dir / "article.preview.html"
    report_path = args.output_dir / "article.render-report.json"
    cdn_map = load_cdn_map(args.cdn_map or (args.output_dir / "cdn_map.json"))
    fragment_path.write_text(fragment, encoding="utf-8")
    noimage_path.write_text(noimage, encoding="utf-8")
    import_path.write_text(import_document(fragment, title), encoding="utf-8")
    preview_path.write_text(preview_document(fragment, title, cdn_map, noimage), encoding="utf-8")
    report["outputs"] = {
        "fragment": str(fragment_path),
        "noimage": str(noimage_path),
        "import_document": str(import_path),
        "preview": str(preview_path),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(fragment_path)
    print(noimage_path)
    print(import_path)
    print(preview_path)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
