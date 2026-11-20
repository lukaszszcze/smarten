#!/usr/bin/env python3
"""Parse OJAJ multiple-choice papers out of a pdftotext -layout dump.

The papers number their items and mark the key inline as {a}..{d}; the four
options follow on the next line or two, each introduced by "a)" .. "d)" (or
"a." .. "d." in the etap II and III papers). This turns that into JSON items in
the shape MultipleChoice.jsx reads, and refuses anything it cannot read cleanly
rather than guessing.

Example:
    python3 tools/ojaj/ojaj_parse.py tools/ojaj/pdfs/klucz_A.txt 1 60 > tools/ojaj/pdfs/a.json
"""

import json
import re
import sys

DROP = re.compile(r"Olimpiada Języka Angielskiego|KLUCZ DO TESTU|^--- page \d+ ---$|^\s*$")
# Item head: a number, a dot, then the sentence. Anchored at line start so an
# option like "d) 5. something" cannot open a new item.
HEAD = re.compile(r"^\s{0,6}(\d{1,3})[.)]\s+(?=\S)")
KEY = re.compile(r"\{\s*([a-dA-D])\s*\}")
OPT = re.compile(r"(?<![A-Za-z])([a-d])[).]\s*(?=\S)")

LETTERS = ["A", "B", "C", "D"]

# The next task's heading runs into the last option of the block above it.
STOP = re.compile(
    r"\s*(?:Complete the sentences|Match the (?:sentences|idioms)|"
    r"I{1,3}\s+Match|Choose a, b, c or d|Dopasowywanie|Wisielec|"
    r"[Ss]ł(?:ownictwo|owotwórstwo)|Gramatyka)\b.*$"
)


# A blank in these papers is a run of dots or ellipsis characters: at least one
# "…", or three or more full stops. Two full stops never occur as prose.
BLANK = re.compile(r"[.…]*…[.…]*|\.{3,}")


def clean(text, blank=" _________ "):
    """Collapse the runs of spaces the layout dump leaves behind."""
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"\s+", " ", text).strip()
    text = BLANK.sub(blank, text)
    text = STOP.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def chunks(lines, first, last):
    """Split the paper into one text block per item, in numbering order."""
    want, out, cur = first, [], None
    for line in lines:
        if DROP.search(line):
            continue
        m = HEAD.match(line)
        if m and int(m.group(1)) == want:
            if want > last:
                break  # the head of the item after the range ends the last one
            if cur is not None:
                out.append(cur)
            cur = [line[m.end():]]
            want += 1
        elif cur is not None:
            cur.append(line)
    if cur is not None:
        out.append(cur)
    if len(out) != last - first + 1:
        raise SystemExit(f"found {len(out)} items, expected {last - first + 1} ({first}-{last})")
    return out


# A wrapped last option trails onto its own short line; a new item's stem never
# does, so the length is what separates them.
MAX_WRAP = 30


def has_run(marks):
    return any(marks[i:i + 4] == ["a", "b", "c", "d"] for i in range(len(marks) - 3))


def unnumbered_chunks(lines):
    """Split an unnumbered multiple-choice block into one text block per item.

    The etap III paper numbers nothing, so an item is closed by its own a/b/c/d
    option run plus whatever short line the last option wrapped onto.
    """
    out, cur, complete = [], [], False

    for raw in lines:
        line = raw.strip()
        if DROP.search(raw):
            if complete and cur:
                out.append(cur)
                cur, complete = [], False
            continue

        if complete:
            if len(line) < MAX_WRAP and "{" not in line and not OPT.search(line):
                cur.append(line)
                continue
            out.append(cur)
            cur, complete = [], False

        cur.append(line)
        complete = has_run([m.group(1) for m in OPT.finditer(" ".join(cur))])

    if cur:
        out.append(cur)
    return out


def strip_marks(text):
    """Remove the [[ ]] underline markers, keeping the spans they covered."""
    out, spans, start = [], [], None
    i = 0
    while i < len(text):
        if text.startswith("[[", i):
            start = len(out)
            i += 2
        elif text.startswith("]]", i):
            if start is not None:
                spans.append((start, len(out)))
                start = None
            i += 2
        else:
            out.append(text[i])
            i += 1
    if start is not None:
        spans.append((start, len(out)))
    return "".join(out), spans


def split_options(block):
    """The stem, the four options and the key letter from one item block."""
    text = " ".join(block)
    text, underlined = strip_marks(text)

    key = KEY.search(text)
    if not key and not underlined:
        raise ValueError("no {x} key and nothing underlined")
    if key:
        # Blank the key out in place so the option offsets stay valid.
        text = text[: key.start()] + " " * (key.end() - key.start()) + text[key.end():]

    marks = [m for m in OPT.finditer(text)]
    # Keep the first run that reads a, b, c, d in order -- "b)" inside a stem
    # would otherwise start the option list in the wrong place. Two items in
    # these papers print the first option as "b)", so the opening letter is
    # allowed to be wrong as long as the other three are right; the position in
    # the run, not the printed letter, is what the key refers to.
    start, mislabelled = None, False
    for i in range(len(marks) - 3):
        run = [m.group(1) for m in marks[i:i + 4]]
        if run == ["a", "b", "c", "d"]:
            start = i
            break
        if run[1:] == ["b", "c", "d"] and start is None:
            start, mislabelled = i, True
    if start is None:
        raise ValueError("no a) b) c) d) run")
    if mislabelled:
        print(f"  note: first option printed as '{marks[start].group(1)})'", file=sys.stderr)
    marks = marks[start:start + 4]

    stem = clean(text[: marks[0].start()])
    opts, bounds = [], []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        bounds.append((m.start(), end))
        # An option for a two-blank item carries its own blank marker; "..."
        # keeps it readable inline instead of a second nine-underscore run.
        opts.append(clean(text[m.end():end], blank=" ... "))
    if not stem:
        raise ValueError("empty stem")
    for o in opts:
        if not o:
            raise ValueError("empty option")

    if key:
        return stem, opts, key.group(1).lower()

    # No printed key: the answer is the option the paper underlined.
    hit = [i for i, (lo, hi) in enumerate(bounds)
           if any(us < hi and ue > lo for us, ue in underlined)]
    if len(hit) != 1:
        raise ValueError(f"underline covers {len(hit)} options, expected 1")
    return stem, opts, "abcd"[hit[0]]


def tidy(item):
    """Cosmetic repairs the papers' own typesetting leaves behind.

    Stray capitals inside an option ("been Rusing", "has gone / Said") are left
    alone here: some of these papers' distractors are deliberately malformed
    words, so a blanket lowercasing would both hide real content and damage
    proper nouns. The generator repairs the handful of real slips by name.
    """
    # A stray sub-numbering ("39. 4. The names of ...") is printed in two items.
    item["stem"] = re.sub(r"^\d+\.\s+", "", item["stem"])
    return item


def parse(path, first, last, task_id="1", unnumbered=False):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    if unnumbered:
        blocks = unnumbered_chunks(lines)
        numbers = range(1, len(blocks) + 1)
    else:
        blocks = chunks(lines, first, last)
        numbers = range(first, last + 1)

    items, problems = [], []
    for n, block in zip(numbers, blocks):
        try:
            stem, opts, key = split_options(block)
        except ValueError as exc:
            problems.append(f"item {n}: {exc}\n    {' '.join(block)[:200]}")
            continue
        items.append(tidy({
            "id": f"{task_id}.{n - first + 1}" if not unnumbered else f"{task_id}.{n}",
            "stem": stem,
            "options": [f"{LETTERS[i]}) {o}" for i, o in enumerate(opts)],
            "answer": LETTERS["abcd".index(key)],
            "_src": n,
        }))
    return items, problems


def main():
    args = sys.argv[1:]
    unnumbered = "--unnumbered" in args
    args = [a for a in args if a != "--unnumbered"]
    path = args[0]
    first, last = (int(args[1]), int(args[2])) if len(args) > 2 else (1, 0)
    items, problems = parse(path, first, last, unnumbered=unnumbered)
    if problems:
        print("PROBLEMS:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
    print(json.dumps(items, ensure_ascii=False, indent=2))
    print(f"{len(items)} items parsed, {len(problems)} problems", file=sys.stderr)


if __name__ == "__main__":
    main()
