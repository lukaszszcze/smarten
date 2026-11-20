"""Find tasks that carry no items and are not marked skipped.

An empty task renders as an instruction with nothing to answer. KonkursTest.jsx
filters `!t.skipped` when it sums maxPoints, so an empty task that is *not*
marked skipped adds points the student can never earn, and the paper header
overstates what is on offer.

Reports every task with no items across all data, split by whether it is
already marked skipped.

Usage: python3 tools/practice/val_empty_tasks.py
"""
import json
import glob
import os
import sys

BASE = "pub/konkursy/angielski/data"

live, marked = [], []
for f in sorted(glob.glob(BASE + "/**/*.json", recursive=True)):
    try:
        doc = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(doc, dict) or not isinstance(doc.get("tasks"), list):
        continue
    src = os.path.basename(os.path.dirname(f)) + "/" + os.path.basename(f)[:-5]
    kind = "prac" if ("/practice/" in f or "/quest/" in f) else "real"
    lost = 0
    for t in doc["tasks"]:
        if t.get("items"):
            continue
        row = (src, kind, t.get("type"), str(t.get("id")), t.get("points") or 0)
        if t.get("skipped"):
            marked.append(row)
        else:
            live.append(row)
            lost += t.get("points") or 0
    if lost and kind == "real":
        live.append((src, kind, "-- paper total unreachable --", "",
                     "%d of %d" % (lost, doc.get("maxPoints") or 0)))

for title, rows in (("empty and NOT skipped", live),
                    ("empty, already skipped", marked)):
    print("\n%s: %d" % (title, len(rows)))
    if rows:
        head = ("source", "kind", "type", "id", "points")
        w = [max(len(str(r[i])) for r in rows + [head]) for i in range(5)]
        fmt = "  " + "  ".join("%-" + str(x) + "s" for x in w)
        print(fmt % head)
        for r in rows:
            print(fmt % tuple(str(x) for x in r))

sys.exit(1 if live else 0)
