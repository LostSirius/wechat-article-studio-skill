# Layout system

## Art direction

A polished article has one visual argument. It does not demonstrate every component in a library.

Use:

- one dominant background;
- one dark anchor color;
- one restrained accent;
- one neutral text scale;
- 3–5 component families;
- consistent image treatment within each sequence.

Do not confuse “more styled” with “better designed”. Fixed dashboards, English eyebrow text, numbered chapters, gradient cards, and pill labels are common sources of template or AI-generated appearance when they do not serve the content.

## Who decides the look

The user's brief decides the visual direction. This skill improves execution—hierarchy,
spacing, rhythm, consistency, WeChat safety—it does not impose a house style. Concretely:

- when the user names a mood (“清新”, “庄重”, “科技感”, “国风”, “喜庆”, “杂志感”), translate
  it into a preset plus overrides using the table below, and say which one you chose;
- when the user supplies a reference post or screenshot, translate its palette roles, heading
  treatment, caption treatment, and density into the same knobs;
- when the user has no preference, render a gallery and let them point at a column instead
  of silently defaulting to `academy`;
- never switch a preset the user already approved in order to “fix” a small issue; adjust the
  single knob that causes the issue.

Two layers control the output:

1. `theme` — a named preset supplying palette, font stack, and default component variants;
2. `style` — optional overrides for any palette token, the font, each component variant,
   paragraph metrics, image inset, and spacing density.

## Presets

Every preset shares the conservative HTML contract; they differ in palette and component
shapes, not in tag usage.

| `theme` | 中文 | Palette roles | Masthead | Heading | Caption | Quote | Callout | Body | Use for |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `academy` | 学院纪实 | warm paper, ink navy, muted brass | `frame` | `block` | `strip` | `card` | `soft` | justified, indented | university news, study tours, institutional events |
| `editorial` | 杂志特稿 | off-white, charcoal, editorial red | `rule` | `rule` | `strip` | `card` | `soft` | justified, indented | profiles, interviews, brand stories |
| `minimal` | 极简留白 | white, near-black, grey-green | `plain` | `rule` | `strip` | `card` | `soft` | justified, indented | image-led notes, approved copy |
| `campus` | 清新校园 | mint white, pine, grass green | `underline` | `pill` | `plain` | `line` | `soft` | left, no indent | clubs, recruitment, activity recaps |
| `festival` | 节庆典礼 | warm cream, red, gold | `band` | `centered` | `strip` | `card` | `outline` | justified, indented | anniversaries, greetings, ceremonies, awards |
| `tech` | 科技简报 | cool grey, navy, electric blue | `underline` | `bar` | `plain` | `line` | `outline` | left, no indent | research results, products, data explainers |
| `ink` | 水墨人文 | rice paper, ink black, cinnabar | `rule` | `centered` | `centered` | `plain` | `soft` | justified, indented, serif | culture, history, reading, essays |
| `magazine` | 暖调生活 | cream, cocoa, burnt orange | `underline` | `bar` | `plain` | `card` | `soft` | left, no indent | lifestyle, food, weekends, community |

Print the machine-readable list with `python scripts/render.py --list-presets`.

Render the same manuscript in several presets for a side-by-side choice:

```bash
python scripts/gallery.py manuscript.json --output-dir gallery
python scripts/gallery.py manuscript.json --output-dir gallery --presets campus,tech,magazine
```

Open `gallery/index.html`, let the user pick a column, and write that preset name back into
the manuscript `theme`.

## Style overrides

```json
{
  "theme": "campus",
  "style": {
    "palette": {"accent": "#2f8f6b", "ink": "#173d2e"},
    "font": "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif",
    "masthead": "underline",
    "heading": "pill",
    "caption": "plain",
    "quote": "line",
    "callout": "soft",
    "paragraph": {"indent": false, "size": 15, "line_height": 1.9, "align": "left"},
    "image_inset": 16,
    "density": "airy"
  }
}
```

Knobs and accepted values:

| Key | Values | Effect |
| --- | --- | --- |
| `palette.*` | six-digit hex for `paper`, `card`, `ink`, `text`, `muted`, `accent`, `soft`, `line` | replaces one palette role; keep `text` on `paper` readable |
| `font` | font stack without quotes or semicolons | root `font-family` |
| `masthead` | `frame` double line · `rule` top/bottom rules · `plain` · `band` solid ink block with light text · `underline` left-aligned with short accent bar | title block |
| `heading` | `block` numbered dark cell · `rule` small number + bottom rule · `pill` accent label above title · `bar` thick left border · `centered` number, title, short rule | section headings |
| `caption` | `strip` tinted strip · `plain` marker + text · `centered` quiet centered text | caption under each image |
| `quote` | `card` white card · `line` left accent border · `plain` centered, no frame | quote blocks |
| `callout` | `soft` tinted with left border · `outline` accent outline on card | callouts |
| `paragraph.indent` | `true` / `false` | 2em first-line indent |
| `paragraph.size` | 13–18 | body font size in px |
| `paragraph.line_height` | 1.5–2.4 | body line height |
| `paragraph.align` | `justify` / `left` | body alignment |
| `image_inset` | 0–32 | side inset in px for non-full images |
| `density` | `compact` / `normal` / `airy` | scales vertical spacing between blocks (0.8 / 1.0 / 1.3) |

Unknown keys or out-of-range values are fatal. `facts_title` at the top level renames the
facts card heading (default `项目速览`).

## Translating a brief into knobs

| The user says | Start from | Typical overrides |
| --- | --- | --- |
| 正式、庄重、学术、官方 | `academy` | keep; `density: normal`; avoid `pill` |
| 杂志感、人物、特稿、有质感 | `editorial` | `heading: bar` if the reference uses left rules; `caption: plain` |
| 干净、留白、图多字少 | `minimal` | `caption: centered`; `density: airy` |
| 清新、活泼、年轻、社团、招新 | `campus` | shift `accent` toward the club color; keep `pill` |
| 喜庆、节日、周年、颁奖、红色 | `festival` | `masthead: band`; `accent` gold or warm ivory |
| 科技感、数据、理性、蓝色、简报 | `tech` | `heading: bar`; `quote: line`; `paragraph.align: left` |
| 国风、水墨、文化、读书、人文 | `ink` | serif `font`; `quote: plain`; `density: airy` |
| 温暖、生活、美食、周末、橙色 | `magazine` | `accent` toward the brand warm color |
| 参考这篇推文的风格 | closest preset by palette | copy palette roles and heading/caption treatment, not artwork |
| 我不知道要什么 | run `gallery.py` | let the user choose, then refine one knob at a time |

Color words map to `accent` first, then `ink`; never recolor `text` to a saturated hue.
“更活泼” usually means `pill` or `underline` plus `density: airy`, not more components.
“更正式” usually means `frame` or `rule` plus justified, indented paragraphs.

## Density rhythm

Mark each block as:

- **dense**: long paragraph, metadata table, comparison;
- **medium**: short paragraph, heading, quote;
- **light**: image, rule, whitespace, brief caption.

Avoid `dense → dense → dense` and repeated cards. A common reportage rhythm is:

`heading → medium text → image → caption → medium text → light image`.

## Component decisions

Use a component only if removing it would reduce:

- comprehension;
- scanability;
- attribution;
- comparison;
- orientation in chronology;
- emotional pacing.

Otherwise use a paragraph or whitespace.

### Strong limits

- one masthead;
- one facts card at most;
- one date label for each real date transition, not each paragraph;
- callouts: usually 0–2;
- quote cards: only sourced quotations/reflections;
- table: four columns maximum;
- decorative English labels: omit unless part of the organization’s identity;
- strong color anchors: no more than five across the article.

## Manuscript JSON

The renderer accepts this structure:

```json
{
  "theme": "academy",
  "style": {"density": "normal"},
  "title": "潮汐之间，记录一场开放日",
  "kicker": "国际视野",
  "subtitle": "虚构海岸实验室开放日纪要",
  "date": "2026.05.18",
  "hero": {
    "src": "assets/fictional-hero.jpg",
    "alt": "虚构参与者在实验室入口合影",
    "caption": "虚构参与者在实验室入口合影",
    "full": true
  },
  "lead": [
    "第一段。",
    "第二段可选。"
  ],
  "facts": [
    ["主题", "公众科学写作"],
    ["地点", "虚构海岸实验室"]
  ],
  "sections": [
    {
      "number": "壹",
      "title": "进入实验室",
      "note": "5月18日　虚构海岸实验室",
      "blocks": [
        {"type": "p", "text": "正文，允许用 [[em:关键短语]] 做克制强调。"},
        {"type": "date", "text": "8月3日"},
        {
          "type": "image",
          "src": "assets/fictional-scene.jpg",
          "alt": "实验室外的海岸步道",
          "caption": "虚构实验室外的海岸步道",
          "full": true
        },
        {"type": "quote", "text": "经来源确认的虚构引语。", "author": "虚构受访者甲"},
        {"type": "callout", "label": "项目速览", "text": "只放真正需要突出阅读的信息。"},
        {
          "type": "table",
          "rows": [["项目", "内容"], ["主题", "人工智能"]]
        },
        {"type": "rule"}
      ]
    }
  ],
  "closing": ["收束段。"],
  "credits": [
    ["图文", "示例编辑部"],
    ["说明", "匿名虚构示例"]
  ],
  "footer_image": {
    "src": "assets/fictional-footer.gif",
    "alt": "虚构页尾图形"
  }
}
```

Required fields: `title`, `sections`. Other fields may be omitted. `theme` defaults to
`academy`; `style` defaults to the preset's own variants; `facts_title` defaults to `项目速览`.

Supported block types:

- `p`
- `date`
- `image`
- `quote`
- `callout`
- `table`
- `rule`

Unknown block types are fatal. Do not insert raw HTML into JSON.

## Text markup

The only manuscript markup is:

```text
[[em:需要强调的短语]]
```

The renderer escapes all other HTML. This prevents accidental scripts or unsupported tags.

Use emphasis only when the phrase helps a reader scan. Do not add emphasis to every paragraph.

## Output profiles

The renderer uses a conservative profile:

- tags: `section`, `p`, `span`, `table`, `tbody`, `tr`, `td`, `img`;
- inline styles only;
- no class/id;
- no flex/grid;
- no gradient, `rgba`, positioning, transform, animation, or pseudo-elements;
- no headings (`h1`–`h6`) because paragraph-based headings paste more consistently;
- hex colors;
- text nodes wrapped in styled spans.

The preview page may use modern CSS and JavaScript outside the copied article. The clean fragment may not.

The renderer writes four HTML files from one manuscript:

- `article.fragment.html` — the strict fragment with `<img>` tags;
- `article.noimage.html` — the same layout with every image replaced by a numbered
  “图 N · 此处插入图片” slot, for pasting when images only exist locally;
- `article.import.html` — the fragment wrapped in a minimal document for editors that import
  HTML files;
- `article.preview.html` — browser preview with copy and download actions.

## Image width

- `full: true`: image reaches the article container edge.
- `full: false` or omitted: image uses the `style.image_inset` side inset (default 16 px).

Use one treatment for a sequence. Do not alternate without a reason.

Small source images must not be stretched beyond their useful resolution. The asset report should flag them for replacement.

## Reference translation

When learning from a reference:

1. identify palette roles, not exact colors;
2. measure relative spacing, not pixel-copy the whole page;
3. identify which blocks recur;
4. identify where the reference deliberately breaks repetition;
5. map only components that fit the current content.

Do not recreate a proprietary template block-for-block.

