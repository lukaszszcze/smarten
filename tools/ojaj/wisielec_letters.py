#!/usr/bin/env python3
"""Cut the letters a vault wisielec pattern shows down to the papers' number.

The published papers show 1 letter for a word of up to 5 letters, 2 for 6-8,
3 for 9-12 and 4 from 13 (the median at each length over their 70 items).
For each vault row this keeps that many of the letters the pattern already
shows, so the tested spelling stays hidden, choosing the ones that leave the
fewest other dictionary words of that length fitting. It prints the old and
new pattern and the words that still fit, to read against the sentence; a
pattern already at the papers' number is left as it is, so on finished
batches it only lists the words that still fit.

Run:  python3 -I tools/ojaj/wisielec_letters.py [NN ...]   (batches; default all)
      python3 -I tools/ojaj/wisielec_letters.py own        (the own exercises in
                                                      the online test's shape)
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ojaj_online as O  # noqa: E402


def words():
    out = set()
    for f in ("/usr/share/dict/british-english", "/usr/share/dict/american-english"):
        with open(f, encoding="utf-8") as fh:
            for w in fh:
                w = w.strip()
                if w.isalpha() and w.islower() and w.isascii():
                    out.add(w)
    return out


def fits(word, compact):
    return len(word) == len(compact) and all(
        c == "_" or c == w for c, w in zip(compact, word))


def best(compact, answer, by_len):
    n = len(compact)
    shown = [i for i, c in enumerate(compact) if c != "_"]
    k = O.given_letters(n)
    if len(shown) <= k:
        return compact
    pool = by_len.get(n, [])

    def score(keep):
        pat = "".join(answer[i] if i in keep else "_" for i in range(n))
        others = sum(1 for w in pool if w != answer and fits(w, pat))
        spread = min((b - a for a, b in zip(keep, keep[1:])), default=n)
        return (others, -spread, keep), pat

    return min(score(keep) for keep in itertools.combinations(shown, k))[1]


def main():
    """Batches by number, own exercises by id (ojaj_own_wisielec_03), or
    "own" for every own exercise in the online test's shape."""
    sets = [(b, t["hangman"], 11) for b, t in O.TESTS + O.SEMI_TESTS if "hangman" in t]
    sets += [(ex_id, rows, 1) for ex_id, rows in O.OWN.HANGMAN_ONLINE]
    wanted = sys.argv[1:] or [b for b, _ in O.TESTS]
    if "own" in wanted:
        wanted += [ex_id for ex_id, _ in O.OWN.HANGMAN_ONLINE]
    by_len = {}
    for w in words():
        by_len.setdefault(len(w), []).append(w)
    for b, rows, first in sets:
        if b not in wanted:
            continue
        for q, row in enumerate(rows, start=first):
            sentence, compact, answer = row[0], row[1], row[2]
            new = best(compact, answer, by_len)
            alts = sorted(w for w in by_len.get(len(answer), [])
                          if w != answer and fits(w, new))
            print(f"{b}-{q}  {compact} -> {new}  {answer}  "
                  f"(other words: {len(alts)})")
            print(f"    {sentence.format(O.pattern_of(new))}")
            print(f"    {' '.join(alts[:40])}{' ...' if len(alts) > 40 else ''}")


if __name__ == "__main__":
    main()
