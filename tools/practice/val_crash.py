"""Find items that make a renderer throw rather than merely render blank.

GrammarGaps.jsx does `item.context.split(...)` with no guard: an item without a
`context` key raises a TypeError, React unmounts, and the whole task disappears
instead of showing a wrong prompt.

Also reports matching tasks whose `categories` key is present but null, and any
grammar_gaps gap marker that is not the exact string the component splits on.

Usage: python3 tools/practice/val_crash.py
"""
import json
import glob
import os
import re

BASE = "pub/konkursy/angielski/data"

src_gg = open("site/src/components/konkursy/GrammarGaps.jsx").read()
m = re.search(r"const parts = ([^;]+);", src_gg)
print("GrammarGaps splits:", m.group(1).strip())
MARKER = re.search(r'split\("(_+)"\)', src_gg).group(1)
print("gap marker: %d underscores\n" % len(MARKER))

problems = []
for f in sorted(glob.glob(BASE + "/20*/*.json")) + \
        sorted(glob.glob(BASE + "/practice/*.json")):
    if os.path.basename(f) == "index.json":
        continue
    if "/practice/" in f:
        src = "practice/" + os.path.basename(f)[:-5]
    else:
        src = f.split("/")[-2] + "/" + os.path.basename(f)[:-5]
    for t in json.load(open(f)).get("tasks", []):
        items = t.get("items") or []
        if t.get("type") == "grammar_gaps":
            for it in items:
                if it.get("context") is None:
                    problems.append("%-26s grammar_gaps %s: no `context` -> "
                                    "TypeError (text=%r)"
                                    % (src, it["id"], bool(it.get("text"))))
                else:
                    if MARKER not in it["context"]:
                        problems.append("%-26s grammar_gaps %s: context has no "
                                        "%d-underscore gap; renders no input"
                                        % (src, it["id"], len(MARKER)))
                # answers must line up with the number of blanks drawn
                body = it.get("context") or it.get("text") or ""
                n_gaps = body.count(MARKER)
                ans = it.get("answer")
                n_ans = len(ans) if isinstance(ans, list) else 1
                if n_gaps and isinstance(ans, list) and n_gaps != n_ans:
                    problems.append("%-26s grammar_gaps %s: %d blank(s) but %d "
                                    "answer(s)" % (src, it["id"], n_gaps, n_ans))
        if t.get("type") in ("matching", "matching_columns"):
            if "categories" in t and t["categories"] is None:
                problems.append("%-26s %s: `categories` present but null"
                                % (src, t["type"]))

for p in problems:
    print(p)
print("\n%d problem(s)" % len(problems))
