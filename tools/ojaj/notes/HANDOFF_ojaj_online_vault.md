# Handoff: OJAJ online-test vault (etap I, czesc II)

Written 2026-10-24 at the end of a design session with Lukasz. Everything in
"Decisions" was settled with him one question at a time; do not reopen it
unless the code proves it impossible. "Suggested implementation" is my sketch,
not a decision: change it where the code argues otherwise, and say so.

## The goal

A vault of 10 timed practice tests in the format of OJAJ etap I, czesc II (the
online part of the school stage). On the OJAJ page, Tadzio presses one button
and gets a test drawn at random, played in a player that looks like the real
online platform.

The real test is on 16.11.2026, 09:00-09:45 (mazowieckie). The plan is to
release the player with Tests 01-03 about two weeks before that, so time
matters more than polish.

## Where you are

- Worktree `/home/lukasz/workspace/smarten-vault`, branch `ojaj-online-vault`,
  based on `c7c27ea` on `main`. Lukasz may switch branches in the main checkout
  (`/home/lukasz/workspace/smarten`), so stay in the worktree and check
  `git branch --show-current` before any commit.
- Untracked on purpose:
  - `tmp/`: a copy of the main checkout's `tmp/`. All the OJAJ generators and
    checkers live here; they resolve paths from their own location, so in the
    worktree they read and write the worktree. `tmp/` has never been committed
    in this repo.
  - `CONTEXT.md`: the glossary from the design session. Commit it on this
    branch with the work.
  - `site/node_modules` is a symlink to the main checkout's install, listed in
    the repo's local exclude file. Nothing needs installing; ask before
    installing anything.
- Never commit, push or deploy without Lukasz saying so. Commit messages carry
  no Co-Authored-By line. Run `/verify` right before any commit.

## The real test (sources checked 2026-10-24)

- Programme 2026/27, section 1.2: 45 questions, 1 point each, 45 minutes, "test
  generowany indywidualnie z puli zadan", written at school.
  `tools/ojaj/pdfs/Zalacznik-do-Regulaminu-OJAJ-program-OJAJ-edycja-2026-2027.pdf`
- School-stage task types: multiple choice, word formation, key word
  transformations, wisielec; UK culture from the mind map
  (`tools/ojaj/pdfs/uk_2627.pdf`; the study notes are `site/public/ojaj_uk.html`).
  Grammar: tenses, reported speech, conditionals 0-3, relative clauses.
  Vocabulary: everyday and general, collocations, phrasal verbs, idioms.
- The platform (`tools/ojaj/pdfs/INSTRUKCJA-DO-TESTU-ONLINE.txt`) is a Moodle quiz:
  one attempt; timer top left; "Nastepne" button; "Nie mozesz wracac do
  poprzednich pytan ani korzystac z przycisku Wstecz", but a panel on the right
  gives "szybki dostep do wszystkich aktualnych pytan"; finish with "Zatwierdz
  wszystkie i zakoncz" and a confirmation; copy-paste not allowed.
- Marking (coordinator pack, part I, assumed to hold online): 1 or 0 per item,
  no half or negative points, full grammatical and spelling correctness, British
  and American spelling both accepted.
- Not published anywhere: how the 45 questions split between types online.

## Decisions

| Topic | Decision |
|---|---|
| One test | 45 items, 45 min, 1 pt each, all or nothing: task 1 word formation (10), task 2 wisielec (10), task 3 key word transformations (10, AI-marked), task 4 grammar and vocabulary multiple choice (10), task 5 UK culture multiple choice (5) |
| Order | Fixed, grouped by type in that order, questions numbered 1-45. Each question screen repeats its task's instruction |
| Level | See "Level target" below |
| Content | All 450 items are own items, written for the app. No item may repeat any item already in the app (papers, practice, quest). A UK fact may recur as a different question |
| Draw | One "Losuj test" button on the OJAJ page; the 10 tests are not listed for direct choice. Random among unseen tests; once all are done, random among those done least often |
| Unseen | A test with no submitted attempt. An opened and abandoned test stays unseen (accepted as rare) |
| Timer | 45 minutes; at 0:00 the test submits itself |
| Player | New, copying the real platform: one question per screen, "Nastepne", no "Poprzednie" button, a numbered panel that jumps to any question (earlier ones included) and marks answered ones, "Zatwierdz wszystkie i zakoncz" with a confirmation |
| After submit | Score per task type, then a question-by-question review with the key. (The real platform shows less; the review is the practice value) |
| History | Online-test rows on `/postepy` are not links, so the draw stays the only way in |
| Who | Everyone who sees the OJAJ section; unseen is tracked per user |
| Work order | Test 01 as a printout for review, then the build, then Tests 02-10 (details below) |
| Release | Deploy (with approval) once the player, the draw and Tests 01-03 pass every check; Tests 04-10 in later deploys. New tests are unseen, so the draw serves them first |

## Level target

Evidence, from tagging every item of four papers by the CEFR level of what it
tests (my judgement per item, not a lookup; regenerate with
`python3 -I tools/ojaj/ojaj_level_compare.py`):

| Paper | Items | Format | B2 or above | C1 or above | C1+ grammar | C1+ vocabulary |
|---|---|---|---|---|---|---|
| Part I 2022/23, grupa A | 60 | all multiple choice | 13% | 3% | 0% | 9% |
| Part II 2022/23 sample (`etap-I-czesc-II-1.pdf`) | 74 | multiple choice + matching | 64% | 37% | 10% | 54% |
| Part I 2023/24, grupa A | 80 | 3/4 typed | 51% | 10% | 3% | 16% |
| Part I 2024/25, grupa B | 40 | 3/4 typed | 85% | 45% | 33% | 52% |

The part II sample's jump over part I of the same year is almost all
vocabulary: about 30 of its 74 items are idioms (do/head idiom matching, body-part and
colour idioms), several of them informal or dated British. Part I itself has
climbed since, and 2024/25 is already at the sample's level while being mostly
typed.

Lukasz chose: **match the 2024/25 part I paper and add the part II idioms.**
Per 10-item task (tasks 1-4): about 1 B1, 4 B2, 4-5 C1 and 0-1 C2, mixed in so
position does not signal difficulty. In tasks 2 and 4, 3-4 items of 10 test
idioms, collocations or phrasal verbs; prefer idioms in current use over dated
slang ("browned off"). Task 5 is knowledge, so the level profile does not apply
to it.

If Lukasz gets the blank 2026/27 part I paper from the school coordinator (the
coordinator pack says they hand it out on request), recheck Test 01's level
against it before writing Tests 02-10.

## Order of work, with the stops

Status 2026-10-24: step 1 is done and approved without corrections. Test 01's
items are in `tools/ojaj/ojaj_online.py` (run it to check them and rewrite
`tmp/ojaj_online_01_review.md`; `tools/ojaj/ojaj_online_selftest.py` shows each check
catches its case). Its keys are strict on purpose and approved that way: 1.5
only "irreparable", 3.4 only "too heavy for me to". The generator does not yet
write `pub/.../ojaj/online/01.json`; adding that is part of step 2. Use
`tools/ojaj/find_phrase.py` and `tools/ojaj/dump_prompts.py` to check planned items for
Tests 02-10 against the app.

Status 2026-10-24, later: step 2 (the build) is done, nothing committed. New:
`site/src/lib/ojajOnline.js` (draw, screens, clock, player rules as a
reducer, marking, attempt record; 100% covered by `ojajOnline.test.js`),
`saveAttempt` in `resultsSync.js` (now also used by `KonkursTest`),
`pages/ojaj/OjajOnlineTest.jsx`, the route, the OJAJ page section, unlinked
history rows. `gen_ojaj.py` writes `online/NN.json` and the index's `online`
list from `ojaj_online.built_tests()`, which also checks each test against
the vault tests before it. Item ids are now the question numbers "1"-"45".
`val_ojaj.mjs` covers the vault; `render_ojaj.jsx` also renders the 45
one-item screens. `tools/ojaj/e2e_online.mjs` clicks through the player in Chromium
with the API mocked (start `npx vite --port 5179 --strictPort` in `site/`
first; `SHOTS=1 WIDTH=390` saves screenshots to `tmp/_shots/`).
Deviation from the sketch above: only the transformations go to the AI;
the paper player also sends word formation, whose AI accepts unlisted
variants, which would undo the strict keys.
Deploy catch: `site/public/konkursy/angielski/data` is a tracked symlink to
the absolute path of the main checkout's `pub/` data, so a build in this
worktree serves main's data, which has no `online/`. Build and deploy from
main after merging this branch. Lukasz looked at the build and approved it
("looks good", 2026-10-24); still not committed, no commit asked for.

Status 2026-10-24, step 3: Tests 02 and 03 are written (`T02`, `T03` in
`tools/ojaj/ojaj_online.py`, both in `TESTS`), pass every check there, and their
printouts are `tmp/ojaj_online_02_review.md` and `_03_review.md`, waiting
for Lukasz's review. `gen_ojaj.py` has not been run since, so their JSON
does not exist yet. Lesson for Tests 04-10: the app already holds about 220
transformations, and the standard points (wish, enough, no sooner, is being
built, unless you hurry, believed to have been built) are each there several
times, one of them word for word as first planned. The repeat check only
catches an exact keyword and answer, so also compare each planned item by
eye with the existing ones for its keyword, and prefer keywords the app has
not used. Twelve planned wisielec and word-formation answers were taken too.
Lukasz approved Tests 02 and 03 unchanged ("approved", 2026-10-24),
including the judgement calls listed with the printouts (02/10 only
"knowledgeable", 02/21 also bare "the tallest", Test 03 task 3 leaning on
phrasal verbs and collocations, one inversion item per test). Next: step 4,
run `gen_ojaj.py` and every check (including `tools/ojaj/e2e_online.mjs`), then
ask before any commit or deploy.

Status 2026-10-24, step 4: `gen_ojaj.py` wrote `online/02.json`, `03.json`
and the index's three-test `online` list; no other data file changed. All
checks pass: `val_ojaj.mjs` (35/35 auto-marked per test, 10 to the AI),
`render_ojaj.sh` (0 problems), `audit_ojaj.py` (0 problems),
`ojaj_online.py` and its selftest, `npm test` (106), `npm run build`, and
the e2e at 1280 and 390 wide. The e2e was written for a one-test vault (it
expected "0 z 1" and a draw that could only give 01); it now reads the vault
from `ojaj/index.json`, draws until every test is done (each draw must give
a test not done yet), answers each drawn test from its own key (45/45 for
all three), and draws once more with all done. Nothing committed; next is
Lukasz's approval for /verify + commit on this branch, the merge into main,
and the deploy from main. `tmp/` is not in git, so the generator, the item
file, the checks and this handoff live only in this worktree's `tmp/`.
Lukasz approved all three. /verify passed (14 lines over 100 characters
wrapped, a comment added on the offline draw), and the e2e passed again
afterwards. Committed as 5c4df85 on this branch and fast-forwarded into
main; main's build contains `online/01-03`. The deploy command was refused
by the session's permission check; Lukasz ran it himself from main and it is live (2026-10-24, checked: index lists 01-03, each test served):
`cd site && npx wrangler pages deploy dist --project-name smarten`. Next:
step 5, Tests 04-10, in this worktree (re-create this branch's position from
main first if main has moved).

1. **Write Test 01 and stop.** All 45 items with keys, a `level` tag per item
   and a focus tag where the profile needs counting (idiom, collocation, phrasal
   verb). Produce a readable printout (for example
   `tmp/ojaj_online_01_review.md`: each task's instruction, every item with its
   options or base word or pattern, the key, the level, plus per-task level
   counts) and ask Lukasz to review it. Do not build anything before his
   corrections; they apply to the other 405 items.
2. Build the draw, the player, the OJAJ page section and the history change,
   test-first (see below).
3. Write Tests 02 and 03 to the corrected standard.
4. Run every check, then ask for approval to deploy. A deploy also releases
   everything committed on `main` since the last deploy (the handoff note
   `tools/ojaj/notes/HANDOFF_ojaj_extension.md` says nothing since the first OJAJ batch has
   been deployed); say so when asking.
5. Tests 04-10, each batch checked, each deploy approved.

## Writing rules for the items

Formats follow the existing OJAJ files exactly. Copy the shapes from the
2023/24 and 2024/25 conversions and the own-item helpers in `tools/ojaj/ojaj_own.py`
and `tools/ojaj/ojaj_2324.py`:

- Word formation (`word_formation`): `{id, sentence, wordBase, answer: [..]}`,
  one blank of 2+ underscores per sentence, base word in capitals. The sentence
  must allow exactly one derived word; list spelling variants (British and
  American) in `answer`.
- Wisielec (`word_spelling`): `{id, sentence, hint, answer: [..]}`; the pattern
  is `__` per letter, space separated, given letters in place, and it appears
  inside `sentence` too. The 2024/25 paper adds the letter count, `(9)`. The
  sentence must pin the word down on its own, and the given letters must rule
  out any other word of that length. `check_spelling` in the generator asserts
  every given letter against the answer; a wrong pattern still marks correct
  but cannot be solved on screen.
- Key word transformations (`sentence_transformation`):
  `{id, original, keyword, transformed, answer}`. The blank in `transformed` is
  exactly nine underscores (`_________`); eight or ten silently breaks the
  renderer. Keyword unchanged in every accepted answer, at most six words
  including the keyword, no contractions; alternatives in one string joined by
  " / ". These go to the AI checker, which scores 0 or 1 per item and accepts
  any listed phrasing without an AI call, so list every phrasing a marker would
  accept.
- Multiple choice (`multiple_choice`): `{id, stem, options: ["A) ..", ..],
  answer: "C"}`, four options, prefix `"A) "` with a parenthesis. The renderer
  shuffles and maps the answer back. Wrong options must be plausible real forms;
  the part II sample's nonexistent forms ("was been", "will have be") made its
  grammar items easier than their targets.
- UK culture: the 2024/25 paper used `knowledge_questions` with prefix `"A. "`
  (a dot); `multiple_choice` is the other option. Check facts against
  `site/public/ojaj_uk.html` and the mind map. Do not reuse the 50 questions in
  `ojaj_uk_*` or the 2023/24 `ojaj_2324_kultura` and 2024/25 task 5.
- Instructions: online tests are timed tests, so use the papers' printed
  wording for each type with full Polish diacritics (competition convention;
  practice instructions are ASCII). The 2024/25 word formation instruction and
  the 2023/24 transformation instruction (6-word limit, no contractions) are in
  the existing JSON. Say once, on the start screen, that the items are the
  app's own ("zadania wlasne"), as every own exercise does.
- Tadzio is in primary school: content suitable for his age.

## Suggested implementation

Data:
- `pub/konkursy/angielski/data/ojaj/online/NN.json` (01-10) in the same shape as
  a paper, so `scoreTest` works unchanged:
  `{competition: "ojaj", kind: "online", id: "01", label: "Test online 01",
  maxPoints: 45, timeMinutes: 45, tasks: [...]}`, items carrying `level`.
- The vault list as a new key in `ojaj/index.json` (the OJAJ page already
  fetches it), for example `"online": [{"id": "01", "label": "Test online 01"}]`.
- A generator `tools/ojaj/ojaj_online.py` in the style of `tools/ojaj/ojaj_own.py`, with the
  existing checks extended to `online/`: `tools/ojaj/val_ojaj.mjs` (the key scores
  full marks), `tools/ojaj/render_ojaj.sh` (every item renders with its content),
  `tools/ojaj/audit_ojaj.py` (no leftovers, no prompt shared with any other item in the
  app), plus a new check that each test meets the level profile and the
  idiom/collocation/phrasal-verb counts.

Draw:
- A pure function in `site/src/lib/` (for example `ojajVault.js`) taking the
  vault ids and the user's attempts and returning the drawn id. Count only
  attempts with `testId` `ojaj/online/NN` (attempts are only saved on submit, so
  "submitted" needs no extra state). Tests in `site/src/lib/*.test.js`
  (`node:test`, run by `npm test`): unseen first; least-done once all are done;
  other attempts ignored; one unseen left is always drawn. Use
  `t.mock.method(Math, "random", ...)` rather than a `random` argument that only
  tests would pass (Lukasz's rule: keep an argument only when a real caller
  varies it).
- The OJAJ page reads attempts from local storage only (`loadAttempts`, no
  sync) [verified]. Only `Home.jsx` and `Progress.jsx` call `syncAttempts` from
  `site/src/lib/resultsSync.js`. Sync before drawing, or a test done on another
  device counts as unseen.

Player:
- A new page (for example `/ojaj/online/:id`, registered above `/:year/:stage`
  in `site/src/App.jsx`, like the other OJAJ routes). Reuse the task renderers
  by giving each screen the task with only that item:
  `{...task, items: [item]}`.
- `MultipleChoice` shuffles options in a `useMemo` keyed on `task.id`
  [verified], so a renderer mounted afresh on each visit reshuffles the options
  every time he returns to a question. Keep each question's renderer mounted and
  hide the inactive ones, or shuffle once at load.
- `KonkursTest` does not submit at 0:00 [verified]; the new player must.
- AI marking: `markWithAi` in `site/src/lib/aiMarking.js`. When it returns
  `unmarkedTaskIds`, save nothing and offer a retry. In this player the answers
  should stay locked after submit (time may be up), so the retry only re-runs
  the marking. `KonkursTest` has the opposite problem: after a failed check the
  timer is stopped and the answers editable.
- Save the attempt like `KonkursTest.saveResult` does (local storage plus
  `POST /api/results`), with `kind: "competition"`, `competition: "ojaj"` and
  `testId: "ojaj/online/NN"`. `isOjajAttempt` matches on the `ojaj/` prefix, so
  the kuratoryjny averages already leave these out [verified].

Pages:
- OJAJ page (`site/src/pages/ojaj/OjajHome.jsx`): a section "Etap I, czesc II -
  test online" with the "Losuj test" button, how many of the 10 are done, and
  the user's online results (test, date, score). The papers grid must not list
  the online tests.
- History (`site/src/pages/Progress.jsx:481-498`): competition rows link to
  `/${attempt.testId}` and label themselves from `attempt.stage` and
  `attempt.year`, which an online attempt does not have. Render online rows
  unlinked with their own label.
- Update `CLAUDE.md` (project structure, OJAJ section, data format) and the
  `gen_ojaj.py` docstring when done.

## Names

`CONTEXT.md` defines paper, online test, vault, draw, unseen and own items. Use
them in code and UI. "Pool" is taken: in this app a pool (`OJAJ_POOL`,
`PRACTICE_POOL` in `site/src/lib/practiceRewards.js`) is where best scores are
stored.

## Open points

- The navigation sentence in the platform instructions can also be read as
  forward-only. Lukasz chose "panel jumps anywhere"; the school coordinator or
  ojaj@wsjo.pl could confirm before 16.11.
- The programme calls the second stage "etap polfinalowy"; the code labels it
  "okregowy" (`OJAJ_STAGE_LABELS` in `site/src/lib/ojaj.js`). Not part of this
  work; mention it, do not change it.
- The 2026/27 USA mind map (due end of October) is for the semi-final, not this
  test.
