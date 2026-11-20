#!/usr/bin/env python3
"""Print every existing prompt of one task type across the app, so new own
items can be checked against them by eye.

Run: python3 -I tools/ojaj/dump_prompts.py sentence_transformation
     python3 -I tools/ojaj/dump_prompts.py multiple_choice ojaj
The optional second argument keeps only files whose path contains it.
"""

import glob
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA = os.path.join(ROOT, "pub", "konkursy", "angielski", "data")
kind = sys.argv[1]
only = sys.argv[2] if len(sys.argv) > 2 else ""

for path in sorted(glob.glob(f"{DATA}/**/*.json", recursive=True)):
    name = os.path.relpath(path, DATA)
    if only not in name:
        continue
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(doc, dict) or "tasks" not in doc:
        continue
    for task in doc["tasks"]:
        if task["type"] != kind:
            continue
        for it in task.get("items") or []:
            ans = it.get("answer")
            ans = " / ".join(ans) if isinstance(ans, list) else str(ans)
            if kind == "sentence_transformation":
                print(f"{it.get('keyword', '?'):10} | {ans[:55]:55} | {name}")
            elif kind in ("multiple_choice", "dialogue_choice"):
                print(f"{it.get('stem', '')[:90]:90} | {name}")
            elif kind == "knowledge_questions":
                print(f"{it.get('question', '')[:100]:100} | {name}")
            else:
                print(f"{ans[:40]:40} | {name}")
