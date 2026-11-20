"""Find task content the app never shows, across every task type.

The matching audit found 9 real tasks that could not be answered because the
renderer read a field the data does not use. This generalises that check.

For every task type it works out:
  * which `item.X` / `task.X` keys the component reads   (parsed from the .jsx)
  * which keys the scorer reads                          (parsed from scoring.js)
  * which keys the data actually populates               (real papers + practice)

A key present in the data but read by neither is content the student never sees
and that never counts for marks. That is the exact shape of all three matching
faults.

Usage: python3 tools/practice/val_renderers.py
"""
import json
import glob
import re
import os
from collections import defaultdict

BASE = "pub/konkursy/angielski/data"
COMP = "site/src/components/konkursy"

# --- what the app reads -----------------------------------------------------

# type -> component, straight out of TaskRenderer.jsx so this cannot drift.
_tr = open(COMP + "/TaskRenderer.jsx").read()
_block = re.search(r"const COMPONENTS = \{(.*?)\n\};", _tr, re.S).group(1)
TYPE_COMPONENT = dict(re.findall(r"(\w+):\s*(\w+)", _block))

_scoring = open("site/src/lib/scoring.js").read()
SCORING_ITEM_KEYS = set(re.findall(r"item\.(\w+)", _scoring))
SCORING_TASK_KEYS = set(re.findall(r"task\.(\w+)", _scoring))

# gapText.js is used by the two text-with-inline-inputs renderers.
_gap = open("site/src/lib/gapText.js").read()
GAP_ITEM_KEYS = set(re.findall(r"it\.(\w+)", _gap))


def component_keys(component):
    src = open("%s/%s.jsx" % (COMP, component)).read()
    item = set(re.findall(r"item\.(\w+)", src))
    task = set(re.findall(r"task\.(\w+)", src))
    # These two hand their text to parseGapText, which reads item ids itself.
    if "parseGapText" in src:
        item |= GAP_ITEM_KEYS
    # Destructured `const { before, after } = splitSentenceGap(item.sentence)`
    # is already caught by the item.X regex.
    return item, task


# --- what the data holds ----------------------------------------------------

def load_tasks():
    out = []
    for f in sorted(glob.glob(BASE + "/quest/*.json")):
        src = f.split("/")[-2] + "/" + os.path.basename(f)[:-5]
        for t in json.load(open(f)).get("tasks", []):
            out.append(("real", src, t))
    for f in sorted(glob.glob(BASE + "/quest/*.json")):
        if os.path.basename(f) == "index.json":
            continue
        src = "practice/" + os.path.basename(f)[:-5]
        for t in json.load(open(f)).get("tasks", []):
            out.append(("practice", src, t))
    return out


tasks = load_tasks()

# type -> {key -> [(origin, src)]} for item keys and task keys
item_keys = defaultdict(lambda: defaultdict(list))
task_keys = defaultdict(lambda: defaultdict(list))
counts = defaultdict(lambda: [0, 0])  # type -> [real, practice]

for origin, src, t in tasks:
    ttype = t.get("type")
    counts[ttype][0 if origin == "real" else 1] += 1
    for k in t:
        if k in ("type", "id", "items", "vocabItems", "options", "tasks"):
            continue
        task_keys[ttype][k].append((origin, src))
    for it in (t.get("items") or []):
        for k in it:
            item_keys[ttype][k].append((origin, src))
    for it in (t.get("vocabItems") or []):
        for k in it:
            item_keys[ttype][k].append((origin, src))

# --- report -----------------------------------------------------------------

# Keys that are structural rather than content: never displayed by design.
STRUCTURAL = {"id", "answer", "answers", "points", "correctAnswer", "skipped",
              "scoringScheme", "maxPoints", "openQuestion", "modelAnswer",
              "secondAnswer", "acceptable", "note", "notes"}

problems = []
print("%-24s %-24s %5s %5s" % ("type", "component", "real", "prac"))
print("-" * 62)
for ttype in sorted(counts):
    comp = TYPE_COMPONENT.get(ttype, "-")
    print("%-24s %-24s %5d %5d"
          % (ttype, comp, counts[ttype][0], counts[ttype][1]))
print()

for ttype in sorted(counts):
    comp = TYPE_COMPONENT.get(ttype)
    if not comp:
        continue
    ci, ct = component_keys(comp)
    read_item = ci | SCORING_ITEM_KEYS
    read_task = ct | SCORING_TASK_KEYS

    unread_i = {k: v for k, v in item_keys[ttype].items()
                if k not in read_item and k not in STRUCTURAL}
    unread_t = {k: v for k, v in task_keys[ttype].items()
                if k not in read_task and k not in STRUCTURAL}
    if not unread_i and not unread_t:
        continue

    print("=== %s (%s.jsx) ===" % (ttype, comp))
    for kind, unread in (("item", unread_i), ("task", unread_t)):
        for k, where in sorted(unread.items()):
            srcs = sorted({s for _, s in where})
            real = [s for s in srcs if not s.startswith("practice/")]
            print("  %s.%-14s present in %2d task(s), never read  %s%s"
                  % (kind, k, len(srcs),
                     ", ".join(srcs[:4]), " ..." if len(srcs) > 4 else ""))
            problems.append("%s: %s.%s never read (%d tasks, %d real)"
                            % (ttype, kind, k, len(srcs), len(real)))
    print()

print("%d task(s) scanned, %d unread key(s)" % (len(tasks), len(problems)))
for p in problems:
    print("  ", p)
