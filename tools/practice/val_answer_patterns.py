"""Look for answer-key patterns that let a student score without doing the task.

Checks every practice exercise whose answers are single letters or T/F/NI:
  - keys in strict alphabetical order (pick A,B,C,... and win)
  - keys that are all the same letter
  - overall distribution skew per type
Compares against the same type in the real rejonowy/wojewodzki papers.

Usage: python3 tools/practice/val_answer_patterns.py
"""
import json
import glob
import os
from collections import Counter, defaultdict

BASE = "pub/konkursy/angielski/data"


def ascending_run(letters):
    if any(len(x) != 1 for x in letters):
        return 0  # T/F/NI keys have no alphabetical order to leak
    best = run = 1
    for a, b in zip(letters, letters[1:]):
        run = run + 1 if ord(b) - ord(a) == 1 else 1
        best = max(best, run)
    return best


def keys_of(task):
    out = []
    for it in task.get("items", []):
        a = it.get("answer")
        if isinstance(a, list):
            a = a[0] if a else None
        if isinstance(a, str) and (len(a) == 1 and a.isalpha() or a in ("T", "F", "NI")):
            out.append(a)
    return out


def collect(paths, name_fn):
    by_type = defaultdict(list)
    for f in paths:
        data = json.load(open(f))
        for t in data.get("tasks", []):
            keys = keys_of(t)
            if len(keys) >= 4:
                by_type[t["type"]].append((name_fn(f), keys))
    return by_type


practice = collect(sorted(glob.glob(BASE + "/practice/*.json")),
                   lambda f: os.path.basename(f)[:-5])
real = collect(sorted(glob.glob(BASE + "/20*/rejonowy.json") + glob.glob(BASE + "/20*/wojewodzki.json")),
               lambda f: f.split("/")[-2] + "/" + f.split("/")[-1][:-5])

for ttype in sorted(set(practice) | set(real)):
    print("\n=== %s ===" % ttype)
    for label, group in (("PRACTICE", practice.get(ttype, [])), ("REAL", real.get(ttype, []))):
        if not group:
            print("  %-8s (none)" % label)
            continue
        flagged = []
        pool = Counter()
        for src, keys in group:
            pool.update(keys)
            n = len(keys)
            if keys == sorted(keys) and len(set(keys)) == n:
                flagged.append("%s=%s(alphabetical)" % (src, "".join(keys)))
            elif len(set(keys)) == 1:
                flagged.append("%s=%s(all same)" % (src, "".join(keys)))
            elif ascending_run(keys) >= n - 1 and len(set(keys)) == n:
                flagged.append("%s=%s(near-alphabetical)" % (src, "".join(keys)))
        total = sum(pool.values())
        dist = " ".join("%s:%d%%" % (k, round(100 * v / total)) for k, v in sorted(pool.items()))
        print("  %-8s %2d tasks  |  %s" % (label, len(group), dist))
        if flagged:
            print("           %d flagged: %s" % (len(flagged), ", ".join(flagged)))
