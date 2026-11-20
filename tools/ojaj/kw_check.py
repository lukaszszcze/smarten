#!/usr/bin/env python3
"""Every transformation in the app (vault included) whose keyword is one of
the given words, with its answer, to compare planned items by eye.

Run: python3 -I tools/ojaj/kw_check.py SO INTEREST PAID
"""

import glob
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA = os.path.join(ROOT, "pub", "konkursy", "angielski", "data")

wanted = {w.upper() for w in sys.argv[1:]}
for path in sorted(glob.glob(f"{DATA}/**/*.json", recursive=True)):
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        continue
    if not isinstance(doc, dict):
        continue
    for task in doc.get("tasks") or []:
        if task.get("type") != "sentence_transformation":
            continue
        for item in task.get("items") or []:
            kw = str(item.get("keyword", "")).upper()
            if kw in wanted:
                name = os.path.relpath(path, DATA)
                print(f"{kw:10} {name} {item.get('id')}: {item.get('original')} -> "
                      f"{str(item.get('answer'))[:70]}")
