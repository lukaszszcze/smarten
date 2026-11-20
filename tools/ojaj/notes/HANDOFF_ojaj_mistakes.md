# Handoff: build the mistake record into the OJAJ online tests

Rewritten 2026-10-25 at the end of the design session, for a fresh session.
The design is settled and step 1 is done and approved; start at step 2, the
build. Read first, in the worktree `/home/lukasz/workspace/smarten-vault`
(branch `ojaj-online-vault`, level with `main` at 8266f80): this file,
`CONTEXT.md`, and `tools/ojaj/notes/HANDOFF_ojaj_online_vault.md` (item-writing rules,
level profile, how the player and the draw work today). Check
`git branch --show-current` and `git log -1` before anything else; Lukasz may
have moved `main` on.

## The request

Lukasz, verbatim: "let's keep record of the mistakes he makes. I want to put
them back to him again in subsequent test. E.g. we could have a pool of
questions and draw them according to the frequency of 1. the particular
mistake and 2. the type of the mistake (like the -ance/-ence)."

## Where things stand

- Live at https://smarten.pages.dev: three fixed online tests (01-03, OJAJ
  etap I, czesc II rehearsal, 45 items, 45 min), drawn by "Losuj test",
  unseen first. Real test: 16.11.2026, mazowieckie 09:00-09:45.
- Tadzio's online attempts (no other user has any):

  | Test | When (local) | Score | attemptId |
  |---|---|---|---|
  | 02 | 2026-10-24 13:28 | 32/45 (WF 5, WS 7, TR 7, MC 10, UK 3) | `e8c8507a-6b54-4130-9259-e8d467484946` |
  | 01 | 2026-10-24 19:07 | 26/45 (WF 2, WS 9, TR 5, MC 10, UK 0) | `1eb9fbea-082d-4a5c-aa4e-0cb5718dfdf3` |

- So only Test 03's 45 items are unseen by him. If he takes Test 03 before
  the release, the store has no unseen item left, and the first batch of new
  items has to go out with the build. Ask Lukasz whether he plans to.
- Attempts hold `answers` keyed by question number "1"-"45" and
  `taskBreakdown` (points per task), not per-item verdicts. Every verdict of
  both attempts can still be recovered: the strict keys re-mark word
  formation, wisielec, choice and culture; for transformations, the answers
  that match a listed phrasing are exactly the task's points in both
  attempts, so the AI marked the rest wrong (Test 02: 22, 26, 29; Test 01: 21,
  23, 24, 27, 28).
- Culture options are shown in a fixed order and the clicked letter is saved
  (`KnowledgeQuestions.jsx`), so Test 01's 0/5 is what he chose; it looked
  like guessing, but attempts do not record time taken.
- Step 1 done, approved 2026-10-25: `tools/ojaj/ojaj_online.py` holds
  `MISTAKE_TYPES` (31 types), every row of Tests 01-03 ends with its type,
  `build_test` puts it on each item as `mistakeType`, `check_types` checks
  it, and the selftest catches five new cases. Running the file writes the
  approved printout `tmp/ojaj_mistake_types_review.md`. 01/27 (BLAME) gained
  focus "collocation"; 01/8 (unforgettable) is double-letters. The JSON in
  `pub/` has not been regenerated.
- Backup of Tadzio's results from 2026-10-24, before the stray-attempt
  delete: `tmp/_backup_results_Tadzio_2026-10-24.json` (365 attempts; the
  live list has since gained Test 01).
- Danger: before 8266f80 a DELETE to `/api/results` ignored `attemptId` and
  cleared every result of the user. 8266f80 is live (checked with
  `npx wrangler pages deployment list --project-name smarten`); check again
  before any delete.
- Lukasz deploys himself: the session's permission check refuses the deploy
  command. The data symlink in `site/public` points at the main checkout's
  `pub/`, so builds for deploy run from main after the merge.

## Status 2026-10-25: step 2 live

Committed as 36a2341 on `ojaj-online-vault`, fast-forwarded into main, pushed
to GitHub and deployed (Lukasz asked for all three), before the study pages.
So the vault carries a study page link only once its file is in
`site/public/ojaj_study/` (`vault_link`, with selftest cases); live today are
the 7 UK notebook links. After the study pages merge into main: bring this
worktree up to main, re-run `gen_ojaj.py`, commit `online/vault.json`.
Test 03 was not taken before the release (no answer to the question below).
Next: step 4, the batches.

Checks at the commit, all passing: `npm test` (173), `npm run
build`, `ojaj_online.py` and its selftest, `gen_ojaj.py`, `val_ojaj.mjs`,
`render_ojaj.sh`, `audit_ojaj.py`, `e2e_online.mjs` (three drawn tests in a
row, at 1280 and 390 wide).

- `site/src/lib/ojajRecord.js`: `missType` (the 13 cases above are tests),
  `attemptVerdicts` (saved, or re-marked for old 01/02), `mistakeRecord`,
  `typeShare`, `weakTypes`. `ojajDraw.js`: `drawTest`, `assembleTest`.
  `ojajOnline.js`: `DRAWN_TEST_ID` (`ojaj/online/drawn`), `ONLINE_VAULT_PATH`,
  `items` in the attempt, `newQuestionScore`; the fixed-test functions are
  gone. All three at 100% line and branch coverage.
- Data: `online/vault.json` (135 items, task `count`/`levels`/`focus`, 31
  types with label and link); `online/01-03.json` deleted; the index's
  `online` list removed. `ojaj_online.py`: `LEVEL_RANGE`, `FOCUS_RANGE`,
  `build_vault`, `check_links`; `_TYPE_ROWS` has a fifth field, link, with
  the values from `tools/ojaj/notes/HANDOFF_ojaj_learning_material.md` (asked for by the
  learning-material session, with Lukasz's OK).
- On his live record (2 attempts): both re-mark to their saved scores (32,
  26), 32 items wait, 21 weak types; every draw holds 7 repeats (2+2+2+0+1).

Calls made in the build, beyond the sketch:
- The player draws its own test when it opens (sync, vault, record, draw); no
  draw is kept in local storage, so a reload draws a new test. The answers are
  lost on a reload anyway.
- The fill is tiered: a seen item only when the unseen ones cannot complete
  the task's profile (one search over everything picked seen items early).
- The review marks every item seen before, not only same-item repeats, and
  shows the repeats' score beside the score on new questions.
- Weak types: top 6, "Pokaz wszystkie" for the rest; the share as a bar, the
  counts as text ("bledy 3 z 3 · 3 do powtorki"), "Czytaj" link.
- `/ojaj/online/:id` (old fixed-test address) redirects to `/ojaj`.

Open:
- Ask Lukasz whether Tadzio takes Test 03 before the release: once released
  it can no longer be taken on its own, and if he does take it, all 135 items
  are seen and tests fall back to the least seen until batch 04 exists.
- `check.js` compares a transformation key "a / b" as one string, so the 20 of
  30 online transformations with several phrasings always go to the AI, whose
  prompt says to be lenient with spelling. Not changed; worth a fix.

## Decisions

Settled with Lukasz one question at a time on 2026-10-24 and 2026-10-25. Do
not reopen them unless the code proves one impossible.

| Topic | Decision |
|---|---|
| Where repeats go | Every online test is put together at the draw from a store of single own items. Per task, a few slots go to repeats, the rest to items he has not seen, keeping the level profile and the idiom/collocation/phrasal verb counts. Fixed tests go away; the 135 items of Tests 01-03 join the store, and Tests 04-10 are written as batches of 45 items |
| What a repeat is | Same item: an item he missed comes back word for word, from the next test on. Same type: an unseen item of a type he misses |
| Mistake types | One type per item, from the closed list in `ojaj_online.py`, shared across tasks; set when the item is written. Approved as drafted |
| Type of a miss | A typed miss in word formation or wisielec takes its type from his answer compared with the key, first rule that matches: prefix differs; -ance/-ence; -able/-ible; base word left unchanged; an e kept or dropped, or y to i, at an ending; a letter doubled or not (neighbouring letters); only vowels differ. No rule matches, or a blank: the item's own type. Transformations, choice and culture always use the item's type. Items are still drawn by their own type |
| What counts | Any item not marked correct is one miss, typed or blank alike |
| Cap | Tasks 1-4: at most 3 repeats each, at most 2 of them same-item. Task 5: 1 slot, a missed culture question first, an unseen question of a weak branch only when none is waiting. At most 13 of 45. A slot with no candidate goes to an unseen item |
| Weights | Same item: among items whose latest answer was wrong, chance proportional to how many times he has missed it; one right answer takes it off the list. Same type: among unseen items, chance proportional to the type's share, wrong / (answered + 1), so one miss counts 50%, 3 of 3 counts 75%, 10 of 10 counts 91%; a type with no miss is never targeted |
| UK culture | The seven mind-map branches stay as separate types, mainly so the weak-points list says which section of his UK notebook to reread. With 7 culture misses waiting and one slot per test, branch-based picks will be rare before 16.11 |
| Where the record lives | Worked out from the attempts each time; no new storage. Each online attempt saves which items it held and the verdict on each |
| Scope | Online tests only. His practice history only steers which types the new batches lean towards |
| Visibility | Nothing marked during the test. The review marks each same-item repeat "powtorka" and shows, next to the total, the score on new questions (everything he had not seen, type-targeted items included). The OJAJ page lists his weak types with their share and how many items wait to come back, without the words |
| Release order | Step 2 the build (test-first, per-item results first, released together with the rest, not on their own); step 3 one release with the store; step 4 batches of 45 new items leaning on his weak types, each approved |

Calls Claude made without asking, not overruled so far: a miss whose type
comes from the answer counts as one wrong answer for that type and nothing
for the item's own type; repeats count towards the level profile, and a
repeat that would break a level quota is skipped; the weak-points list shows
types and counts, not words.

## Test cases for the miss-type rules

His 13 typed misses in word formation and wisielec, with the type the rules
should give (worked by hand; the rule order matters, e.g. unrecogniseable
also differs only in a vowel, and must stop at the e rule first):

| Test/question | He wrote | Key | Item's type | Rules give |
|---|---|---|---|---|
| 02/1 | resemblence | resemblance | ance-ence | ance-ence |
| 02/3 | unaccessible | inaccessible | negative-prefix | negative-prefix |
| 02/4 | pronounciation | pronunciation | base-change | base-change (pronounc- kept) |
| 02/10 | knowledgable | knowledgeable | suffix-spelling | suffix-spelling |
| 02/14 | mischevious | mischievous | vowels | vowels |
| 01/1 | unrecogniseable | unrecognisable | negative-prefix | suffix-spelling |
| 01/3 | speachless | speechless | base-change | vowels |
| 01/4 | emberrassment | embarrassment | double-letters | vowels |
| 01/5 | irrepairable | irreparable | negative-prefix | base-change (repair kept) |
| 01/6 | childlish | childish | word-ending | no rule, so word-ending |
| 01/7 | indecidous | indecisive | negative-prefix | base-change (decid- kept) |
| 01/8 | unforgetable | unforgettable | double-letters | double-letters |
| 01/10 | accidentaly | accidentally | suffix-spelling | double-letters |

## Step 2, the build: a suggested plan

A sketch, not decisions; change it where the code argues otherwise and say so.
Tests first (`node:test`, `npm test` in `site/`); `Math.random` mocked with
`t.mock.method`, no arguments that only tests would pass.

1. Per-item results in the attempt. `onlineAttempt` in
   `site/src/lib/ojajOnline.js` saves the store ids the test held and, per
   item, the verdict from `result.tasks[].items[]` (`markWithAi` merges the
   AI's items into the task results, so transformations carry them too).
2. The store. Stable item ids that keep the two existing attempts readable,
   e.g. `01-23` for Test 01 question 23. `gen_ojaj.py` writes the store and
   the type list (key and Polish label) from `ojaj_online.py`; where they
   live under `pub/.../ojaj/online/` is open.
3. Old attempts (no saved verdicts): re-mark from the key; a transformation
   that matches no listed phrasing counts wrong when the task's points equal
   the number of matching answers (true for both), otherwise it is left out.
4. The record, as pure functions: per item, misses and the latest verdict; per
   type, answers and misses with the miss-type rules and the damping.
5. The miss-type rules, with the table above as cases.
6. The draw: puts a test together from the store and his attempts, per the
   Cap and Weights rows; then unseen items, then least seen; the level
   profile and focus counts as `check_profile` in `ojaj_online.py` checks
   them; no answer word twice in one test.
7. The player. Today it loads `online/NN.json`; it gets the drawn test
   instead. Keeping the drawn item list in local storage until submit would
   let a reload resume the same test. Online attempts are recognised by the
   `ojaj/online/` testId prefix (`isOnlineAttempt`, `onlineAttemptLabel`,
   `doneCounts`), so a drawn test needs a testId under it and a history label
   (rows stay unlinked).
8. The review: the "powtorka" mark and the score on new questions.
9. The OJAJ page: the weak-points list, and a count of unseen items in place
   of "x z 10".
10. The checks: `gen_ojaj.py`, `tools/ojaj/val_ojaj.mjs`, `tools/ojaj/render_ojaj.sh`,
    `tools/ojaj/audit_ojaj.py`, `tools/ojaj/e2e_online.mjs`, `npm test`, `npm run build`.
11. Docs: `CLAUDE.md` (OJAJ section, data format), `CONTEXT.md` (the vault
    becomes the set of own items tests are put together from; add mistake
    type and repeat; "pool" stays taken), the `gen_ojaj.py` docstring.
12. Stop: show Lukasz, then ask about /verify, commit, merge into main. He
    deploys from main.

## Step 4, the batches

Status 2026-10-31: batches 04 and 05 (T04, T05 in `ojaj_online.py`, 225
items in the vault) approved by Lukasz, committed as 347b9b0, with b6dfc08
before it (check.js splits " / " keys, so a listed phrasing scores without
the AI; check.js's first tests). 03-29 now accepts "than anyone on". Main
fast-forwarded and pushed to GitHub; `e2e_online.mjs` passes from main.
Deploy left to Lukasz. Weighting came from his record that day: he had seen
all 135 items by 28.10 (7 drawn tests, 29 -> 43 of 45, about 60% on items new
to him); base-change 13/19 wrong, vowels 11/24, double-letters 9/21,
uk-politics 5/12, comparison 4/10, suffix-spelling 4/11, collocation 11/36.
Next: batch 06 onwards. One batch is about one fresh test, and he takes
about one a day until 16.11.

Status 2026-10-31, later: batches 06 and 07 written (`T06`, `T07`, in
`TESTS`), 315 items in the worktree's `vault.json`, not committed. His
record had not moved (last online test 30.10, before 04-05 went live), so
the lean is the same as 04-05's, plus word-ending and two-steps, which 04-05
left out. Every check passes; printouts `tmp/ojaj_online_06_review.md` and
`_07_review.md` wait for Lukasz. New: `tools/ojaj/near_repeat.py 06 07` lists
items that share most of their content words with an existing one, and
vault answers printed in another vault item. Run on 04-05 it finds items
already committed that repeat 01-03 or the app nearly word for word: 04/34
= 01/35 (fire alarm, maths test), 04/38 = 01/40 (Should you need any help),
05/39 = quest_grammar_04 1.1 (this book for weeks), 05/40 ~ 01/23 (two
older brothers, both of whom), 04/19 ~ 02/33 (came across old photos while
tidying), 04/30 ~ 03/36 (got home, realised I had lost); and give-aways:
05/18 prints "broke" (03/13's answer), 02/33 prints "across" (04/19's).
Reported to Lukasz, not changed.

Later on 2026-10-31: 04-05 deployed (production 347b9b0). He then submitted a
test after answering 5 of 45 (11:24, attempt 7ff3ab94-0936-4561-b370-6741c9076de7,
5/45): its 40 blanks count as misses, so 30 items he knows wait to come back
(50 waiting against 20 without it). Lukasz approved, and the attempt was
deleted the same day (379 attempts left, 20 waiting). Then a full test (11:34, 31/45, 36 items from 04-05); results saved as
tmp/tadzio_results_2026-10-31b.json. He has now seen 05/39 and 05/40 (both
right), so leave those; 04/19, 04/30, 04/34, 04/38 and 05/18 are still unseen.

Also 2026-10-31: Tadzio said the wisielec patterns give too many letters. They
did: 44-52% of the letters in 01-03 and about 70% in 04-07, against 22-33% in
the published papers. All 70 patterns now give the papers' number for the
word's length (`given_letters` in `ojaj_online.py`: 1 up to 5 letters, 2 for
6-8, 3 for 9-12, 4 from 13), taken from the letters already given so the
tested spelling stays hidden; `check_given_letters` refuses any other number,
and the selftest has both cases. Four picked by hand because another word fit
the sentence too (properly cold, very little, show any conclusions, burnt
down). With 06-07, 04/38 replaced ("But for"; it tested 01/40's point) and
05/18 printing "lost" instead of "broke": committed 922dde0, main
fast-forwarded and pushed, e2e passes; Lukasz deploys. 04/19, 04/30, 04/34
stay: he had seen them (12:48 test, 35/45) before they could be replaced.

Status 2026-11-02: 06-07 were live by 1.11, when he took four tests (13, 29,
33, 40 of 45) and had then seen all 315 items. The 9:29 one (attempt
272762b6-2a68-48aa-95b2-a8a468ad7dff, 13/45) was left after about 23
questions: 25 blanks, all of 24-45, so 20 items count as seen only through
it. Not deleted; asked Lukasz. Batches 08 and 09 (`T08`, `T09`) written
from his record without that attempt
(`tmp/tadzio_results_2026-11-02_noabandon.json`): uk-politics 52%,
base-change 50%, vowels 48%, suffix-spelling 39%, uk-people 36%,
double-letters 35%, uk-parks 30%. Every check passes, `vault.json`
regenerated in the worktree (405 items; the 315 old ones unchanged), npm
test passes; printouts `tmp/ojaj_online_08_review.md` and `_09_review.md`.
Approved the same day; committed as 485364d, main fast-forwarded locally,
e2e passes from main (405 items served). The push to GitHub was refused by
the session's permission check, so Lukasz pushes and deploys. `near_repeat.py` is clean except three
loose matches kept on purpose (08/41 and 03/42 share devolution options;
08/44 asks 1637 where ojaj_uk_londyn 1.6 asks 1536; 09/7 shares "festival
takes place"). Found taken while writing 08-09, on top of the list below:
regret + -ing, apart from, had I known, had it not been for, accused of,
not only (inversion), must have left, little did, looking forward to,
narrow escape, reminded us to, feel like, admitted, warmer and warmer,
keen on, no point, in spite of, due to, even though, unless, warned,
asked me whether, having finished, have something repaired, the first
time + perfect, despite being, so that (04/37), at no time, besides,
of whom, as if, needn't, don't have to bring, will have started, had
been waiting, storm in a teacup, early bird. Words a new item must not
print, because another vault item asks for their spelling: weather,
broke, across, fast, flight, tomorrow, crystal, medicine, moon, tongue,
wide, chew (the script's leak list finds them).

Status 2026-11-02, later: Lukasz pushed main (485364d) and asked for
batches 10 and 11. His record had not moved (no test since 1.11; 08-09 not
yet seen), so `T10` and `T11` keep 08-09's lean and give more room to
verb-patterns, linking-words, silent-letters and inversion. Every check
passes, `vault.json` regenerated in the worktree (495 items; the 405 old ones
unchanged), npm test passes; printouts `tmp/ojaj_online_10_review.md` and
`_11_review.md`. Lukasz then said "deploy all": committed as 1ce5973, main
fast-forwarded and pushed, e2e passes (495 served), and 08-11 deployed to
production the same day (deployment e4a7ccfa, `--branch main`). Built from
this worktree, not from main, because main has an uncommitted OjajHome.jsx
change (coloured weak-point bars and a key) that Lukasz chose to keep off
the site for now; the page code deployed is the same as before (the build
produced the same script file name, index-v4IHA4CN.js). `near_repeat.py 10 11`
shows no give-aways; five loose matches kept on purpose (10/41 on devolution
shares names with ojaj_uk_parlament 1.10 and 07/42 but asks the year; 10/44
shares king names with 08/44, 03/45 and ojaj_uk_londyn 1.6; 11/43 asks a
birthplace like ojaj_uk_postacie 1.8, about Pankhurst, without Edinburgh in
the options). Found taken while writing 10-11, on top of the lists here:
such ... that, can't / cannot be (deduction), wish + would, prevented from,
avoid + -ing, remember + -ing, ought to see, if I had known, not only ... but
also, Nowhere will you find, burst into tears, flying colours (printed in
the vault), spill the beans, let me stay up, heavy traffic, if only + past,
as soon as, fewer, get over, managed to, didn't mean to (printed in the
vault), fish out of water, as far as, what time I (reported), been able to.
Answer words already in the app: curiosity, height, maintenance,
irresponsible, explanation, strength, courageous, horrible, generosity,
temperature, jealous, muscle, receipt, applause, magnificent, dessert,
colleague, and the other `cand_words.py` hits.

Status 2026-11-11: by 10.11 he had seen all 495 items (tests daily 7-10.11;
results `tmp/tadzio_results_2026-11-11.json`). Lukasz asked for wisielec
exercises "i do banku": 50 vault items and 5 practice exercises of 10 (his
choice of size). Written, every check passes, nothing committed:
- `ojaj_online.py` takes a batch of wisielec alone (`{"hangman": [...]}`,
  `build_hangman_batch`, ids 11-20, checked as task 2; `build_vault` puts its
  items in task 2). `T12`-`T16` are five such batches; the vault grows to 545
  (task 2: 160), the 495 old items unchanged. The selftest has the new cases.
- `ojaj_own.py` `HANGMAN_3`-`HANGMAN_7` (`HANGMAN_ONLINE`): wisielec (3)-(7),
  rows in the vault's 7-tuple form, written in the online test's shape;
  `ojaj_online.check_own_exercises` holds them to the vault's rules and keeps
  their words out of the vault and the app. 67 practice exercises.
- `val_ojaj.mjs` accepts a wisielec-only batch; `wisielec_letters.py own`
  covers the practice sets. Printouts `tmp/ojaj_online_12_review.md`-`_16_` and
  `tmp/ojaj_own_wisielec_review.md`.
- Lean: vowels, double letters, silent letters (his worst spelling types), 3
  idiom / collocation / phrasal-verb items per 10. With his record each drawn
  test now gets 8 new wisielec items of 10.
- Another session worked in parallel on an inversion study page: in main it
  left `CLAUDE.md`, `vault.json` (inversion link), `ojaj_study/index.html`
  modified and `inversion.html` untracked, and it set the inversion link in
  this worktree's `ojaj_online.py`. A fast-forward of main onto a commit here
  is refused while main has those files modified; the vault has to be
  regenerated where the inversion page exists, or the inversion type loses
  its link again.
- Later the same day, on "commit and deploy": the other session had committed
  the inversion page on main (e12e70f) and deployed it. This branch's commit
  was moved onto it (668af11), the data regenerated there unchanged (inversion
  link kept), main fast-forwarded, e2e passes (545 served), deployed to
  production (6675b6a2, data only; same script file as before). Main pushed to
  GitHub the same day.

Status 2026-11-11, later: Lukasz asked for "100 nowych zadan", to the vault,
split by his weak types, reviewed all at once. Results fetched again
(`tmp/tadzio_results_2026-11-11b.json`, 4 more tests that morning, 39-43 of
45); his record without the three tests he left early (13, 14, 16 of 45):
uk-politics 44%, uk-parks 39%, vowels 36%, base-change 35%, uk-people 30%,
suffix-spelling 28%, inversion 28%. Written, every check passes, nothing
committed:
- `ojaj_online.py` takes a batch of any one task alone
  (`build_one_task_batch`, `one_task_kind`, `TASK_OF`, `check_task`; the
  wisielec batch is now one case of it). Old batches build byte-identical
  (vault and printouts compared). Selftest has 4 passing and 10 refused cases
  for the new batches. `val_ojaj.mjs` accepts one task alone;
  `wisielec_letters.py` skips batches with no wisielec.
- `T17`-`T29`: word formation 17-19 (30), transformations 20-21 (20), choice
  22-23 (20), culture 24-29 (30). Agreed split was 30/25/20/25, but a
  transformation batch must hold 10 (profile per 10), so 5 moved to culture,
  his weakest task. Vault 645 (140, 160, 130, 130, 85); the 545 old items
  unchanged.
- `near_repeat.py 17 ... 29` clean of leaks; near matches left on purpose:
  24/42 (Lord Speaker) against 07/41 (Speaker), 26/42 (Senedd) against 03/42,
  28/41 shares Prime Minister names with 04/44 and 05/42, 26/45 (13,000
  houses) shares "Great Fire" with 08/45. Replaced while writing: a piece of
  cake, the dialogue_024 1.3 idiom, sore throat (own wisielec 03), Big Ben
  (knowledge_022), in the event of (transform_030), fingers crossed (06/20),
  the last straw (05/18), red-handed and might have caught (print "caught"),
  and answer words printed elsewhere: hungry, angry, relief, behaviour, Welsh.
- New helpers: `list_vault.py 3|4` (the vault's transformations or choice
  items, one line each), `list_culture.py` (every culture question asked),
  `draw_sim.mjs <results> [tests]` (new items per task in his next tests).
  With his record: new word formation lasts about 4 tests, transformations and
  choice about 3, culture about 7, wisielec about 5.
- Printout for Lukasz: `tmp/ojaj_online_17-29_review.md` (the 13 batch
  printouts joined). Accepted the same day: `/verify` READY, committed as
  95308d0, main fast-forwarded (its uncommitted OjajHome.jsx left alone), e2e
  passes from main with 645 items served. On "1": main pushed to GitHub and
  deployed to production from this worktree (b0fba3ab, `--branch main`, data
  only; same script file index-v4IHA4CN.js), the live vault serves 645.

Next, agreed 2026-11-11 for a new session: a second round of transformations
and choice, 20 each, as batches 30-31 (transformations) and 32-33 (choice),
written like 20-23. By `draw_sim.mjs` the new ones in those two tasks run out
around 13.11, so they should be live by the evening of 12.11. Fetch his
results again first and weight towards his weak types in those two tasks.
Before writing, read `list_vault.py 3` and `list_vault.py 4` for what is
taken (20-23 included). Same flow as 17-29: printout to review, then on
approval `/verify`, commit, fast-forward main, e2e, push and deploy from
this worktree. Still open separately: the three tests he left early (1.11,
7.11, 8.11) and whether to delete them; ask first, and check the DELETE
on `/api/results` before using it.

Status 2026-11-11, evening: batches 30-33 written (`T30`-`T33`, in
`TESTS`), nothing committed. His results fetched again were identical to
`tadzio_results_2026-11-11b.json` (no test since the morning), so the record
is the `_noabandon` one. New helper `node tools/ojaj/rec_task.mjs <results>` prints
his record per mistake type within transformations and within choice, with
every miss (the types are shared across tasks, so `record_now.mjs` mixes
them). Transformations: inversion 5/15, collocation 8/33, modals 3/14, idiom
2/9, comparison 7/35, verb patterns 5/25; choice: inversion 3/13,
conditionals 5/24, linking words 2/15, collocation 4/34, relative clauses
2/21. His choice misses have a pattern: "would have been" for "would be" in
mixed conditionals, "Without"/"Unless" for "But for", "what" for "that", and
the wrong verb form after a correct inverted opening. The 40 items lean on
those. Vault 685 (140, 160, 150, 150, 85), the 645 old items unchanged; every
check passes (`ojaj_online.py` and selftest, `gen_ojaj.py`, `val_ojaj.mjs`,
`audit_ojaj.py`, `render_ojaj.sh`, npm test 175). `near_repeat.py 30 31 32
33` clean except 32/35 against 03/34 (function words only). `draw_sim.mjs`:
new transformations and choice now last about 5 tests. New helper
`python3 -I tools/ojaj/kw_check.py KEYWORD ...` lists every transformation in the
app with that keyword. Printout `tmp/ojaj_online_30-33_review.md`. Found
taken or leaking while writing: "Only after ... did" and "Only then" and
"Hardly ever" (grammar_016), "rings a bell" (2020-21 szkolny 3.3), "pain in
the neck" (2020-21 rejonowy), "is capable of doing" (ojaj_2324 transformacje),
"unless" and "if it hadn't been for" (many), helmet (transform_006), lost keys
(04-30, quest_grammar_07); vault answers that must not be printed: fuss,
slim, narrow, potato, teeth, vegetable, bitterly. Accepted the same evening
("1"): `/verify` READY, committed as d4e1033, main fast-forwarded (its
uncommitted OjajHome.jsx left alone), e2e passes (685 served), main pushed,
deployed from this worktree (6247f438, `--branch main`, data only; same
script file index-v4IHA4CN.js); the live vault serves 685. Still open: the
three tests he left early.

Status 2026-11-15: Lukasz asked for 120 new items in the pool, the day
before the real test (16.11, 9:00). Results fetched
(`tmp/tadzio_results_2026-11-15.json`, 35 online attempts, last two that
day 38 and 42 of 45); he had seen all 685. Split by his last eight tests
(12-15.11, `node tools/ojaj/task_acc.mjs <results> 2026-11-12` prints the share
wrong per task): wisielec 26% -> 30 items, transformations 24% -> 30, word
formation 11% -> 20, choice 5% -> 20, culture 13% -> 20. Written as
`T34`-`T47`, every check passes, nothing committed:
- word formation 34-35, wisielec 36-38, transformations 39-41, choice
  42-43, culture 44-47 (5 each). Vault 805 (160, 190, 180, 170, 105); the
  685 old items unchanged (`node tools/ojaj/cmp_vault.mjs <old vault.json>`
  compares). `gen_ojaj.py`, `val_ojaj.mjs`, `audit_ojaj.py`,
  `render_ojaj.sh`, selftest and npm test (175) pass.
- Every inversion transformation fixes the opening word in the stem
  ("Barely {} at the table", keyword DOWN), so a plain word order cannot fit;
  30-21 and 20-26 do not do this, and "The puzzle was so difficult" or "We had
  scarcely got" would fit there and go to the AI.
- `near_repeat.py 34 ... 47` clean except 'parliament' (04/12's answer) in
  the culture questions 44/41 and 46/42, which cannot avoid the word; the
  older culture items print it too. Replaced while writing because the word
  was taken in the app or printed in the vault: 20 first candidates (see
  `python3 -I tools/ojaj/printed.py word ...`, which shows both), caught (08/19),
  pigeon (10/13), opposite (14/15), fast (06/19), draw (07/18), and
  Downing Street (knowledge_022, 026).
- `draw_sim.mjs`: his next two tests almost all new in every task; new
  wisielec and transformations last about 4 tests, culture about 5.
- Printout `tmp/ojaj_online_34-47_review.md`.
- Keys worth a look, from his misses: 31-22 "in an emergency may you open"
  (three times; the key has only "use"), 20-30 "As much as I like" (twice).
- Accepted the same day ("1 i 2"): both keys widened (31-22 "... open",
  20-30 "As much as I ..."); his past verdicts on them stay misses, so both
  still come back once. `/verify` READY, committed as a8b2681, main
  fast-forwarded (its uncommitted OjajHome.jsx left alone) and pushed, e2e
  passes, deployed from this worktree (312f6b8e, `--branch main`, data only;
  same script file index-v4IHA4CN.js); the live vault serves 805.

Status 2026-11-15, evening: Lukasz asked for "another batch"; read as another
120 in the same split. Results refetched (`tmp/tadzio_results_2026-11-15b.json`):
three more tests that afternoon (42, 44, 45 of 45), all before the 34-47
deploy went live (15:57 UTC, his last test 15:51), so he has seen none of
34-47 and nothing waits to come back. Written as `T48`-`T61`, every check
passes, nothing committed:
- word formation 48-49, wisielec 50-52, transformations 53-55, choice
  56-57, culture 58-61 (5 each). Vault 925 (180, 220, 210, 190, 125); the
  805 old items unchanged (`git diff --patience` shows insertions only).
  `gen_ojaj.py`, `val_ojaj.mjs`, `audit_ojaj.py`, `render_ojaj.sh`,
  selftest and npm test (175) pass.
- The common transformation and choice points are nearly all used by now.
  `python3 -I tools/ojaj/tr_points.py "phrase" ...` checks a point against every
  item in the app and the vault with each blank filled in from its key, so a
  phrase split by the blank of a choice or wisielec item is found too
  (`find_phrase.py` misses those). About half the first candidates were taken that way (not once, on
  no account, under no circumstances, in charge of, nobody ... did they,
  half as big as, fast asleep, show off, figure out, ...).
- `python3 -I tools/ojaj/free_words.py word ...` checks answer words against the
  app's and the vault's answers and the vault's printed text in one go;
  `python3 -I tools/ojaj/culture_asked.py [word]` lists every culture question
  asked, with its key; `node tools/ojaj/last_attempts.mjs <results> [n]` lists his
  last tests with their misses; `python3 -I tools/ojaj/keys_of.py NN ...` prints
  each choice and culture key with its option text.
- Culture options are shown in the written order (only task 4 shuffles), so
  the keys were spread over A-D and three distractor sets lengthened where
  the answer was clearly the longest.
- `near_repeat.py 48 ... 61` clean except 'parliament' in 59/41 and 60/41
  (as before). Replaced while checking: wrinkles (crinkles fits the pattern),
  "people knelt" (now "can't kneel"), mile (03/5 prints "miles"), the FEAR
  item (04/37 is the same train sentence), and sentences printing weather,
  queue, broken, dictionary, runner.
- `draw_sim.mjs`: with 34-61 unseen his next four tests are all new in every
  task; wisielec and transformations stay new for about six, culture eight.
- Printout `tmp/ojaj_online_48-61_review.md`.
- On "ok, commit and deploy" the same evening: `/verify` READY, committed as
  504866e, main fast-forwarded (OjajHome.jsx still left alone) and pushed,
  e2e passes, deployed from this worktree (aa40c1d2, `--branch main`, data
  only, same script file); the live vault serves 925.

### How 04 and 05 were written (do the same for 06+)

1. His results now: `curl -s "https://smarten.pages.dev/api/results?user=Tadzio"
   > tmp/tadzio_results_<date>.json`, then
   `node tools/ojaj/record_now.mjs tmp/tadzio_results_<date>.json` (run from this
   worktree's root) prints the weak types and every miss, with the app's own
   code. Weight the batch towards the top types; check each miss's key for
   answers that are in fact right (03-29 was one).
2. Draft all 45 rows first, then check the tasks 1-2 answer words in one go:
   `python3 -I tools/ojaj/cand_words.py word1 word2 ...` (app and vault). About a
   third of the first candidates were taken for 04-05.
3. Check every transformation and choice point with
   `python3 -I tools/ojaj/find_phrase.py "phrase" ...`, looking only at answer,
   stem and original hits. The built-in check only catches the same keyword
   with the same answer; near-repeats need the eye. Already used, so avoid as
   the point of an item: the more ... the, no sooner had, need not have, not to
   touch, wish I could, as long as, provided (that), run out of, is being
   repaired, supposed to be, in case it rains, cannot have taken, might have
   forgotten, call it a day, by far, although + was (ALTHOUGH). Found taken
   while writing 06-07: the most boring book, taken into account,
   otherwise you will miss, not worth, were made to, turned down, unlikely
   to, never before, gets on my nerves, in order to, even if, if only + past
   perfect, is said to be, offered to, apologised for, had better, cut down
   on, called off, put off, rarely / seldom, no matter how, see eye to eye,
   spent two hours, suggested going, high time, whereas, would rather you,
   as a result, owing to, wish I had gone, fancy going, can't afford, no use
   + -ing, in which I was born, happen to know, insisted on, succeeded in,
   advised me to, remember to, can't wait, takes after, will be lying,
   heavy defeat, standing ovation (2024/25 paper), music down, have to wear,
   allowed to, made us + verb, difficulty + -ing, "wake the baby".
   Then run `python3 -I tools/ojaj/near_repeat.py NN NN` and read every line. Write each wisielec pattern hiding the tested letters, then
   `python3 -I tools/ojaj/wisielec_letters.py NN NN` cuts it to the papers' number of
   given letters and lists the dictionary words that still fit; read each
   list against its sentence and hand-pick where one fits.
4. Keep each task's profile while drafting: per task 0-2 B1, 3-5 B2, 4-5 C1,
   0-1 C2; 3-4 idiom/collocation/phrasal-verb items in tasks 2 and 4. Count
   before running, the checks only say which bound broke.
5. UK culture: check facts in `site/public/ojaj_uk.html`; asked already are
   the 20 ojaj_uk_* / 2023-24 / 2024-25 questions and the vault's 25. Not yet
   asked, for example: Speaker's "Order!", the Yeomen of the Guard and the
   Gunpowder Plot (1605), the Senedd in Cardiff, Stormont, the 2014 Scottish
   referendum (55% No), Thatcher "the Iron Lady", Starmer (July 2024), the
   Conservative name (1830s), Magna Carta's four copies, Thomas More, Pepys,
   the Great Fire's 13,000 houses, the Falklands surrender (14 June 1982),
   the Lovelace language Ada, Pankhurst's WSPU (1903, Manchester), the votes
   of 1918 and 1928, Joseph Bell, the Reichenbach Falls, Nolan's knighthood
   (2024), the Monument's 311 steps and golden urn, the Tower's ravens legend,
   Hyde Park opened to the public (1637), the Serpentine, Speakers' Corner by
   Marble Arch, Animals in War (2004, Park Lane), Kensington Palace (1689,
   William III and Mary II), the Albert Memorial facing the Royal Albert Hall.
6. Add `T06` after T05 and to `TESTS`; run `ojaj_online.py` and its
   selftest, `gen_ojaj.py`, `node tools/ojaj/val_ojaj.mjs`, `audit_ojaj.py`,
   `bash tools/ojaj/render_ojaj.sh`, `npm test` in site/. Only `vault.json` should
   change. The printout `tmp/ojaj_online_06_review.md` goes to Lukasz.
7. On approval: `/verify`, commit here, `git merge --ff-only
   ojaj-online-vault` in the main checkout, push main, then
   `e2e_online.mjs` with `npx vite --port 5179 --strictPort` running in
   this worktree's site/ (it serves main's data through the symlink; the
   first run can fail while vite is still starting). Lukasz deploys.

45 new items per batch, written to the rules in
`tools/ojaj/notes/HANDOFF_ojaj_online_vault.md`, each row ending with its type, checked
with `ojaj_online.py` (and against the app with `tools/ojaj/find_phrase.py` and
`tools/ojaj/dump_prompts.py`, comparing by eye), printed for approval. Lean on his
weak types: base-change, suffix-spelling, the in-/un- choice, vowels, double
letters, silent letters, and UK politics. His practice history agrees: the
negative prefix was his most frequent word-formation mistake there
(undistinguishable, undispensable, unseparated, deniable for undeniable),
with spelling slips on words he knows (accomodation, excersices, percieving)
(`tools/ojaj/scan_mistakes.mjs` re-marks all his saved answers). Many of his old
kuratoryjny answers do not line up with today's keys, probably because those
exercises were edited after he did them [inferred].

## Rules carried over

No commit, push or deploy without Lukasz saying so; no Co-Authored-By line;
`/verify` right before a commit; check `git branch --show-current` first.
Tests first, mock at the source rather than adding arguments only tests
would use. Temp scripts as `tmp/_*.py` written with the Write tool, run, then
removed. Keys stay strict. Content must suit a primary-school pupil. In the
UI, Polish without diacritics, as on the OJAJ page; timed-test instructions
keep their diacritics.
