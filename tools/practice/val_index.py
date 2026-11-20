"""Check practice/index.json against the exercise files on disk.

Catches orphan entries, duplicate ids, files missing from the index, and
mismatched taskType / taskCount / points.

Usage: python3 tools/practice/val_index.py
"""
import json
import glob
import os
from collections import Counter

BASE = "pub/konkursy/angielski/data/practice"

index = json.load(open(os.path.join(BASE, "index.json")))["exercises"]
problems = []

dupes = [i for i, n in Counter(e["id"] for e in index).items() if n > 1]
if dupes:
    problems.append("duplicate index ids: %s" % dupes)

on_disk = {os.path.basename(p)[:-5] for p in glob.glob(BASE + "/*.json")} - {"index"}
in_index = {e["id"] for e in index}

for missing in sorted(in_index - on_disk):
    problems.append("index entry with no file: %s" % missing)
for orphan in sorted(on_disk - in_index):
    problems.append("file not listed in index: %s" % orphan)

for entry in index:
    path = os.path.join(BASE, entry["id"] + ".json")
    if not os.path.exists(path):
        continue
    data = json.load(open(path))
    tasks = data["tasks"]
    if entry["taskCount"] != len(tasks):
        problems.append("%s: taskCount %s but file has %d tasks"
                        % (entry["id"], entry["taskCount"], len(tasks)))
    if entry["taskType"] != tasks[0]["type"]:
        problems.append("%s: index taskType %s but file type %s"
                        % (entry["id"], entry["taskType"], tasks[0]["type"]))
    total = sum(t["points"] for t in tasks)
    if entry["points"] != total:
        problems.append("%s: index points %s but file totals %s"
                        % (entry["id"], entry["points"], total))
    if data.get("type") != "practice":
        problems.append("%s: file type is %r, expected 'practice'" % (entry["id"], data.get("type")))

for p in problems:
    print("PROBLEM:", p)
print("\n%d index entries, %d files on disk, %d problems"
      % (len(index), len(on_disk), len(problems)))
