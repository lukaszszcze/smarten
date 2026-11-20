"""Check the three task types nothing had exercised against real data.

sentence_transformation, writing and grammar_gaps carry no items in most real
papers, so the earlier sweeps never reached their renderers. This checks the
field contracts those renderers assume, plus one whole-file contract that
applies to every type.

Checks
  A  sentence_transformation — every item carries transformed / original /
     keyword / answer. SentenceTransformation.jsx does
     `item.transformed.split("_________")` unguarded, so a missing field throws
     and (with no error boundary) blanks the page. It also keeps only
     `parts[1]`, so a second blank silently drops the rest of the sentence, and
     it splits on exactly nine underscores, so a run of any other length draws
     no box at all mid-sentence.
  B  grammar_gaps — the renderer counts blanks by splitting on nine
     underscores; check.js counts them as `answer.length`, falling back to runs
     of two-or-more underscores. Where those disagree the student gets a
     different number of boxes than the grader scores.
  C  writing — Writing.jsx stores its answer under the fixed key "writing".
     Both players keep one flat answers object for the whole paper, so two
     writing tasks in one file share a single textarea value.
  D  every type — same flat answers object means an item id repeated across two
     tasks of one file is one shared answer.

Usage: python3 tools/practice/val_st_writing.py
"""
import json
import glob
import os
import re
import sys

BASE = "pub/konkursy/angielski/data"
BLANK = "_________"          # exactly what both renderers split on
RUN = re.compile(r"_{2,}")


def source(f):
    if "/practice/" in f or "/quest/" in f:
        return os.path.basename(os.path.dirname(f)) + "/" + os.path.basename(f)[:-5]
    return os.path.basename(os.path.dirname(f)) + "/" + os.path.basename(f)[:-5]


def is_real(f):
    return "/practice/" not in f and "/quest/" not in f


def answer_list(a):
    return a if isinstance(a, list) else [a]


files = sorted(glob.glob(BASE + "/**/*.json", recursive=True))
a_rows, b_rows, c_rows, d_rows = [], [], [], []
seen = {"sentence_transformation": 0, "grammar_gaps": 0, "writing": 0}

for f in files:
    try:
        doc = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("UNPARSEABLE %s: %s" % (f, e))
        continue
    if not isinstance(doc, dict):
        continue
    tasks = doc.get("tasks") or []
    src = source(f)
    tag = "real" if is_real(f) else "prac"

    # ---- C: two writing tasks share one hardcoded answer key
    writing_tasks = [t for t in tasks if t.get("type") == "writing" and not t.get("skipped")]
    if len(writing_tasks) > 1:
        c_rows.append((src, tag, ", ".join(str(t.get("id")) for t in writing_tasks)))

    # ---- D: item ids repeated across tasks of one file
    owner = {}
    for t in tasks:
        if t.get("skipped"):
            continue
        for it in (t.get("items") or []):
            iid = str(it.get("id"))
            if iid in owner and owner[iid] != t.get("id"):
                d_rows.append((src, tag, iid, str(owner[iid]), str(t.get("id"))))
            owner.setdefault(iid, t.get("id"))

    for t in tasks:
        ttype = t.get("type")
        if ttype not in seen or t.get("skipped"):
            continue
        items = t.get("items") or []
        if items:
            seen[ttype] += 1

        # ---- A: sentence_transformation field and blank contract
        if ttype == "sentence_transformation":
            for it in items:
                iid = str(it.get("id"))
                missing = [k for k in ("transformed", "original", "keyword", "answer")
                           if not it.get(k)]
                if missing:
                    a_rows.append((src, tag, iid, "missing " + ",".join(missing)))
                    continue
                tr = it["transformed"]
                n = tr.count(BLANK)
                runs = RUN.findall(tr)
                odd = sorted({len(r) for r in runs if len(r) != len(BLANK)})
                if n == 0:
                    a_rows.append((src, tag, iid,
                                   "no 9-underscore blank; runs of %s -> box lands at the end"
                                   % (odd or "none")))
                elif n > 1:
                    a_rows.append((src, tag, iid,
                                   "%d blanks; renderer keeps only the first, drops the rest" % n))
                elif odd:
                    a_rows.append((src, tag, iid,
                                   "extra underscore run(s) of length %s beside the blank" % odd))

        # ---- B: grammar_gaps box count vs graded gap count
        if ttype == "grammar_gaps":
            for it in items:
                iid = str(it.get("id"))
                ctx = it.get("context")
                if not ctx:
                    b_rows.append((src, tag, iid, "no context", "-", "-"))
                    continue
                boxes = ctx.count(BLANK)
                graded = len(answer_list(it.get("answer")))
                fallback = len(RUN.findall(ctx)) or 1
                if boxes == 0:
                    b_rows.append((src, tag, iid, "no 9-underscore blank -> 0 boxes",
                                   str(boxes), str(graded)))
                elif boxes != graded:
                    b_rows.append((src, tag, iid, "boxes != graded gaps",
                                   str(boxes), "%d (fallback %d)" % (graded, fallback)))

print("tasks with items reached: " + ", ".join(
    "%s=%d" % (k, v) for k, v in seen.items()))

for title, rows, head in (
    ("A  sentence_transformation", a_rows, ("source", "kind", "id", "problem")),
    ("B  grammar_gaps", b_rows, ("source", "kind", "id", "problem", "boxes", "graded")),
    ("C  two writing tasks in one file", c_rows, ("source", "kind", "task ids")),
    ("D  item id shared across tasks", d_rows, ("source", "kind", "id", "task", "task")),
):
    print("\n%s: %d" % (title, len(rows)))
    if rows:
        w = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
        fmt = "  " + "  ".join("%-" + str(x) + "s" for x in w)
        print(fmt % head)
        for r in rows:
            print(fmt % tuple(str(x) for x in r))

sys.exit(1 if (a_rows or b_rows or c_rows or d_rows) else 0)
