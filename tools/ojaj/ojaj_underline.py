#!/usr/bin/env python3
"""Dump an OJAJ PDF as text with the underlined answers marked.

The published OJAJ keys mark the correct option by underlining it. `pdftotext`
drops the underline (it is a drawn rectangle, not a font attribute), so the
answers are invisible in a plain text extraction. This reads mutool's trace
output instead: glyph positions plus the thin filled rectangles, and wraps every
underlined run in [[ ]].

The trace is scanned line by line rather than parsed as XML -- mutool emits
unbalanced <structure> tags, so an XML parser rejects it.

Example:
    python3 tools/ojaj/ojaj_underline.py tools/ojaj/pdfs/e1c2_key.pdf > tmp/e1c2_marked.txt
"""

import re
import subprocess
import sys

# A drawn rectangle counts as an underline when it is this thin and this flat.
MAX_RULE_HEIGHT = 2.5
# How far above the rule a glyph's baseline sits. Word puts the rule ~2pt below.
BASELINE_ABOVE_RULE = (0.0, 6.0)
# Glyphs within this many points of each other vertically are one line.
LINE_TOLERANCE = 3.0

RE_PAGE = re.compile(r"<page ")
RE_SPAN = re.compile(r'<span [^>]*trm="([-\d.]+)')
RE_GLYPH = re.compile(r'<g unicode="(.*?)" glyph="\d+" x="([-\d.]+)" y="([-\d.]+)" adv="([-\d.]+)"')
RE_FILL = re.compile(r"<fill_path ")
RE_PT = re.compile(r'<(?:moveto|lineto) x="([-\d.]+)" y="([-\d.]+)"')
RE_ENDFILL = re.compile(r"</fill_path>")


def scan(pdf):
    """Every page as (glyphs, rules)."""
    out = subprocess.run(
        ["mutool", "draw", "-F", "trace", "-o", "-", pdf],
        capture_output=True, check=True,
    ).stdout.decode("utf-8", "replace")

    pages, glyphs, rules = [], [], []
    size, in_fill, xs, ys = 1.0, False, [], []

    for line in out.splitlines():
        if RE_PAGE.search(line):
            if glyphs or rules:
                pages.append((glyphs, rules))
            glyphs, rules = [], []
            continue

        m = RE_SPAN.search(line)
        if m:
            size = abs(float(m.group(1))) or 1.0
            continue

        m = RE_GLYPH.search(line)
        if m:
            char = m.group(1)
            # mutool XML-escapes the glyph's character.
            for esc, plain in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')):
                char = char.replace(esc, plain)
            glyphs.append({
                "c": char,
                "x": float(m.group(2)),
                "y": float(m.group(3)),
                "w": float(m.group(4)) * size,
            })
            continue

        if RE_FILL.search(line):
            in_fill, xs, ys = True, [], []
            continue

        if in_fill:
            m = RE_PT.search(line)
            if m:
                xs.append(float(m.group(1)))
                ys.append(float(m.group(2)))
            elif RE_ENDFILL.search(line):
                in_fill = False
                if len(xs) >= 3 and max(ys) - min(ys) <= MAX_RULE_HEIGHT and max(xs) - min(xs) > 4:
                    rules.append({"x0": min(xs), "x1": max(xs), "y": max(ys)})

    if glyphs or rules:
        pages.append((glyphs, rules))
    return pages


def mark(glyphs, rules):
    """Flag every glyph sitting on an underline rule."""
    for g in glyphs:
        g["u"] = False
    for r in rules:
        lo, hi = BASELINE_ABOVE_RULE
        for g in glyphs:
            dy = g["y"] - r["y"]
            if lo <= dy <= hi and r["x0"] - 1 <= g["x"] < r["x1"]:
                g["u"] = True


def lines(glyphs):
    """Group glyphs into visual lines, top to bottom, left to right."""
    out = []
    for g in sorted(glyphs, key=lambda g: (-g["y"], g["x"])):
        if out and abs(out[-1][0]["y"] - g["y"]) <= LINE_TOLERANCE:
            out[-1].append(g)
        else:
            out.append([g])
    return [sorted(line, key=lambda g: g["x"]) for line in out]


def render(line):
    """One line as text, underlined runs wrapped in [[ ]], gaps as spaces."""
    parts, open_run, prev = [], False, None
    for g in line:
        if prev is not None:
            space = g["x"] - (prev["x"] + prev["w"])
            if space > 0.6:
                if open_run:
                    parts.append("]]")
                    open_run = False
                parts.append(" " * max(1, int(space / 2.5)))
        if g["u"] and not open_run:
            parts.append("[[")
            open_run = True
        elif not g["u"] and open_run:
            parts.append("]]")
            open_run = False
        parts.append(g["c"])
        prev = g
    if open_run:
        parts.append("]]")
    return "".join(parts).rstrip()


def main():
    for n, (glyphs, rules) in enumerate(scan(sys.argv[1]), start=1):
        print(f"--- page {n} ---")
        mark(glyphs, rules)
        for line in lines(glyphs):
            text = render(line)
            if text.strip():
                print(text)
        print()


if __name__ == "__main__":
    main()
