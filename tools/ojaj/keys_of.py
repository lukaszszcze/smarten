#!/usr/bin/env python3
"""Print each choice and culture item of the named batches with the option its
key points at, to check the keys after reordering options; ends with the key
letters per batch. Temporary helper.

Run: python3 -I tools/ojaj/keys_of.py 56 57 58 59 60 61
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ojaj_online as O  # noqa: E402

batches = dict(O.TESTS)
for bid in sys.argv[1:]:
    rows = batches[bid]
    kind, = rows
    letters = []
    for row in rows[kind]:
        prompt, opts, key = row[0], row[1], row[2]
        letters.append(key)
        print(f"{bid} {key}  {opts['ABCD'.index(key)]:58.58}  | {prompt[:60]}")
    print(f"{bid} keys: {' '.join(letters)}\n")
