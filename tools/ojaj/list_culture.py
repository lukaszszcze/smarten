"""Print every UK culture question already in the app and the vault, with its key.

Purpose: see which facts of the UK notebook are taken before writing new ones.

    python3 -I tools/ojaj/list_culture.py
"""
import glob
import json
import os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pub",
                    "konkursy", "angielski", "data", "ojaj")
for path in sorted(glob.glob(f"{DATA}/**/*.json", recursive=True)):
    doc = json.load(open(path, encoding="utf-8"))
    if not isinstance(doc, dict):
        continue
    for task in doc.get("tasks", []):
        if task.get("type") != "knowledge_questions":
            continue
        for it in task.get("items", []):
            key = it.get("answer")
            chosen = ""
            for o in it.get("options") or []:
                if isinstance(key, str) and o[:1] == key:
                    chosen = o[3:]
            print(f"{os.path.relpath(path, DATA)} {it.get('id')}: "
                  f"{it.get('question')} -> {chosen or key}")
