#!/usr/bin/env python3
"""Cross-check a parsed OJAJ multiple-choice paper against the bold answers.

The 2022/23 papers mark the correct option twice: once as an inline {a}..{d}
key, which the parser reads, and once by printing that option in bold, which the
parser never sees. Comparing the two catches a mis-parsed option list.

The PDFs carry subsetted fonts named CIDFont+F1..F3, so "bold" cannot be read
off the font name. It is found by usage instead: at the body text size, the
most-used font is the regular one and any other font at that size is emphasis.

Example:
    python3 tools/ojaj/ojaj_bold.py tools/ojaj/pdfs/klucz_2223_A.pdf tools/ojaj/pdfs/parse_A.json
"""

import json
import re
import subprocess
import sys
from collections import Counter

RE_PAGE = re.compile(r"<page number=")
RE_FONT = re.compile(r'<fontspec id="(\d+)"[^>]*size="(\d+)"')
RE_TEXT = re.compile(r'<text[^>]*font="(\d+)"[^>]*>(.*?)</text>')
RE_TAG = re.compile(r"<[^>]+>")


def unescape(text):
    for esc, plain in (("&lt;", "<"), ("&gt;", ">"), ("&#34;", '"'),
                       ("&quot;", '"'), ("&amp;", "&")):
        text = text.replace(esc, plain)
    return text


def emphasised(pdf):
    """Every text fragment set in a non-regular font at body size."""
    out = subprocess.run(
        ["pdftohtml", "-xml", "-stdout", pdf], capture_output=True, check=True
    ).stdout.decode("utf-8", "replace")

    runs = []
    for chunk in out.split("<page number=")[1:]:
        sizes = {fid: int(size) for fid, size in RE_FONT.findall(chunk)}
        nodes = [(fid, unescape(RE_TAG.sub("", body)).strip())
                 for fid, body in RE_TEXT.findall(chunk)]
        nodes = [(f, t) for f, t in nodes if t]
        if not nodes:
            continue

        body_size = Counter(sizes.get(f) for f, _ in nodes).most_common(1)[0][0]
        at_size = [(f, t) for f, t in nodes if sizes.get(f) == body_size]
        if not at_size:
            continue
        regular = Counter(f for f, _ in at_size).most_common(1)[0][0]
        runs += [t for f, t in at_size if f != regular]

    return runs


def norm(text):
    text = text.replace("’", "'").replace("…", " ").replace("–", "-")
    text = re.sub(r"^[A-Da-d][).]\s*", "", text)
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def main():
    pdf, parsed = sys.argv[1], sys.argv[2]
    items = json.load(open(parsed, encoding="utf-8"))
    runs = [norm(r) for r in emphasised(pdf)]
    runs = [r for r in runs if r]
    blob = " || ".join(runs)

    letters = ["A", "B", "C", "D"]
    # A short distractor ("to", "for", "is") is often the keyed answer of some
    # other item, so an emphasised run matching it proves nothing. Only a string
    # that is nobody's key is evidence of a mis-read option list.
    keyed = {norm(i["options"][letters.index(i["answer"])]) for i in items}

    missing, wrong = [], []
    for item in items:
        chosen = norm(item["options"][letters.index(item["answer"])])
        others = [norm(o) for i, o in enumerate(item["options"])
                  if letters[i] != item["answer"]]
        if chosen and chosen not in blob:
            missing.append(f"{item['_src']}: keyed '{chosen}' is not emphasised anywhere")
        for other in others:
            if other and other not in keyed and other in runs:
                wrong.append(f"{item['_src']}: distractor '{other}' is emphasised, key says '{chosen}'")

    for line in missing + wrong:
        print("  " + line)
    print(f"{len(items)} items, {len(runs)} emphasised runs: "
          f"{len(missing)} keys not emphasised, {len(wrong)} emphasised distractors")


if __name__ == "__main__":
    main()
