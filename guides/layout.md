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

## Recipes

### `academy`

For university news, study tours, academic exchange, institutional events.

- palette: warm paper, ink navy, muted brass;
- title: restrained double-line or plain editorial masthead;
- section: Chinese numeral block plus factual date/location note;
- body: open paper background, no card around every paragraph;
- images: mostly full bleed or one consistent inset;
- captions: attached neutral strip;
- quotes: white card with a single brass quotation mark;
- suitable modules: project facts, date labels, credits.

### `editorial`

For profiles, interviews, brand stories, long-form reporting.

- palette: off-white, charcoal, one muted editorial red or ochre;
- title: left aligned with strong typographic hierarchy;
- section: plain headline plus thin rule;
- body: generous whitespace;
- images: inset with short factual captions;
- quotes: pull quote only when sourced;
- suitable modules: byline, deck, dialogue, pull quote.

### `minimal`

For image-led travel notes or already approved copy.

- palette: white or warm grey, near-black, one low-saturation accent;
- title: simple, no decorative frame;
- section: small number plus title, or title only;
- body: widest whitespace;
- images: full width;
- suitable modules: brief lead, section title, image, caption, credits.

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

Required fields: `title`, `sections`. Other fields may be omitted.

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

## Image width

- `full: true`: image reaches the article container edge.
- `full: false` or omitted: image uses a 16 px inset.

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

