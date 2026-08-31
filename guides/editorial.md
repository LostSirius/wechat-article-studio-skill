# Editorial system

## Order of operations

Edit in this order:

1. facts;
2. information sequence;
3. paragraph logic;
4. voice;
5. sentence rhythm;
6. polish.

Starting with “humanization” risks making unsupported claims sound more convincing.

## Evidence control

### Fact classes

- **Observed**: visible in supplied material or recorded in an authoritative schedule.
- **Attributed**: supplied by a named person or source; preserve attribution.
- **Contextual**: verified background needed to understand the event.
- **Promotional**: biography, superlative, forecast, impact claim, or unsourced number.
- **Unknown**: conflict, missing name, incomplete date, or unclear role.

Publish observed and attributed facts. Verify contextual facts. Cut or qualify promotional claims. Leave an explicit placeholder for unknowns instead of guessing.

### Conflict handling

Record both claims and choose the stronger source:

1. direct user correction;
2. contemporaneous programme/schedule;
3. official announcement;
4. handbook or planning document;
5. filename/caption;
6. model inference.

Mention conflicts to the user only when they change the published result.

## Voice fingerprint

Describe the target in operational terms, not adjectives:

- “third-person campus reportage” is useful;
- “warm, premium, poetic” is not enough.

Capture examples for:

- first sentence;
- how dates begin sections;
- teacher/title naming;
- treatment of English names;
- talk-title punctuation;
- captions;
- student quotations;
- credits.

Do not transfer factual details or distinctive phrases from reference articles.

## Low-AI editing

AI-like prose is mainly a discourse problem, not a forbidden-word problem. Diagnose before rewriting.

### High-value checks

1. **Zero-reference evaluation**  
   A paragraph begins with “值得注意的是”“这充分体现了” without naming what “this” is. Replace it with the concrete subject.

2. **Information echo**  
   The final sentence repeats the paragraph using grander words. Delete it unless it adds consequence or evidence.

3. **Abstract stack**  
   Three or more abstractions appear together: “平台、生态、视野、赋能、融合、路径、动能”. Replace at least one with an action, person, place, object, or result.

4. **Empty symmetry**  
   “不仅……更……”“从 A 到 B，从 C 到 D”“理论上、实践上、方法上” creates balance without new information. Keep the stronger clause.

5. **Colon-list reflex**  
   A vague sentence introduces three generic bullets. Convert to prose or use a list only when the items are genuinely parallel and useful for scanning.

6. **Idealized metaphor**  
   Avoid “如同一位不知疲倦的导师” and similar generic personification. Use a concrete comparison only when it explains mechanism.

7. **Uniform cadence**  
   All sentences and paragraphs have similar length. Combine or split where the idea changes, not at a fixed word count.

8. **Canned significance**  
   “具有重要意义”“奠定坚实基础”“开启崭新篇章” needs evidence. State what changed, for whom, or omit it.

9. **Vague authority**  
   “研究表明”“专家认为”“业内普遍认为” requires a named source. Otherwise delete it.

10. **Template ending**  
    Do not append a generic call for likes/comments or repeat the opening thesis. End on the final fact, a sourced reflection, or a restrained consequence.

### Do not overcorrect

- Human writing may use questions, metaphors, parallelism, and transitions.
- Do not ban a word merely because AI often uses it.
- Do not force slang into institutional news.
- Do not create random sentence fragments to imitate spontaneity.
- Do not add first person unless the account’s voice calls for it.

## Reportage recipe

### Opening

Within the first paragraph establish:

- date;
- organization or group;
- destination/venue;
- programme;
- participants or leaders when relevant;
- duration.

The second paragraph may state the programme purpose, but tie it to actual activities.

### Body

For chronological events:

- begin with the date or concrete scene;
- name the speaker/activity;
- give the talk title using the account’s punctuation convention;
- summarize one or two substantive points;
- place the corresponding image immediately after the relevant paragraph.

Avoid turning every speaker into a biography card. Add background only when it explains the lecture.

### Captions

A caption should answer “who is doing what, where?”:

- Good: `虚构讲者甲在实验教室介绍演示流程`
- Weak: `精彩课堂瞬间`
- Weak: `图为活动现场`

Use the person’s approved display name. Do not add facts not visible or sourced.

### Reflections

Keep a student’s wording unless correction is requested. Remove only clear duplication or errors. Use a full quote block and a simple right-aligned name; do not surround every quotation with heavy decoration.

### Closing

Summarize what the programme actually combined and what participants did. One modest evaluation is enough.

## Readability targets

These are guides, not automatic rewrite commands:

- body text: usually 15–16 px in HTML;
- paragraph: commonly 2–5 sentences;
- very long sentence: inspect above 55 Chinese characters;
- very long paragraph: inspect above 180 Chinese characters;
- 2–6 body sections for most articles;
- no more than two strong emphases in one paragraph;
- heading depth: normally two levels.

The automated auditor deliberately uses looser thresholds—72 Chinese characters per
sentence and 200 per paragraph—to reduce false positives. The shorter values above are
editorial review targets, not contradictions in the acceptance gate.

## Final copy pass

- [ ] Names and titles are consistent.
- [ ] Dates and chronology agree.
- [ ] Chinese/English spacing follows the account’s convention.
- [ ] Talk titles use the requested punctuation.
- [ ] Every quotation has a real source.
- [ ] Every paragraph advances information.
- [ ] No unsupported accolade or number remains.
- [ ] No generic summary duplicates the preceding paragraph.
- [ ] The ending sounds specific to this article.

