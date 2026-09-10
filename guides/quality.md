# Quality rubric and iteration

## Benchmark principle

Do not declare state of the art because one model likes its own output. Compare:

- deterministic feature coverage;
- static audit results;
- blinded or reference-based editorial review;
- rendered mobile review;
- task-specific user feedback.

Record the comparator name/version/date when possible.

## Hard gates

All must pass:

- [ ] factual conflicts resolved or exposed;
- [ ] no invented quotation, title, number, or accolade;
- [ ] no forbidden strict-profile HTML;
- [ ] clean fragment contains no preview script/button;
- [ ] every image has a nonempty source and alt text;
- [ ] all supplied/approved content is represented;
- [ ] GIF frames share dimensions and duration plan;
- [ ] external images are clearly marked for WeChat transfer;
- [ ] no unresolved placeholder is hidden from the user.
- [ ] every claimed screenshot or preview artifact exists at the reported path.

## Six-dimension, five-point rubric

### 1. Factual integrity

- 5: every claim traceable; conflicts handled; uncertainty explicit.
- 4: minor contextual claims need final source check.
- 3: one potentially misleading title/date/causal claim.
- 2: several unsupported promotional statements.
- 1: invented or materially wrong content.

### 2. Human editorial voice

- 5: specific, coherent voice; natural rhythm; every paragraph advances.
- 4: a few generic transitions or one redundant summary.
- 3: repeated abstractions, symmetry, or uniform paragraph rhythm.
- 2: template prose dominates.
- 1: generic AI-style expansion with little source information.

### 3. Information architecture

- 5: opening, sections, images, and ending form an obvious reading path.
- 4: one section is overlong or misplaced.
- 3: chronology/topics are understandable but scanning is weak.
- 2: component order obscures the narrative.
- 1: information is missing or incoherent.

### 4. Visual direction

- 5: one coherent system; content-shaped components; strong density rhythm.
- 4: coherent with one unnecessary decorative block.
- 3: polished but visibly template-driven or repetitive.
- 2: too many competing styles, cards, labels, or colors.
- 1: broken, illegible, or arbitrary.

### 5. Mobile readability

- 5: comfortable type, deliberate wraps, attached captions, no overflow.
- 4: one minor spacing/wrapping issue.
- 3: dense areas or inconsistent image treatment.
- 2: small text, wide tables, detached captions, or awkward animation.
- 1: not usable on a phone.

### 6. WeChat handoff

- 5: strict fragment passes; preview copies correctly; asset states documented.
- 4: passes but external assets still need transfer.
- 3: one risky property or manual repair.
- 2: several elements likely to be stripped.
- 1: requires unsupported script/style after paste.

## Static editorial signals

The audit script flags, but does not automatically rewrite:

- template connectors;
- unsupported authority phrases;
- abstract buzzwords;
- `不仅…更…` patterns;
- repeated paragraph endings;
- long sentences and paragraphs;
- uniform sentence-length distribution;
- excessive colons/dashes;
- empty generic ending;
- overuse of emphasis.

A warning is evidence to inspect, not proof that a human did not write the text.

## Comparative experiment

Use at least three fixtures:

1. **Chronological study tour**  
   Conflicting schedules, bilingual names, talk titles, many photos, mixed-orientation GIF.

2. **Academic news**  
   Dense facts, one table, two quotations, few images, institutional voice.

3. **Profile/interview**  
   Dialogue, attributed quotations, narrative scenes, editorial recipe.

4. **Club recap with style overrides**  
   Non-institutional voice, `campus` preset, overridden accent and variants, airy density.

For each fixture:

1. generate a manuscript without manual HTML;
2. render;
3. run `audit.py`;
4. review at 375/414 px;
5. score all six dimensions;
6. list exact failures;
7. revise the skill or renderer, not only the fixture;
8. regenerate.

## Regression checks

- format-only mode does not rewrite prose;
- asset-only mode does not touch HTML copy;
- blocked reference URLs do not produce invented style claims;
- empty facts list does not render an empty card;
- missing kicker/date/hero/credits/footer are handled cleanly;
- unknown block type fails loudly;
- special characters are escaped;
- `[[em:...]]` is the only accepted inline markup;
- strict fragment contains only allowed tags;
- preview button is outside copied root;
- audit exits nonzero on fatal compatibility errors.
- a review cannot claim screenshots that are absent from the output directory.

## Stop condition

Stop iterating when:

- hard gates pass;
- each rubric dimension is at least 4/5;
- static audit has no fatal error;
- remaining warnings were individually reviewed;
- a new iteration no longer improves a named failure.

If the user’s aesthetic preference remains the only uncertainty, present one best version and one clearly differentiated alternative instead of endless random restyling.

