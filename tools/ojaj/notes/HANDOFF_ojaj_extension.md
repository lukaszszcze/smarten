# OJAJ — where the conversion stands

Every OJAJ paper with a published answer key has been converted. Nothing is
committed and **nothing since the first batch is deployed**.

## What is there

`pub/konkursy/angielski/data/ojaj/` holds 3 timed papers and 58 practice
exercises:

- `2022-2023/szkolny-a.json`, `szkolny-b.json` — 60 items each, 60 pkt, 60 min
  (the time is derived at one minute per item, not published)
- `2024-2025/szkolny.json` — 45 items
- `practice/` — 58 exercises, grouped in the index by source paper:
  4 sample-type exercises with no group, then etap I cz. 2 (8), etap II cz. 1
  (8), etap III (8), test gramatyczno-leksykalny etap I (8) and etap II (8)

Build and check, all green as of 2026-09-05:

```
python3 tools/ojaj/gen_ojaj.py     # writes the JSON, asserts the shapes
node tools/ojaj/val_ojaj.mjs       # the answer key must score full marks
bash tools/ojaj/render_ojaj.sh     # every task renders with its content visible
python3 tools/ojaj/audit_ojaj.py   # no extraction leftovers, no item served twice
npm --prefix site test       # 25/25
```

`bash tools/ojaj/peek_ojaj.sh <id>...` prints what a student sees for named exercises.

Deploy: `cd site && npm run build && npx wrangler pages deploy dist --project-name smarten`

## Added 2026-09-27

- **2023/24 etap szkolny** (`tools/ojaj/ojaj_2324.py`): 9 exercises, 90 items, read
  off page images (the scans have no text layer and OCR scrambles the option
  columns). Wersja B is wersja A's items in a different task order, so only A
  is converted.
- **UK culture 2026/27** (`tools/ojaj/ojaj_uk.py`): 5 exercises, 50 questions written
  for this app from the school round's mind map
  (`.../uploads/2026/08/OJAJ-2026_2027-The-UK.pdf`). Not official material;
  titles say "pytania wlasne".
- `tools/ojaj/peek_ojaj.sh` currently fails for every exercise ("Element type is
  invalid"), old ones included; `render_ojaj.sh` still passes.

## What is left, and why it is hard

- **The USA mind map** for the semi-final is due at the end of October 2026;
  it will want the same treatment as the UK one.
- **The 2025/26 final** (`.../uploads/2026/04/OJAJ-Test-finalowy-*.pdf`) has no
  published key. Nothing to check an answer against, so it stays out.
- **Listening and the final's oral part** have no material published at all.

## What the conversion learned

Written up in `CLAUDE.md` and in the docstrings of `tools/ojaj/gen_ojaj.py`,
`tools/ojaj/ojaj_new.py` and `tools/ojaj/ojaj_gl.py`. The parts most likely to be needed
again:

1. **A paper published twice, with and without the key, needs both versions.**
   The key version prints the answers over the blanks, so it does not show
   where they were; the gramatyczno-leksykalny papers also drop their word bank
   and base words there, and number one task differently.
2. **`grammar_gaps`: `answer` as an array means one answer per blank**, not a
   list of alternatives. One blank takes a string; alternatives go inside it,
   separated by `/`.
3. **`GrammarGaps` and `SentenceTransformation` split on a run of exactly nine
   underscores.** Eight or ten renders the sentence with the input stranded at
   the end and nothing errors. `word_formation` splits on `/_{2,}/`.
4. **`knowledge_questions` options need an `"A. "` prefix (dot);
   `multiple_choice` uses `"A) "` (paren).** MultipleChoice strips the prefix
   and shuffles, mapping the answer back, so the key's spread does not matter.
5. **`matching` puts its options on the task**: `options: [{letter, text}]` and
   `items: [{id, statement, answer}]`.
6. **`word_spelling` patterns are `__` per letter, space separated**, the
   pattern also appears inside `sentence`, and `check_spelling` asserts every
   given letter against the answer. A wrong pattern still marks correct but is
   unsolvable on screen.
7. **`word_formation` has two shapes**: a sentence and a base word per item, or
   one shared `text` with numbered blanks plus a `wordBank`. The second one has
   no per-item prompt, which both the validator and the render checker have to
   be told about.
8. **`true_false_ni` shows a T, F and NI column** unless the task sets
   `options`. A paper offering only T and F must say so.
9. **Two-column option layouts read A, C on the first line and B, D on the
   second.** Getting this wrong silently mislabels every option.
10. **Competition instructions keep full Polish diacritics** (they are quoted
    from the paper); practice instructions are ASCII. The exception is content
    where folding changes the word — the etap I Polish-to-English list keeps its
    diacritics because "łąka" and "laka" are different words.
