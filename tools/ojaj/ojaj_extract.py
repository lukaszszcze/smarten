#!/usr/bin/env python3
"""Pull the multiple-choice items out of the OJAJ papers into one JSON file.

The papers live as PDFs; this reads them once and writes tools/ojaj/ojaj_items.json,
which tools/ojaj/gen_ojaj.py then turns into the app's data files. Splitting the two
steps keeps the generator runnable without the PDFs, and keeps the parsing
(which needs eyeballing against the originals) separate from the assembly.

The PDFs are downloaded into tools/ojaj/pdfs/ by the commands in the module
docstring of tools/ojaj/gen_ojaj.py.

Run:  python3 tools/ojaj/ojaj_extract.py
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ojaj_parse as P  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PDFS = os.path.join(HERE, "pdfs")
OUT = os.path.join(HERE, "ojaj_items.json")


def text_of(name, marked=False):
    """The paper as text: plain, or with the underlined answers marked."""
    pdf = os.path.join(PDFS, name + ".pdf")
    if not os.path.exists(pdf):
        raise SystemExit(f"missing {pdf} -- see the download commands in gen_ojaj.py")
    if marked:
        out = subprocess.run(
            [sys.executable, os.path.join(HERE, "ojaj_underline.py"), pdf],
            capture_output=True, check=True,
        ).stdout.decode("utf-8")
    else:
        out = subprocess.run(
            ["pdftotext", "-layout", pdf, "-"], capture_output=True, check=True
        ).stdout.decode("utf-8")
    path = os.path.join(PDFS, name + (".marked.txt" if marked else ".txt"))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    return path


def block(path, first, last):
    items, problems = P.parse(path, first, last)
    if problems:
        for p in problems:
            print("  " + p, file=sys.stderr)
    return items


def slice_lines(path, start_marker, end_marker, out_name):
    """Write the lines between two section headings to their own file."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    lo = next(i for i, l in enumerate(lines) if start_marker in l) + 1
    hi = next(i for i, l in enumerate(lines[lo:], start=lo) if end_marker in l)
    dest = os.path.join(PDFS, out_name)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines[lo:hi]) + "\n")
    return dest


def main():
    out = {}

    # 2022/23 etap I czesc I: 60 numbered items, key printed as {a}..{d}.
    for group in ("A", "B"):
        path = text_of(f"klucz_2223_{group}")
        out[f"test_2223_{group.lower()}"] = block(path, 1, 60)

    # Etap I czesc II: numbered, but the key is only the underline.
    e1c2 = text_of("e1c2_key", marked=True)
    out["e1c2_verbs"] = block(e1c2, 1, 20)          # 21 is repaired in the generator
    out["e1c2_vocab_a"] = block(e1c2, 32, 46)
    out["e1c2_prep"] = block(e1c2, 47, 56)
    out["e1c2_vocab_b"] = block(e1c2, 67, 75)

    # Etap II czesc I: numbered, key printed as {a}..{d}.
    e2c1 = text_of("e2c1_key")
    out["e2c1_grammar"] = block(e2c1, 6, 35)
    out["e2c1_vocab"] = block(e2c1, 36, 65)

    # Etap III: the vocabulary items carry no numbers at all.
    e3 = text_of("e3z1_key")
    e3mc = slice_lines(e3, "słownictwo: test wyboru", "wisielec", "e3_mc.txt")
    items, problems = P.parse(e3mc, 1, 0, unnumbered=True)
    for p in problems:
        print("  " + p, file=sys.stderr)
    out["e3_vocab"] = items

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    for name, items in out.items():
        print(f"{name:16} {len(items):3} items")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
