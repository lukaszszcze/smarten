"""Check every word_spelling hint against its own answer.

The hint is a per-letter pattern: one token per letter of the answer, either an
underscore or the revealed letter. So len(tokens) must equal len(answer), and
every revealed letter must sit at the matching position.

Usage: python3 tools/practice/val_hint_align.py
"""
import json
import glob
import os
import re

BASE = "pub/konkursy/angielski/data"


def toks(s):
    out = []
    for t in str(s or "").split():
        t = t.strip(".,;:!?–-")
        if t:
            out.append("_" if re.fullmatch(r"_+", t) else t.lower())
    return out


bad, checked = [], 0
for f in sorted(glob.glob(BASE + "/20*/*.json")) + \
        sorted(glob.glob(BASE + "/practice/spelling_*.json")):
    if "/practice/" in f:
        src = "practice/" + os.path.basename(f)[:-5]
    else:
        src = f.split("/")[-2] + "/" + os.path.basename(f)[:-5]
    for t in json.load(open(f)).get("tasks", []):
        if t.get("type") != "word_spelling":
            continue
        for it in (t.get("items") or []):
            hint = it.get("hint")
            if not hint:
                continue
            ans = it.get("answer")
            ans = (ans[0] if isinstance(ans, list) else ans) or ""
            ans = ans.strip().lower()
            checked += 1
            pat = toks(hint)
            why = None
            if len(pat) != len(ans):
                why = "%d marks for a %d-letter answer" % (len(pat), len(ans))
            else:
                for i, (p, c) in enumerate(zip(pat, ans)):
                    if p != "_" and p != c:
                        why = "position %d shows %r, answer has %r" % (i + 1, p, c)
                        break
            if why:
                bad.append("%-26s %-5s %-26s %-14s %s"
                           % (src, it["id"], hint[:26], ans, why))

print("%-26s %-5s %-26s %-14s %s"
      % ("source", "id", "hint", "answer", "problem"))
for b in bad:
    print(b)
print("\n%d hint(s) checked, %d that do not match their answer" % (checked, len(bad)))
