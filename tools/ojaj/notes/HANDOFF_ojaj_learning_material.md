# Handoff: learning material for Tadzio's mistake types

Written 2026-10-25 for a fresh session. The job is to prepare learning
material for the mistake types the mistake record uses, so that when the OJAJ
page lists one of his weak types he has something to read and practise.

The design interview took place on 2026-10-25, and its decisions are in the
next section. They override the suggestions further down. Next step: the
sample of three pages (see Order).

## Progress (2026-10-25, sample session)

- DEPLOYED 2026-10-25 at Lukasz's request ("publish"): the 7 word pages and the
  index are live at https://smarten.pages.dev/ojaj_study/ (main d4f5e29, on top
  of the build's 36a2341, which was already live). The canonical generator and
  page data are now in the main checkout's `tmp/` (`gen_study.py`,
  `_study_pages/`, with Test 03 frozen in `_study_pages/test03.json` because
  `online/03.json` left `pub/`).
- Links DONE 2026-10-25 (78ffe56, deployed): no edit to `_TYPE_ROWS` was needed;
  `vault_link` holds a study link back until its page exists, so fast-forwarding
  `ojaj-online-vault` to main (which brought the pages into this worktree) and
  re-running `gen_ojaj.py` filled in the 7 word links. The grammar types stay
  unlinked because their pages are off the site. This worktree's branch is now
  at 78ffe56, the same as main.
- Lists: a list of 12 entries or fewer is shown whole, an Advanced box with fewer
  than 5 words folds into its list, and ance-ence has no boxes (`SPLIT = False`).
- All 11 pages and the index are built in `/home/lukasz/workspace/smarten-study`
  (branch `ojaj-study-pages`, nothing committed). Lukasz approved the sample
  (index, checklist, base-change) after these changes: no task numbers in the
  headings; the checklist lost its short-forms list and its key-word table; the
  base-change page got the full list (his call: word lists are exhaustive). The
  other 9 pages were then written the same way and wait for his review.
- Pages other than the index and the checklist are generated:
  `tools/study/gen_study.py` writes `site/public/ojaj_study/<key>.html` from
  `tools/study/pages/<key>.py` and refuses to write if a word is missing from the
  British dictionaries, if anything from Test 03 is on the page, if a word is
  listed twice, or if a marking or wisielec hint does not fit. Edit the data,
  not the HTML. The worktree's `tmp/` is untracked: copy `gen_study.py`,
  `_study_pages/`, `e2e_study.mjs`, `text_study.mjs` and `shot_part.mjs` to
  the main checkout's `tmp/` when the branch is merged.
- Left out because of Test 03: neglect/negligible, humour/humorous,
  breath/breathe, disappear/appearance, rhythm, tongue, "supposing" on the
  conditionals page, relative "when", "than anyone else". Add them after he has
  done Test 03.
- Lukasz took the transformations and grammar pages off the site for now (word
  formation and wisielec first). Their data has `PUBLISH = False`; the checklist is
  kept in `tools/study/pages/unpublished/transformations.html`; the group sits in an
  HTML comment on the index. He agreed the build session should set the 11 grammar
  links in `_TYPE_ROWS` to None (he passes that on).
- Word lists are in columns, sorted alphabetically, with C1-C2 words in an
  "Advanced" box under each list (`ADVANCED` in each page's data, judged by hand).
- `OjajHome.jsx`: a `StaticPageCard` serves the notebook's card and the new one.
  CLAUDE.md has a "Study pages" section.
- `npm run dev` does not serve `/ojaj_study/<key>` without `.html`; `vite build`
  + `vite preview --port 5191` does. Test: `node tools/study/e2e_study.mjs [shot-dir]`.

## Start here (fresh session, after the interview)

- Lukasz sent the build session the link values (2026-10-25). Do not send them
  again. That session adds the `link` field to `_TYPE_ROWS`; this one does not
  edit `ojaj_online.py`.
- Create the worktree, after checking whether main has moved:
  `git -C /home/lukasz/workspace/smarten worktree add -b ojaj-study-pages
  /home/lukasz/workspace/smarten-study main`. Nothing from smarten-vault's
  `tmp/` is needed there. Read the evidence (`tmp/ojaj_mistake_types_review.md`,
  this file) from the vault path and edit nothing there except this file.
- Copy the design from `site/public/ojaj_uk.html` (703 lines: the colour
  tokens on `:root` with the dark set, the fonts, `.branch` sections, the
  `details` self-checks, and the "I've learnt this" script at the end, which
  uses the key `uk-notebook-learnt`). Use a key of its own for the study
  pages. The notebook card is in `site/src/pages/ojaj/OjajHome.jsx` at about
  lines 316-343; the index card goes right after it, in the same style.
- Checked 2026-10-25: neither `existing_items()` in `ojaj_online.py` nor
  `tools/ojaj/find_phrase.py` reads HTML; both scan only the JSON under `pub/`. With
  "No separation" decided, nothing needs to change there.
- The typed checks are static JavaScript with no test runner, so test them in
  a browser. Cloudflare Pages serves `site/public/ojaj_study/base-change.html`
  at `/ojaj_study/base-change`, and that address is the one used in links (the
  notebook's card links to `/ojaj_uk`). `vite.config.js` has nothing for
  addresses without `.html`, so whether `npm run dev` resolves them is
  unchecked; open the pages there with `.html` if it does not.
- Each page's content (rule, word list, checks) must be correct English and
  suit a primary-school pupil. Show the sample in the browser and as text for
  approval before writing the other eight pages.

## Decisions (design interview, 2026-10-25)

| Topic | Decision |
|---|---|
| Material | Study pages: static HTML in `site/public`. Practice sets come later, and only where reading alone will not do |
| Scope before 16.11 | The transformations checklist; conditionals, relative-clauses and comparison (his three grammar slips: if I had had, both of whom, too heavy for me to); base-change; suffix-spelling; double-letters; vowels; silent-letters; negative-prefix; ance-ence (added by Lukasz). UK culture: links into the notebook only. Every other type waits |
| Pages | One page per type, named by its type key (Lukasz switched to this from one page per task): `site/public/ojaj_study/<key>.html`, served at `/ojaj_study/<key>`. The checklist is at `/ojaj_study/transformations` and the index at `/ojaj_study/`. All pages share one stylesheet, and the typed checks one script |
| Language | English throughout, with no Polish labels in the headings (Lukasz answered "English"). The card on the OJAJ page is in Polish without diacritics |
| Entry point | One card next to the notebook's on the OJAJ page. It opens the index page, which lists the pages grouped by task, the checklist first |
| Links from the weak-points list | A link field per type in `_TYPE_ROWS`, added by the build session. This session sends it the values below, with Lukasz's OK |
| Types without a page | The grammar types link to the checklist; word and vocabulary types get no link. A type's link moves to its own page once that page is written |
| Self-check | Word pages: typed boxes, with the exact spelling checked on the spot. Checklist and grammar pages: questions whose answer opens on a click (`details`/`summary`). An "I've learnt this" tick on every page, kept in local storage; nothing else is saved |
| Overlap with online items | No separation (Lukasz): a word used on a page may appear in a new online item |
| Examples | His miss leads, phrased neutrally ("Common mistake: pronounciation / Right: pronunciation"), then common words of the same pattern. Nothing from Test 03, which he has not seen |
| Page layout | Back link to the index; title and tick; the common mistake; the rule with a word list; "Watch out"; "Check yourself" (5-8 items); a link to OJAJ practice |
| Design | The notebook's: its fonts, light and dark colours, and the layout of `ojaj_uk.html` |
| Worktree | `/home/lukasz/workspace/smarten-study`, branch `ojaj-study-pages`, made from main at 8266f80. The build session works in smarten-vault at the same time |
| Order | A sample first: the index, the checklist and base-change, shown to Lukasz. The other pages after he approves them |
| Release | Together with the build, in one deploy (Lukasz) |

Link values for `_TYPE_ROWS`:

- `/ojaj_study/<key>`: negative-prefix, ance-ence, base-change,
  suffix-spelling, double-letters, silent-letters, vowels, conditionals,
  relative-clauses, comparison.
- `/ojaj_study/transformations`: inversion, reported-speech, passive, modals,
  verb-patterns, tenses, participle-clauses, linking-words.
- No link: able-ible, two-steps, word-ending, idiom, collocation,
  phrasal-verb.
- The notebook: uk-symbols `/ojaj_uk#symbols`, uk-countries `#nations`,
  uk-politics `#parliament`, uk-history `#history`, uk-people `#britons`,
  uk-london `#landmarks`, uk-parks `#parks`.

Read first, in the worktree `/home/lukasz/workspace/smarten-vault` (branch
`ojaj-online-vault`): this file; `tools/ojaj/notes/HANDOFF_ojaj_mistakes.md` (the mistake
record: its decisions and the build plan); `CONTEXT.md`; and the type list
`_TYPE_ROWS` in `tools/ojaj/ojaj_online.py` (lines 65-153). Check
`git branch --show-current` and `git log -1` before anything else.

## The request

Lukasz, 2026-10-25: "write a handoff to a fresh session to prepare learning
material for the various mistake types". He said nothing more specific, so
format, scope and order are all open.

## Background

- The real test is on 16.11.2026: etap I, czesc II, online, mazowieckie
  09:00-09:45. That is three weeks away, so material he can read before then
  is worth more than covering all 31 types.
- The mistake record (separate handoff; design settled, build not started):
  every online test will be put together from single items. Items he missed
  come back, and unseen items of the types he misses are drawn more often. The
  OJAJ page will list his weak types by their Polish label, with the share
  missed. The learning material is what that list should point to.
- The 31 types each have a key, a Polish label (no diacritics), a note on what
  they cover, and the tasks they appear in. Groups: building a word (7 types,
  tasks 1-2), spelling (3, tasks 1-2), vocabulary (idiom, collocation,
  phrasal-verb; tasks 2-4), grammar (11, tasks 3-4), UK culture (7, task 5,
  one per branch of the mind map). `tmp/ojaj_mistake_types_review.md` lists
  all 135 items of Tests 01-03 under their type; use it for examples.
- Tasks: 1 word formation, 2 wisielec (spell a word from a few given letters),
  3 key word transformations (marked by the AI), 4 multiple choice, 5 UK
  culture.

## His evidence

Two online attempts, both on 2026-10-24: Test 02, 32/45, and Test 01, 26/45,
so 32 misses in all. Test 03 is still unseen (checked 2026-10-25). All of this
comes from `node tmp/_types_missed.mjs tmp/_results_Tadzio_2026-10-25.json`.
Transformations are marked there by matching the listed phrasings, which gives
the AI's points exactly in both attempts.

### Word formation and wisielec: 17 misses

"From his answer" is the type the record's rules will give (worked out by hand
in the build handoff; a blank keeps the item's own type).

| Test/q | He wrote | Key | Item's type | From his answer |
|---|---|---|---|---|
| 02/1 | resemblence | resemblance | ance-ence | ance-ence |
| 02/3 | unaccessible | inaccessible | negative-prefix | negative-prefix |
| 02/4 | pronounciation | pronunciation | base-change | base-change |
| 02/6 | (blank) | hindrance | base-change | base-change |
| 02/10 | knowledgable | knowledgeable | suffix-spelling | suffix-spelling |
| 02/13 | (blank) | guarantee | silent-letters | silent-letters |
| 02/14 | mischevious | mischievous | vowels | vowels |
| 02/16 | (blank) | conscientious | silent-letters | silent-letters |
| 01/1 | unrecogniseable | unrecognisable | negative-prefix | suffix-spelling |
| 01/3 | speachless | speechless | base-change | vowels |
| 01/4 | emberrassment | embarrassment | double-letters | vowels |
| 01/5 | irrepairable | irreparable | negative-prefix | base-change |
| 01/6 | childlish | childish | word-ending | word-ending |
| 01/7 | indecidous | indecisive | negative-prefix | base-change |
| 01/8 | unforgetable | unforgettable | double-letters | double-letters |
| 01/10 | accidentaly | accidentally | suffix-spelling | double-letters |
| 01/19 | (blank) | compliment | collocation | collocation |

Counted by the type from his answer: base-change 4, vowels 3,
suffix-spelling 2, double-letters 2, silent-letters 2, and one each for
negative-prefix, ance-ence, word-ending and collocation.

What the answers show:

- He keeps the base word whole where it has to change: pronounce stays in
  pronounciation, repair in irrepairable, decide in indecidous.
- The prefix itself was right in 6 of his 7 negative-prefix items; 01/1, 01/5
  and 01/7 go wrong later in the word, and only 02/3 picks the wrong prefix
  (un- for in-). In his practice history, though, the negative prefix was his
  most frequent word-formation mistake (undistinguishable, undispensable,
  unseparated, deniable for undeniable; `tools/ojaj/scan_mistakes.mjs`).
- The e before an ending goes wrong both ways: dropped in knowledgable, kept
  in unrecogniseable.
- A single consonant where there should be two: unforgetable, accidentaly.
- Unstressed vowels: speachless, emberrassment, mischevious. His practice
  history adds accomodation, excersices and percieving.
- The three blanks (guarantee, conscientious, hindrance) look like words he
  did not know rather than words he misspelt [inferred].

### Transformations: 8 misses

Most of these are not about the grammar point the item tests. The
instruction on the paper says: "Słów podanych nie wolno w żaden sposób
zmieniać. [...] Konieczna jest pełna poprawność gramatyczna i ortograficzna
wpisywanych fraz."

| Test/q | Key word | He wrote | Key | What went wrong |
|---|---|---|---|---|
| 02/22 | HELP | was helpless with laughter | could not help laughing | changed the key word |
| 02/29 | WONDER | was wondering if I could | wonder if I could | changed the key word |
| 02/26 | BUT | but Ksia can help | but Kasia can help | spelling (the name) |
| 01/28 | PUT | put op with | put up with | spelling |
| 01/21 | HAD | if I have had | if I had had | wrong tense |
| 01/27 | BLAME | is to blame for | was to blame for | the original's tense not kept |
| 01/24 | TOO | too heavy to | too heavy for me to | part of the meaning left out |
| 01/23 | BOTH | both of which | both of whom | which used for people |

A short checklist for the task (the key word exactly as given, the same tense
and the whole meaning of the original, read it back for spelling) may fix more
of these than pages on the eleven grammar types would.

### Multiple choice

20 of 20 right. Nothing to fix.

### UK culture: 7 misses

Test 02: 3 of 5 right. Test 01: 0 of 5.

| Test/q | Type | Question, shortened | Answer |
|---|---|---|---|
| 02/42 | uk-countries | When is St George's Day? | on 23 April |
| 02/43 | uk-politics | Who writes the King's Speech? | the government |
| 01/41 | uk-politics | Nickname for the Conservative Party | the Tories |
| 01/42 | uk-politics | Last step before a bill becomes law | Royal Assent |
| 01/43 | uk-people | Sherlock Holmes's address | 221B Baker Street |
| 01/44 | uk-parks | What happened in Hyde Park in 1851 | the Great Exhibition in the Crystal Palace |
| 01/45 | uk-london | Oldest part of the Tower of London | the White Tower |

Every one of these answers is already in the UK notebook, and the King's
Speech is one of its self-check questions. There is no way to tell whether he
has read it: the notebook's "I've learnt this" ticks are kept only in his
browser's local storage.

## What exists already

- The UK notebook, `site/public/ojaj_uk.html`, served at `/ojaj_uk` and linked
  from a card at the top of the OJAJ page (`OjajHome.jsx`,
  `UK_NOTEBOOK_PATH`). English text, its own light and dark design and fonts.
  Its seven sections have ids matching the seven culture types: `symbols`
  (uk-symbols), `nations` (uk-countries), `parliament` (uk-politics),
  `history` (uk-history), `britons` (uk-people), `landmarks` (uk-london),
  `parks` (uk-parks); there is also a `timeline`. Each section ends with
  self-check questions (`details`/`summary`), an "I've learnt this" tick and a
  link to a SmartEn quiz. There are five quizzes, from `tools/ojaj/ojaj_uk.py`:
  `ojaj_uk_symbole` also serves the nations section, and `ojaj_uk_londyn`
  also serves the parks section. So for the culture types the material
  exists; what is missing is a link from the weak-points list to the section.
- For the other 24 types there is no explanation anywhere in the app.
  Exercises hold items and keys only (the only renderer that shows an
  `explanation` is the true/false/no-information one). Practice for these
  types does exist: the OJAJ exercises for word formation, wisielec,
  transformations, grammar, idioms and phrasal verbs (`exercises` in
  `pub/konkursy/angielski/data/ojaj/index.json`), the Quest track "Spelling
  and word building", and the kuratoryjny practice sets.
- `exactSpelling: true` on a task turns off the one-letter allowance
  (`site/src/lib/scoring.js`); the Quest spelling sets use it. Any spelling
  practice for double letters, silent letters or vowels needs it, or the one
  letter the exercise is about gets forgiven.
- Own exercise sets are written in `tools/ojaj/ojaj_own.py` (wisielec and
  transformations; its docstring holds the writing rules) and
  `tools/ojaj/ojaj_uk.py` (culture). `tools/ojaj/gen_ojaj.py` writes and checks them.

## Traps

- Practice exercises use up words. `existing_items()` in
  `tools/ojaj/ojaj_online.py` refuses an online item whose prompt, word-formation
  or wisielec word, or key word with answer already appears in any JSON under
  `pub/` (outside `ojaj/online/`). So a practice exercise that reuses an item
  from Tests 01-03 makes those tests fail their check, and every word a new
  practice exercise uses can no longer go into the new batches of online items
  (step 4 of the build handoff). HTML pages are not scanned, so a study page
  can quote his misses and any other examples.
- Two sessions, one checkout. The build session will also work in
  `smarten-vault`, and both may touch `OjajHome.jsx`, `CLAUDE.md`,
  `ojaj/index.json` and `ojaj_online.py`. If the two run at the same time,
  give this one its own worktree (ask Lukasz first). Two things to know about
  that:
  - `tmp/` is untracked, and only smarten-vault's `tmp/` has
    `ojaj_online.py` (main's `tmp/` has no such file). A new worktree starts
    with none of the scripts, and copies of them drift apart.
  - The data symlink `site/public/konkursy/angielski/data` points at the main
    checkout's `pub/` in every checkout. A dev server in any worktree shows
    main's data, not exercise JSON newly written in that worktree.
- The type keys connect this work to the build. If the section ids on new
  pages are the type keys, the weak-points list can link to `page#key`.
  Renaming a type means changing both.

## Suggested questions for the design interview

Suggestions only, in a workable order, each with my recommendation.

1. What the material is: pages that explain (the rule, worked examples, a
   self-check), practice exercises, or both. Recommend pages first: they can
   use his own misses as examples and use up no words. Add practice sets only
   where a page alone will not do, such as spelling.
2. Which types come before 16.11. Recommend, from the evidence above:
   - the transformation checklist;
   - base-change;
   - adding an ending (the e kept or dropped, doubled consonants:
     suffix-spelling and double-letters together);
   - unstressed vowels and silent letters;
   - the in-/un-/ir- choice;
   - for culture, only links into the notebook.
   The 10 types with no miss yet can wait.
3. One page per group or one per type. Recommend one page per group in the
   notebook's style, as static HTML in `site/public`: a words page (the 10
   types of tasks 1-2), a transformations and grammar page (the checklist and
   the 11 grammar types), perhaps a vocabulary page. Each section's id is its
   type key.
4. Language. The notebook is in English and the OJAJ screens are in Polish
   without diacritics. Rules written for a Polish primary-school pupil may
   work better in Polish, with English examples. Ask; the evidence does not
   settle this one.
5. How he gets to the pages. Recommend a card on the OJAJ page next to the
   notebook's, plus links from the weak-points list (step 9 of the build).
   One way to keep each link next to its type: add a link column to
   `_TYPE_ROWS` (e.g. `ojaj_uk#parliament` for uk-politics), so that the type
   list the build writes carries it. That is a file the build session edits
   too, so agree who adds it.
6. Self-check and tracking. Recommend copying the notebook: `details` and
   `summary` questions and the "I've learnt this" tick (kept in local storage
   only).
7. Examples. His own misses (he has seen those items, and they will come back
   as repeats anyway) plus common words of the same pattern at B2-C1 that suit
   a primary-school pupil. Recommend making his miss the first example in each
   section.
8. Practice sets, if any: own items with titles that say so ("zadania
   wlasne"), a group heading on the OJAJ page, `exactSpelling` on spelling
   tasks, and an agreed list of words kept back for the new online batches.

## Helper files

- `tmp/_types_missed.mjs` (new, kept): lists his online misses with their
  types and counts missed/answered per type. Run
  `node tmp/_types_missed.mjs tmp/_results_Tadzio_2026-10-25.json`. It reads
  the types from the review printout, because the JSON in `pub/` has none yet.
- `tmp/_results_Tadzio_2026-10-25.json`: his results as downloaded on
  2026-10-25 (365 attempts).
- `tools/ojaj/scan_mistakes.mjs`: re-marks all his saved answers, per task type
  (his practice history).
- `tools/ojaj/find_phrase.py`, `tools/ojaj/dump_prompts.py`: check whether a word or
  phrase is already in the app.
- `tools/ojaj/val_ojaj.mjs`, `tools/ojaj/render_ojaj.sh`, `tools/ojaj/audit_ojaj.py`: the checks
  for any new OJAJ exercise.

## Rules carried over

- No commit, push or deploy unless Lukasz asks, and no Co-Authored-By line.
- Run `/verify` right before a commit, and check `git branch --show-current`
  first.
- Lukasz deploys himself.
- Never install a package without asking. Ask before deleting anything.
- Temp scripts are `tmp/_*.py` files made with the Write tool, run, then
  removed.
- Code is written test-first (`node:test`, `npm test` in `site/`).
- Keys stay strict. Content must suit a primary-school pupil.
- Polish on screens without diacritics, as on the OJAJ page; exercise
  instructions in ASCII.
