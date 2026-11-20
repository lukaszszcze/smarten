"""For every task, work out what the student actually sees as the prompt.

val_renderers.py lists keys the app never reads. That only matters when the
unread key is the *only* thing carrying the prompt — then the row renders as a
bare number and the task cannot be answered. This separates the two.

The fallback chains are parsed out of the component sources, so the check
cannot drift from what the app really draws. Types with two render paths
(matching: one-to-one vs grouped; word_formation: shared text vs per-sentence)
are routed the same way the component routes them.

Usage: python3 tools/practice/val_prompt_visible.py
"""
import json
import glob
import os
import re
import sys
from collections import defaultdict

BASE = "pub/konkursy/angielski/data"
# Pass a directory of .jsx files to check a different version of the renderers
# (e.g. the committed ones, for a before/after comparison).
COMP = sys.argv[1] if len(sys.argv) > 1 else "site/src/components/konkursy"

# The prompt expression sits right after the `{item.id}` label span, possibly
# with a JSX comment in between. re.S so a multi-line comment is skipped.
AFTER_ID = r"marginRight: 8 \}\}>\{item\.id\}</span>\s*(?:\{/\*.*?\*/\}\s*)?\{([^}]+)\}"


def chain(component, pattern):
    """Pull an `item.a || item.b || item.id` chain out of a component."""
    src = open("%s/%s.jsx" % (COMP, component)).read()
    m = re.search(pattern, src, re.S)
    if not m:
        raise SystemExit("chain not found in %s" % component)
    keys = [k for k in re.findall(r"item\.(\w+)", m.group(1)) if k != "id"]
    if not keys:
        raise SystemExit("empty chain parsed from %s — check the regex" % component)
    return keys


CHAINS = {
    "word_spelling": chain("WordSpelling", AFTER_ID),
    "multiple_choice": chain("MultipleChoice", AFTER_ID),
    "knowledge_questions": chain("KnowledgeQuestions", AFTER_ID),
    "true_false_ni": chain("TrueFalseNI", AFTER_ID),
    "matching_one": chain("Matching", r"const label = ([^;]+);"),
    "matching_grouped": chain("Matching", r"fontWeight: 600 \}\}>\{([^}]+)\}</td>"),
}
CHAINS["dialogue_choice"] = CHAINS["multiple_choice"]

print("prompt chains read from the components:")
for name in ("word_spelling", "multiple_choice", "knowledge_questions",
             "true_false_ni", "matching_one", "matching_grouped"):
    print("  %-22s %s" % (name, " || ".join("item." + k for k in CHAINS[name]) + " || item.id"))
print()


def has_text(it, keys):
    return any(str(it.get(k) or "").strip() for k in keys)


blank = defaultdict(list)

for f in sorted(glob.glob(BASE + "/quest/*.json")) + \
        sorted(glob.glob(BASE + "/quest/*.json")):
    if os.path.basename(f) == "index.json":
        continue
    if "/practice/" in f:
        src = "practice/" + os.path.basename(f)[:-5]
    else:
        src = f.split("/")[-2] + "/" + os.path.basename(f)[:-5]

    for t in json.load(open(f)).get("tasks", []):
        ttype = t.get("type")
        items = t.get("items") or []
        if not items:
            continue
        missing = None

        if ttype in ("word_spelling", "multiple_choice", "dialogue_choice",
                     "knowledge_questions", "true_false_ni"):
            missing = [it["id"] for it in items if not has_text(it, CHAINS[ttype])]

        elif ttype == "matching":
            if isinstance(items[0].get("answers"), list):
                # A grouped row falls back to item.id, which in these papers is
                # the category name ("England"); only a numeric id is blank.
                missing = [it["id"] for it in items
                           if not has_text(it, CHAINS["matching_grouped"])
                           and str(it["id"]).replace(".", "").isdigit()]
            else:
                missing = [it["id"] for it in items
                           if not has_text(it, CHAINS["matching_one"])]

        elif ttype in ("open_cloze", "word_formation"):
            per_sentence = (ttype == "word_formation" and not t.get("text")
                            and any(it.get("sentence") for it in items))
            if per_sentence:
                missing = [it["id"] for it in items
                           if not re.search(r"_{2,}", str(it.get("sentence") or ""))]
            elif not str(t.get("text") or "").strip():
                missing = [it["id"] for it in items]
            else:
                missing = []

        if missing:
            other = sorted({k for it in items for k in it
                            if k not in ("id", "answer", "answers", "points")})
            blank[ttype].append((src, len(missing), len(items), t.get("points"), other))

total_tasks = 0
total_pts = 0
for ttype in sorted(blank):
    print("=== %s ===" % ttype)
    print("  %-28s %-9s %-4s %s" % ("source", "blank", "pts", "keys the items carry"))
    for src, n, of, pts, other in blank[ttype]:
        print("  %-28s %-9s %-4s %s" % (src, "%d/%d" % (n, of), pts, ", ".join(other)))
        total_tasks += 1
        total_pts += pts or 0
    print()

print("%d task(s) render at least one item with no visible prompt (%d points)"
      % (total_tasks, total_pts))
