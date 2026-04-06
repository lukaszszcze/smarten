# SmartEn

Interactive practice platform for the English language competition (Konkurs Języka Angielskiego) for primary school students in Mazowieckie voivodeship, Poland.

Live at **https://smarten.pages.dev**

## Features

- **Competition tests** — 7 years of past papers (2019–2026), all three stages (szkolny, rejonowy, wojewódzki), solvable online with auto-scoring
- **Practice exercises** — 105 exercises across 12 task types:
  - Wiedza o krajach (knowledge questions with A/B/C/D)
  - Literowanie (word spelling)
  - Słowotwórstwo (word formation)
  - Uzupełnianie luk (open cloze)
  - Prawda / Fałsz / NI (true/false/no information)
  - Wybór A/B/C (multiple choice grammar)
  - Luki w zdaniach (gap fill with sentences)
  - Dialogi (idioms & expressions)
  - Dopasowywanie (matching)
  - Transformacje zdań (sentence transformation) — AI-graded
  - Luki gramatyczne (grammar gaps) — AI-graded
  - Wypowiedź pisemna (writing) — AI-graded
- **Per-user accounts** with independent progress tracking
- **Performance dashboard** on home page — overall average, strongest/weakest task type
- **Per-type metrics** — completion rate, average best score, mastery levels, progress bars
- **Practice rewards** — star system (0–5 per exercise), titles (Beginner → Champion), per-type mastery (Beginner → Master)
- **Retry** — redo any exercise without leaving the page
- **Server-side results** — all answers saved to Cloudflare KV, viewable via API
- **Quest mode** — gamified lower-difficulty on-ramp for younger learners:
  - 3 branches (Vocabulary, Grammar, Reading), leveled exercises
  - Star system (0–5 per exercise) with global titles (Explorer → Legend)
  - Cross-device progress sync via Cloudflare KV
  - Bridge to full competition exercises when a branch is completed

## Tech stack

- React 19 + Vite + React Router 7
- Cloudflare Pages (hosting + serverless functions)
- Cloudflare KV (results storage)
- Claude API (Sonnet for AI-graded exercises)
- No backend framework — Pages Functions at `/api/results`, `/api/quest-progress`, and `/api/check`

## Project structure

```
site/                    # React app
  src/
    pages/
      Home.jsx           # Landing page with dashboard
      Practice.jsx       # Practice list, type list, exercise views
      KonkursTest.jsx    # Competition test page with timer
      Progress.jsx       # Detailed progress history
      quest/
        QuestHome.jsx    # Quest dashboard — branches, stars, exercise list
        QuestExercise.jsx # Quest exercise player with star scoring
    components/
      konkursy/          # Task renderers (one per task type)
      Layout.jsx         # Nav with user switcher
    lib/
      scoring.js         # Auto-scoring logic (9 deterministic types)
      practiceRewards.js # Practice stars, titles, per-type mastery
      questProgress.js   # Quest progress: load/save, stars, KV sync
      questData.js       # Quest branch config, star titles, constants
      questStars.js      # Shared star computation (used by client + server)
  functions/api/
    check.js             # AI grading — sentence transformation, grammar gaps, writing
    results.js           # Cloudflare Pages Function — competition results
    quest-progress.js    # Cloudflare Pages Function — quest progress sync
  wrangler.toml          # Cloudflare config with KV binding

pub/                     # Static data (copied to site/public/)
  konkursy/angielski/data/
    tests.json           # Competition test index
    2019-2020/ .. 2025-2026/  # Competition test JSON files
    practice/
      index.json         # Practice exercise index
      knowledge_001..010.json
      spelling_001..010.json
      formation_001..010.json
      cloze_001..010.json
      tfni_001..010.json
      mc_001..010.json
      gapfill_001..010.json
      dialogue_001..010.json
      matching_001..010.json
      transform_001..N.json    # AI-graded: sentence transformation
      grammar_001..N.json      # AI-graded: grammar gaps
      writing_001..N.json      # AI-graded: writing
    quest/
      index.json         # Quest exercise index (branches + levels)
      quest_vocab_01..N.json   # Quest exercise files
      quest_grammar_01..N.json
      quest_reading_01..N.json
```

## Development

```bash
cd site
npm install
npm run dev
```

## Deploy

```bash
cd site
npm run build
npx wrangler pages deploy dist --project-name smarten
```

**Important:** Run from `site/` directory so wrangler finds both `dist/` and `functions/`.

Requires `ANTHROPIC_API_KEY` secret set in Cloudflare Pages for AI grading.

## API

Results are stored in Cloudflare KV and accessible via:

```
GET  /api/results           # all users' results
GET  /api/results?user=Name # single user's results
POST /api/results           # save a result (JSON body with user, testId, score, etc.)

GET  /api/quest-progress?user=Name  # fetch quest progress from KV
PUT  /api/quest-progress            # merge and store quest progress (body: { user, progress })

POST /api/check                     # AI-grade an exercise (body: { type, task, answers })
                                    # types: sentence_transformation, grammar_gaps, writing
                                    # returns: { items: [{ id, earned, max, correct, feedback }], earned, max }
```
