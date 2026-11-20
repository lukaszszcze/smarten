#!/usr/bin/env python3
"""Which transformation or choice points are already used: for each phrase,
the items in the app and the vault whose answer, keyword, prompt or options
contain it (reading passages left out). Prints FREE or the hits, one line per
phrase. Temporary helper.

Run: python3 -I tools/ojaj/tr_points.py "not a single" "only then" ...
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA = os.path.join(ROOT, "pub", "konkursy", "angielski", "data")
FIELDS = ("answer", "keyword", "original", "transformed", "stem", "sentence",
          "context", "question", "options", "statement", "prompt")


GAP = re.compile(r"(?:_{3,}|(?:\b__ |[a-z] )(?:(?:__|[a-z]) )*(?:__|[a-z])"
                 r" \(\d+\))")


def filled(it):
    """The item's prompt with its gap filled by the keyed answer, so a phrase
    split by the gap (a choice stem, a wisielec sentence) is still found."""
    ans = it.get("answer")
    if isinstance(ans, list):
        ans = ans[0] if ans else ""
    ans = str(ans or "")
    opts = it.get("options") or []
    if len(ans) == 1 and opts:
        hit = [str(o) for o in opts if str(o)[:1] == ans]
        if hit:
            ans = re.sub(r"^[A-Z][).]\s*", "", hit[0])
    ans = ans.split(" / ")[0]
    out = []
    for f in ("stem", "sentence", "transformed", "context"):
        v = it.get(f)
        if isinstance(v, str) and ans:
            out.append(GAP.sub(ans, v, count=1))
    return out


def items():
    for path in sorted(glob.glob(f"{DATA}/**/*.json", recursive=True)):
        name = os.path.relpath(path, DATA)
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(doc, dict) or "tasks" not in doc:
            continue
        for task in doc["tasks"]:
            for it in task.get("items") or []:
                parts = filled(it)
                for f in FIELDS:
                    v = it.get(f)
                    if isinstance(v, list):
                        parts += [str(x) for x in v]
                    elif v is not None:
                        parts.append(str(v))
                yield (f"{name.replace('ojaj/online/vault.json', 'vault')} "
                       f"{it.get('id')} ({task['type'][:5]})",
                       " | ".join(parts).lower())


ALL = list(items())
for phrase in sys.argv[1:]:
    pat = re.compile(rf"\b{re.escape(phrase.lower())}")
    hits = [where for where, text in ALL if pat.search(text)]
    print(f"{phrase:24} " + ("FREE" if not hits else
                              f"{len(hits)}: " + ", ".join(hits[:6])))
