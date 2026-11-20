#!/usr/bin/env python3
"""Near-repeats and give-aways for new vault batches, to read by eye.

ojaj_online.py refuses only an exact repeat (the same prompt, the same
derived or spelt word, the same keyword with the same answer). This lists
what it lets through:

  near   other items in the app or the vault that share most of their
         content words with a new item (01/35 and 04/34 both read "The fire
         alarm went off in the middle of our maths test");
  leak   a word formation or wisielec answer printed in another vault item's
         text, which gives the spelling away when the draw puts both in one
         test (the player lets him jump to any question).

Run:  python3 -I tools/ojaj/near_repeat.py 06 07     (the batches to check)
"""

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ojaj_online as O  # noqa: E402

STOP = set("""a an the and or but of to in on at for with from by as is are was
were be been being it its this that these those i you he she we they me him
her us them my your his our their not no do does did have has had will would
can could should must may might so than then there here what which who whom
whose when where why how all any some very too just only also about into out
up down over after before again once more most much many such own same other
off while because if""".split())


def words(text):
    return {w for w in re.findall(r"[a-z]+", text.lower())
            if len(w) > 2 and w not in STOP}


def item_text(item):
    """Every string the pupil sees in an item, joined."""
    out = []
    for key in ("stem", "sentence", "original", "transformed", "question",
                "context", "statement", "prompt", "options"):
        val = item.get(key)
        if isinstance(val, list):
            out += [v for v in val if isinstance(v, str)]
        elif isinstance(val, str):
            out.append(val)
    return " ".join(out)


def app_items():
    """(where, task type, text) for every item outside the vault."""
    for path in sorted(glob.glob(f"{O.DATA}/**/*.json", recursive=True)):
        name = os.path.relpath(path, O.DATA)
        if name.startswith("ojaj/online/"):
            continue
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(doc, dict) or "tasks" not in doc:
            continue
        for task in doc["tasks"]:
            for item in task.get("items") or []:
                yield f"{name} {item.get('id')}", task["type"], item_text(item)


def main(batches):
    tests = O.built_tests()
    tests = tests + O.built_semi_tests(tests)
    vault = [(f"{t['id']}/{it['id']}", task["type"], it)
             for t in tests for task in t["tasks"] for it in task["items"]]
    new = [v for v in vault if v[0].split("/")[0] in batches]
    others = [(w, k, words(x)) for w, k, x in app_items()]
    others += [(w, k, words(item_text(it))) for w, k, it in vault]

    print("near: shared content words / the smaller item's words")
    for where, kind, item in new:
        mine = words(item_text(item))
        hits = []
        for w, k, theirs in others:
            if w == where or not mine or not theirs:
                continue
            shared = mine & theirs
            score = len(shared) / min(len(mine), len(theirs))
            if len(shared) >= 4 and score >= 0.5:
                hits.append((score, w, sorted(shared)))
        for score, w, shared in sorted(hits, reverse=True)[:3]:
            print(f"  {where:6} ~ {w}  {score:.2f}  {' '.join(shared)}")

    print("\nleak: a vault answer printed in another vault item")
    answers = [(where, a.lower()) for where, kind, it in vault
               if kind in ("word_formation", "word_spelling")
               for a in it["answer"]]
    for where, word in answers:
        rx = re.compile(rf"\b{re.escape(word)}\w*", re.I)
        for w, k, it in vault:
            if w == where:
                continue
            if where.split("/")[0] not in batches and w.split("/")[0] not in batches:
                continue
            m = rx.search(item_text(it))
            if m:
                print(f"  {where:6} '{word}' shows in {w}: ...{m.group(0)}...")


if __name__ == "__main__":
    main(set(sys.argv[1:]) or {"06", "07"})
