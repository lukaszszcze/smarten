#!/usr/bin/env python3
"""Which candidate answer words are free on both counts: not an answer anywhere
in the app or the vault (as cand_words.py checks), and not printed in another
vault item (as printed.py checks). Prints the free ones on one line, then
each taken or printed one with where. Temporary helper.

Run: python3 -I tools/ojaj/free_words.py word1 word2 ...
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ojaj_online as O  # noqa: E402

_, words, _ = O.existing_items()
vault = json.load(open(os.path.join(O.DATA, "ojaj", "online", "vault.json")))
texts = []
for task in vault["tasks"]:
    for it in task["items"]:
        if task["type"] in ("word_formation", "word_spelling"):
            for a in it["answer"]:
                words.setdefault(a.lower(), f"vault {it['id']}")
        parts = [str(it.get(f, "")) for f in
                 ("sentence", "stem", "original", "transformed", "question")]
        parts += [str(o) for o in it.get("options") or []]
        if task["type"] == "sentence_transformation":
            parts.append(str(it.get("answer", "")))
        texts.append((it["id"], " ".join(parts).lower()))
free, notes = [], []
for w in sys.argv[1:]:
    taken = words.get(w.lower())
    hits = [i for i, t in texts if re.search(rf"\b{re.escape(w.lower())}\b", t)]
    if taken or hits:
        notes.append(f"{w:16} {'TAKEN ' + taken if taken else '':44} "
                     f"printed: {', '.join(hits) if hits else '-'}")
    else:
        free.append(w)
print("free:", " ".join(free))
print("\n".join(notes))
