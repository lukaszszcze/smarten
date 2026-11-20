#!/usr/bin/env python3
"""Where candidate answer words are printed in the vault (any field), so a new
answer is not given away by another vault item, and whether the app already
uses them as an answer. Temporary helper.

Run: python3 -I tools/ojaj/printed.py word1 word2 ...
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
        parts = [str(it.get(f, "")) for f in
                 ("sentence", "stem", "original", "transformed", "question")]
        parts += [str(o) for o in it.get("options") or []]
        if task["type"] == "sentence_transformation":
            parts.append(str(it.get("answer", "")))
        texts.append((it["id"], " ".join(parts).lower()))
for w in sys.argv[1:]:
    hits = [i for i, t in texts if re.search(rf"\b{re.escape(w.lower())}", t)]
    taken = words.get(w.lower())
    print(f"{w:14} {'TAKEN ' + taken if taken else 'free':40} printed in: "
          f"{', '.join(hits) if hits else '-'}")
