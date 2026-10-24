# SmartEn — English Competition Practice Platform

Interactive practice tool for the Mazowieckie English competition (Konkurs Jezyka Angielskiego, klasy IV-VIII). Built with React 19 + Vite 6 on Cloudflare Pages.

Live: https://smarten.pages.dev

## Project structure

```
smarten/
├── pub/konkursy/angielski/data/     # Static JSON data (competition tests + practice exercises)
│   ├── tests.json                   # Competition test index
│   ├── 2019-2020/ .. 2025-2026/     # Competition tests by year/stage (szkolny, rejonowy, wojewodzki)
│   ├── practice/                    # 105 practice exercises + index.json
│   ├── quest/                       # Quest exercises + index.json (branches, levels)
│   └── ojaj/                        # OJAJ: index.json, {year}/{stage}.json, practice/
├── site/                            # React app
│   ├── src/
│   │   ├── App.jsx                  # Routes, user auth gate, UserContext
│   │   ├── pages/
│   │   │   ├── Home.jsx             # Dashboard with stats + test list
│   │   │   ├── Practice.jsx         # Practice exercise browser + exercise player
│   │   │   ├── KonkursTest.jsx      # Competition test player with timer + AI grading
│   │   │   ├── Progress.jsx         # History, per-type stats, SVG chart
│   │   │   ├── quest/
│   │   │   │   ├── QuestHome.jsx    # Quest dashboard — branches, XP bar, exercise list
│   │   │   │   └── QuestExercise.jsx # Quest exercise player with XP + KV sync
│   │   │   └── ojaj/
│   │   │       └── OjajHome.jsx     # OJAJ section: papers + exercises (players are reused)
│   │   ├── components/konkursy/     # Task type renderers (one per type)
│   │   │   ├── TaskRenderer.jsx     # Dispatches to correct component by task.type
│   │   │   └── taskStyles.js        # Shared inline styles
│   │   └── lib/
│   │       ├── scoring.js           # Auto-scoring for all task types
│   │       ├── aiMarking.js         # Sends open tasks to /api/check; lists the ones left unmarked
│   │       ├── questProgress.js     # Quest progress: load/save, stars, KV sync (fetch/push/merge)
│   │       ├── questData.js         # Quest branch config, star titles, unlock thresholds
│   │       ├── questStars.js        # Shared star computation (client + server)
│   │       └── ojaj.js              # OJAJ paths, stage labels, player configs, isOjajAttempt
│   ├── functions/api/               # Cloudflare Pages Functions (serverless)
│   │   ├── check.js                 # AI grading via Claude API (Haiku/Sonnet)
│   │   ├── results.js               # KV-backed competition results storage
│   │   └── quest-progress.js        # Quest progress: GET/PUT with server-side merge
│   ├── public/_routes.json          # Routes /api/* to Functions, rest to static
│   ├── wrangler.toml                # Cloudflare config (KV binding: RESULTS)
│   └── package.json
```

## Commands

```bash
cd site
npm run dev        # Local dev server
npm run build      # Production build -> dist/
```

## Deployment

Deploy via wrangler (no auto-deploy from git):

```bash
cd site && npm run build && npx wrangler pages deploy dist --project-name smarten
```

Cloudflare secrets:
- `ANTHROPIC_API_KEY` — Claude API key for AI grading (set via `wrangler pages secret put`)

## Task types

12 task types, each with its own renderer in `components/konkursy/`:

| Type | Component | Scoring |
|------|-----------|---------|
| `true_false_ni` | TrueFalseNI.jsx | Auto — radio T/F/NI (a task may set `options` to narrow the columns, e.g. `["T","F"]`), graduated scoring scheme |
| `open_cloze` | OpenCloze.jsx | Auto — exact word match, band scoring |
| `multiple_choice` | MultipleChoice.jsx | Auto — A/B/C radio |
| `dialogue_choice` | MultipleChoice.jsx | Auto — same renderer as MC |
| `gap_fill_sentences` | GapFillSentences.jsx | Auto — dropdown select A-G |
| `word_spelling` | WordSpelling.jsx | Auto — exact word match |
| `word_formation` | WordFormation.jsx | Auto — exact word match |
| `matching` | Matching.jsx | Auto — multi-answer categorical |
| `matching_columns` | MatchingColumns.jsx | Auto — multi-select pairs |
| `knowledge_questions` | KnowledgeQuestions.jsx | Auto — text/MC, supports 2-part questions |
| `sentence_transformation` | SentenceTransformation.jsx | AI-graded (Haiku) |
| `grammar_gaps` | GrammarGaps.jsx | AI-graded (Haiku) |
| `writing` | Writing.jsx | AI-graded (Sonnet) |

AI-checked types are defined in `scoring.js` as `AI_CHECKED_TYPES`.

## Two competitions

The app covers two separate competitions. They share every renderer, the scoring
code and both players; what differs is the data root each player is pointed at.

| | Konkurs kuratoryjny | OJAJ |
|---|---|---|
| Full name | Konkurs Jezyka Angielskiego, woj. mazowieckie | Olimpiada Jezyka Angielskiego dla Juniorow |
| Level | B1-C1 | B2-C1+ |
| Stages | szkolny / rejonowy / wojewodzki | szkolny / okregowy / final |
| Data | `data/{year}/{stage}.json`, `data/practice/` | `data/ojaj/` |
| Routes | `/:year/:stage`, `/cwiczenia/:type/:id` | `/ojaj`, `/ojaj/:year/:stage`, `/ojaj/cwiczenia/:id` |
| Attempt testId | `{year}/{stage}`, `practice/{id}` | `ojaj/{year}/{stage}`, `ojaj/practice/{id}` |
| Best scores | `stored.rewards.bestScores` | `stored.ojajRewards.bestScores` |

`KonkursTest` and `PracticeExercise` each take a `config` prop that defaults to
the kuratoryjny one; `src/lib/ojaj.js` holds OJAJ's. Attempts carry
`competition: "ojaj"`, and `isOjajAttempt()` keeps OJAJ scores out of the
kuratoryjny averages, charts and star ladder — the two are marked on different
scales, so averaging them together describes neither. The history lists on
`/postepy` still show every attempt, each labelled and linked to its own paper.

OJAJ holds three timed papers (2022/23 grupa A and B, 2024/25) and 58 practice
exercises. Five of them (`ojaj_uk_*`) are not from a published paper: they are
the app's own questions on the 2026/27 UK-culture mind map, and their titles say
so. A year with two papers of the same stage needs two route slugs
(`szkolny-a`, `szkolny-b`), which are not readable names, so those papers and
their index entries carry a `label` that `KonkursTest` and `ojajStageTitle()`
prefer. Exercises may carry a `group`, which is the source paper; `OjajHome`
puts a heading above each run of them.

OJAJ data is built by `tmp/_gen_ojaj.py` from the papers published at
ojaj.wsjo.pl, checked by `tmp/_val_ojaj.mjs` (the answer key must score full
marks), `tmp/_render_ojaj.sh` (every task renders with its content visible) and
`tmp/_audit_ojaj.py` (no extraction leftovers, no item served twice).
`tmp/_peek_ojaj.sh <id>...` prints what a student sees for named exercises. The
generator's docstring lists the papers not yet converted and why.

Two of the papers publish their key only as an underline on the right option,
which `pdftotext` drops — it is a drawn rectangle, not a font attribute.
`tmp/_ojaj_underline.py` recovers it from mutool's trace (glyph positions plus
thin filled rectangles) and `tmp/_ojaj_parse.py` reads the marked text;
`tmp/_ojaj_extract.py` runs both over the PDFs and writes `tmp/_ojaj_items.json`,
which `tmp/_ojaj_new.py` turns into tasks. The 2022/23 papers mark their key
twice, inline and in bold, and `tmp/_ojaj_bold.py` checks the two agree.

The two gramatyczno-leksykalny papers have subsetted fonts with incomplete
character maps, so extraction drops whole words and every item in
`tmp/_ojaj_gl.py` was read off `pdftoppm` page images instead. Both versions of
each paper are needed: the one with the key marks the answers but prints them
over the blanks and omits the word bank and the base words, and the one without
the key has all of those but no answers.

## Data format

Competition test: `{ year, stage, date, maxPoints, timeMinutes, tasks: [...] }`

Practice exercise: `{ title, type: "practice", tasks: [{ id, type, points, instruction, items, scoringScheme?, openQuestion? }] }`

Answer formats vary by type — items use `answer` (string or array of accepted answers). Some types have `scoringScheme` for graduated/band scoring (e.g. `{"4":2,"3":1,"0-2":0}`).

## Styling

All inline styles, no CSS files. Dark theme (`#0a0a12` bg). Shared styles in `taskStyles.js`. Fonts: DM Sans (body), Playfair Display (headings).

## Auth & storage

Simple password gate in App.jsx (hardcoded users). User stored in localStorage as `smarten_user`. Attempt history saved to both localStorage (`smarten_konkursy_{user}`) and Cloudflare KV via `/api/results`.

Quest progress stored in localStorage (`smarten_quest_{username}`) and synced to Cloudflare KV (`quest:{username}` key) via `/api/quest-progress`. Server-side merge: highest bestScore wins per exercise, attempts unioned by attemptId. Stars always recomputed from bestScores (never trusted from client). Star system: 0-5 stars per exercise based on percentage (0%→0, 1-39%→1, 40-59%→2, 60-79%→3, 80-99%→4, 100%→5). 9 stars in a level unlocks the next. Global titles from total stars. Allowed users: Tadzio, Zosia, Lidia.

## Conventions

- Polish UI text (instructions, labels), English content in exercises
- Exercise instructions use ASCII (no Polish diacritics) for compatibility
- Practice exercise IDs follow pattern: `{type}_{NNN}` (e.g. `tfni_001`, `cloze_005`)
- Quest exercise IDs follow pattern: `quest_{branch}_{NN}` (e.g. `quest_vocab_01`)
- All data in static JSON under `pub/` — no database for content
- Scoring schemes use string keys for ranges: `"0-2"`, `"3"`, `"4"`
