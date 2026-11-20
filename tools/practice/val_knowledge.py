"""Check the knowledge_questions exercises against what scoring.js can score.

Three faults are possible in this type:

  1. A 2-point item with a multi-element `answer` and NO `secondAnswer`.
     scoring.js then treats the array as "all parts required, comma-separated
     in one box", so a student typing one accepted alternative gets 1 of 2.
     Alternatives and required-parts are indistinguishable in that shape.
  2. Declared task points not equal to the sum of item points.
  3. An answer variant that could never be typed exactly - matching is a plain
     trim + lowercase string comparison, so trailing punctuation or a long
     explanatory sentence can never be matched by a real student.

Usage: python3 tools/practice/val_knowledge.py
"""
import json
import glob
import os

BASE = "pub/konkursy/angielski/data/practice"

problems = []
files = sorted(glob.glob(BASE + "/knowledge_*.json"))
open_format = 0

for path in files:
    data = json.load(open(path))
    name = os.path.basename(path)[:-5]
    for t in data["tasks"]:
        items = t.get("items", [])
        if not any(it.get("options") for it in items):
            open_format += 1

        declared = t.get("points")
        summed = sum(it.get("points", 1) for it in items)
        if declared != summed:
            problems.append("%s: task points %s but items sum to %s"
                            % (name, declared, summed))

        for it in items:
            ans = it.get("answer")
            pts = it.get("points", 1)
            variants = ans if isinstance(ans, list) else [ans]

            if pts == 2 and not it.get("secondAnswer") and len(variants) >= 2:
                problems.append(
                    "%s %s: 2 points, %d answers, no secondAnswer - scoring.js "
                    "will require ALL of them in one comma-separated box"
                    % (name, it["id"], len(variants)))

            for group, label in ((variants, "answer"),
                                 (it.get("secondAnswer") or [], "secondAnswer")):
                for v in group:
                    if not isinstance(v, str):
                        problems.append("%s %s: non-string %s" % (name, it["id"], label))
                        continue
                    if v != v.strip():
                        problems.append("%s %s: %s %r has stray whitespace"
                                        % (name, it["id"], label, v))
                    if len(v.split()) > 8:
                        problems.append("%s %s: %s %r is too long to type exactly"
                                        % (name, it["id"], label, v))

            # duplicates within a variant list are harmless but signal a slip
            for group, label in ((variants, "answer"),
                                 (it.get("secondAnswer") or [], "secondAnswer")):
                low = [v.strip().lower() for v in group if isinstance(v, str)]
                if len(low) != len(set(low)):
                    problems.append("%s %s: duplicate %s variants"
                                    % (name, it["id"], label))

for p in problems:
    print("PROBLEM:", p)
print("\n%d knowledge exercises checked (%d in open format), %d problems"
      % (len(files), open_format, len(problems)))
