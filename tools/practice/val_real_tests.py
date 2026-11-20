"""Audit the real competition test files for tasks with no content.

A task with points but no items renders as an instruction with nothing to
answer. Reports per file and per type.

Usage: python3 tools/practice/val_real_tests.py
"""
import json
import glob
from collections import defaultdict

BASE = "pub/konkursy/angielski/data"

by_type = defaultdict(lambda: [0, 0])  # type -> [empty, total]
rows = []

for f in sorted(glob.glob(BASE + "/20*/*.json")):
    data = json.load(open(f))
    empty = []
    total_pts = 0
    lost_pts = 0
    for t in data.get("tasks", []):
        n = len(t.get("items", []) or []) + len(t.get("vocabItems", []) or [])
        by_type[t["type"]][1] += 1
        total_pts += t.get("points", 0)
        if n == 0:
            by_type[t["type"]][0] += 1
            empty.append("%s(%s pts)" % (t["type"], t.get("points")))
            lost_pts += t.get("points", 0)
    if empty:
        rows.append((f.replace(BASE + "/", ""), data.get("maxPoints"), total_pts, lost_pts, empty))

print("=== test papers containing tasks with no items ===")
for name, declared_max, total_pts, lost, empty in rows:
    print("%-28s maxPoints=%-4s sum(task points)=%-4s unanswerable=%-3s  %s"
          % (name, declared_max, total_pts, lost, ", ".join(empty)))

print("\n=== per task type: tasks with no items / total tasks ===")
for t, (empty, total) in sorted(by_type.items(), key=lambda kv: -kv[1][0]):
    mark = "  <--" if empty else ""
    print("  %-26s %2d / %2d%s" % (t, empty, total, mark))
