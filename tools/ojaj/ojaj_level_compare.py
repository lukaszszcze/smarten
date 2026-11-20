"""Compare the estimated CEFR level of the OJAJ etap I czesc II sample with the
czesc I papers.

Levels are my own per-item judgement of what the item tests (the target
structure or word sense), not a lookup. Each entry: (paper, task kind, skill,
level, label). kind = recognition (MC, matching) or production (typed answer).
skill = grammar or vocab (vocab includes collocations, phrasal verbs, idioms).

Run: python3 -I tools/ojaj/ojaj_level_compare.py
"""

from collections import Counter, defaultdict

LEVELS = ["A2", "B1", "B2", "C1", "C2"]

P2 = "II 2022/23 sample"
I22 = "I 2022/23 A"
I23 = "I 2023/24 A"
I24 = "I 2024/25 B"

R, P = "recognition", "production"
G, V = "grammar", "vocab"

ITEMS = []


def add(paper, kind, skill, rows):
    for level, label in rows:
        ITEMS.append((paper, kind, skill, level, label))


# ---- czesc II sample, 2022/23 (created 29.11.2022), 74 unique items ----------
add(P2, R, G, [
    ("B1", "are eaten"), ("A2", "didn't know"), ("B1", "is flowing (temporary)"),
    ("B2", "is being selfish"), ("B1", "has gone to"), ("B2", "will have been (fut. perf.)"),
    ("B2", "once (conjunction)"), ("C1", "it was a month before I realised"),
    ("B2", "what on earth have you been doing"), ("A2", "for ten years"),
    ("A2", "since"), ("B1", "had already gone"), ("B1", "is having dinner"),
    ("B1", "used to think"), ("B2", "were going to travel"), ("A2", "shall I"),
    ("B2", "when I've phoned"), ("B2", "was able to (one achievement)"),
    ("B1", "if I were you"),
    ("B1", "twice as much as"), ("B2", "allow smoking"), ("C1", "was seen to leave"),
    ("B1", "is known as"), ("B2", "is said to be"), ("C1", "will have been built"),
    ("B1", "if you don't do"), ("A2", "both"), ("B1", "wherever"), ("A2", "those"),
])
add(P2, R, V, [
    ("A2", "at the bus stop"), ("B1", "leaning against"), ("B2", "get through to (phone)"),
    ("B2", "go after"), ("B1", "any minute now"), ("C1", "first leg (two-match tie)"),
    ("C1", "an old hand"), ("B2", "heart of the countryside"), ("B2", "foot of the mountain"),
    ("B2", "arm of the chair"), ("B1", "summer comes"), ("B1", "harmless"),
    ("B2", "do without"), ("B1", "do me a favour"), ("C1", "spine of a book"),
    ("C1", "a lot of cheek"), ("B2", "gadget"), ("B1", "give me no choice"),
    ("B2", "no point in"), ("C1", "no trace of"), ("C1", "green with envy"),
    ("B1", "make an effort"), ("C1", "once in a blue moon"), ("C2", "browned off"),
    ("B2", "kept in detention"),
])
add(P2, R, V, [  # the two matching sets
    ("B1", "do you a favour"), ("C2", "it does him credit"), ("C2", "having a do"),
    ("C1", "won't do (unsatisfactory)"), ("C2", "doing over a hundred"),
    ("C1", "does go on"), ("C1", "make do"), ("B2", "do-it-yourself"),
    ("B1", "won't do you any harm"), ("B2", "could do with"),
    ("C1", "never entered my head"), ("C1", "keep my head down"),
    ("C2", "bring matters to a head"), ("C1", "head in the clouds"),
    ("C1", "in over my head"), ("C1", "make head or tail of"), ("C2", "off my head"),
    ("C1", "gone to my head"), ("C2", "keep my head"), ("C2", "standing on my head"),
])

# ---- czesc I, 2022/23 grupa A, 60 MC ----------------------------------------
add(I22, R, G, [
    ("A2", "have read"), ("A2", "will help"), ("B1", "everyone is"), ("B1", "had forgotten"),
    ("B1", "was ... written"), ("B1", "what time it is"), ("A2", "there is"),
    ("B1", "isn't she"), ("A2", "each other"), ("A2", "whose"), ("B1", "by himself"),
    ("A2", "has eaten"), ("B1", "has known"), ("A2", "was doing"), ("A2", "a camel"),
    ("A2", "could you"), ("A2", "does ... do"), ("A2", "those"), ("B1", "himself"),
    ("B1", "must be"), ("B1", "has been running"), ("B1", "offered to lend"),
    ("B1", "was coming (reported)"), ("A2", "sometimes"), ("A2", "bigger"),
    ("B1", "had eaten"), ("A2", "who"), ("B1", "used to like"), ("A2", "is taking"),
    ("A2", "fast enough"), ("A2", "was swimming"), ("A2", "was doing"),
    ("B1", "is going to fall"), ("A2", "have you been"), ("B1", "would never agree"),
    ("B2", "am having my car fixed"), ("A2", "couldn't do"), ("A2", "does ... do"),
])
add(I22, R, V, [
    ("B2", "vandalism"), ("B2", "commit crimes"), ("B2", "expelled"), ("B1", "bullying"),
    ("A2", "interested in"), ("A2", "quiet"), ("A2", "seafood"), ("B1", "allergic to"),
    ("B1", "keep a diary"), ("B2", "tutorial"), ("A2", "take a photo"), ("B1", "chapters"),
    ("B1", "hold the door"), ("B1", "keen on"), ("B1", "roast potato"), ("B1", "famous for"),
    ("B1", "give me a lift"), ("A2", "fish and chips"), ("B2", "prohibited"),
    ("C1", "late (deceased)"), ("C1", "tiptoe"), ("B1", "mother-in-law"),
])

# ---- czesc I, 2023/24 grupa A, 80 language items (UK culture left out) -------
add(I23, R, G, [
    ("B2", "will have been working"), ("B1", "what time it is"), ("A2", "which"),
    ("B2", "..., will you? (after imperative)"), ("B1", "hardly ever"),
    ("B1", "recommend watching"), ("B1", "keen on watching"), ("B1", "expect me to explain"),
    ("B2", "wishes he knew"), ("A2", "worked hard"), ("B2", "must have left"),
    ("A2", "was doing"), ("B1", "if he had"), ("B1", "unless it rains"), ("A2", "whose"),
])
add(I23, R, V, [
    ("B1", "lean against"), ("B1", "married to"), ("A2", "arrived at"),
    ("B1", "allergic to"), ("A2", "in a few hours"),
])
add(I23, P, V, [  # word formation
    ("B2", "unreliable"), ("B1", "entrance"), ("B1", "unfortunately"), ("B1", "advised"),
    ("B2", "impression"), ("B1", "unexpected"), ("B2", "activate"), ("B1", "exhibition"),
    ("B1", "pleased"), ("B2", "miserable"), ("B1", "employees"), ("B2", "unsuitable"),
    ("B2", "disappointment"), ("B2", "inconvenient"), ("B2", "endless"),
    ("B2", "courageous"), ("B2", "curiosity"), ("B2", "inexperienced"),
    ("C1", "amazement"), ("B2", "warmth"),
])
add(I23, P, V, [  # wisielec
    ("A2", "both"), ("B2", "misunderstood"), ("B2", "go through"), ("B1", "neither"),
    ("B1", "sister-in-law"), ("B1", "none"), ("B1", "impressive"), ("C1", "make ends meet"),
    ("C1", "disposable"), ("B2", "contribution"), ("B2", "inactive"), ("B1", "explanation"),
    ("C1", "issued warnings"), ("B2", "dull"), ("C1", "dim"), ("C1", "inevitable"),
    ("C1", "utter chaos"), ("B1", "cruise"), ("B2", "antique"), ("B2", "theft"),
])
add(I23, P, G, [  # key word transformations
    ("B2", "capable of doing"), ("B2", "regret eating"), ("B2", "provide you with"),
    ("B1", "care about"), ("B1", "enough money to"), ("B1", "on foot"),
    ("B2", "has no interest"), ("B1", "so boring that"), ("B2", "third conditional"),
    ("B2", "we were introduced"), ("B2", "feel like having"), ("B1", "are meeting"),
    ("B1", "used to dye"), ("B2", "first time she had eaten"), ("B1", "had reached"),
    ("B2", "until Jack collected"), ("B1", "the same age as"), ("B2", "in case it rains"),
    ("C1", "no matter how hard"), ("B1", "unless you exercise"),
])

# ---- czesc I, 2024/25 grupa B, 40 language items (UK culture left out) -------
add(I24, P, V, [  # word formation
    ("C1", "disregard"), ("B2", "repetitive"), ("C1", "unquestionably"), ("B1", "solutions"),
    ("B2", "unbelievably"), ("C1", "newlyweds"), ("C1", "charitable"), ("B2", "generosity"),
    ("C1", "tolerable"), ("B2", "imaginary"),
])
add(I24, P, V, [  # wisielec
    ("B2", "unplugged"), ("C1", "ransom"), ("B2", "downwards"), ("C1", "tedious"),
    ("C1", "formerly"), ("C1", "flashback"), ("B2", "civilians"), ("B1", "casual"),
    ("C1", "flawless"), ("B2", "unbearable"),
])
add(I24, P, G, [  # grammar from words in brackets
    ("B2", "is being delivered"), ("B1", "saw children playing"), ("B2", "provided that"),
    ("B2", "the fifth time I have been"), ("B2", "made me think of changing"),
    ("C1", "is rumoured to have been stealing"), ("C1", "it is no use trying to"),
    ("C1", "get aunt Betty to organise ...'s"), ("B2", "had already bumped into"),
    ("C1", "I'd rather you hadn't brought"),
])
add(I24, R, G, [
    ("B1", "as soon as you arrive"), ("C1", "What surprised ... was"), ("B2", "the more ..., the less"),
    ("B2", "were able to"), ("B2", "very few ... have been revealed"),
])
add(I24, R, V, [
    ("B1", "let us"), ("C1", "eligible"), ("C1", "a narrow escape"),
    ("C1", "didn't need to buy vs needn't have"), ("B1", "raised his hand"),
])

# ---- report -------------------------------------------------------------------
PAPERS = [I22, I23, I24, P2]


def dist(rows):
    c = Counter(r[3] for r in rows)
    n = len(rows)
    return n, [round(100 * c[l] / n) for l in LEVELS]


def show(title, key):
    print(f"\n{title}")
    print(f"{'':<22}{'n':>4}  " + "  ".join(f"{l:>4}" for l in LEVELS) + "   C1+")
    for p in PAPERS:
        rows = [r for r in ITEMS if r[0] == p and key(r)]
        if not rows:
            continue
        n, pct = dist(rows)
        print(f"{p:<22}{n:>4}  " + "  ".join(f"{x:>3}%" for x in pct) + f"   {pct[3] + pct[4]:>3}%")


show("All language items (UK culture left out)", lambda r: True)
show("Grammar items only", lambda r: r[2] == G)
show("Vocabulary items only (incl. collocations, phrasal verbs, idioms)", lambda r: r[2] == V)

print("\nTask format share (recognition = choose; production = type the answer)")
for p in PAPERS:
    rows = [r for r in ITEMS if r[0] == p]
    k = Counter(r[1] for r in rows)
    print(f"  {p:<22} recognition {k[R]:>3}  production {k[P]:>3}")
