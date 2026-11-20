#!/usr/bin/env python3
# Validate new word_formation files by re-implementing parseGapText's GAP_RE
# logic, confirming each gap maps to an item and counts line up.
import json, re, glob

GAP_RE = re.compile(r"(?:(\d+(?:\.\d+)?)\.\s*)?_{2,}")

def parse(text, items):
    parts = []
    gi = 0
    for m in GAP_RE.finditer(text):
        label = m.group(1)
        item = None
        if label:
            item = next((it for it in items if str(it["id"]) == label), None) \
                or next((it for it in items if str(it["id"]).endswith("." + label)), None)
        if not item and gi < len(items):
            item = items[gi]
        parts.append((label, item["id"] if item else None))
        gi += 1
    return parts

def check_per_sentence(t):
    """The easier shape: no shared text, each item carries its own sentence."""
    problems = []
    for it in t["items"]:
        if not it.get("sentence"):
            problems.append("%s: no sentence" % it["id"])
        elif len(GAP_RE.findall(it["sentence"])) != 1:
            problems.append("%s: %d blanks in the sentence, want 1"
                            % (it["id"], len(GAP_RE.findall(it["sentence"]))))
        if not it.get("wordBase"):
            problems.append("%s: no wordBase" % it["id"])
        if not it.get("answer"):
            problems.append("EMPTY answer %s" % it["id"])
        # The point of this shape is that the base word sits at its own blank,
        # so a word bank would put the choosing step back in.
    if t.get("wordBank"):
        problems.append("per-sentence task should have no wordBank")
    if t.get("points") != len(t["items"]):
        problems.append("points=%s but %d items" % (t.get("points"), len(t["items"])))
    return problems


ok = True
for f in sorted(glob.glob("pub/konkursy/angielski/data/practice/formation_*.json")):
    n = int(f.split("_")[1].split(".")[0])
    d = json.load(open(f))
    for t in d["tasks"]:
        items = t["items"]
        if not t.get("text") and any(it.get("sentence") for it in items):
            problems = check_per_sentence(t)
            print("%-24s %s" % (f.split("/")[-1],
                                "OK (per-sentence)" if not problems
                                else "FAIL " + "; ".join(problems)))
            if problems:
                ok = False
            continue
        if n < 27:
            continue
        gaps = parse(t["text"], items)
        ids_in_text = [g[1] for g in gaps]
        item_ids = [it["id"] for it in items]
        problems = []
        if len(gaps) != 8:
            problems.append("GAPCOUNT=%d" % len(gaps))
        if any(g[1] is None for g in gaps):
            problems.append("UNMAPPED")
        if ids_in_text != item_ids:
            problems.append("ORDER %s != %s" % (ids_in_text, item_ids))
        # word bank checks
        bank = t["wordBank"]
        for it in items:
            if it["baseWord"] not in bank:
                problems.append("BASE %s not in bank" % it["baseWord"])
            if not it["answer"]:
                problems.append("EMPTY answer %s" % it["id"])
        if len(bank) != 10:
            problems.append("BANK=%d" % len(bank))
        status = "OK" if not problems else "FAIL " + "; ".join(problems)
        print("%-16s %s" % (f.split("/")[-1], status))
        if problems:
            ok = False
print("\nALL OK" if ok else "\nPROBLEMS FOUND")
