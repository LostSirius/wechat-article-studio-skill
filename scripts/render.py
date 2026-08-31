#!/usr/bin/env python3
"""Render a structured manuscript into strict WeChat HTML and a copy preview."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


THEMES = {
    "academy": {
        "paper": "#f7f3ec",
        "card": "#ffffff",
        "ink": "#1a2740",
        "text": "#3c3834",
        "muted": "#786f66",
        "accent": "#c4a06a",
        "soft": "#efe8dc",
        "line": "#e4d8c5",
        "font": "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif",
    },
    "editorial": {
        "paper": "#fbfaf7",
        "card": "#ffffff",
        "ink": "#26221f",
        "text": "#38332f",
        "muted": "#7d746c",
        "accent": "#9d3f35",
        "soft": "#f1ebe5",
        "line": "#ded6ce",
        "font": "Optima, Palatino Linotype, PingFang SC, Microsoft YaHei, sans-serif",
    },
    "minimal": {
        "paper": "#ffffff",
        "card": "#ffffff",
        "ink": "#242424",
        "text": "#393939",
        "muted": "#808080",
        "accent": "#74867f",
        "soft": "#f4f4f1",
        "line": "#e6e6e2",
        "font": "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif",
    },
}

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


class Renderer:
    def __init__(self, manuscript: dict[str, Any]):
        theme_name = manuscript.get("theme", "academy")
        if theme_name not in THEMES:
            raise ValueError(f"Unknown theme: {theme_name}")
        self.m = manuscript
        self.name = theme_name
        self.t = THEMES[theme_name]
        self.images: list[dict[str, str]] = []
        self.block_counts: dict[str, int] = {}

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

    def paragraph(self, text: Any, margin: str = "13px 0 0 0") -> str:
        p_style = style(
            margin=margin,
            padding="0",
            font_size="15px",
            line_height="2",
            text_align="justify",
            color=self.t["text"],
            text_indent="2em",
        )
        return f'<p style="{p_style}">{self.rich(text, style(color=self.t["text"]))}</p>'

    def masthead(self) -> str:
        title = self.m.get("title", "")
        kicker = self.m.get("kicker")
        subtitle = self.m.get("subtitle")
        date = self.m.get("date")
        if not title:
            raise ValueError("Manuscript title is required")

        lines: list[str] = []
        if kicker:
            lines.append(
                f'<p style="{style(margin="0", padding="0", text_align="center", font_size="12px", letter_spacing="4px", color=self.t["ink"])}">'
                f'{self.span(kicker, style(color=self.t["ink"]))}</p>'
            )
        lines.append(
            f'<p style="{style(margin="14px 0 0 0" if kicker else "0", padding="0", text_align="center", font_size="24px", font_weight="bold", line_height="1.5", letter_spacing="1px", color=self.t["ink"])}">'
            f'{self.span(title, style(color=self.t["ink"], font_weight="bold"))}</p>'
        )
        if subtitle:
            lines.append(
                f'<p style="{style(margin="12px 0 0 0", padding="0", text_align="center", font_size="13px", line_height="1.9", color=self.t["muted"])}">'
                f'{self.span("·" + str(subtitle) + "·", style(color=self.t["muted"]))}</p>'
            )
        if date:
            lines.append(
                f'<p style="{style(margin="12px 0 0 0", padding="0", text_align="center", font_size="12px", color=self.t["muted"])}">'
                f'{self.span(date, style(color=self.t["muted"]))}</p>'
            )

        inner = "".join(lines)
        if self.name == "academy":
            return (
                f'<section style="{style(margin="22px 16px 18px 16px", padding="3px", border="1px solid " + self.t["ink"])}">'
                f'<section style="{style(padding="26px 16px 22px 16px", border="1px solid " + self.t["accent"])}">{inner}</section>'
                "</section>"
            )
        if self.name == "editorial":
            return (
                f'<section style="{style(margin="24px 20px 20px 20px", padding="24px 0 20px 0", border_top="2px solid " + self.t["ink"], border_bottom="1px solid " + self.t["line"])}">'
                f"{inner}</section>"
            )
        return f'<section style="{style(margin="32px 22px 24px 22px", padding="0")}">{inner}</section>'

    def image(self, data: dict[str, Any], hero: bool = False) -> str:
        src = str(data.get("src", "")).strip()
        alt = str(data.get("alt", "")).strip()
        caption = str(data.get("caption", "")).strip()
        full = bool(data.get("full", False))
        self.images.append({"src": src, "alt": alt, "caption": caption})
        margin = "0" if full or hero else "14px 16px 0 16px"
        img_style = style(width="100%", max_width="100%", height="auto", display="block", border="0")
        result = (
            f'<section style="{style(margin=margin, padding="0")}">'
            f'<img src="{esc(src)}" alt="{esc(alt)}" style="{img_style}" />'
        )
        if caption:
            cap_style = style(padding="9px 16px 11px 16px", background_color=self.t["soft"])
            p_style = style(margin="0", padding="0", font_size="12px", line_height="1.7", color=self.t["muted"])
            result += (
                f'<section style="{cap_style}"><p style="{p_style}">'
                f'{self.span("▍", style(color=self.t["accent"]))}'
                f'{self.span(" " + caption, style(color=self.t["muted"]))}</p></section>'
            )
        return result + "</section>"

    def facts(self) -> str:
        facts = self.m.get("facts") or []
        if not facts:
            return ""
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
            f'<section style="{style(margin="18px 16px 8px 16px", padding="2px", border="1px solid " + self.t["accent"])}">'
            f'<section style="{style(padding="16px 14px 8px 14px", border="1px solid " + self.t["line"], background_color=self.t["card"])}">'
            f'<p style="{style(margin="0 0 8px 0", padding="0", text_align="center", font_size="13px", color=self.t["ink"], letter_spacing="3px")}">'
            f'{self.span("项目速览", style(color=self.t["ink"]))}</p>'
            f'<table cellpadding="0" cellspacing="0" style="{style(width="100%", border_collapse="collapse")}"><tbody>'
            + "".join(rows)
            + "</tbody></table></section></section>"
        )

    def section_heading(self, section: dict[str, Any], index: int) -> str:
        number = section.get("number") or str(index).zfill(2)
        title = section.get("title", "")
        note = section.get("note")
        if not title:
            raise ValueError(f"Section {index} has no title")
        title_p = (
            f'<p style="{style(margin="0", padding="0", font_size="18px", font_weight="bold", color=self.t["ink"])}">'
            f'{self.span(title, style(color=self.t["ink"], font_weight="bold"))}</p>'
        )
        note_p = ""
        if note:
            note_p = (
                f'<p style="{style(margin="4px 0 0 0", padding="0", font_size="12px", color=self.t["muted"])}">'
                f'{self.span(note, style(color=self.t["muted"]))}</p>'
            )
        if self.name == "academy":
            return (
                f'<section style="{style(margin="28px 16px 8px 16px")}"><table cellpadding="0" cellspacing="0" '
                f'style="{style(width="100%", border_collapse="collapse")}"><tbody><tr>'
                f'<td style="{style(width="52px", background_color=self.t["ink"], text_align="center", vertical_align="middle", padding="14px 0 14px 0")}">'
                f'<p style="{style(margin="0", padding="0", font_size="18px", font_weight="bold", color="#ffffff", line_height="1.2")}">'
                f'{self.span(number, style(color="#ffffff", font_weight="bold"))}</p></td>'
                f'<td style="{style(padding="10px 14px 10px 14px", background_color=self.t["card"], border_top="1px solid " + self.t["ink"], border_right="1px solid " + self.t["ink"], border_bottom="1px solid " + self.t["ink"], vertical_align="middle")}">'
                f"{title_p}{note_p}</td></tr></tbody></table></section>"
            )
        left = f"{str(number).zfill(2)}　" if number else ""
        return (
            f'<section style="{style(margin="30px 20px 8px 20px", padding="0 0 10px 0", border_bottom="1px solid " + self.t["accent"])}">'
            f'<p style="{style(margin="0", padding="0", font_size="12px", color=self.t["accent"], letter_spacing="2px")}">'
            f'{self.span(left, style(color=self.t["accent"]))}</p>{title_p}{note_p}</section>'
        )

    def render_block(self, block: dict[str, Any]) -> str:
        kind = block.get("type")
        if kind not in ALLOWED_BLOCKS:
            raise ValueError(f"Unknown block type: {kind}")
        self.block_counts[kind] = self.block_counts.get(kind, 0) + 1
        if kind == "p":
            return f'<section style="{style(padding="6px 20px 4px 20px")}">{self.paragraph(block.get("text", ""), "8px 0 0 0")}</section>'
        if kind == "date":
            p = (
                f'<p style="{style(margin="0", padding="0")}">'
                f'<span style="{style(display="inline-block", background_color=self.t["ink"], color="#ffffff", font_size="12px", padding="3px 9px 3px 9px")}">'
                f'{esc(block.get("text", ""))}</span></p>'
            )
            return f'<section style="{style(padding="12px 20px 4px 20px")}">{p}</section>'
        if kind == "image":
            return self.image(block)
        if kind == "quote":
            author = block.get("author")
            body = (
                f'<p style="{style(margin="0", padding="0", font_size="28px", line_height="0.9", color=self.t["accent"])}">'
                f'{self.span("“", style(color=self.t["accent"]))}</p>'
            )
            for index, chunk in enumerate(quote_chunks(block.get("text", ""))):
                body += (
                    f'<p style="{style(margin="7px 0 0 0" if index == 0 else "10px 0 0 0", padding="0", font_size="14px", line_height="1.95", text_align="justify", color=self.t["text"], text_indent="2em")}">'
                    f'{self.rich(chunk, style(color=self.t["text"]))}</p>'
                )
            if author:
                body += (
                    f'<p style="{style(margin="14px 0 0 0", padding="0", text_align="right", font_size="13px", color=self.t["ink"])}">'
                    f'{self.span("—— " + str(author), style(color=self.t["ink"]))}</p>'
                )
            return f'<section style="{style(margin="14px 16px 0 16px", padding="18px 16px 16px 16px", background_color=self.t["card"], border="1px solid " + self.t["line"])}">{body}</section>'
        if kind == "callout":
            label = block.get("label")
            label_html = ""
            if label:
                label_html = (
                    f'<p style="{style(margin="0 0 8px 0", padding="0", font_size="12px", letter_spacing="2px", color=self.t["accent"])}">'
                    f'{self.span(label, style(color=self.t["accent"]))}</p>'
                )
            return (
                f'<section style="{style(margin="16px 20px 8px 20px", padding="14px 14px 14px 14px", background_color=self.t["soft"], border_left="3px solid " + self.t["accent"])}">'
                f'{label_html}<p style="{style(margin="0", padding="0", font_size="14px", line_height="1.9", color=self.t["text"])}">'
                f'{self.rich(block.get("text", ""), style(color=self.t["text"]))}</p></section>'
            )
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
                f'<section style="{style(margin="14px 20px 8px 20px")}"><table cellpadding="0" cellspacing="0" '
                f'style="{style(width="100%", border_collapse="collapse")}"><tbody>{"".join(trs)}</tbody></table></section>'
            )
        return f'<section style="{style(margin="24px auto 20px auto", width="36px", height="1px", background_color=self.t["accent"], font_size="0", line_height="0")}">&nbsp;</section>'

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
            f'<section style="{style(padding="22px 20px 14px 20px")}"><p style="{style(margin="0", padding="0", text_align="center", font_size="12px", line_height="2.15", color=self.t["muted"])}">'
            f"{body}</p></section>"
        )

    def render(self) -> tuple[str, dict[str, Any]]:
        sections = self.m.get("sections")
        if not isinstance(sections, list) or not sections:
            raise ValueError("Manuscript sections must be a nonempty list")
        root_style = style(
            width="100%",
            max_width="677px",
            margin="0 auto",
            padding="0",
            background_color=self.t["paper"],
            font_family=self.t["font"],
        )
        parts = [f'<section style="{root_style}">', self.masthead()]
        hero = self.m.get("hero")
        if hero:
            parts.append(self.image(hero, hero=True))
        lead = self.m.get("lead") or []
        if lead:
            parts.append(f'<section style="{style(padding="16px 20px 6px 20px")}">')
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
            parts.append(
                f'<section style="{style(margin="28px auto 0 auto", width="36px", height="1px", background_color=self.t["accent"], font_size="0", line_height="0")}">&nbsp;</section>'
            )
            parts.append(f'<section style="{style(padding="18px 20px 8px 20px")}">')
            for idx, paragraph in enumerate(closing):
                parts.append(self.paragraph(paragraph, "0" if idx == 0 else "14px 0 0 0"))
            parts.append("</section>")
        parts.append(self.credits())
        footer = self.m.get("footer_image")
        if footer:
            parts.append(self.image({**footer, "full": True}))
        parts.append("</section>")
        fragment = "\n".join(part for part in parts if part)
        report = {
            "theme": self.name,
            "title": self.m.get("title"),
            "sections": len(sections),
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


def preview_document(fragment: str, title: str) -> str:
    escaped_title = esc(title)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{escaped_title} · 公众号预览</title>
<style>
body{{margin:0;background:#e9e6e1;font-family:Arial,sans-serif}}
.bar{{position:sticky;top:0;z-index:9;padding:10px;text-align:center;background:#1f2937;color:#fff}}
.bar button{{border:0;border-radius:6px;padding:9px 18px;background:#fff;color:#111;cursor:pointer}}
#article-root{{max-width:677px;margin:18px auto;background:#fff}}
.hint{{font-size:12px;opacity:.75;margin-left:10px}}
</style>
</head>
<body>
<div class="bar"><button onclick="copyArticle()">复制到公众号</button><span class="hint" id="status">请先等待图片加载</span></div>
<div id="article-root">{fragment}</div>
<script>
async function copyArticle(){{
 const root=document.getElementById('article-root');
 const html=root.innerHTML;
 const text=root.innerText;
 try{{
  await navigator.clipboard.write([new ClipboardItem({{
   'text/html':new Blob([html],{{type:'text/html'}}),
   'text/plain':new Blob([text],{{type:'text/plain'}})
  }})]);
  document.getElementById('status').textContent='已复制，请粘贴到公众号编辑器';
 }}catch(e){{
  const range=document.createRange();range.selectNodeContents(root);
  const sel=window.getSelection();sel.removeAllRanges();sel.addRange(range);
  document.execCommand('copy');sel.removeAllRanges();
  document.getElementById('status').textContent='已复制（兼容模式）';
 }}
}}
window.addEventListener('load',()=>{{document.getElementById('status').textContent='图片加载完成，可复制';}});
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manuscript", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    data = json.loads(args.manuscript.read_text(encoding="utf-8"))
    renderer = Renderer(data)
    fragment, report = renderer.render()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fragment_path = args.output_dir / "article.fragment.html"
    preview_path = args.output_dir / "article.preview.html"
    report_path = args.output_dir / "article.render-report.json"
    fragment_path.write_text(fragment, encoding="utf-8")
    preview_path.write_text(preview_document(fragment, str(data.get("title", "公众号文章"))), encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(fragment_path)
    print(preview_path)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

