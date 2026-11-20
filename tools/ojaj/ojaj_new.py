#!/usr/bin/env python3
"""The second batch of OJAJ material: two 2022/23 papers and three sample pools.

Imported by tools/ojaj/gen_ojaj.py, which writes the JSON and the index. The
multiple-choice items come from tools/ojaj/ojaj_items.json (produced by
tools/ojaj/ojaj_extract.py); everything else -- the two matching tasks, the idiom
matching, the word formation and the twenty-five hangman clues -- is
transcribed here, because those sections are short and their shapes differ too
much per task to be worth parsing.

What became a test and what became practice
-------------------------------------------
The two 2022/23 papers are real sat papers, so they stay whole and timed. The
etap I czesc II, etap II czesc I and etap III papers are the compendium's
sample pools: 75 items each, longer than any real sitting, and organised in
blocks by task type. They are split along their own block boundaries into
practice exercises of about ten items. No item appears both as a test question
and as practice.

Repairs
-------
The papers carry a handful of printing slips. An item is repaired only when it
is unanswerable as printed, or when the slip is plainly typesetting (a capital
letter dropped into the middle of an option). Deliberately malformed
distractors -- "misrequited", "illicensed", "menton" -- are left exactly as
printed: inventing plausible spellings would change what the item tests.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ojaj_gl as GL  # noqa: E402
import ojaj_2324 as T2324  # noqa: E402
import ojaj_uk as UK  # noqa: E402
import ojaj_own as OWN  # noqa: E402

with open(os.path.join(HERE, "ojaj_items.json"), encoding="utf-8") as _fh:
    ITEMS = json.load(_fh)

SRC = "https://ojaj.wsjo.pl/wp-content/uploads"


# --------------------------------------------------------------------------
# Repairs, keyed by (block, item number as printed on the paper)
# --------------------------------------------------------------------------

# Option text replaced, letter by letter.
OPTION_FIXES = {
    ("e2c1_grammar", 10): {"D": "is"},
    ("e2c1_grammar", 29): {"D": "paint"},
    ("e2c1_vocab", 40): {"D": "disciples"},
    ("e2c1_vocab", 63): {"A": "sole"},
    ("e3_vocab", 9): {"D": "will have been using"},
    ("e3_vocab", 10): {"D": "has gone / said"},
    # The keyed answer is printed in Polish; "preface" is the word the item
    # asks for, and without the fix the item has no correct option at all.
    ("e3_vocab", 14): {"D": "preface"},
    ("e3_vocab", 17): {"A": "is to be following"},
    ("e3_vocab", 20): {"D": "that Greg is saying"},
    ("e3_vocab", 23): {"D": "won't be reading"},
    ("e3_vocab", 30): {"D": "Should a child get"},
    # "Has" is a stray; the option stays ungrammatical, which is its job.
    ("e3_vocab", 33): {"D": "complained that he have"},
}

# Items the paper prints twice, or prints with two identical options.
DROPPED = {
    ("e1c2_verbs", 20),   # word for word the same item as number 1
    ("e2c1_grammar", 20),  # options a and c both read "for spreading"
}


def pick(block, numbers, task_id):
    """The named items of a block, repaired, renumbered under one task."""
    by_src = {it["_src"]: it for it in ITEMS[block]}
    out = []
    for n in numbers:
        if (block, n) in DROPPED:
            raise SystemExit(f"{block} {n} is dropped but still asked for")
        item = dict(by_src[n])
        fixes = OPTION_FIXES.get((block, n))
        if fixes:
            opts = list(item["options"])
            for letter, text in fixes.items():
                i = "ABCD".index(letter)
                opts[i] = f"{letter}) {text}"
            item["options"] = opts
        out.append({
            "id": f"{task_id}.{len(out) + 1}",
            "stem": item["stem"],
            "options": item["options"],
            "answer": item["answer"],
        })
    return out


def kept(block, first, last):
    """The printed numbers first..last of a block, minus the dropped ones."""
    return [n for n in range(first, last + 1) if (block, n) not in DROPPED]


def mc_exercise(ex_id, title, instruction, block, numbers, source):
    items = pick(block, numbers, "1")
    return ex_id, {
        "title": title,
        "type": "practice",
        "source": source,
        "tasks": [{
            "id": "1",
            "type": "multiple_choice",
            "points": len(items),
            "instruction": instruction,
            "items": items,
        }],
    }


# --------------------------------------------------------------------------
# Tests: 2022/2023, etap I czesc I, grupa A and grupa B
# --------------------------------------------------------------------------

TEST_INSTRUCTION = (
    "W każdym zdaniu znajduje się luka. Wybierz jedyną poprawną odpowiedź "
    "spośród czterech podanych. Za każdą poprawną odpowiedź otrzymujesz "
    "1 punkt."
)


def build_test(group, source):
    """One 60-item paper.

    The 2022/23 sitting's own time limit is not published anywhere I could
    find; 60 minutes is the competition's current rate of one minute per item
    (45 items in 45 minutes for the etap I and II written parts, 50 in 60 for
    the final -- ojaj.wsjo.pl/etapy-26-27/), applied to a 60-item paper.
    """
    items = pick(f"test_2223_{group.lower()}", range(1, 61), "1")
    return {
        "competition": "ojaj",
        "year": "2022/2023",
        "stage": f"szkolny-{group.lower()}",
        # The route slug is the only thing telling the two groups apart, and it
        # is not a name, so the paper carries the one the player shows.
        "label": f"Etap szkolny, cz. 1 (grupa {group})",
        "part": "1",
        "variant": group,
        "maxPoints": 60,
        "timeMinutes": 60,
        "source": source,
        "tasks": [{
            "id": "1",
            "type": "multiple_choice",
            "points": 60,
            "instruction": TEST_INSTRUCTION,
            "items": items,
        }],
    }


TEST_2223_A = build_test(
    "A", f"{SRC}/2025/09/Test-przykladowy-I-etap-I-czesc-2022_2023-Grupa-A.pdf"
)
TEST_2223_B = build_test(
    "B", f"{SRC}/2025/09/Test-przykladowy-I-etap-I-czesc-2022_2023-%E2%80%93-Grupa-B.pdf"
)

TESTS = [
    ("2022-2023/szkolny-a.json", TEST_2223_A),
    ("2022-2023/szkolny-b.json", TEST_2223_B),
]


# --------------------------------------------------------------------------
# Etap I, czesc II -- sample pool, 74 usable items
# --------------------------------------------------------------------------

E1C2_SRC = f"{SRC}/2025/06/etap-I-czesc-II-1.pdf"

INSTR_MC = (
    "W kazdym zdaniu znajduje sie luka. Wybierz jedyna poprawna odpowiedz "
    "sposrod czterech podanych."
)

E1C2_DO_ITEMS = [
    ("He'll do you a favour.", "C"),
    ("It does him credit.", "I"),
    ("John is having a do.", "G"),
    ("Susan just won't do.", "A"),
    ("Mary was doing over a hundred.", "J"),
    ("Jack does go on.", "E"),
    ("He'll make do.", "D"),
    ("Sam likes do-it-yourself.", "H"),
    ("Spiky won't do you any harm.", "B"),
    ("I could do with one.", "F"),
]

E1C2_DO_OPTIONS = [
    "She is unsatisfactory for the job.",
    "The dog is quite safe.",
    "He will help you.",
    "He can manage, don't worry.",
    "He talks all the time.",
    "I need one of those.",
    "It's his party on Saturday.",
    "His hobby is fixing his own house.",
    "It shows how good he is.",
    "She was driving extremely fast.",
]

E1C2_HEAD_ITEMS = [
    ("I never even thought of it.", "B"),
    ("I avoid attracting attention.", "J"),
    ("I made sure that something had to be decided.", "C"),
    ("I'm not a practically minded person.", "D"),
    ("I'm involved so far that it's out of my control.", "F"),
    ("I don't understand it at all.", "E"),
    ("I've gone mad.", "I"),
    ("I've let my feelings get out of control.", "H"),
    ("I never lose control of my emotions.", "A"),
    ("I find it really easy.", "G"),
]

E1C2_HEAD_OPTIONS = [
    "I always keep my head.",
    "It never entered my head.",
    "I brought matters to a head.",
    "My head is in the clouds.",
    "I can't make head or tail of it.",
    "I'm in way over my head.",
    "I could do it standing on my head.",
    "It's completely gone to my head.",
    "I'm off my head.",
    "I keep my head down.",
]


def matching_exercise(ex_id, title, instruction, statements, options, source):
    letters = [chr(ord("A") + i) for i in range(len(options))]
    return ex_id, {
        "title": title,
        "type": "practice",
        "source": source,
        "tasks": [{
            "id": "1",
            "type": "matching",
            "points": len(statements),
            "instruction": instruction,
            "options": [{"letter": l, "text": t} for l, t in zip(letters, options)],
            "items": [
                {"id": f"1.{i}", "statement": s, "answer": a}
                for i, (s, a) in enumerate(statements, start=1)
            ],
        }],
    }


# The paper prints item 21 with its first option's "a)" marker missing, so the
# parser cannot read it; the four options are as printed.
E1C2_ITEM_21 = {
    "id": "1.10",
    "stem": "If I _________ you I would cut down on chocolate and start going to the gym.",
    "options": ["A) am", "B) wasn't", "C) were", "D) weren't"],
    "answer": "C",
}


def e1c2_verbs_02():
    ex_id, ex = mc_exercise(
        "ojaj_e1p2_czasy_02",
        "OJAJ etap I cz. 2: formy czasownika (2)",
        INSTR_MC, "e1c2_verbs", kept("e1c2_verbs", 11, 19), E1C2_SRC,
    )
    ex["tasks"][0]["items"].append(E1C2_ITEM_21)
    ex["tasks"][0]["points"] = len(ex["tasks"][0]["items"])
    return ex_id, ex


E1C2_EXERCISES = [
    mc_exercise("ojaj_e1p2_czasy_01", "OJAJ etap I cz. 2: formy czasownika (1)",
                INSTR_MC, "e1c2_verbs", kept("e1c2_verbs", 1, 10), E1C2_SRC),
    e1c2_verbs_02(),
    matching_exercise(
        "ojaj_e1p2_idiomy_do", "OJAJ etap I cz. 2: idiomy z 'do'",
        "Dopasuj do kazdego zdania jego znaczenie (A-J). Kazde znaczenie pasuje "
        "do dokladnie jednego zdania.",
        E1C2_DO_ITEMS, E1C2_DO_OPTIONS, E1C2_SRC,
    ),
    mc_exercise("ojaj_e1p2_slownictwo_01", "OJAJ etap I cz. 2: slownictwo (1)",
                INSTR_MC, "e1c2_vocab_a", kept("e1c2_vocab_a", 32, 39), E1C2_SRC),
    mc_exercise("ojaj_e1p2_slownictwo_02", "OJAJ etap I cz. 2: slownictwo (2)",
                INSTR_MC, "e1c2_vocab_a", kept("e1c2_vocab_a", 40, 46), E1C2_SRC),
    mc_exercise("ojaj_e1p2_przyimki", "OJAJ etap I cz. 2: przyimki i czasowniki zlozone",
                INSTR_MC, "e1c2_prep", kept("e1c2_prep", 47, 56), E1C2_SRC),
    matching_exercise(
        "ojaj_e1p2_idiomy_head", "OJAJ etap I cz. 2: idiomy z 'head'",
        "Dopasuj do kazdego zdania idiom, ktory znaczy to samo (A-J). Kazdy "
        "idiom pasuje do dokladnie jednego zdania.",
        E1C2_HEAD_ITEMS, E1C2_HEAD_OPTIONS, E1C2_SRC,
    ),
    mc_exercise("ojaj_e1p2_slownictwo_03", "OJAJ etap I cz. 2: slownictwo (3)",
                INSTR_MC, "e1c2_vocab_b", kept("e1c2_vocab_b", 67, 75), E1C2_SRC),
]


# --------------------------------------------------------------------------
# Etap II, czesc I -- sample pool, 74 usable items
# --------------------------------------------------------------------------

E2C1_SRC = f"{SRC}/2025/06/etap-II-czesc-I.pdf"

E2C1_IDIOM_ITEMS = [
    ("to see eye to eye", "D"),
    ("to compare notes", "F"),
    ("to touch base with someone", "A"),
    ("to draw someone out", "C"),
    ("to clam up", "E"),
]

E2C1_IDIOM_OPTIONS = [
    "to talk to someone briefly",
    "to tell someone a secret",
    "to try to make someone talk about their feeling",
    "to agree with someone",
    "to refuse to talk",
    "to share opinions on something",
]

# Sentence, pattern, answer. The pattern appears in the sentence as printed.
E2C1_HANGMAN = [
    ("Doesn't Brian look __ __ E __ __ these days? He's really fat! Look at his "
     "double chin, chubby cheeks and plump hands.", "__ __ E __ __", "obese"),
    ("'Carl's a __ __ D __ __ T.' 'True! He's not even 1.20m! All of his "
     "classmates are much taller.'", "__ __ D __ __ T", "midget"),
    ("Mr Todd __ __ R __ __ D his lips tightly in a small circle, thinking. He "
     "always did this to show his doubt or disapproval.", "__ __ R __ __ D", "pursed"),
    ("The detective identified the woman by a small __ __ R __ __ M __ __ __ she "
     "had since she was born on her left shoulder.",
     "__ __ R __ __ M __ __ __", "birthmark"),
    ("If dad's going bald at that speed I guess he'll soon get himself a small "
     "__ O __ __ E __! He'll look hilarious!", "__ O __ __ E __", "toupee"),
    ("Alice smoothed the __ R __ A __ __ __ from her skirt and entered the office.",
     "__ R __ A __ __ __", "creases"),
    ("You must wear a __ L __ __ under this dress. It's almost transparent.",
     "__ L __ __", "slip"),
    ("Although she couldn't have her own children, she was the best "
     "__ O __ T __ __ mother ever.", "__ O __ T __ __", "foster"),
    ("I've always known you as Mrs Smith. What's your __ __ __ D __ N name?",
     "__ __ __ D __ N", "maiden"),
    ("I'm getting married in three months. Luke, will you be my "
     "__ E __ __ __ A __?", "__ E __ __ __ A __", "bestman"),
]

INSTR_HANGMAN = (
    "Uzupelnij brakujace litery. Liczba kreseczek odpowiada liczbie liter w "
    "wyrazie. Wymagana jest pelna poprawnosc ortograficzna."
)


def hangman_exercise(ex_id, title, rows, source):
    return ex_id, {
        "title": title,
        "type": "practice",
        "source": source,
        "tasks": [{
            "id": "1",
            "type": "word_spelling",
            "points": len(rows),
            "instruction": INSTR_HANGMAN,
            "items": [
                {"id": f"1.{i}", "sentence": s, "hint": h, "answer": [a]}
                for i, (s, h, a) in enumerate(rows, start=1)
            ],
        }],
    }


E2C1_EXERCISES = [
    matching_exercise(
        "ojaj_e2p1_idiomy", "OJAJ etap II cz. 1: idiomy",
        "Dopasuj do kazdego idiomu jego znaczenie (A-F). Jedno znaczenie jest "
        "dodatkowe i nie pasuje do zadnego idiomu.",
        E2C1_IDIOM_ITEMS, E2C1_IDIOM_OPTIONS, E2C1_SRC,
    ),
    mc_exercise("ojaj_e2p1_gramatyka_01", "OJAJ etap II cz. 1: gramatyka (1)",
                INSTR_MC, "e2c1_grammar", kept("e2c1_grammar", 6, 15), E2C1_SRC),
    mc_exercise("ojaj_e2p1_gramatyka_02", "OJAJ etap II cz. 1: gramatyka (2)",
                INSTR_MC, "e2c1_grammar", kept("e2c1_grammar", 16, 25), E2C1_SRC),
    mc_exercise("ojaj_e2p1_gramatyka_03", "OJAJ etap II cz. 1: gramatyka (3)",
                INSTR_MC, "e2c1_grammar", kept("e2c1_grammar", 26, 35), E2C1_SRC),
    mc_exercise("ojaj_e2p1_slownictwo_01", "OJAJ etap II cz. 1: slownictwo (1)",
                INSTR_MC, "e2c1_vocab", kept("e2c1_vocab", 36, 45), E2C1_SRC),
    mc_exercise("ojaj_e2p1_slownictwo_02", "OJAJ etap II cz. 1: czasowniki zlozone",
                INSTR_MC, "e2c1_vocab", kept("e2c1_vocab", 46, 55), E2C1_SRC),
    mc_exercise("ojaj_e2p1_slownictwo_03", "OJAJ etap II cz. 1: cialo i wyglad",
                INSTR_MC, "e2c1_vocab", kept("e2c1_vocab", 56, 65), E2C1_SRC),
    hangman_exercise("ojaj_e2p1_wisielec", "OJAJ etap II cz. 1: wisielec",
                     E2C1_HANGMAN, E2C1_SRC),
]


# --------------------------------------------------------------------------
# Etap III -- sample pool, 75 items
# --------------------------------------------------------------------------

E3_SRC = f"{SRC}/2025/06/Zestaw-I-z-kluczami.pdf"

E3_FORMATION = [
    ("Jessica has never even imagined she could be working as a/an __________ "
     "for the FBI.", "INFORM", "informant"),
    ("Every time my cat breaks something I see this __________ grin on its "
     "mouth - I swear!", "DEVIL", "devilish"),
    ("When I asked my dad if I could stay out late on Saturday night his answer "
     "was a/an __________ 'no'.", "DECIDE", "decisive"),
    ("The tradition of dressing a Christmas Tree __________ in Germany, right?",
     "ORIGIN", "originated"),
    ("Diane finally found __________ when she appeared in a film made by a "
     "famous Hollywood producer.", "FAMOUS", "fame"),
    ("Since flu is so highly __________ you should get vaccinated.",
     "INFECTION", "infectious"),
    ("Can you please make sure that all the electrical __________ in the "
     "kitchen are turned off?", "APPLY", "appliances"),
    ("I've never liked carrot cake and I knew it would taste __________ even "
     "before I tried it.", "HORROR", "horrible"),
    ("Joe wrote a __________ essay but the teacher rejected as saying it "
     "contained too many details.", "LONG", "lengthy"),
    ("The teacher tried really hard but the new students wasn't very __________ "
     "and didn't answer any of the questions.", "RESPOND", "responsive"),
]

E3_HANGMAN = [
    ("When your dad was a boy people didn't use GPS but an old fashioned map and "
     "a __ __ M __ __ __ __ to find their way.", "__ __ M __ __ __ __", "compass"),
    ("During this weekend we can expect over a hundred "
     "__ __ H __ __ __ T __ __ __ presenting their products at the book fair in "
     "Poznan.", "__ __ H __ __ __ T __ __ __", "exhibitors"),
    ("Mum brought dozens of holiday __ R __ __ __ __ R __ __ home yesterday and "
     "now we need to choose where to spend our summer vacation.",
     "__ R __ __ __ __ R __ __", "brochures"),
    # The paper's own sentence runs on into a clause left over from another
    # item ("...she had since she was born on her left shoulder"); dropped.
    ("This running event is highly popular as it's open to professionals as well "
     "as to __ __ __ T __ U __ __ .", "__ __ __ T __ U __ __", "amateurs"),
    ("The young guitarist is expecting his first __ __ Y __ __ __ Y payment as "
     "his brand new CD has just been released.", "__ __ Y __ __ __ Y", "royalty"),
    ("When Mary saw the exam results and realised that she failed she was on the "
     "__ __ R __ __ of tears.", "__ __ R __ __", "verge"),
    ("I hope that public TV will be able to __ R __ __ __ C __ __ __ the match "
     "as I can't watch EuroSport channel at home.",
     "__ R __ __ __ C __ __ __", "broadcast"),
    ("There are five __ U __ __ E __ __ __ boards on the walls of our school "
     "corridor. Students and teachers put there different information, pictures "
     "or posters prepared by the children.", "__ U __ __ E __ __ __", "bulletin"),
    ("I always check the __ __ N __ __ N __ __ page first. If it says that there "
     "are over 10 chapters in a book I don't read it - it's too long for me.",
     "__ __ N __ __ N __ __", "contents"),
    ("Haven't you got a __ __ C __ __ __ C __ you could take with you at the "
     "camp? It would be more comfortable than a suitcase as you could carry it "
     "on your shoulders.", "__ __ C __ __ __ C __", "rucksack"),
    ("'You have points taken away for both __ __ N __ __ U __ T __ __ __ and "
     "spelling mistakes, so if you forget to put a colon you'll lose priceless "
     "points.'", "__ __ N __ __ U __ T __ __ __", "punctuation"),
    ("Carl is a fan of __ __ B __ O __ __ __ . He enjoys reading about scandals "
     "and famous people and detests serious political news.",
     "__ __ B __ O __ __ __", "tabloids"),
    ("'__ __ M __ __ R has it that the vice principal has been sacked!' 'I don't "
     "believe it, it's just gossip.'", "__ __ M __ __ R", "rumour"),
    ("'To be or not to be, that is the question,' he __ __ O __ E __ from "
     "Shakespeare.", "__ __ O __ E __", "quoted"),
    ("'Do you know the __ __ B __ __ V __ __ __ I __ __ of the phrase "
     "'for example'?' 'Sure, it's e.g.'", "__ __ B __ __ V __ __ __ I __ __",
     "abbreviation"),
]

E3_EXERCISES = [
    ("ojaj_e3_slowotworstwo", {
        "title": "OJAJ etap III: slowotworstwo",
        "type": "practice",
        "source": E3_SRC,
        "tasks": [{
            "id": "1",
            "type": "word_formation",
            "points": len(E3_FORMATION),
            "instruction": (
                "Uzupelnij kazde zdanie slowem utworzonym od wyrazu podanego "
                "wielkimi literami. Wymagana jest pelna poprawnosc ortograficzna."
            ),
            "items": [
                {"id": f"1.{i}", "sentence": s, "wordBase": base, "answer": [a]}
                for i, (s, base, a) in enumerate(E3_FORMATION, start=1)
            ],
        }],
    }),
    mc_exercise("ojaj_e3_slownictwo_01", "OJAJ etap III: slownictwo (1)",
                INSTR_MC, "e3_vocab", range(1, 11), E3_SRC),
    mc_exercise("ojaj_e3_slownictwo_02", "OJAJ etap III: slownictwo (2)",
                INSTR_MC, "e3_vocab", range(11, 21), E3_SRC),
    mc_exercise("ojaj_e3_slownictwo_03", "OJAJ etap III: slownictwo (3)",
                INSTR_MC, "e3_vocab", range(21, 31), E3_SRC),
    mc_exercise("ojaj_e3_slownictwo_04", "OJAJ etap III: slownictwo (4)",
                INSTR_MC, "e3_vocab", range(31, 41), E3_SRC),
    mc_exercise("ojaj_e3_slownictwo_05", "OJAJ etap III: slownictwo (5)",
                INSTR_MC, "e3_vocab", range(41, 51), E3_SRC),
    hangman_exercise("ojaj_e3_wisielec_01", "OJAJ etap III: wisielec (1)",
                     E3_HANGMAN[:8], E3_SRC),
    hangman_exercise("ojaj_e3_wisielec_02", "OJAJ etap III: wisielec (2)",
                     E3_HANGMAN[8:], E3_SRC),
]


# --------------------------------------------------------------------------
# What the generator consumes
# --------------------------------------------------------------------------

# Each exercise carries the paper it came from, so the OJAJ page can group the
# list instead of showing forty-four rows in a row. The third batch (the two
# gramatyczno-leksykalny papers, read off page images) adds its own groups from
# tools/ojaj/ojaj_gl.py, and so do the 2023/24 paper (tools/ojaj/ojaj_2324.py) and the
# self-written UK-culture sets (tools/ojaj/ojaj_uk.py); the generator reads only EXERCISES and GROUP_OF, so nothing
# there needed changing to pick them up.
GROUPS = [
    ("Etap I, czesc 2 - test przykladowy", E1C2_EXERCISES),
    ("Etap II, czesc 1 - test przykladowy", E2C1_EXERCISES),
    ("Etap III - test przykladowy", E3_EXERCISES),
] + GL.GROUPS + T2324.GROUPS + UK.GROUPS + OWN.GROUPS

EXERCISES = [pair for _, group in GROUPS for pair in group]

GROUP_OF = {ex_id: name for name, group in GROUPS for ex_id, _ in group}

EDITION_2223 = {
    "year": "2022/2023",
    "yearPath": "2022-2023",
    "stages": [
        {
            "stage": "szkolny-a",
            "label": TEST_2223_A["label"],
            "part": "1",
            "variant": "A",
            "maxPoints": TEST_2223_A["maxPoints"],
            "timeMinutes": TEST_2223_A["timeMinutes"],
        },
        {
            "stage": "szkolny-b",
            "label": TEST_2223_B["label"],
            "part": "1",
            "variant": "B",
            "maxPoints": TEST_2223_B["maxPoints"],
            "timeMinutes": TEST_2223_B["timeMinutes"],
        },
    ],
}
