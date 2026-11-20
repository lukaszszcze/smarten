"""Show every 2-point knowledge_questions item and how scoring.js treats it.

scoring.js branches on `pts === 2 && item.answer.length >= 2`. That branch
assumes the array lists TWO REQUIRED answers and splits the student's input on
commas, awarding one mark per listed answer found. When the array is really a
list of ALTERNATIVE wordings for one answer, a fully correct reply scores 1/2.

Usage: python3 tools/practice/val_kq_twopoint.py
"""
import json
import glob
import os

BASE = "pub/konkursy/angielski/data"

for f in sorted(glob.glob(BASE + "/20*/*.json")) + \
        sorted(glob.glob(BASE + "/practice/knowledge_*.json")):
    if "/practice/" in f:
        src = "practice/" + os.path.basename(f)[:-5]
    else:
        src = f.split("/")[-2] + "/" + os.path.basename(f)[:-5]
    for t in json.load(open(f)).get("tasks", []):
        if t.get("type") != "knowledge_questions":
            continue
        for it in (t.get("items") or []):
            if it.get("points", 1) != 2 or it.get("secondAnswer"):
                continue
            ans = it.get("answer")
            n = len(ans) if isinstance(ans, list) else "STRING"
            branch = "split-on-comma" if isinstance(ans, list) and len(ans) >= 2 \
                else ("CRASH" if isinstance(ans, str) else "exact-match")
            print("%-26s %-6s %-15s %s" % (src, it["id"], branch, str(ans)[:90]))
            print("%-26s %-6s %-15s Q: %s" % ("", "", "", it.get("question", "")[:90]))
