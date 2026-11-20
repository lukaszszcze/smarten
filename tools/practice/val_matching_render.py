"""Check every matching / matching_columns task actually renders and scores.

Two shapes exist in the data:
  one-to-one  item has `answer` (a single letter)      -> one select per row
  grouped     item has `answers` (a list of letters)   -> several selects per row

Three things can go wrong:
  1. Matching.jsx labels a one-to-one row with `item.name || item.statement ||
     item.id`. A task that carries the prompt in `label` shows the bare id
     ("8.1") and the student cannot tell what to match.
  2. MatchingColumns.jsx always draws exactly two selects per row and writes an
     array answer. A one-to-one task routed there can never be answered.
  3. The number of selects drawn must equal the number of answers expected.

Usage: python3 tools/practice/val_matching_render.py
"""
import json
import glob
import re

BASE = "pub/konkursy/angielski/data"

# Read the fallback chain straight out of the component so this check cannot
# drift from what the app actually shows.
_src = open("site/src/components/konkursy/Matching.jsx").read()
_m = re.search(r"const label = ([^;]+);", _src)
LABEL_KEYS_MATCHING = tuple(
    k for k in re.findall(r"item\.(\w+)", _m.group(1)) if k != "id")
_g = re.search(r"fontWeight: 600 \}\}>\{([^}]+)\}</td>", _src)
GROUPED_ROW_KEYS = tuple(
    k for k in re.findall(r"item\.(\w+)", _g.group(1)) if k != "id")

print("Matching.jsx labels a one-to-one row with: %s (then the bare id)"
      % " || ".join("item." + k for k in LABEL_KEYS_MATCHING))
print("            and a grouped row with: %s (then the bare id)\n"
      % " || ".join("item." + k for k in GROUPED_ROW_KEYS))

rows = []
problems = []


def audit(src, task):
    items = task.get("items", []) or []
    if not items:
        return
    ttype = task["type"]
    grouped = isinstance(items[0].get("answers"), list)
    shape = "grouped" if grouped else "one-to-one"

    label_key = None
    for k in ("name", "statement", "label", "category"):
        if any(k in it for it in items):
            label_key = k
            break

    note = []

    if ttype == "matching":
        if not grouped:
            # SingleAnswerList: name || statement || id
            if not any(any(k in it for k in LABEL_KEYS_MATCHING) for it in items):
                note.append("row label falls back to the bare id (prompt is in %r)"
                            % label_key)
        else:
            n = len(items[0]["answers"])
            if any(len(it.get("answers", [])) != n for it in items):
                note.append("rows expect different numbers of answers")
            # MultiAnswerTable labels a row with category || id
            if any(it.get("category") and it["category"] != it["id"] for it in items):
                if "category" not in GROUPED_ROW_KEYS:
                    note.append("row shows its number, not the category")
    elif ttype == "matching_columns":
        if not grouped:
            note.append("one-to-one task sent to the two-select city table")
        else:
            n = len(items[0]["answers"])
            if n != 2:
                note.append("table draws 2 selects but rows expect %d" % n)

    rows.append((src, ttype, shape, len(items), task.get("points"),
                 label_key, "; ".join(note)))
    for x in note:
        problems.append("%s (%s): %s" % (src, ttype, x))


for f in sorted(glob.glob(BASE + "/20*/*.json")):
    src = f.split("/")[-2] + "/" + f.split("/")[-1][:-5]
    for t in json.load(open(f)).get("tasks", []):
        if t.get("type") in ("matching", "matching_columns"):
            audit(src, t)

for f in sorted(glob.glob(BASE + "/practice/matching_*.json")):
    src = "practice/" + f.split("/")[-1][:-5]
    for t in json.load(open(f))["tasks"]:
        if t.get("type") in ("matching", "matching_columns"):
            audit(src, t)

print("%-28s %-17s %-11s %-5s %-4s %-9s %s"
      % ("source", "type", "shape", "items", "pts", "label key", "problem"))
for r in rows:
    print("%-28s %-17s %-11s %-5s %-4s %-9s %s"
          % (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))

print("\n%d tasks, %d that do not render or score correctly" % (len(rows), len(problems)))
