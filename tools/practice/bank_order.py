"""Find tasks whose word bank lists the answers in gap order.

Scans every JSON file under pub/ for tasks with a `wordBank` and reports how
far the bank's order follows the order of the gaps.

    python3 tools/practice/bank_order.py
"""
import json
import pathlib

ROOT = pathlib.Path("pub/konkursy/angielski/data")


def bank_key(item):
    """The bank entry an item uses: its base word, else its answer."""
    if "baseWord" in item:
        return item["baseWord"]
    ans = item.get("answer")
    return ans[0] if isinstance(ans, list) else ans


def walk_tasks(obj):
    if isinstance(obj, dict):
        if "wordBank" in obj and "items" in obj:
            yield obj
        for v in obj.values():
            yield from walk_tasks(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_tasks(v)


rows = []
for path in sorted(ROOT.rglob("*.json")):
    data = json.loads(path.read_text())
    for task in walk_tasks(data):
        bank = [str(w).strip().lower() for w in task["wordBank"]]
        keys = [str(bank_key(it) or "").strip().lower() for it in task["items"]]
        pos = [bank.index(k) if k in bank else None for k in keys]
        known = [p for p in pos if p is not None]
        # longest run of consecutive gaps whose bank positions increase by 1
        best = run = 1 if known else 0
        for a, b in zip(pos, pos[1:]):
            run = run + 1 if a is not None and b is not None and b == a + 1 else 1
            best = max(best, run)
        in_order = known == sorted(known) and len(known) == len(keys)
        rows.append((str(path.relative_to(ROOT)), task.get("id"), task.get("type"),
                     len(keys), len(known), best, in_order))

print(f"{len(rows)} tasks with a word bank")
flag = [r for r in rows if r[6] or r[5] >= 3]
print(f"{len(flag)} with the bank in gap order or a run of 3+ consecutive gaps\n")
for r in flag:
    print(f"{r[0]:55s} task {r[1]!s:4s} {r[2]:22s} gaps={r[3]} found={r[4]} "
          f"run={r[5]} in_order={r[6]}")
