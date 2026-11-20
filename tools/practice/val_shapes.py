"""Second pass: answer-shape and option-format traps the eye does not catch.

Checks, per type:
  1. multiple_choice / dialogue_choice — the renderer maps options positionally
     onto A,B,C,D. More than 4 options, or an answer letter outside the range
     the options cover, means the correct answer can never be selected.
  2. knowledge_questions — the renderer turns an option into a letter with
     /^([A-D])\\..*/ . An option not in "A. text" form yields the whole string
     as the stored answer, which can never match the key.
  3. knowledge_questions — scoring.js does `item.answer.filter(...)` when
     points==2 and there is no secondAnswer. On a *string* answer that throws.
  4. gap_fill_sentences — the row shows only the id, so the numbered blank must
     appear in task.text or the student cannot tell which gap is which.
  5. open_cloze / word_formation — every item must map to a gap in the text.

Usage: python3 tools/practice/val_shapes.py
"""
import json
import glob
import os
import re

BASE = "pub/konkursy/angielski/data"
LETTERS = ["A", "B", "C", "D"]
GAP_RE = re.compile(r"(?:(\d+(?:\.\d+)?)\.\s*)?_{2,}")

problems = []


def note(src, ttype, msg):
    problems.append("%-28s %-22s %s" % (src, ttype, msg))


def parse_gaps(text, items):
    """Mirror of parseGapText: (gap label, matched item id) in order."""
    out = []
    for i, m in enumerate(GAP_RE.finditer(text or "")):
        label = m.group(1)
        item = None
        if label:
            item = next((it for it in items if str(it["id"]) == label), None) or \
                next((it for it in items if str(it["id"]).endswith("." + label)), None)
        if item is None and i < len(items):
            item = items[i]
        out.append((label, item["id"] if item else None))
    return out


for f in sorted(glob.glob(BASE + "/20*/*.json")) + \
        sorted(glob.glob(BASE + "/practice/*.json")):
    if os.path.basename(f) == "index.json":
        continue
    if "/practice/" in f:
        src = "practice/" + os.path.basename(f)[:-5]
    else:
        src = f.split("/")[-2] + "/" + os.path.basename(f)[:-5]

    for t in json.load(open(f)).get("tasks", []):
        ttype = t.get("type")
        items = t.get("items") or []
        if not items:
            continue

        if ttype in ("multiple_choice", "dialogue_choice"):
            for it in items:
                opts = it.get("options")
                if not isinstance(opts, list) or not opts:
                    note(src, ttype, "%s: no options list" % it["id"])
                    continue
                if len(opts) > 4:
                    note(src, ttype, "%s: %d options, renderer only labels A-D"
                         % (it["id"], len(opts)))
                ans = it.get("answer")
                if not isinstance(ans, str) or ans not in LETTERS[:len(opts)]:
                    note(src, ttype, "%s: answer %r outside A-%s"
                         % (it["id"], ans, LETTERS[len(opts) - 1]))

        if ttype == "knowledge_questions":
            for it in items:
                opts = it.get("options")
                if opts:
                    for o in opts:
                        if not re.match(r"^[A-D]\.", o):
                            note(src, ttype, "%s: option %r is not 'A. text' form"
                                 % (it["id"], o[:40]))
                            break
                    ans = it.get("answer")
                    key = ans[0] if isinstance(ans, list) else ans
                    if key not in LETTERS:
                        note(src, ttype, "%s: multiple-choice answer %r is not a letter"
                             % (it["id"], key))
                pts = it.get("points", 1)
                if pts == 2 and not it.get("secondAnswer"):
                    if isinstance(it.get("answer"), str):
                        note(src, ttype,
                             "%s: 2 points with a string answer -> scoring.js "
                             "calls .filter on a string" % it["id"])
                    elif len(it.get("answer") or []) < 2:
                        note(src, ttype, "%s: 2 points but only %d accepted answer(s)"
                             % (it["id"], len(it.get("answer") or [])))

        if ttype == "gap_fill_sentences":
            text = t.get("text") or ""
            for it in items:
                num = str(it["id"]).split(".")[-1]
                if str(it["id"]) not in text and \
                        not re.search(r"\b%s\b\s*[_.]" % re.escape(num), text):
                    note(src, ttype, "%s: no numbered blank in task.text" % it["id"])
                    break

        if ttype in ("open_cloze", "word_formation"):
            if ttype == "word_formation" and not t.get("text") and \
                    any(it.get("sentence") for it in items):
                for it in items:
                    if not it.get("sentence"):
                        note(src, ttype, "%s: per-sentence task, item has no sentence"
                             % it["id"])
                    elif not re.search(r"_{2,}", it["sentence"]):
                        note(src, ttype, "%s: sentence has no blank" % it["id"])
                continue
            mapped = parse_gaps(t.get("text"), items)
            hit = {m for _, m in mapped if m}
            missing = [it["id"] for it in items if it["id"] not in hit]
            if missing:
                note(src, ttype, "%d gap(s) drawn for %d items; no input for %s"
                     % (len(mapped), len(items), ", ".join(map(str, missing[:5]))))

for p in problems:
    print(p)
print("\n%d shape problem(s)" % len(problems))
