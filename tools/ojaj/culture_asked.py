#!/usr/bin/env python3
"""Every UK culture question already asked, in the vault and in the app, with
its key, so new culture items do not repeat one. Temporary helper.

Run: python3 -I tools/ojaj/culture_asked.py [word ...]   (only questions with a word)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ojaj_online as O  # noqa: E402

words = [w.lower() for w in sys.argv[1:]]
rows = []
vault = json.load(open(os.path.join(O.DATA, "ojaj", "online", "vault.json")))
for task in vault["tasks"]:
    if task["type"] != "knowledge_questions":
        continue
    for it in task["items"]:
        rows.append((it["id"], it.get("mistakeType"), it["question"], it["options"],
                     it["answer"]))
for name, doc in O.app_docs():
    if not name.startswith("ojaj/"):
        continue
    for task in doc["tasks"]:
        if task["type"] != "knowledge_questions":
            continue
        for it in task.get("items") or []:
            rows.append((f"{name} {it.get('id')}", "", it.get("question", ""),
                         it.get("options") or [], it.get("answer")))
for rid, mt, q, opts, ans in rows:
    text = " ".join([q] + [str(o) for o in opts]).lower()
    if words and not any(w in text for w in words):
        continue
    key = next((o for o in opts if str(o).startswith(f"{ans}")), ans)
    print(f"{rid:34} {mt or '':12} {q} -> {key}")
