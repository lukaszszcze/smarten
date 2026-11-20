"""Check whether gap_fill_sentences answer keys leak the answer through ordering.

If the correct letters run A, B, C, D... a student can score full marks without
reading the text. Compares the practice set against the real papers.

Usage: python3 tools/practice/val_gapfill.py
"""
import json
import glob

BASE = "pub/konkursy/angielski/data"


def ascending_run(letters):
    """Longest run of letters that ascend by exactly one position."""
    best = run = 1
    for a, b in zip(letters, letters[1:]):
        run = run + 1 if ord(b) - ord(a) == 1 else 1
        best = max(best, run)
    return best


def report(label, pairs):
    print("\n===== %s =====" % label)
    leaky = 0
    for src, t in pairs:
        letters = [i["answer"] for i in t.get("items", [])]
        n = len(letters)
        run = ascending_run(letters)
        sorted_flag = letters == sorted(letters)
        tag = ""
        if sorted_flag:
            tag = "  <-- fully in alphabetical order"
            leaky += 1
        elif run >= n - 1:
            tag = "  <-- all but one in order"
            leaky += 1
        print("%-26s %s   longest ascending run %d/%d%s"
              % (src, "".join(letters), run, n, tag))
    print("%d of %d tasks give the answer away by ordering" % (leaky, len(pairs)))


practice = []
for f in sorted(glob.glob(BASE + "/practice/gapfill_*.json")):
    for t in json.load(open(f))["tasks"]:
        practice.append((f.split("/")[-1][:-5], t))

real = []
for f in sorted(glob.glob(BASE + "/20*/rejonowy.json") + glob.glob(BASE + "/20*/wojewodzki.json")):
    for t in json.load(open(f)).get("tasks", []):
        if t.get("type") == "gap_fill_sentences":
            real.append((f.split("/")[-2] + "/" + f.split("/")[-1][:-5], t))

report("PRACTICE", practice)
report("REAL rejonowy/wojewodzki", real)
