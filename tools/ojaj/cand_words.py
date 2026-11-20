#!/usr/bin/env python3
"""Which candidate answer words for a new vault batch are already taken: used
as a word formation or wisielec answer anywhere in the app or the vault. A
taken word fails ojaj_online.py's checks, so try candidates here first.

Run: python3 -I tools/ojaj/cand_words.py monstrous width desperate ...
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ojaj_online as O  # noqa: E402

_, words, _ = O.existing_items()
vault = json.load(open(os.path.join(O.DATA, "ojaj", "online", "vault.json")))
for task in vault["tasks"][:2]:
    for item in task["items"]:
        for a in item["answer"]:
            words[a.lower()] = f"vault {item['id']}"

for w in sys.argv[1:]:
    hit = words.get(w.lower())
    print(f"{w:20} {'TAKEN at ' + hit if hit else 'free'}")
