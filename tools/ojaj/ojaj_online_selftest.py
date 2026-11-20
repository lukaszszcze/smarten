#!/usr/bin/env python3
"""Show that tools/ojaj/ojaj_online.py's checks catch what they claim to: each case
breaks one thing in a copy of Test 01 and expects check_test to refuse it.

Run: python3 -I tools/ojaj/ojaj_online_selftest.py
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ojaj_online as O  # noqa: E402

existing = O.existing_items()
print(f"existing: {len(existing[0])} prompts, {len(existing[1])} words, "
      f"{len(existing[2])} keyword answers")


def breaks(label, mutate):
    rows = copy.deepcopy(O.T01)
    mutate(rows)
    test = O.build_test("01", rows)
    try:
        O.check_test(test, existing)
    except AssertionError as e:
        print(f"caught  {label}: {str(e).splitlines()[0]}")
        return
    raise SystemExit(f"MISSED  {label}")


def set_row(kind, i, j, value):
    def f(rows):
        r = list(rows[kind][i])
        r[j] = value
        rows[kind][i] = tuple(r)
    return f


def two(*fs):
    def f(rows):
        for g in fs:
            g(rows)
    return f


breaks("hangman word already in the app",
       two(set_row("hangman", 1, 1, "p_i__l___"),
           set_row("hangman", 1, 2, "priceless")))
breaks("formation word already in the app",
       set_row("formation", 1, 2, ["solutions"]))
breaks("wrong given letter in a pattern",
       set_row("hangman", 0, 1, "w_e_h_r"))
breaks("more given letters than the papers give",
       set_row("hangman", 0, 1, "w_a_h_r"))
breaks("fewer given letters than the papers give",
       set_row("hangman", 0, 1, "_______"))
breaks("ten-underscore transformation gap",
       set_row("transform", 1, 2, "You {}_ at school by eight o'clock."))
breaks("contraction in a key",
       set_row("transform", 1, 3, "aren't supposed to be"))
breaks("seven-word key",
       set_row("transform", 1, 3, "are very much supposed to be here"))
breaks("six C1 in a task", two(set_row("formation", 1, 3, "C1"),
                                set_row("formation", 3, 3, "C1")))
breaks("two focus items in task 4", two(set_row("choice", 2, 4, None),
                                        set_row("choice", 4, 4, None)))
breaks("culture question already in the app",
       set_row("culture", 0, 0, "Who is the patron saint of Wales?"))
breaks("unknown mistake type", set_row("formation", 0, 6, "prefix"))
breaks("grammar type in word formation",
       set_row("formation", 0, 6, "inversion"))
breaks("grammar type on a culture question",
       set_row("culture", 0, 4, "inversion"))
breaks("idiom item typed as spelling", set_row("hangman", 0, 6, "vowels"))
breaks("vocabulary type without a focus", set_row("transform", 0, 7, "idiom"))

# A batch of wisielec items alone: ten rows, checked as task 2 of a full batch
# is, its questions numbered 11-20. T01's rows are not in the app outside the
# vault, so they pass as such a batch; its idiom items are allowed in task 2.
alone = O.build_test("12", {"hangman": copy.deepcopy(O.T01["hangman"])})
O.check_test(alone, existing)
assert [(t["id"], t["type"]) for t in alone["tasks"]] == [("2", "word_spelling")]
assert [it["id"] for it in alone["tasks"][0]["items"]] == [str(n) for n in range(11, 21)]
print("passed  a wisielec batch of ten")


def breaks_alone(label, mutate):
    rows = {"hangman": copy.deepcopy(O.T01["hangman"])}
    mutate(rows)
    try:
        O.check_test(O.build_test("12", rows), existing)
    except AssertionError as e:
        print(f"caught  {label}: {str(e).splitlines()[0]}")
        return
    raise SystemExit(f"MISSED  {label}")


breaks_alone("wisielec batch of nine", lambda rows: rows["hangman"].pop())
breaks_alone("grammar type in a wisielec batch",
             set_row("hangman", 2, 6, "inversion"))
breaks_alone("too many given letters in a wisielec batch",
             set_row("hangman", 0, 1, "w_a_h_r"))
try:
    O.build_test("12", {"hangman": O.T01["hangman"], "choice": O.T01["choice"]})
except AssertionError as e:
    print(f"caught  batch with some tasks but not all: {e}")
else:
    raise SystemExit("MISSED  batch with some tasks but not all")

# A batch of any other task alone (since 2026-11-11, later): its rows as in a
# full batch, checked as that task is there, its questions numbered as there.
ALONE = [("13", "formation", "1", "word_formation", 1, 10),
         ("14", "transform", "3", "sentence_transformation", 21, 10),
         ("15", "choice", "4", "multiple_choice", 31, 10),
         ("16", "culture", "5", "knowledge_questions", 41, 5)]
singles = []
for batch, kind, task_id, task_type, first, n in ALONE:
    test = O.build_test(batch, {kind: copy.deepcopy(O.T01[kind])})
    O.check_test(test, existing)
    assert [(t["id"], t["type"]) for t in test["tasks"]] == [(task_id, task_type)]
    assert [it["id"] for it in test["tasks"][0]["items"]] == [
        str(k) for k in range(first, first + n)]
    assert test["maxPoints"] == n
    singles.append(test)
    print(f"passed  a {task_type} batch of {n}")


def breaks_single(label, kind, mutate):
    rows = {kind: copy.deepcopy(O.T01[kind])}
    mutate(rows)
    try:
        O.check_test(O.build_test("13", rows), existing)
    except AssertionError as e:
        print(f"caught  {label}: {str(e).splitlines()[0]}")
        return
    raise SystemExit(f"MISSED  {label}")


breaks_single("word formation batch of nine", "formation",
              lambda rows: rows["formation"].pop())
breaks_single("culture batch of four", "culture",
              lambda rows: rows["culture"].pop())
breaks_single("grammar type in a word formation batch", "formation",
              set_row("formation", 0, 6, "inversion"))
breaks_single("formation word already in the app, in its own batch",
              "formation", set_row("formation", 1, 2, ["solutions"]))
breaks_single("ten-underscore gap in a transformation batch", "transform",
              set_row("transform", 1, 2, "You {}_ at school by eight o'clock."))
breaks_single("seven-word key in a transformation batch", "transform",
              set_row("transform", 1, 3, "are very much supposed to be here"))
breaks_single("six C1 in a choice batch", "choice",
              two(set_row("choice", 0, 3, "C1"), set_row("choice", 1, 3, "C1"),
                  set_row("choice", 5, 3, "C1")))
breaks_single("three options in a choice batch", "choice",
              set_row("choice", 0, 1, ["a", "b", "c"]))
breaks_single("culture question already in the app, in its own batch",
              "culture", set_row("culture", 0, 0, "Who is the patron saint of Wales?"))
breaks_single("grammar type on a culture question, in its own batch",
              "culture", set_row("culture", 0, 4, "inversion"))

# In the vault each batch's items join their task after the full batches'
# items, and every task's count stays as it was.
full = [O.build_test(b, copy.deepcopy(rows)) for b, rows in O.TESTS[1:3]]
vault = O.build_vault(full + [alone] + singles)
assert [len(t["items"]) for t in vault["tasks"]] == [30, 30, 30, 30, 15]
assert [t["count"] for t in vault["tasks"]] == [10, 10, 10, 10, 5]
assert [it["id"] for it in vault["tasks"][1]["items"][-10:]] == [
    f"12-{n}" for n in range(11, 21)]
for batch, _, task_id, _, first, n in ALONE:
    task = vault["tasks"][int(task_id) - 1]
    assert [it["id"] for it in task["items"][-n:]] == [
        f"{batch}-{k}" for k in range(first, first + n)], f"task {task_id}"
print("passed  one-task batches join their tasks of the vault")

# The app's own wisielec exercises in the online test's shape keep to the same
# rules as a vault wisielec task: here one gives too many letters.
own_rows = copy.deepcopy(O.T01["hangman"])
own_rows[0] = (own_rows[0][0], "w_a_h_r") + own_rows[0][2:]
try:
    O.check_own_hangman("ojaj_own_test", own_rows,
                        O.OWN.hangman_online_exercise("ojaj_own_test", "t",
                                                      own_rows, "src")[1])
except AssertionError as e:
    print(f"caught  too many given letters in an own exercise: {e}")
else:
    raise SystemExit("MISSED  too many given letters in an own exercise")
for ex_id, rows in O.OWN.HANGMAN_ONLINE:
    O.check_own_hangman(ex_id, rows, dict(O.OWN.EXERCISES)[ex_id])
print(f"passed  {len(O.OWN.HANGMAN_ONLINE)} own wisielec exercises")

# A study page link is carried only once its page exists; a notebook link
# must name a section that exists.
study = os.path.join(O.TMP, "_selftest_study")
os.makedirs(study, exist_ok=True)
open(os.path.join(study, "vowels.html"), "w").close()
O.STUDY_DIR = study
notebook = '<section id="parks">'
try:
    assert O.vault_link("vowels", "/ojaj_study/vowels", notebook) == "/ojaj_study/vowels"
    assert O.vault_link("comparison", "/ojaj_study/comparison", notebook) is None
    assert O.vault_link("parks", "/ojaj_uk#parks", notebook) == "/ojaj_uk#parks"
    assert O.vault_link("idiom", None, notebook) is None
    for label, link in [("missing notebook section", "/ojaj_uk#nations"),
                        ("malformed study link", "/ojaj_study/Vowels.html")]:
        try:
            O.vault_link("x", link, notebook)
        except AssertionError as e:
            print(f"caught  {label}: {e}")
        else:
            raise SystemExit(f"MISSED  {label}")
finally:
    os.remove(os.path.join(study, "vowels.html"))
    os.rmdir(study)
print("all cases caught")
