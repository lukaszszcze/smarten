#!/usr/bin/env python3
import json, re, glob, os, subprocess, sys
from collections import Counter

BASE = "pub/konkursy/angielski/data/practice"
GAP_RE = re.compile(r"(?:(\d+(?:\.\d+)?)\.\s*)?_{2,}")

def parse_ids(text, items):
    out = []
    gi = 0
    for m in GAP_RE.finditer(text):
        label = m.group(1)
        item = None
        if label:
            item = next((it for it in items if str(it["id"]) == label), None) \
                or next((it for it in items if str(it["id"]).endswith("." + label)), None)
        if not item and gi < len(items):
            item = items[gi]
        out.append(item["id"] if item else None)
        gi += 1
    return out

idx = json.load(open(os.path.join(BASE, "index.json")))["exercises"]
ids = [e["id"] for e in idx]
dups = [k for k, v in Counter(ids).items() if v > 1]
print("index entries:", len(idx), "| duplicate ids:", dups or "none")

# every index entry has a file; every practice file has an index entry
files = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(BASE, "*.json"))
         if os.path.basename(f) != "index.json"}
missing_file = [i for i in ids if i not in files]
orphan_file = [f for f in files if f not in set(ids)]
print("index entries with no file:", missing_file or "none")
print("files with no index entry:", orphan_file or "none")

NEW = (["formation_%03d" % n for n in range(27, 35)]
       + ["cloze_028","cloze_029","cloze_030","cloze_031","cloze_032",
          "cloze_033","cloze_034","cloze_035"])
bad = 0
for fid in NEW:
    d = json.load(open(os.path.join(BASE, fid + ".json")))
    for t in d["tasks"]:
        items = t["items"]
        gids = parse_ids(t["text"], items)
        iids = [it["id"] for it in items]
        probs = []
        if None in gids: probs.append("UNMAPPED")
        if gids != iids: probs.append("ORDER %s!=%s" % (gids, iids))
        if t["type"] == "open_cloze" and len(items) != 10: probs.append("nItems=%d" % len(items))
        if t["type"] == "word_formation" and len(items) != 8: probs.append("nItems=%d" % len(items))
        for it in items:
            a = it["answer"]
            if not a or (isinstance(a, list) and not all(a)): probs.append("EMPTY %s" % it["id"])
        # ensure index title for this file matches file title minus prefix
        if probs:
            bad += 1
            print("  FAIL", fid, "; ".join(probs))
print("per-file checks:", "ALL OK" if bad == 0 else "%d FAILED" % bad)

# no word bank may list its answers in gap order (all banks, not only practice)
bank = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "bank_order.py")],
                      capture_output=True, text=True)
print(bank.stdout.rstrip())
print("word-bank order:", "ALL OK" if bank.returncode == 0 else "FAILED")
