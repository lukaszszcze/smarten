#!/usr/bin/env python3
"""Find phrases anywhere in the app's data, reporting file, task type, item id
and field, so a planned own item can be checked against what already exists.

Run: python3 -I tools/ojaj/find_phrase.py "high time" "over the moon"
A hit in a reading passage (field "text" on the task) is usually harmless; a
hit in an item's answer or prompt is a repeat to avoid.
"""

import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA = os.path.join(ROOT, "pub", "konkursy", "angielski", "data")


def walk(node, path):
    """Yield (path, string) for every string inside a JSON value."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}")


docs = []
for p in sorted(glob.glob(f"{DATA}/**/*.json", recursive=True)):
    try:
        docs.append((os.path.relpath(p, DATA), json.load(open(p, encoding="utf-8"))))
    except Exception:
        pass

for phrase in sys.argv[1:]:
    rx = re.compile(re.escape(phrase), re.I)
    print(f"=== {phrase}")
    for name, doc in docs:
        for where, text in walk(doc, ""):
            m = rx.search(text)
            if m:
                lo, hi = max(0, m.start() - 70), m.end() + 50
                print(f"  {name} {where}: ...{text[lo:hi]}...")
