"""Print the vault's transformation and choice items in one line each.

Purpose: see which grammar and vocabulary points the vault already tests
before writing new items.

    python3 -I tools/ojaj/list_vault.py 3      (transformations)
    python3 -I tools/ojaj/list_vault.py 4      (choice)
"""
import json
import os
import re
import sys

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pub",
                    "konkursy", "angielski", "data", "ojaj", "online", "vault.json")
task = json.load(open(DATA, encoding="utf-8"))["tasks"][int(sys.argv[1]) - 1]
for it in task["items"]:
    if task["type"] == "sentence_transformation":
        print(f"{it['id']:6} {it['mistakeType']:18} {it['keyword']}: "
              f"{it['answer'].split(' / ')[0]}")
    else:
        chosen = next(o for o in it["options"] if o[0] == it["answer"])[3:]
        print(f"{it['id']:6} {it['mistakeType']:18} "
              f"{re.sub(r'_{2,}', '[' + chosen + ']', it['stem'])}")
