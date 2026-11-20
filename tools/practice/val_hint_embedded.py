"""Confirm the word_spelling letter pattern is visible in the displayed sentence.

WordSpelling.jsx never renders `item.hint`. That is only harmless if the same
pattern already appears inside the sentence the student sees (stem / clue /
sentence). Where it does not, the student gets no letter clues at all.

The papers write the pattern as "_ _ _ d" in some files and "__ __ __ d" in
others, so both sides are reduced to a list of whitespace-separated tokens
(a run of underscores -> "_", a lone letter -> that letter) and the hint's
token list is looked for as a contiguous run inside the sentence's.

Usage: python3 tools/practice/val_hint_embedded.py
"""
import json
import glob
import os
import re

BASE = "pub/konkursy/angielski/data"


def toks(s):
    out = []
    for t in str(s or "").split():
        # The last blank of a sentence usually carries the full stop or comma
        # ("_ _ n _ _ _ _ _."), so strip trailing punctuation before comparing.
        t = t.strip(".,;:!?–-")
        if not t:
            continue
        out.append("_" if re.fullmatch(r"_+", t) else t.lower())
    return out


def contains(hay, needle):
    if not needle:
        return False
    return any(hay[i:i + len(needle)] == needle
               for i in range(len(hay) - len(needle) + 1))


missing, checked = [], 0
for f in sorted(glob.glob(BASE + "/20*/*.json")) + \
        sorted(glob.glob(BASE + "/practice/spelling_*.json")):
    if "/practice/" in f:
        src = "practice/" + os.path.basename(f)[:-5]
    else:
        src = f.split("/")[-2] + "/" + os.path.basename(f)[:-5]
    for t in json.load(open(f)).get("tasks", []):
        if t.get("type") != "word_spelling":
            continue
        for it in (t.get("items") or []):
            hint = it.get("hint")
            if not hint:
                continue
            checked += 1
            shown = it.get("stem") or it.get("clue") or it.get("sentence") or ""
            if not contains(toks(shown), toks(hint)):
                missing.append("%-26s %-5s hint %r not visible; sentence: %s"
                               % (src, it["id"], hint, str(shown)[:60]))

for m in missing:
    print(m)
print("\n%d item(s) with a hint, %d whose pattern the student cannot see"
      % (checked, len(missing)))
