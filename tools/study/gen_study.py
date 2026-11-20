"""Write the OJAJ study pages (site/public/ojaj_study/<key>.html) from their data.

Each page is a module in tools/study/pages/ (file name = key with _ for -). Fields:
  KEY, TITLE (the h1), HEAD_TITLE (<title>), BODY ("wordpage" or "grammar"),
  EYEBROW, INDEX_TITLE (the page's card on the index), LEDE (html),
  MISTAKES_INTRO (html or ""), WIDE (bool),
  MISTAKES: dicts {wrong, right, why (html), task: (original, KEY WORD, gapped) or None},
  RULE_TITLE, RULE_HTML (html before the lists, or ""), LEGEND (html or ""),
  GROUPS: [(title, tip or None, [(label or None, [entry, ...]), ...]), ...],
  WATCH: [html, ...], CHECK_INTRO (html),
  TYPED: [(sentence with ___ for the box, "answer|other", why, hint or None), ...]
    hint is a wisielec pattern such as "k _ _ _ h _": shown with its letter count,
  DETAILS: [(original, KEY WORD, gapped with ___, answer html), ...],
  CHECK_TIP (html), PRACTICE: [(href, label), ...], APP_PAIRS (optional),
  ON_INDEX (optional, default True; False keeps the page off the index),
  PUBLISH (optional, default True; False: the page is checked but not written),
  ADVANCED: words (the first new word of an entry, lower case) shown in each
    list's "Advanced" box instead of the list itself; a list of SHOW_ALL_UP_TO
    entries or fewer is shown whole, and so is a list with fewer than MIN_ADVANCED
    advanced words; SPLIT = False shows every list on the page whole.
Lists are sorted alphabetically by base word.

A list entry is either "base > word, word | note" or a single word "defin{i}tely | note".
[x] marks letters that go (crossed out), {x} letters that come in or need care (green).

Checks, which stop the script before anything is written:
- every word in the lists, and every typed answer, is in /usr/share/dict/british-english
  or the hunspell en_GB stems (or ALLOWED);
- nothing from OJAJ online Test 03 (unseen by Tadzio): its word-formation and wisielec
  answers and base words, and its transformation answers, are not on the page;
- no word is listed twice on a page; markings fit their words; hints fit their answers;
- APP_PAIRS, where given, are all listed; 5-8 check questions per page.

Run from the checkout root: python3 tools/study/gen_study.py [key ...]   (all pages by default)
"""
import html
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAGES = ROOT / "tools/study/pages"
OUT = ROOT / "site/public/ojaj_study"
DICT = "/usr/share/dict/british-english"
HUNSPELL_GB = "/usr/share/hunspell/en_GB.dic"
# British forms missing from both word lists, checked by hand.
ALLOWED = {"non-fiction"}
# A list this short is shown whole, without an "Advanced" box (Lukasz, 2026-10-25).
SHOW_ALL_UP_TO = 12
# Fewer advanced words than this go into the list itself (Lukasz, 2026-10-25).
MIN_ADVANCED = 5
# OJAJ online Test 03 as it was at commit 8266f80, before the tests became a vault of
# items (the file left pub/ then). Its items stay off the pages.
TEST03 = ROOT / "tools/study/pages/test03.json"
# Close relatives of Test 03 answers, kept off the pages too.
EXTRA_EXCLUDED = {"appearance", "negligence", "unwilling", "humour", "rhythmic"}


def esc(text):
    return html.escape(text, quote=False)


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test03():
    words, phrases = set(EXTRA_EXCLUDED), set()
    for task in json.load(open(TEST03))["tasks"]:
        for it in task.get("items", []):
            if task["type"] in ("word_formation", "word_spelling"):
                words.update(a.lower() for a in it["answer"])
                if it.get("wordBase"):
                    words.add(it["wordBase"].lower())
            elif task["type"] == "sentence_transformation":
                phrases.update(a.strip().lower() for a in it["answer"].split(" / "))
    return words, phrases


def plain(text):
    return re.sub(r"[\[\]{}]", "", text)


def parse(entry):
    main, _, note = entry.partition(" | ")
    if " > " in main:
        base, words = main.split(" > ")
        return base, [w.strip() for w in words.split(", ")], note.strip()
    return None, [w.strip() for w in main.split(", ")], note.strip()


def first_word(entry):
    return plain(parse(entry)[1][0]).lower()


def sort_key(entry):
    base, words, _ = parse(entry)
    return plain(base or words[0]).lower()


def render_entry(entry):
    base, words, note = parse(entry)
    ws = ", ".join(re.sub(r"\{([^}]+)\}", r"<b>\1</b>", esc(w)) for w in words)
    tail = f" <i>({esc(note)})</i>" if note else ""
    if base is None:
        return f'<li class="one">{ws}{tail}</li>'
    b = re.sub(r"\[([^\]]+)\]", r"<s>\1</s>", esc(base))
    return f'<li><span>{b}</span><span class="arrow">&rarr;</span><span>{ws}{tail}</span></li>'


def check_page(p, dictionary, excluded_words, excluded_phrases):
    errors = []
    entries = [e for _, _, subs in getattr(p, "GROUPS", []) for _, es in subs for e in es]
    seen = {}

    def in_dict(word):
        return all(w in dictionary or w.lower() in dictionary for w in word.split())

    for e in entries:
        base, words, _ = parse(e)
        for w in ([base] if base else []) + words:
            if not in_dict(plain(w)):
                errors.append(f"not in the dictionary: {plain(w)} ({e})")
            if plain(w).lower() in excluded_words:
                errors.append(f"from Test 03: {plain(w)} ({e})")
        for w in words:
            key = plain(w).lower()
            if key in seen:
                errors.append(f"listed twice: {key} ({e}; {seen[key]})")
            seen[key] = e
        if base and "[" in base:
            outside = re.split(r"\[[^\]]*\]", base)
            for w in words:
                ins = re.findall(r"\{([^}]*)\}", w) or [""] * (len(outside) - 1)
                expected = (outside[0] + "".join(i + o for i, o in zip(ins, outside[1:]))).lower()
                tries = {expected, expected[:-1] if expected.endswith(("e", "y")) else expected}
                word = plain(w).lower()
                bare = re.sub(r"^(in|ir|il|im|un|dis)", "", word)
                if not any(word.startswith(t) or bare.startswith(t) for t in tries):
                    errors.append(f"marking does not match: {w} ({e})")
    firsts = {first_word(e) for e in entries}
    for w in getattr(p, "ADVANCED", []):
        if w not in firsts:
            errors.append(f"advanced word not in the lists: {w}")
    for base_word, word in getattr(p, "APP_PAIRS", []):
        if word not in seen:
            errors.append(f"pair from the app missing: {base_word} > {word}")
    typed = getattr(p, "TYPED", [])
    details = getattr(p, "DETAILS", [])
    n = len(typed) + len(details)
    if not 5 <= n <= 8:
        errors.append(f"{n} check questions, want 5-8")
    for sentence, answers, _, hint in typed:
        if sentence.count("___") != 1:
            errors.append(f"one ___ needed: {sentence}")
        for a in answers.split("|"):
            if not in_dict(a):
                errors.append(f"typed answer not in the dictionary: {a}")
            if a.lower() in excluded_words:
                errors.append(f"typed answer from Test 03: {a}")
        if hint:
            letters = hint.split()
            a = answers.split("|")[0].lower()
            if len(letters) != len(a) or any(c != "_" and c != a[i] for i, c in enumerate(letters)):
                errors.append(f"hint does not fit {a}: {hint}")
    return errors


def page_text_errors(text, excluded_words, excluded_phrases):
    errors = []
    low = re.sub(r"<[^>]+>", " ", text).lower()
    tokens = set(re.findall(r"[a-z]+", low))
    for w in excluded_words & tokens:
        errors.append(f"Test 03 word on the page: {w}")
    flat = re.sub(r"\s+", " ", low)
    for ph in excluded_phrases:
        if len(ph.split()) >= 2 and ph in flat:
            errors.append(f"Test 03 answer on the page: {ph}")
    return errors


def mistakes_html(p):
    out = []
    if p.MISTAKES_INTRO:
        out.append(f"    <p>{p.MISTAKES_INTRO}</p>")
    out.append(f'    <div class="mistakes{" wide" if p.WIDE else ""}">')
    for m in p.MISTAKES:
        out.append('      <div class="mk">')
        if m.get("task"):
            orig, kw, gapped = m["task"]
            gapped = esc(gapped).replace("___", '<span class="gap"></span>')
            out.append(f'        <p class="task"><span class="orig">{esc(orig)}</span>'
                       f'<span class="kw">{esc(kw)}</span> {gapped}</p>')
        out.append('        <div class="row"><span class="lab">Common mistake</span>'
                   f'<span class="no">{esc(m["wrong"])}</span></div>')
        out.append('        <div class="row"><span class="lab">Right</span>'
                   f'<span class="yes">{esc(m["right"])}</span></div>')
        out.append(f'        <p class="why">{m["why"]}</p>')
        out.append("      </div>")
    out.append("    </div>")
    return "\n".join(out)


def groups_html(p):
    advanced = set(getattr(p, "ADVANCED", []))
    out = []
    for n, (title, tip, subs) in enumerate(p.GROUPS, 1):
        out.append(f"    <h3>{n}. {esc(title)}</h3>")
        for label, entries in subs:
            if label:
                out.append(f"    <h4>{esc(label)}</h4>")
            ordered = sorted(entries, key=sort_key)
            if not getattr(p, "SPLIT", True) or len(ordered) <= SHOW_ALL_UP_TO:
                basic, harder = ordered, []
            else:
                basic = [e for e in ordered if first_word(e) not in advanced]
                harder = [e for e in ordered if first_word(e) in advanced]
                if len(harder) < MIN_ADVANCED:
                    basic, harder = ordered, []
            if basic:
                out.append('    <ul class="pairs">')
                out.extend(f"      {render_entry(e)}" for e in basic)
                out.append("    </ul>")
            if harder:
                out.append('    <details class="more">')
                out.append(f"      <summary>Advanced: {len(harder)} more "
                           f"word{'s' if len(harder) > 1 else ''}</summary>")
                out.append('      <ul class="pairs">')
                out.extend(f"        {render_entry(e)}" for e in harder)
                out.append("      </ul>")
                out.append("    </details>")
        if tip:
            out.append(f'    <p class="tip">{tip}</p>')
    return "\n".join(out)


def check_html(p):
    out = [f"    <p>{p.CHECK_INTRO}</p>"]
    typed = getattr(p, "TYPED", [])
    if typed:
        out.append('    <ol class="typed">')
        for sentence, answers, why, hint in typed:
            box = '<input class="gapin">'
            if hint:
                a = answers.split("|")[0]
                box += f' (<span class="hint">{esc(hint)}</span>, {len(a)} letters)'
            body = esc(sentence).replace("___", box)
            out.append(f'      <li class="tq" data-answer="{html.escape(answers)}" '
                       f'data-why="{html.escape(why)}">')
            out.append(f"        <p>{body}</p>")
            out.append("      </li>")
        out.append("    </ol>")
        out.append('    <p class="tally" aria-live="polite"></p>')
    for orig, kw, gapped, answer in getattr(p, "DETAILS", []):
        gapped = esc(gapped).replace("___", '<span class="gap"></span>')
        out.append("    <details>")
        out.append(f'      <summary><span class="orig">{esc(orig)}</span>'
                   f'<span class="kw">{esc(kw)}</span> {gapped}</summary>')
        out.append(f"      <p>{answer}</p>")
        out.append("    </details>")
    if p.CHECK_TIP:
        out.append(f'    <p class="tip">{p.CHECK_TIP}</p>')
    out.append('    <div class="practice">')
    for href, label in p.PRACTICE:
        out.append(f'      <a class="quiz" href="{href}">{esc(label)} &rarr;</a>')
    out.append("    </div>")
    return "\n".join(out)


def page_html(p):
    rule = []
    if p.RULE_HTML:
        rule.append(p.RULE_HTML.rstrip("\n"))
    if getattr(p, "GROUPS", None):
        if p.LEGEND:
            more = (' Harder words are in the "Advanced" box under each list.'
                    if getattr(p, "ADVANCED", None) and getattr(p, "SPLIT", True) else "")
            rule.append(f'    <p class="legend">{p.LEGEND}{more}</p>')
        rule.append(groups_html(p))
    watch = "\n".join(f"        <li>{w}</li>" for w in p.WATCH)
    return f"""<!doctype html>
<html lang="en">
<!-- Written by tools/study/gen_study.py from tools/study/pages/{p.KEY.replace("-", "_")}.py.
     Edit the data there. -->
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(p.HEAD_TITLE)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap">
<link rel="stylesheet" href="/ojaj_study/study.css">
</head>
<body class="{p.BODY}">
<div class="wrap">
  <p><a href="/ojaj_study/">&larr; All study pages</a></p>
  <p class="eyebrow">{esc(p.EYEBROW)}</p>
  <div class="page-head">
    <h1>{esc(p.TITLE)}</h1>
    <label class="learnt"><input type="checkbox" data-learnt="{p.KEY}"> I've learnt this</label>
  </div>
  <p class="lede">{p.LEDE}</p>

  <section class="part">
    <h2>Common mistakes</h2>
{mistakes_html(p)}
  </section>

  <section class="part">
    <h2>{esc(p.RULE_TITLE)}</h2>
{chr(10).join(rule)}
  </section>

  <section class="part">
    <h2>Watch out</h2>
    <div class="watch">
      <ul>
{watch}
      </ul>
    </div>
  </section>

  <section class="part check">
    <h2>Check yourself</h2>
{check_html(p)}
  </section>

  <footer>
    <p>The tick is saved only on this device.</p>
  </footer>
</div>
<script src="/ojaj_study/study.js"></script>
</body>
</html>
"""


def link_on_index(p):
    path = OUT / "index.html"
    index = path.read_text()
    title = esc(p.INDEX_TITLE)
    pat = re.compile(r'<div class="card later"><strong>' + re.escape(title) +
                     r'</strong><span>(.*?)</span><span class="badge">Not written yet</span></div>')
    m = pat.search(index)
    if m:
        card = (f'<a class="card" href="/ojaj_study/{p.KEY}"><strong>{title}</strong>'
                f'<span>{m.group(1)}</span><span class="done" data-done="{p.KEY}"></span></a>')
        path.write_text(index[:m.start()] + card + index[m.end():])
    elif f'href="/ojaj_study/{p.KEY}"' not in index:
        sys.exit(f"no card on the index for {p.KEY} ({title})")


def main():
    keys = sys.argv[1:]
    files = sorted(PAGES.glob("*.py"))
    if keys:
        files = [PAGES / f"{k.replace('-', '_')}.py" for k in keys]
    dictionary = set(open(DICT, encoding="utf-8").read().split())
    # The hunspell en_GB stems add hyphenated British forms (non-stop, non-smoker).
    for line in open(HUNSPELL_GB, encoding="utf-8", errors="replace").read().splitlines()[1:]:
        dictionary.add(line.split("/")[0])
    dictionary |= ALLOWED
    excluded_words, excluded_phrases = test03()
    pages = [load(f) for f in files]
    failed = False
    built = {}
    for p in pages:
        text = page_html(p)
        errors = check_page(p, dictionary, excluded_words, excluded_phrases)
        errors += page_text_errors(text, excluded_words, excluded_phrases)
        if errors:
            failed = True
            print(f"{p.KEY}:\n  " + "\n  ".join(errors))
        built[p.KEY] = (p, text)
    if failed:
        sys.exit(1)
    for key, (p, text) in built.items():
        if not getattr(p, "PUBLISH", True):
            if (OUT / f"{key}.html").exists():
                sys.exit(f"{key} is not published but {key}.html is in {OUT}: move it out first")
            print(f"{key}: not published")
            continue
        (OUT / f"{key}.html").write_text(text)
        if getattr(p, "ON_INDEX", True):
            link_on_index(p)
        n = sum(len(parse(e)[1]) for _, _, subs in getattr(p, "GROUPS", []) for _, es in subs
                for e in es)
        print(f"{key}: written ({n} listed words)")


main()
