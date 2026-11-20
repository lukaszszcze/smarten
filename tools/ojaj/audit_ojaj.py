#!/usr/bin/env python3
"""Scan every OJAJ item for the marks a bad extraction leaves behind.

Run: python3 tools/ojaj/audit_ojaj.py

Reads the written JSON rather than the generator, so it catches anything the
build introduces as well as anything the source carried. Reports, per file:
leftover extraction markers, Polish diacritics in English content, stems long
enough to be two items run together, keys that all sit on one letter, and
duplicated stems across the whole tree.
"""

import glob
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA = os.path.join(ROOT, "pub", "konkursy", "angielski", "data", "ojaj")

# What an extraction leftover looks like: a key marker the parser should have
# eaten, an underline marker, a section heading pulled into an option.
LEFTOVER = re.compile(
    r"\{\s*[a-dA-D]\s*\}|\[\[|\]\]|--- page|KLUCZ|Olimpiada Języka|"
    r"Wybierz|Dopasuj\w* |Uzupe[lł]nij", re.I
)
POLISH = re.compile(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]")

problems = []
stem_owner = defaultdict(list)


def texts(task, item):
    """Every string a student reads on this item, with a label for each."""
    out = []
    for field in ("stem", "sentence", "statement", "context", "question",
                  "clue", "prompt"):
        if item.get(field):
            out.append((field, item[field]))
    for opt in item.get("options") or []:
        out.append(("option", opt))
    return out


for path in sorted(glob.glob(f"{DATA}/**/*.json", recursive=True)):
    name = os.path.relpath(path, DATA)
    if name == "index.json":
        continue
    doc = json.load(open(path, encoding="utf-8"))

    for task in doc["tasks"]:
        keys = []
        for item in task["items"]:
            for field, text in texts(task, item):
                if LEFTOVER.search(text):
                    problems.append(f"{name} {item['id']} {field}: extraction leftover")
                # Polish belongs in instructions and in the etap I word list,
                # never in an English stem or option.
                if field in ("option", "context") and POLISH.search(text):
                    problems.append(f"{name} {item['id']} {field}: Polish in English content")
                if field in ("stem", "context", "sentence") and len(text) > 320:
                    problems.append(f"{name} {item['id']} {field}: {len(text)} chars")
                if unicodedata.normalize("NFC", text) != text:
                    problems.append(f"{name} {item['id']} {field}: not NFC-normalised")
            if isinstance(item.get("answer"), str) and task["type"] in (
                    "multiple_choice", "matching", "true_false_ni"):
                keys.append(item["answer"])
            stem = item.get("stem") or item.get("sentence") or item.get("statement")
            if stem:
                stem_owner[stem].append(f"{name} {item['id']}")

        # A whole task keyed to one letter is what a mis-read key looks like.
        if len(keys) >= 5 and len(set(keys)) == 1:
            problems.append(f"{name} task {task['id']}: every key is {keys[0]}")

# The 2022/23 grupa A and grupa B papers were sat side by side and share 16 of
# their 60 items. That is how the exam was set, so both stay whole; a repeat
# anywhere else means the same item is being served twice.
GRUPY = {"2022-2023/szkolny-a.json", "2022-2023/szkolny-b.json"}
shared_ab = 0
for stem, owners in stem_owner.items():
    if len(owners) == 1:
        continue
    if {o.split()[0] for o in owners} == GRUPY and len(owners) == 2:
        shared_ab += 1
        continue
    problems.append(f"repeated item: {' / '.join(owners)} -- {stem[:60]}")

print(f"scanned {len(stem_owner)} distinct prompts, "
      f"{shared_ab} shared by the two 2022/23 grupy")
for p in problems:
    print("  " + p)
print(f"problems: {len(problems)}")
raise SystemExit(1 if problems else 0)
