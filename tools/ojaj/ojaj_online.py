#!/usr/bin/env python3
"""The vault of own items the OJAJ online tests (etap I, czesc II) are put
together from, written for this app.

The real etap I, czesc II is a 45-minute online test of 45 one-point
questions, generated for each student from a pool of tasks (programme 2026/27,
section 1.2). Its pool is not published, so every item here is the app's own.
One online test is five tasks in a fixed order:

    1  word formation                        10 items   word_formation
    2  wisielec                              10 items   word_spelling
    3  key word transformations (AI-marked)  10 items   sentence_transformation
    4  grammar and vocabulary, choice        10 items   multiple_choice
    5  UK culture, choice                     5 items   knowledge_questions

A batch holds all five tasks, or (since 2026-11-11) one task alone, as many
items as a full batch has of it and numbered as there, which join that task
of the vault (build_one_task_batch).

Since 2026-11-18 it also holds the semi-final pool (etap polfinalowy, czesc
I, 7.12.2026): full batches S01 up in SEMI_TESTS, checked to the harder
SEMI_LEVEL_RANGE, with USA culture in task 5 (the usa-* types), and against
every etap I item so the pools share none (built_semi_tests). Their printouts
are tmp/ojaj_semi_SNN_review.md. They are not written into vault.json, whose
mistake types stay etap I's (pool_types).

Run:  python3 -I tools/ojaj/ojaj_online.py
Checks every batch in TESTS and writes tmp/ojaj_online_NN_review.md, a
printout of each for review, and tmp/ojaj_mistake_types_review.md. It also
checks the own wisielec exercises in the online test's shape
(ojaj_own.HANGMAN_ONLINE, check_own_exercises) and prints them to
tmp/ojaj_own_wisielec_review.md. The app
does not serve the batches as tests: tools/ojaj/gen_ojaj.py writes them all into
one vault, pub/konkursy/angielski/data/ojaj/online/vault.json (build_vault),
and the app puts each test together from it at the draw, aimed at the
pupil's mistakes (site/src/lib/ojajDraw.js).

Level target (settled 2026-10-24, evidence in tools/ojaj/ojaj_level_compare.py):
match the 2024/25 part I paper plus the part II sample's idioms. Per 10-item
task in tasks 1-4: about 1 B1, 4 B2, 4-5 C1 and 0-1 C2, mixed so position does
not signal difficulty. In tasks 2 and 4, 3-4 items test an idiom, a
collocation or a phrasal verb. Every item carries `level`; those items also
carry `focus`. Task 5 is knowledge, so it has no level.

Writing rules the items keep to:
  - word formation: the sentence allows exactly one derived word; British and
    American spellings are both listed.
  - wisielec: the 2024/25 paper's shape, given letters in lower case and the
    letter count in brackets. As many given letters as the papers give for a
    word of that length (given_letters), never the letters the item tests. The
    sentence pins the word down, and the given letters rule out any other word
    of that length that could fill the gap; tools/ojaj/wisielec_letters.py lists the
    dictionary words a pattern still fits.
  - transformations: the keyword unchanged in every accepted answer, at most
    six words, no contractions (a possessive 's is not one), alternatives
    joined with " / ". The AI checker accepts a listed phrasing without a call,
    so the key lists every phrasing a marker would accept.
  - choice: four options, every wrong option a real form; the renderer
    shuffles grammar options, the culture options stay in order.
  - no prompt, and no word-formation or wisielec answer, that already appears
    as an item anywhere in the app (papers, practice, quest).
"""

import glob
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gen_ojaj import check_choice, check_spelling  # noqa: E402
import ojaj_own as OWN  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA = os.path.join(ROOT, "pub", "konkursy", "angielski", "data")
TMP = os.path.join(ROOT, "tmp")

GAP = "_________"        # exactly nine: SentenceTransformation splits on it
BLANK = "__________"     # word formation splits on any run of two or more

LEVELS = ["B1", "B2", "C1", "C2"]
FOCI = {"idiom", "collocation", "phrasal verb"}

# The level profile of tasks 1-4, and how many items of tasks 2 and 4 test an
# idiom, a collocation or a phrasal verb (settled 2026-10-24). check_profile
# holds every batch to it, and the vault carries it, so the app puts every
# drawn test together to the same profile.
LEVEL_RANGE = {"B1": (0, 2), "B2": (3, 5), "C1": (4, 5), "C2": (0, 1)}
# The semi-final pool's profile (settled 2026-11-18): harder than etap I's,
# after his feedback that the real etap I online test was harder than the
# vault, and calibrated on the etap II czesc I sample (ojaj_e2p1_*). No B1.
SEMI_LEVEL_RANGE = {"B1": (0, 0), "B2": (2, 3), "C1": (5, 6), "C2": (1, 2)}
FOCUS_RANGE = (3, 4)
FOCUS_TASKS = ("word_spelling", "multiple_choice")

# Mistake types (settled 2026-10-24, tools/ojaj/notes/HANDOFF_ojaj_mistakes.md). Each item
# has exactly one: the point that makes it hard. A miss counts against the
# item's type, and the next tests draw more unseen items of the types he
# misses. The list is shared across tasks, so -ance/-ence covers both word
# formation and wisielec.
#   (key, label shown to the pupil, what it covers, tasks it may appear in,
#    link)
# The link is the page the OJAJ page's weak-points list points to for the
# type (settled 2026-10-25, tools/ojaj/notes/HANDOFF_ojaj_learning_material.md): its own
# study page, the transformations checklist for the grammar types without a
# page yet, a section of the UK notebook, or None. The study pages are static
# files in site/public/ojaj_study/, built on the ojaj-study-pages branch; the
# vault carries a study link only once its page is there (vault_link).
_TYPE_ROWS = [
    # Building a word (tasks 1-2)
    ("negative-prefix", "przedrostki przeczace (un-, in-, im-, il-, ir-, dis-)",
     "which negative prefix, and not leaving it off (inaccessible, "
     "irreparable)", (1, 2), "/ojaj_study/negative-prefix"),
    ("ance-ence", "-ance czy -ence",
     "the -ance / -ence ending, -ant / -ent too (resemblance, acquaintance)",
     (1, 2), "/ojaj_study/ance-ence"),
    ("able-ible", "-able czy -ible",
     "the -able / -ible ending (gullible, accessible)", (1, 2), None),
    ("base-change", "zmiana w srodku slowa (pronounce - pronunciation)",
     "the base word changes inside, not only at the end (pronunciation, "
     "hindrance, suspicious)", (1, 2), "/ojaj_study/base-change"),
    ("suffix-spelling", "pisownia przy dodawaniu koncowki (e, y - i, -ally)",
     "spelling where an ending joins the base: e kept or dropped, y to i, "
     "-ally (knowledgeable, laziness, accidentally); a doubled letter is "
     "double-letters", (1, 2), "/ojaj_study/suffix-spelling"),
    ("two-steps", "slowo budowane w dwoch krokach (origin - originality)",
     "a word built in two or more steps, usually an adverb or a noun from a "
     "derived adjective (passionately, originality)", (1, 2), None),
    ("word-ending", "wybor koncowki (-ness, -ity, -ish, -eer)",
     "which ending makes the noun, adjective or adverb the sentence needs "
     "(childish, willingness, engineer)", (1, 2), None),
    # Spelling (tasks 1-2)
    ("double-letters", "podwojne litery",
     "double or single letters (embarrassment, millennium, questionnaire)",
     (1, 2), "/ojaj_study/double-letters"),
    ("silent-letters", "litery, ktorych nie slychac",
     "letters not heard in speech (rhythm, queue, guarantee)", (1, 2),
     "/ojaj_study/silent-letters"),
    ("vowels", "samogloski, ktorych nie slychac wyraznie",
     "vowels that sound alike when unstressed (definitely, privilege, "
     "mischievous)", (1, 2), "/ojaj_study/vowels"),
    # Vocabulary (tasks 2-4); an item with a focus has its focus as its type
    ("idiom", "idiomy", "idioms (under the weather, over the moon)",
     (2, 3, 4), None),
    ("collocation", "kolokacje (make an effort, rave reviews)",
     "words that go together (reach a compromise, torrential rain)",
     (2, 3, 4), None),
    ("phrasal-verb", "czasowniki frazowe", "phrasal verbs (put up with, "
     "come across)", (2, 3, 4), None),
    # Grammar (tasks 3-4)
    ("conditionals", "zdania warunkowe i wish",
     "conditionals, mixed and inverted ones, wish, as long as, supposing",
     (3, 4), "/ojaj_study/conditionals"),
    ("inversion", "inwersja (Little did I know, Only when ...)",
     "inversion after a negative or limiting word", (3, 4),
     "/ojaj_study/inversion"),
    ("reported-speech", "mowa zalezna i pytania posrednie",
     "reported statements, questions and commands; indirect questions "
     "(I wonder if)", (3, 4), "/ojaj_study/transformations"),
    ("passive", "strona bierna",
     "the passive, with modals and reporting verbs (is known to be)", (3, 4),
     "/ojaj_study/transformations"),
    ("modals", "czasowniki modalne (should have, be supposed to)",
     "modal verbs and their stand-ins (bound to, supposed to)", (3, 4),
     "/ojaj_study/transformations"),
    ("verb-patterns", "-ing czy to (can't help laughing)",
     "what form follows a verb or phrase (help laughing, forget seeing, "
     "no idea how to)", (3, 4), "/ojaj_study/transformations"),
    ("relative-clauses", "zdania wzgledne (whose, about whom)",
     "relative clauses (whose, about whom, both of whom)", (3, 4),
     "/ojaj_study/relative-clauses"),
    ("comparison", "stopniowanie i porownania",
     "comparatives, superlatives, too and enough", (3, 4),
     "/ojaj_study/comparison"),
    ("tenses", "czasy i operatory (present perfect, question tags)",
     "tenses and auxiliaries (since, future perfect, used to, question "
     "tags)", (3, 4), "/ojaj_study/transformations"),
    ("participle-clauses", "imieslowy (Having seen, Woken by)",
     "participle clauses", (3, 4), "/ojaj_study/transformations"),
    ("linking-words", "wyrazenia laczace (nobody but, strange as it may "
     "seem)", "linking and contrast words (nobody but, adjective + as + "
     "clause)", (3, 4), "/ojaj_study/transformations"),
    # UK culture (task 5): the branches of the mind map
    ("uk-symbols", "UK: symbole", "Symbols of the UK", (5,),
     "/ojaj_uk#symbols"),
    ("uk-countries", "UK: cztery kraje", "The four countries of the UK",
     (5,), "/ojaj_uk#nations"),
    ("uk-politics", "UK: parlament i polityka", "Political life", (5,),
     "/ojaj_uk#parliament"),
    ("uk-history", "UK: wydarzenia historyczne", "Selected historical events",
     (5,), "/ojaj_uk#history"),
    ("uk-people", "UK: slynni Brytyjczycy", "Notable Britons", (5,),
     "/ojaj_uk#britons"),
    ("uk-london", "UK: zabytki Londynu", "Landmarks of London", (5,),
     "/ojaj_uk#landmarks"),
    ("uk-parks", "UK: parki krolewskie", "London's Royal Parks", (5,),
     "/ojaj_uk#parks"),
    # USA culture (task 5 of the semi-final pool): the branches of the
    # semi-final's mind map (OJAJ-2026_2027-USA.pdf). No notebook yet, so no
    # links.
    ("usa-native", "USA: historia rdzennych Amerykanow",
     "Native American history", (5,), None),
    ("usa-symbols", "USA: symbole narodowe", "National emblems of the USA",
     (5,), None),
    ("usa-landmarks", "USA: pomniki i cuda natury",
     "Landmarks: monuments and natural landmarks", (5,), None),
    ("usa-culture", "USA: uczelnie, muzea, nagrody, komiksy",
     "Education, museums, awards and ceremonies, comics and superheroes",
     (5,), None),
    ("usa-constitution", "USA: Konstytucja i poprawki",
     "Politics: the U.S. Constitution and its amendments", (5,), None),
    ("usa-civil-rights", "USA: ruch praw obywatelskich",
     "The Civil Rights Movement", (5,), None),
    ("usa-cold-war", "USA: zimna wojna", "The Cold War", (5,), None),
]
MISTAKE_TYPES = {key: {"label": label, "covers": covers, "tasks": tasks,
                       "link": link}
                 for key, label, covers, tasks, link in _TYPE_ROWS}
FOCUS_TYPE = {"idiom": "idiom", "collocation": "collocation",
              "phrasal verb": "phrasal-verb"}
# Each pool's culture: the prefix of the types its task 5 may carry.
ETAP1_CULTURE = "uk-"
SEMI_CULTURE = "usa-"

# Instructions as printed on the papers, with diacritics (competition
# convention for timed tests). Tasks 1, 2, 4 and 5: the 2024/25 paper. Task 3:
# the 2023/24 paper, read off the page image (tools/ojaj/pdfs/hi_A-3.png); its
# example has no answer in the key, so it is left out.
INSTR = {
    "word_formation": (
        "W każdą z luk wpisz odpowiednie słowo przekształcając wyraz podany na "
        "końcu zdania drukowanymi literami. Wymagana jest pełna poprawność "
        "gramatyczna i ortograficzna wpisywanych słów.\n\n"
        "Przykład: The __________ (SERVE) in this restaurant was absolutely "
        "appalling. — prawidłowa odpowiedź: SERVICE"
    ),
    "word_spelling": (
        "Wpisz słowo poprawnie uzupełniające każde ze zdań. Liczba kreseczek "
        "odpowiada liczbie liter w słowie. Wymagana jest pełna poprawność "
        "gramatyczna i ortograficzna wpisywanych słów.\n\n"
        "Przykład: She asked for a(n) __ __ e __ __ __ i __ (8) type of flower "
        "for her bouquet. — prawidłowa odpowiedź: SPECIFIC"
    ),
    "sentence_transformation": (
        "Wykorzystując podane słowa (wyróżnione pogrubionym drukiem), należy "
        "uzupełnić luki w zdaniach tak, aby zachować sens zdania wyjściowego. "
        "Można wpisać do sześciu słów, wliczając w to wyraz wymagany. Słów "
        "podanych nie wolno w żaden sposób zmieniać. Niedopuszczalne są formy "
        "skrócone (isn't, won't, would've itd.). Konieczna jest pełna "
        "poprawność gramatyczna i ortograficzna wpisywanych fraz."
    ),
    "multiple_choice": (
        "Uzupełnij lukę w każdym ze zdań, wybierając jedną poprawną odpowiedź "
        "z zaproponowanych możliwości A) – D)."
    ),
    "knowledge_questions": (
        "Odpowiedz na pytania wybierając jedną poprawną odpowiedź z "
        "zaproponowanych możliwości A) – D)."
    ),
}

# --------------------------------------------------------------------------
# Test 01
# --------------------------------------------------------------------------
# Every row ends with (level, focus, what the item tests, mistake type).
# focus is None unless the item tests an idiom, a collocation or a phrasal
# verb; the mistake type is a key of MISTAKE_TYPES.

T01 = {
    # (sentence with {} for the blank, base word, [answers], level, focus, tests)
    "formation": [
        ("After the renovation our old school was almost {}: nobody could "
         "believe it was the same building.", "RECOGNISE",
         ["unrecognisable", "unrecognizable"], "C1", None,
         "un- + -able on a verb; both spellings", "negative-prefix"),
        ("These new shoes are so {} that I can hardly walk in them.",
         "COMFORT", ["uncomfortable"], "B1", None, "negative adjective",
         "negative-prefix"),
        ("When the singer walked onto the stage right in front of us, my "
         "sister was completely {}: she just stood there with her mouth open.",
         "SPEAK", ["speechless"], "C1", None,
         "noun change (speak -> speech) + -less", "base-change"),
        ("He went red with {} when he realised that everyone on the bus had "
         "heard him singing.", "EMBARRASS", ["embarrassment"], "B2", None,
         "noun; double r, double s", "double-letters"),
        ("The flood caused {} damage to the old church, and it will never "
         "look the same again.", "REPAIR", ["irreparable"], "C2", None,
         "ir- + stem change (repair -> repar-)", "negative-prefix"),
        ("Stop being so {}! You are fourteen, not four.", "CHILD",
         ["childish"], "B2", None, "-ish, negative sense (not childlike)",
         "word-ending"),
        ("My brother is the most {} person I know: it takes him twenty "
         "minutes to choose an ice-cream flavour.", "DECIDE", ["indecisive"],
         "C1", None, "in- + -ive with stem change (decide -> decis-)",
         "negative-prefix"),
        ("The view from the top of the mountain was {}: I will remember it "
         "for the rest of my life.", "FORGET", ["unforgettable"], "B2", None,
         "un- + -able, double t", "double-letters"),
        ("Mum shook her head in {} when she saw the mess in my room.",
         "APPROVE", ["disapproval"], "C1", None, "dis- + noun in -al",
         "negative-prefix"),
        ("I {} deleted all my holiday photos when I was trying to free up "
         "some space on my phone.", "ACCIDENT", ["accidentally"], "B2", None,
         "adverb in -ally (not *accidently)", "suffix-spelling"),
    ],
    # (sentence with {} for the pattern, compact pattern, answer, level,
    #  focus, tests). Compact pattern: one character per letter, _ = blank.
    "hangman": [
        ("I'm feeling a bit under the {} today, so I think I'll stay in bed.",
         "w___h__", "weather", "C1", "idiom",
         "under the weather", "idiom"),
        ("I'm {} coming to your party on Saturday: I wouldn't miss it for "
         "anything!", "d_f_____l_", "definitely", "B1", None,
         "spelling (not *definately)", "vowels"),
        ("The mosquitoes were a real {} on our camping trip: nobody could "
         "sleep.", "n_____c_", "nuisance", "C1", None, "spelling",
         "ance-ence"),
        ("Don't {}! It was only a small spider, not a giant one.",
         "e__g____t_", "exaggerate", "B2", None,
         "double g, single r; the g rules out exasperate", "double-letters"),
        ("After an hour of arguing about which film to watch, my parents "
         "finally reached a {}: we watched half of each.", "__m_r___s_",
         "compromise", "C1", "collocation", "reach a compromise",
         "collocation"),
        ("The jeweller told us that the ring was not {}: the stones were only "
         "coloured glass.", "g__u___", "genuine", "B2", None, "spelling",
         "vowels"),
        ("I think I've {} off more than I can chew: I've joined four clubs "
         "and I have no time left for homework.", "b_t___", "bitten", "C1",
         "idiom", "bite off more than you can chew; irregular participle",
         "idiom"),
        ("My little brother is so {} that he believed me when I told him "
         "that spaghetti grows on trees.", "g_l_____", "gullible", "C2",
         None, "spelling", "able-ible"),
        ("My grandma paid me a {} on my new haircut, which really made my "
         "day.", "c___li____", "compliment", "B2", "collocation",
         "pay someone a compliment; the i rules out complement",
         "collocation"),
        ("The comedy we watched last night was absolutely {}: we laughed from "
         "beginning to end.", "h_l_r____", "hilarious", "B2", None,
         "spelling", "vowels"),
    ],
    # (original, keyword, transformed with {} for the gap, answer, level,
    #  focus, tests)
    "transform": [
        ("I am hungry now because I did not have breakfast.", "HAD",
         "I would not be hungry now {} breakfast.",
         "if I had had / if I had eaten", "C1", None,
         "mixed conditional (past cause, present result)", "conditionals"),
        ("Everyone expects you to be at school by eight o'clock.", "SUPPOSED",
         "You {} at school by eight o'clock.", "are supposed to be", "B2",
         None, "be supposed to", "modals"),
        ("I have two older brothers. They both play in the school band.",
         "BOTH", "I have two older brothers, {} play in the school band.",
         "both of whom", "C1", None,
         "non-defining relative clause with a quantifier", "relative-clauses"),
        ("The box was so heavy that I could not lift it.", "TOO",
         "The box was {} lift.", "too heavy for me to", "B1", None,
         "too + adjective + for + object + to", "comparison"),
        ("I had no idea that my friends were planning a surprise party for "
         "me.", "LITTLE", "{} my friends were planning a surprise party for "
         "me.",
         "Little did I know that / Little did I know / "
         "Little did I realise that / Little did I realise / "
         "Little did I realize that / Little did I realize / "
         "Little did I suspect that / Little did I suspect",
         "C2", None, "inversion after a negative adverbial", "inversion"),
        ("'Don't swim too far from the beach,' the lifeguard said to us.",
         "WARNED", "The lifeguard {} too far from the beach.",
         "warned us not to swim / warned us against swimming", "B2", None,
         "reported command", "reported-speech"),
        ("It was Kasia's fault that the vase got broken.", "BLAME",
         "Kasia {} the broken vase.",
         "was to blame for / was the one to blame for", "C1", "collocation",
         "be to blame for", "collocation"),
        ("I cannot tolerate my brother's loud music any longer.", "PUT",
         "I cannot {} my brother's loud music any longer.", "put up with",
         "B2", "phrasal verb", "put up with", "phrasal-verb"),
        ("Everyone was surprised when Tom won the race.", "MUCH",
         "{} surprise, Tom won the race.",
         "Much to everyone's / Much to everybody's", "C1", "idiom",
         "much to someone's surprise", "idiom"),
        ("You can borrow my bike, but only if you bring it back by six.",
         "LONG", "You can borrow my bike {} it back by six.",
         "as long as you bring / so long as you bring / "
         "as long as you give / so long as you give", "B2", None,
         "condition: as long as", "conditionals"),
    ],
    # (stem with {} for the gap, [four options], answer letter, level, focus,
    #  tests)
    "choice": [
        ("My bike isn't where I left it. It must {} while I was in the shop.",
         ["have stolen", "have been stolen", "be stolen", "be stealing"], "B",
         "C1", None, "passive with a modal of deduction about the past",
         "passive"),
        ("I {} to the zoo since I was a little kid.",
         ["didn't go", "wasn't", "haven't been", "don't go"], "C", "B1", None,
         "present perfect with since", "tenses"),
        ("You've hit the {} on the head: that's exactly what the problem is.",
         ["nail", "spot", "point", "hammer"], "A", "C1", "idiom",
         "hit the nail on the head", "idiom"),
        ("Our teacher asked us {} the homework.",
         ["if we had finished", "had we finished", "did we finish",
          "that we had finished"], "A", "B2", None,
         "reported question: word order", "reported-speech"),
        ("The fire alarm went {} in the middle of our maths test, so we all "
         "had to leave the building.", ["out", "up", "over", "off"], "D",
         "B2", "phrasal verb", "go off (an alarm)", "phrasal-verb"),
        ("The new student, {} we had heard so much, turned out to be really "
         "shy.", ["who", "that", "about whom", "about which"], "C", "C1",
         None, "relative clause with a fronted preposition",
         "relative-clauses"),
        ("By the time we get to the cinema, the film {}, so we'll miss the "
         "beginning.", ["will start", "will have started", "has started",
                        "is starting"], "B", "B2", None, "future perfect",
         "tenses"),
        ("She made a {} effort to be friendly to the new girl in her class.",
         ["knowing", "sensible", "aware", "conscious"], "D", "C1",
         "collocation", "make a conscious effort", "collocation"),
        ("When Grandma heard that I had won the competition, she was over "
         "the {}.", ["sun", "moon", "stars", "rainbow"], "B", "B2", "idiom",
         "over the moon", "idiom"),
        ("{} you need any help with your project, just give me a call.",
         ["Should", "Would", "Had", "Were"], "A", "C1", None,
         "conditional with inversion (should)", "conditionals"),
    ],
    # (question, [four options], answer letter, mind-map branch). Facts
    # checked against site/public/ojaj_uk.html.
    "culture": [
        ("What nickname is often used for the Conservative Party and its "
         "members?", ["the Whigs", "the Tories", "the Roundheads",
                      "the Jacobites"], "B",
         "Political life: two major political parties", "uk-politics"),
        ("What is the last step before a bill passed by both Houses of "
         "Parliament becomes law?",
         ["Royal Assent", "the King's Speech", "a referendum",
          "the State Opening of Parliament"], "A",
         "Political life: the three components", "uk-politics"),
        ("At which London address did Sherlock Holmes live in Arthur Conan "
         "Doyle's stories?",
         ["10 Downing Street", "32 Windsor Gardens", "221B Baker Street",
          "17 Cherry Tree Lane"], "C", "Notable Britons: Arthur Conan Doyle",
         "uk-people"),
        ("Which event took place in Hyde Park in 1851?",
         ["the coronation of Queen Victoria", "the first modern Olympic Games",
          "the opening of the first Underground line",
          "the Great Exhibition in the Crystal Palace"], "D",
         "London's Royal Parks: Hyde Park, history", "uk-parks"),
        ("Which is the oldest part of the Tower of London, begun by William "
         "the Conqueror?",
         ["the Bloody Tower", "the White Tower", "Traitors' Gate",
          "the Jewel House"], "B", "Landmarks of London: Tower of London",
         "uk-london"),
    ],
}

# --------------------------------------------------------------------------
# Test 02
# --------------------------------------------------------------------------

T02 = {
    "formation": [
        ("The {} between the twins is amazing: even their own parents "
         "sometimes mix them up.", "RESEMBLE", ["resemblance"], "C1", None,
         "noun in -ance", "ance-ence"),
        ("I lost three points for {} mistakes, even though I knew all the "
         "answers!", "CARE", ["careless"], "B1", None, "-less adjective",
         "word-ending"),
        ("In winter the mountain village is {} by car, so food and medicine "
         "arrive by helicopter.", "ACCESS", ["inaccessible"], "C1", None,
         "in- + -ible", "negative-prefix"),
        ("Her English {} is excellent: everyone thinks she grew up in "
         "London.", "PRONOUNCE", ["pronunciation"], "B2", None,
         "stem change (pronounce -> pronunc-)", "base-change"),
        ("We have just moved to a quiet {} with lots of trees and hardly any "
         "traffic.", "NEIGHBOUR", ["neighbourhood", "neighborhood"], "B2",
         None, "-hood; both spellings", "word-ending"),
        ("The bad weather was a real {} to the rescue team, who could not use "
         "their helicopter.", "HINDER", ["hindrance"], "C2", None,
         "stem change (hinder -> hindr-) + -ance", "base-change"),
        ("The shop assistant became {} when the boy kept looking around "
         "nervously and putting things into his pockets.", "SUSPECT",
         ["suspicious"], "B2", None, "-ious with stem change (suspect -> "
         "suspic-)", "base-change"),
        ("It was really {} of you to play loud music while your brother was "
         "revising for his exams.", "CONSIDER", ["inconsiderate"], "C1", None,
         "in- + -ate (not inconsiderable)", "negative-prefix"),
        ("My brother's {} is unbelievable: he spent the whole weekend lying "
         "on the sofa.", "LAZY", ["laziness"], "B2", None, "-ness, y -> i",
         "suffix-spelling"),
        ("Our guide was very {}: she could answer every question we asked "
         "about the castle.", "KNOW", ["knowledgeable"], "C1", None,
         "noun + -able, keeping the e (the rare variant knowledgable is not "
         "listed)", "suffix-spelling"),
    ],
    "hangman": [
        ("I always get {} in my stomach before I have to speak in front of "
         "the class.", "b_____f___s", "butterflies", "C1", "idiom",
         "have butterflies in your stomach", "idiom"),
        ("Can you keep a {}? I'm planning a surprise party for Mum.",
         "s_c___", "secret", "B1", "collocation", "keep a secret",
         "collocation"),
        ("The shop gives a two-year {} on all its laptops, so if one breaks, "
         "they repair it for free.", "g_a_a____", "guarantee", "B2", None,
         "spelling (gua-, double e); the length rules out warranty",
         "silent-letters"),
        ("My little brother is so {}: yesterday he hid Dad's car keys in the "
         "fridge.", "m___h___o__", "mischievous", "C1", None,
         "spelling (not *mischievious, which is one letter longer)", "vowels"),
        ("I can't {} out how to switch off the alarm on my new watch.",
         "f_g___", "figure", "B2", "phrasal verb", "figure out",
         "phrasal-verb"),
        ("Kasia is a very {} pupil: she always does her homework carefully "
         "and hands it in on time.", "c___c___t___s", "conscientious", "C2",
         None, "spelling (-sci-, -tious)", "silent-letters"),
        ("There was a long {} outside the cinema, so we waited for half an "
         "hour.", "q____", "queue", "B2", None, "spelling (ueue)",
         "silent-letters"),
        ("Missing the school bus was a blessing in {}: I walked to school "
         "instead and found a lost puppy, who is now our dog.", "____u_s_",
         "disguise", "C1", "idiom", "a blessing in disguise; silent u",
         "idiom"),
        ("Mum keeps her {} in a small wooden box: two rings, a necklace and a "
         "pair of earrings.", "j__e____y", "jewellery", "B2", None,
         "British spelling, double l (American jewelry is two letters "
         "shorter)", "double-letters"),
        ("She isn't really a friend, just an {} from my old school.",
         "a_____n____e", "acquaintance", "C1", None,
         "spelling (acq-, -ance)", "ance-ence"),
    ],
    "transform": [
        ("Nobody in my class is taller than Kuba.", "TALLEST",
         "Kuba is {} in my class.",
         "the tallest boy / the tallest pupil / the tallest student / "
         "the tallest person / the tallest child / the tallest", "B1", None,
         "superlative from a comparative with nobody", "comparison"),
        ("When I saw my dad's new haircut, I couldn't stop laughing.", "HELP",
         "When I saw my dad's new haircut, I {}.",
         "could not help laughing / could not help but laugh", "C1", None,
         "cannot help + -ing", "verb-patterns"),
        ("'Do you like pizza?' my new classmate said to me.", "ASKED",
         "My new classmate {} pizza.",
         "asked me if I liked / asked me whether I liked / "
         "asked if I liked / asked whether I liked", "B2", None,
         "reported yes/no question, tense back-shift", "reported-speech"),
        ("The film was not as good as I had expected.", "LIVE",
         "The film did not {} expectations.", "live up to my / live up to",
         "C1", "phrasal verb", "live up to", "phrasal-verb"),
        ("I don't know how to solve this maths problem.", "IDEA",
         "I have {} this maths problem.",
         "no idea how to solve / no idea how I can solve / "
         "no idea how I should solve", "B2", None,
         "have no idea + how to", "verb-patterns"),
        ("Kasia is the only person who can help us.", "BUT",
         "Nobody {} us.", "but Kasia can help / but Kasia is able to help",
         "C1", None, "nobody but", "linking-words"),
        ("There is no milk left in the fridge.", "RUN",
         "We have {} milk.", "run out of", "B2", "phrasal verb",
         "run out of", "phrasal-verb"),
        ("You must not open this door under any circumstances.",
         "CIRCUMSTANCES", "Under {} this door.",
         "no circumstances must you open / no circumstances should you open / "
         "no circumstances are you to open / no circumstances can you open",
         "C2", None, "inversion after under no circumstances", "inversion"),
        ("Do you think I could borrow your pen for a moment?", "WONDER",
         "I {} borrow your pen for a moment.",
         "wonder if I could / wonder whether I could / "
         "wonder if I might / wonder whether I might", "B2", None,
         "polite request with an indirect question", "reported-speech"),
        ("Everybody knows that this beach is the cleanest in Poland.",
         "KNOWN", "This beach {} the cleanest in Poland.", "is known to be",
         "C1", None, "passive reporting structure (be known to)", "passive"),
    ],
    "choice": [
        ("{} it not for your help, I would still be stuck on the first "
         "question.", ["Had", "Were", "Should", "Did"], "B", "C1", None,
         "conditional with inversion (were it not for)", "conditionals"),
        ("You're coming to Ola's party on Saturday, {}?",
         ["aren't you", "isn't it", "don't you", "won't you"], "A", "B1",
         None, "question tag", "tenses"),
        ("I {} across some old photos of my parents while I was tidying the "
         "attic.", ["came", "took", "got", "put"], "A", "B2", "phrasal verb",
         "come across", "phrasal-verb"),
        ("Our teacher turned a {} eye to our chatting because it was the last "
         "day of term.", ["deaf", "blind", "closed", "shut"], "B", "C1",
         "idiom", "turn a blind eye (deaf belongs to turn a deaf ear)",
         "idiom"),
        ("I wish I {} more time to finish this project.",
         ["have", "had", "would have", "will have"], "B", "B2", None,
         "wish + past simple for the present", "conditionals"),
        ("{} by the noise, the baby started to cry.",
         ["Waking", "Woken", "Woke", "Having woken"], "B", "C1", None,
         "participle clause with a passive meaning", "participle-clauses"),
        ("The new head teacher is very strict, so we had better be on our "
         "best {}.", ["behaviour", "manners", "conduct", "attitude"], "A",
         "B2", "idiom", "be on your best behaviour", "idiom"),
        ("The football match was called off because of {} rain.",
         ["strong", "thick", "torrential", "powerful"], "C", "C1",
         "collocation", "torrential rain", "collocation"),
        ("I'll never forget {} the sea for the first time when I was four.",
         ["to see", "seeing", "see", "to have seen"], "B", "B2", None,
         "forget + -ing for a memory", "verb-patterns"),
        ("{} as it may seem, the story is completely true.",
         ["Strangely", "Stranger", "Strange", "However strange"], "C", "C2",
         None, "concession: adjective + as + clause", "linking-words"),
    ],
    "culture": [
        ("In which year was the cross of St Patrick added to the Union Flag?",
         ["1606", "1707", "1801", "1922"], "C",
         "Symbols of the UK: the Union Jack", "uk-symbols"),
        ("When do people in England celebrate St George's Day?",
         ["on 1 March", "on 23 April", "on 17 March", "on 30 November"], "B",
         "The four countries: patron saints", "uk-countries"),
        ("Who writes the King's Speech that the King reads at the State "
         "Opening of Parliament?",
         ["the King himself", "the Speaker of the House of Commons",
          "Black Rod", "the government"], "D",
         "Political life: the State Opening of Parliament", "uk-politics"),
        ("In which language was the Magna Carta written?",
         ["Latin", "English", "French", "Welsh"], "A",
         "Historical events: Magna Carta (1215)", "uk-history"),
        ("On which islands did Charles Darwin notice that the finches and "
         "tortoises were slightly different on each island?",
         ["the Canary Islands", "the Galápagos Islands",
          "the Falkland Islands", "the Isles of Scilly"], "B",
         "Notable Britons: Charles Darwin", "uk-people"),
    ],
}

# --------------------------------------------------------------------------
# Test 03
# --------------------------------------------------------------------------

T03 = {
    "formation": [
        ("My cousin is very {}: she started her own cake business when she "
         "was only sixteen.", "ENTERPRISE", ["enterprising"], "C1", None,
         "-ing adjective from a noun", "word-ending"),
        ("Her {} to help others makes her a wonderful friend.", "WILLING",
         ["willingness"], "B2", None, "-ness", "word-ending"),
        ("The difference in price between the two phones is {}, so just buy "
         "the one you like more.", "NEGLECT", ["negligible"], "C2", None,
         "stem change (neglect -> neglig-) + -ible", "base-change"),
        ("My dad is an {}: he designs bridges and motorways.", "ENGINE",
         ["engineer"], "B1", None, "-eer (not *enginer)", "word-ending"),
        ("The view from the castle tower was {} beautiful: we could see for "
         "miles.", "BREATH", ["breathtakingly"], "C1", None,
         "compound adjective + -ly", "two-steps"),
        ("Grandpa told us a {} story about his first day at school, and we "
         "couldn't stop laughing.", "HUMOUR", ["humorous"], "B2", None,
         "-ous, dropping the u (not *humourous)", "suffix-spelling"),
        ("The prices in the new café are {} high: eight pounds for a small "
         "glass of orange juice is a joke!", "REASON", ["unreasonably"], "C1",
         None, "un- + -ably", "negative-prefix"),
        ("The sudden {} of the dinosaurs about 66 million years ago is still "
         "a bit of a mystery.", "DISAPPEAR", ["disappearance"], "B2", None,
         "-ance; single s, double p", "ance-ence"),
        ("The judges praised the {} of her story: nobody had ever written "
         "anything like it.", "ORIGIN", ["originality"], "C1", None,
         "two steps (origin -> original -> originality)", "two-steps"),
        ("Our guide spoke so {} about the old castle that nobody wanted the "
         "tour to end.", "PASSION", ["passionately"], "B2", None,
         "-ate + -ly", "two-steps"),
    ],
    "hangman": [
        ("Clap your hands to the {} of the music.", "r___h_", "rhythm", "B2",
         None, "spelling (rh-, no vowel after y)", "silent-letters"),
        ("Sorry, Miss Nowak, I didn't mean to call you 'Mum': it was just a "
         "slip of the {}.", "t___u_", "tongue", "C1", "idiom",
         "a slip of the tongue; silent ue", "idiom"),
        ("Our car {} down on the motorway, so we had to wait two hours for "
         "help.", "__o__", "broke", "B1", "phrasal verb",
         "break down; irregular past", "phrasal-verb"),
        ("Dad's old mobile phone is completely {}: nobody uses phones like "
         "that any more.", "o_s_____", "obsolete", "C1", None,
         "spelling; the s rules out outdated", "vowels"),
        ("Our teacher asked us to fill in a {} about our eating habits.",
         "q_e_t____a___", "questionnaire", "B2", None,
         "spelling (double n, -aire)", "double-letters"),
        ("Finding my lost phone in the snow was a real {} of luck.",
         "s__o__", "stroke", "C1", "collocation",
         "a stroke of luck; the o rules out streak", "collocation"),
        ("People all over the world celebrated the start of the new {} on 1 "
         "January 2000.", "m___e____m", "millennium", "B2", None,
         "spelling (double l, double n)", "double-letters"),
        ("My uncle is a real {} of cheese: he can tell you which farm each "
         "one comes from.", "c___o_____r", "connoisseur", "C2", None,
         "spelling (double n, double s, -eur)", "double-letters"),
        ("Don't put all your eggs in one {}: apply to more than one secondary "
         "school.", "b_s___", "basket", "B2", "idiom",
         "don't put all your eggs in one basket", "idiom"),
        ("It was a real {} to meet the famous writer in person.",
         "__i___e_e", "privilege", "C1", None,
         "spelling (no d, -ege)", "vowels"),
    ],
    "transform": [
        ("I checked the train times on the internet.", "LOOKED",
         "I {} on the internet.",
         "looked up the train times / looked the train times up", "B2",
         "phrasal verb", "look up, with the object before or after up",
         "phrasal-verb"),
        ("I'm sure it will rain later: look at those dark clouds.", "BOUND",
         "It is {} later: look at those dark clouds.", "bound to rain", "C1",
         None, "be bound to", "modals"),
        ("I can't wait for the summer holidays.", "FORWARD",
         "I am really {} the summer holidays.", "looking forward to", "B1",
         "phrasal verb", "look forward to", "phrasal-verb"),
        ("My friend persuaded me to join the drama club.", "TALKED",
         "My friend {} the drama club.", "talked me into joining", "C1",
         "phrasal verb", "talk someone into + -ing", "phrasal-verb"),
        ("I will never forget the day. I met my best friend on that day.",
         "WHEN", "I will never forget the day {} my best friend.",
         "when I met / when I first met", "B2", None,
         "relative clause with when", "relative-clauses"),
        ("Imagine you could live anywhere in the world. Where would you "
         "live?", "SUPPOSING", "{} anywhere in the world, where would you "
         "live?",
         "Supposing you could live / Supposing that you could live / "
         "Supposing you were able to live", "C1", None,
         "supposing + past for an imagined condition", "conditionals"),
        ("My brother is really good at chess.", "TALENT",
         "My brother has {} chess.",
         "a real talent for / a talent for / a great talent for / "
         "a real talent for playing / a talent for playing / "
         "a great talent for playing", "B2", "collocation",
         "have a talent for", "collocation"),
        ("It is very likely that the match will be cancelled.", "LIKELIHOOD",
         "In {} be cancelled.", "all likelihood the match will", "C2",
         "collocation", "in all likelihood", "collocation"),
        ("Sam is the best football player in our team.", "ANYONE",
         "Sam plays football better {} our team.",
         "than anyone else in / than anyone in / than anyone else on / "
         "than anyone on", "B2", None,
         "comparative + than anyone else ('on our team' accepted, "
         "2026-10-31)", "comparison"),
        ("Grandma is very proud of her garden.", "PRIDE",
         "Grandma {} her garden.",
         "takes great pride in / takes a lot of pride in / takes pride in",
         "C1", "collocation", "take pride in", "collocation"),
    ],
    "choice": [
        ("When I was little, I {} be afraid of the dark.",
         ["used to", "use to", "was used to", "am used to"], "A", "B1", None,
         "used to for a past state", "tenses"),
        ("The new animated film got {} reviews: the critics loved it.",
         ["rave", "loud", "wild", "crazy"], "A", "C1", "collocation",
         "rave reviews", "collocation"),
        ("The woman {} car was stolen went straight to the police.",
         ["who", "whose", "whom", "which"], "B", "B2", None,
         "relative pronoun whose", "relative-clauses"),
        ("If I hadn't stayed up so late last night, I {} so tired now.",
         ["wouldn't be", "wouldn't have been", "won't be", "hadn't been"],
         "A", "C1", None, "mixed conditional (past cause, present result)",
         "conditionals"),
        ("The plane {} off an hour late because of the fog.",
         ["took", "went", "made", "put"], "A", "B2", "phrasal verb",
         "take off", "phrasal-verb"),
        ("Only when I got home {} that I had lost my wallet.",
         ["I realised", "did I realise", "had I realised", "I did realise"],
         "B", "C1", None, "inversion after only when", "inversion"),
        ("These new trainers cost an arm and a {}, but they are really "
         "comfortable.", ["leg", "hand", "foot", "finger"], "A", "B2",
         "idiom", "cost an arm and a leg", "idiom"),
        ("Everyone knew who would win: the result of the match was a {} "
         "conclusion.", ["forgotten", "foreseen", "foregone", "forbidden"],
         "C", "C2", "collocation", "a foregone conclusion", "collocation"),
        ("You {} have told me about the party: I would have bought Ola a "
         "present!", ["should", "must", "can", "would"], "A", "B2", None,
         "should have for criticism of the past", "modals"),
        ("{} the film before, I knew exactly how it would end.",
         ["Seeing", "Having seen", "Seen", "To have seen"], "B", "C1", None,
         "perfect participle clause", "participle-clauses"),
    ],
    "culture": [
        ("Which king joined the white rose of York and the red rose of "
         "Lancaster into the Tudor rose?",
         ["Henry VII", "Henry VIII", "Richard III", "Edward IV"], "A",
         "The four countries: plants (the rose)", "uk-countries"),
        ("What is the name of the building where the Scottish Parliament "
         "meets?", ["Stormont", "the Senedd", "Holyrood", "Westminster Hall"],
         "C", "Political life: devolution", "uk-politics"),
        ("What do people in Argentina call the Falkland Islands?",
         ["Tierra del Fuego", "Las Malvinas", "Patagonia", "Las Canarias"],
         "B", "Historical events: the Falklands War (1982)", "uk-history"),
        ("Which scientist designed the Monument together with Sir Christopher "
         "Wren?", ["Isaac Newton", "Charles Darwin", "Michael Faraday",
                   "Robert Hooke"], "D", "Landmarks of London: the Monument",
         "uk-london"),
        ("Who was born in Kensington Palace?",
         ["Queen Victoria", "Princess Diana", "Queen Elizabeth II",
          "King Charles III"], "A",
         "London's Royal Parks: Kensington Gardens, history", "uk-parks"),
    ],
}

# --------------------------------------------------------------------------
# Batch 04 (written 2026-10-31, leaning on the weak types of his record:
# base-change, vowels, double-letters, uk-politics, comparison,
# suffix-spelling, collocation)
# --------------------------------------------------------------------------

T04 = {
    "formation": [
        ("In the film, a {} creature climbs out of the lake and terrifies "
         "the whole town.", "MONSTER", ["monstrous"], "C1", None,
         "stem change (monster -> monstr-) + -ous", "base-change"),
        ("The {} of the river here is about fifty metres, so nobody tries to "
         "swim across.", "WIDE", ["width"], "B1", None,
         "stem change (wide -> wid-) + -th", "base-change"),
        ("The storm left a trail of {} across the town: trees down, roofs "
         "gone and cars crushed.", "DESTROY", ["destruction"], "B2", None,
         "stem change (destroy -> destruct-) + -ion", "base-change"),
        ("This old photo is {}: it's the only one we have of "
         "Great-Grandpa.", "REPLACE", ["irreplaceable"], "C1", None,
         "ir- + -able, keeping the e", "negative-prefix"),
        ("Being late once is fine, but being late every single day is {}.",
         "EXCUSE", ["inexcusable"], "C1", None,
         "in- (not *unexcusable) + -able", "negative-prefix"),
        ("I am {} sorry for breaking your favourite mug.", "TRUE", ["truly"],
         "B2", None, "drop the e (not *truely)", "suffix-spelling"),
        ("Fifteen pounds for a cheese sandwich? That's {}!", "OUTRAGE",
         ["outrageous"], "C1", None, "-ous, keeping the e after g",
         "suffix-spelling"),
        ("Thunderstorms in January are a rare {} in Poland.", "OCCUR",
         ["occurrence"], "C1", None, "double c, double r, -ence",
         "double-letters"),
        ("It would be {} to take an umbrella: the sky is very dark.", "SENSE",
         ["sensible"], "B2", None, "-ible (not *sensable)", "able-ible"),
        ("We got {} lost in the forest and had to phone Dad to come and find "
         "us.", "HOPE", ["hopelessly"], "B2", None,
         "two steps (hope -> hopeless -> hopelessly)", "two-steps"),
    ],
    "hangman": [
        ("After three days lost in the mountains, the climbers were {} for "
         "food and water.", "_e_p___t_", "desperate", "B2", None,
         "spelling (-per-, -ate)", "vowels"),
        ("The UK {} meets in the Palace of Westminster, the building with "
         "Big Ben.", "p__l__m___", "parliament", "B2", None,
         "spelling (the a in -ia- is not heard)", "silent-letters"),
        ("I'm in a real {}: my two best friends are having their birthday "
         "parties on the same day.", "d_____a", "dilemma", "C1", None,
         "spelling (double m)", "double-letters"),
        ("Our neighbour's dog is quite {}: it barks and growls at everyone "
         "who walks past.", "a___e___v_", "aggressive", "B2", None,
         "spelling (double g, double s)", "double-letters"),
        ("Please keep the white clothes {} from the coloured ones when you "
         "do the washing.", "s_p_____", "separate", "B2", None,
         "spelling (-par-, not *seperate)", "vowels"),
        ("It was {} cold on the beach, so we went home after ten minutes.",
         "b_t_____", "bitterly", "C1", "collocation", "bitterly cold",
         "collocation"),
        ("Ola said sorry, and I don't hold a {} against her: we're friends "
         "again.", "g___g_", "grudge", "C1", "collocation", "hold a grudge",
         "collocation"),
        ("We missed the train, but every cloud has a silver {}: we found a "
         "lovely café at the station.", "l____g", "lining", "C1", "idiom",
         "every cloud has a silver lining", "idiom"),
        ("While I was tidying my room, I came {} some old photos of my "
         "grandparents.", "____ss", "across", "B2", "phrasal verb",
         "come across; one c (not *accross)", "phrasal-verb"),
        ("It's {} to tell everyone else to save water and then spend an hour "
         "in the shower.", "h___c___y", "hypocrisy", "C1", None,
         "spelling (-o-, -isy, not *hypocracy)", "vowels"),
    ],
    "transform": [
        ("My new bike was much cheaper than I expected.", "NEARLY",
         "My new bike was not {} as I expected.",
         "nearly as expensive / nearly as dear / nearly so expensive", "C1",
         None, "not nearly as + adjective + as", "comparison"),
        ("The water was too cold for us to swim in.", "WARM",
         "The water was not {} swim in.",
         "warm enough for us to / warm enough to", "B2", None,
         "not + adjective + enough (for us) to", "comparison"),
        ("It doesn't matter how hard I try, I can't remember her name.",
         "HOWEVER", "{}, I cannot remember her name.",
         "However hard I try / However much I try", "C1", None,
         "however + adverb + clause", "linking-words"),
        ("Nobody listened to what the guide was saying.", "ATTENTION",
         "Nobody {} what the guide was saying.",
         "paid attention to / paid any attention to", "B1", "collocation",
         "pay attention to", "collocation"),
        ("The new school rules will affect every pupil.", "IMPACT",
         "The new school rules will {} every pupil.",
         "have an impact on / make an impact on / have a big impact on / "
         "have a great impact on / have a huge impact on / "
         "have a real impact on", "C1", "collocation", "have an impact on",
         "collocation"),
        ("I'm sorry I didn't call you yesterday.", "REGRET",
         "I {} you yesterday.",
         "regret not calling / regret not phoning / regret not ringing / "
         "regret not having called / regret not having phoned / "
         "regret that I did not call / regret I did not call / "
         "regret that I did not phone / regret I did not phone", "B2", None,
         "regret + not + -ing", "verb-patterns"),
        ("Without your help, I would have failed the test.", "NOT",
         "{} your help, I would have failed the test.",
         "Had it not been for / If it had not been for", "C1", None,
         "had it not been for (third conditional)", "conditionals"),
        ("A builder is repairing our roof this week.", "HAVING",
         "We {} this week.",
         "are having our roof repaired / are having the roof repaired / "
         "are having our roof fixed / are having the roof fixed", "B2", None,
         "have something done", "passive"),
        ("'Have you finished your project?' the teacher asked me.", "WHETHER",
         "The teacher asked me {} my project.",
         "whether I had finished / whether I had already finished / "
         "whether or not I had finished", "B2", None,
         "reported yes/no question with whether", "reported-speech"),
        ("I didn't realise I had lost my keys until I got home.", "UNTIL",
         "Not {} realise that I had lost my keys.",
         "until I got home did I / until I arrived home did I / "
         "until I came home did I / until I got back did I", "C1", None,
         "inversion after not until", "inversion"),
    ],
    "choice": [
        ("The storm caused {} damage to the village: dozens of houses lost "
         "their roofs.", ["extensive", "wide", "broad", "long"], "A", "C1",
         "collocation", "extensive damage", "collocation"),
        ("It's {} unlikely that it will snow in May.",
         ["strongly", "highly", "deeply", "heavily"], "B", "C1",
         "collocation", "highly unlikely", "collocation"),
        ("Go on, tell me what happened at the party: I'm all {}!",
         ["eyes", "hands", "ears", "mouth"], "C", "C1", "idiom",
         "be all ears", "idiom"),
        ("The fire alarm went {} in the middle of our maths test.",
         ["off", "out", "up", "down"], "A", "B2", "phrasal verb",
         "go off (of an alarm)", "phrasal-verb"),
        ("Your essay is {} better than last time: well done!",
         ["very", "a great many", "too", "a great deal"], "D", "C1", None,
         "a great deal + comparative", "comparison"),
        ("She sings {} than anyone else in the choir.",
         ["more beautifully", "most beautifully", "beautifully",
          "more beautiful"], "A", "B2", None, "comparative adverb",
         "comparison"),
        ("We left home early {} we wouldn't miss the train.",
         ["in case", "so that", "as long as", "unless"], "B", "B2", None,
         "so that for a purpose", "linking-words"),
        ("{} for our goalkeeper, we would have lost the match 0-5.",
         ["Unless", "Apart", "But", "Without"], "C", "C1", None,
         "but for (= if it had not been for)", "conditionals"),
        ("The winners of the competition {} next Monday.",
         ["will be announced", "will announce", "are announcing",
          "have announced"], "A", "B2", None, "future passive", "passive"),
        ("Do you know anyone {} can fix a broken laptop?",
         ["which", "who", "whose", "whom"], "B", "B1", None,
         "relative pronoun who", "relative-clauses"),
    ],
    "culture": [
        ("Which king burst into the House of Commons in 1642 to arrest five "
         "MPs, which is why the door is slammed in Black Rod's face at the "
         "State Opening?", ["James I", "Charles I", "Charles II",
                            "Henry VIII"], "B",
         "Political life: the State Opening, Black Rod", "uk-politics"),
        ("Which party was founded in 1900 by trade unions and socialist "
         "groups to represent working people?",
         ["the Conservative Party", "the Liberal Democrats",
          "the Scottish National Party", "the Labour Party"], "D",
         "Political life: the two major parties", "uk-politics"),
        ("Why is the Royal Standard never flown at half-mast, even when a "
         "monarch dies?",
         ["There is always a monarch: the next one reigns from the moment "
          "the last one dies.",
          "It is flown only on the monarch's birthday.",
          "By law, only the Union Flag may be flown at half-mast.",
          "It is too large to be lowered halfway."], "A",
         "Symbols of the UK: the Royal Standard", "uk-symbols"),
        ("Which Prime Minister resigned in January 1957 after the Suez "
         "Crisis?", ["Winston Churchill", "Anthony Eden", "Clement Attlee",
                     "Harold Wilson"], "B",
         "Historical events: the Suez Crisis (1956)", "uk-history"),
        ("Where is Charles Darwin buried?",
         ["in St Paul's Cathedral", "on the Galápagos Islands",
          "in Westminster Abbey", "in Canterbury Cathedral"], "C",
         "Notable Britons: Charles Darwin", "uk-people"),
    ],
}

# --------------------------------------------------------------------------
# Batch 05 (written 2026-10-31, with batch 04)
# --------------------------------------------------------------------------

T05 = {
    "formation": [
        ("She is very {}: she always notices when I'm upset, even when I try "
         "to hide it.", "PERCEIVE", ["perceptive"], "C1", None,
         "stem change (perceive -> percept-) + -ive", "base-change"),
        ("The police asked for a {} of the man who had taken the bike.",
         "DESCRIBE", ["description"], "B2", None,
         "stem change (describe -> descript-) + -ion", "base-change"),
        ("The {} of the pool is two metres, so only good swimmers are "
         "allowed in.", "DEEP", ["depth"], "B1", None,
         "vowel change (deep -> dep-) + -th", "base-change"),
        ("The noise from the building site next door was {}: nobody could "
         "work.", "TOLERATE", ["intolerable"], "C1", None,
         "in- (not *untolerable) + -able", "negative-prefix"),
        ("The heavy snow in April was {}: nothing like it had ever happened "
         "here before.", "PRECEDENT", ["unprecedented"], "C2", None,
         "un- + -ed", "negative-prefix"),
        ("At the end of the concert, the singer {} thanked her fans for "
         "their support.", "PUBLIC", ["publicly"], "C1", None,
         "-ly, not -ally (not *publically)", "suffix-spelling"),
        ("There has been a {} improvement in your handwriting this term.",
         "NOTICE", ["noticeable"], "B2", None,
         "-able, keeping the e after c", "suffix-spelling"),
        ("The clown was so funny that my little sister laughed {}.",
         "CONTROL", ["uncontrollably"], "C1", None,
         "un- + double l + -ably", "double-letters"),
        ("Thanks to my teacher's {}, I passed the exam with flying colours.",
         "GUIDE", ["guidance"], "B2", None, "-ance, dropping the e",
         "ance-ence"),
        ("The smell of fresh bread from the bakery was {}: we had to go in "
         "and buy some.", "RESIST", ["irresistible"], "C1", None,
         "ir- + -ible (not *irresistable)", "able-ible"),
    ],
    "hangman": [
        ("The old church has a small {} where people from the village have "
         "been buried for centuries.", "__m_t___", "cemetery", "C1", None,
         "spelling (-e-e-, not *cemetary)", "vowels"),
        ("Our film won first prize in the 'Best Animation' {}.", "__t_g___",
         "category", "B2", None, "spelling (-e-o-, not *catagory)",
         "vowels"),
        ("The school {} has decided to hold the summer fair on a Saturday.",
         "c______ee", "committee", "B2", None,
         "spelling (double m, double t, double e)", "double-letters"),
        ("Don't take any {} risks when you ride your bike in the city.",
         "u____e___r_", "unnecessary", "B2", None,
         "spelling (double n, one c, double s)", "double-letters"),
        ("The two shades of blue are almost the same: the difference between "
         "them is very {}.", "s__t__", "subtle", "C1", None,
         "spelling (silent b)", "silent-letters"),
        ("The {} majority of pupils in our school walk or cycle to school.",
         "v___", "vast", "C1", "collocation", "the vast majority",
         "collocation"),
        ("We had a {} escape when a big branch fell just behind our car.",
         "n____w", "narrow", "B2", "collocation", "a narrow escape",
         "collocation"),
        ("My little brother lost my headphones again, and that was the last "
         "{}!", "____w", "straw", "C1", "idiom", "the last straw", "idiom"),
        ("My grandma {} up four children on her own after the war.",
         "b____h_", "brought", "B2", "phrasal verb",
         "bring up; -ough- (not *brougt)", "phrasal-verb"),
        ("For no {} reason, our dog started barking at the wall.",
         "a______t", "apparent", "C1", None, "-ent, double p", "ance-ence"),
    ],
    "transform": [
        ("Her latest film is not nearly as good as her first one.", "FAR",
         "Her first film is {} her latest one.",
         "far better than / a far better film than / a far better one than",
         "C1", None, "far + comparative", "comparison"),
        ("The exam was easier than I had expected.", "AS",
         "The exam was not {} I had expected.",
         "as difficult as / as hard as / so difficult as / so hard as / "
         "as tough as / so tough as", "B2", None,
         "not as + adjective + as", "comparison"),
        ("Although she felt ill, Ola went to school.", "DESPITE",
         "Ola went to school {} ill.",
         "despite feeling / despite being / despite the fact that she felt / "
         "despite the fact she felt / despite the fact that she was / "
         "despite the fact she was", "B2", None,
         "although + clause -> despite + -ing", "linking-words"),
        ("Even though the task was difficult, we finished it on time.",
         "THOUGH", "Difficult {}, we finished it on time.",
         "though the task was / though it was", "C2", None,
         "adjective + though + clause for contrast", "linking-words"),
        ("Ania didn't keep her promise.", "WORD", "Ania did not {}.",
         "keep her word", "B2", "collocation", "keep your word",
         "collocation"),
        ("I completely forgot about the dentist appointment.", "MIND",
         "The dentist appointment completely {}.", "slipped my mind", "C1",
         "idiom", "slip your mind", "idiom"),
        ("Don't stop trying: you're nearly there!", "GIVE",
         "Do not {}: you are nearly there!", "give up", "B1", "phrasal verb",
         "give up", "phrasal-verb"),
        ("I would rather walk than take the bus.", "PREFER",
         "I {} the bus.",
         "prefer walking to taking / prefer to walk rather than take", "C1",
         None, "prefer + -ing + to + -ing", "verb-patterns"),
        ("It was wrong of you not to tell me about the party.", "OUGHT",
         "You {} me about the party.", "ought to have told", "C1", None,
         "ought to have + past participle", "modals"),
        ("'Where did you buy your jacket?' Ola asked me.", "WHERE",
         "Ola asked me {} my jacket.", "where I had bought / where I bought",
         "B2", None, "reported wh- question, no inversion",
         "reported-speech"),
    ],
    "choice": [
        ("My grandpa has a very {} sense of humour: he tells jokes with a "
         "completely serious face.", ["dry", "wet", "flat", "thin"], "A",
         "C1", "collocation", "a dry sense of humour", "collocation"),
        ("Please {} in mind that the museum closes at five o'clock.",
         ["hold", "bear", "take", "carry"], "B", "B2", "collocation",
         "bear in mind", "collocation"),
        ("Stop {} around the bush and tell me what really happened!",
         ["hitting", "running", "beating", "jumping"], "C", "C1", "idiom",
         "beat around the bush", "idiom"),
        ("I can't {} out what this sign says: the letters are too small.",
         ["make", "take", "put", "give"], "A", "B2", "phrasal verb",
         "make out (see or read with difficulty)", "phrasal-verb"),
        ("It was the {} interesting museum I have ever visited: I was bored "
         "the whole time.", ["less", "fewest", "little", "least"], "D", "B2",
         None, "the least + adjective", "comparison"),
        ("Kasia is {} the cleverest person in our class: nobody else even "
         "comes close.", ["widely", "easily", "highly", "greatly"], "B",
         "C1", None, "easily + superlative", "comparison"),
        ("I'll write your phone number down {} I forget it.",
         ["in case", "unless", "so that", "as long as"], "A", "B2", None,
         "in case for a precaution", "linking-words"),
        ("Not only {} the cake, but she also made all the decorations.",
         ["she baked", "did she bake", "she did bake", "she had baked"], "B",
         "C1", None, "inversion after not only", "inversion"),
        ("I {} this book for weeks, and I'm still only on page 50.",
         ["have read", "am reading", "have been reading", "read"], "C", "B2",
         None, "present perfect continuous with for", "tenses"),
        ("I have two older brothers, {} are at university now.",
         ["both of whom", "both of who", "both of them", "both of which"],
         "A", "C1", None, "both of whom in a relative clause",
         "relative-clauses"),
    ],
    "culture": [
        ("Who was the last monarch to refuse Royal Assent to a bill passed by "
         "Parliament?", ["Queen Victoria", "King George III",
                         "Queen Elizabeth I", "Queen Anne"], "D",
         "Political life: Royal Assent", "uk-politics"),
        ("Which Prime Minister's government created the NHS (National Health "
         "Service) in 1948?", ["Winston Churchill", "Margaret Thatcher",
                               "Clement Attlee", "Tony Blair"], "C",
         "Political life: the Labour Party", "uk-politics"),
        ("According to a legend, how did the thistle help Scotland?",
         ["St Andrew planted thistles around Edinburgh Castle to keep "
          "enemies out.",
          "Barefoot Viking attackers stepped on thistles and cried out, which "
          "woke the Scots.",
          "Scottish soldiers ate thistles to survive a long winter siege.",
          "A thistle grew where the first King of Scotland was crowned."],
         "B", "The four countries: plants (the thistle)", "uk-countries"),
        ("Which queen was beheaded at the Tower of London in 1536?",
         ["Anne Boleyn", "Catherine of Aragon", "Jane Seymour",
          "Catherine Parr"], "A",
         "Landmarks of London: the Tower of London", "uk-london"),
        ("What does the golden statue of Prince Albert in the Albert Memorial "
         "hold?", ["a sword", "the crown of England",
                   "a map of the British Empire",
                   "the catalogue of the Great Exhibition"], "D",
         "London's Royal Parks: Kensington Gardens, the Albert Memorial",
         "uk-parks"),
    ],
}

# --------------------------------------------------------------------------
# Batch 06 (written 2026-10-31, with batch 07)
# --------------------------------------------------------------------------

T06 = {
    "formation": [
        ("She is so {} that she always gets her parents to say yes in the "
         "end.", "PERSUADE", ["persuasive"], "C1", None,
         "stem change (persuade -> persuas-) + -ive", "base-change"),
        ("Marie Curie is one of the most {} scientists in history: her work "
         "changed medicine for ever.", "INFLUENCE", ["influential"], "C1",
         None, "stem change (influence -> influent-) + -ial, not "
         "*influencial", "base-change"),
        ("The police had no {} that he had taken the money, so they let him "
         "go.", "PROVE", ["proof"], "B2", None, "stem change (prove -> proof)",
         "base-change"),
        ("Her {} makes it hard for her to talk to people she doesn't know.",
         "SHY", ["shyness"], "B2", None, "-ness, keeping the y (not *shiness)",
         "suffix-spelling"),
        ("The {} sun burnt our backs as we walked through the desert.",
         "MERCY", ["merciless"], "C1", None, "y to i before -less",
         "suffix-spelling"),
        ("Learning to play the violin well takes years of hard work and {}.",
         "COMMIT", ["commitment"], "C1", None,
         "single t before -ment (not *committment)", "double-letters"),
        ("I waited {} for the bus, looking at my watch every few seconds.",
         "PATIENT", ["impatiently"], "B2", None, "im- before p, + -ly",
         "negative-prefix"),
        ("My little sister is very {}: she never stops chatting, even during "
         "films.", "TALK", ["talkative"], "B2", None,
         "-ative for the adjective", "word-ending"),
        ("The children clapped {} when the clown came onto the stage.",
         "ENTHUSIASM", ["enthusiastically"], "C1", None,
         "two steps (enthusiasm -> enthusiastic -> enthusiastically), -ally",
         "two-steps"),
        ("Do you believe in the {} of ghosts?", "EXIST", ["existence"], "B2",
         None, "-ence (not *existance)", "ance-ence"),
    ],
    "hangman": [
        ("I've written the date of the party on the {} in the kitchen.",
         "__l__d__", "calendar", "B1", None, "spelling (-ar, not *calender)",
         "vowels"),
        ("In the park there are {} copies of famous buildings, small enough "
         "to step over.", "m______re", "miniature", "C1", None,
         "spelling (-ia-, not *miniture)", "vowels"),
        ("Giving up chocolate for a whole month was a real {} for me.",
         "s____f__e", "sacrifice", "C1", None,
         "spelling (-i-i-, not *sacrafice)", "vowels"),
        ("Our old {} cleaner is so loud that we can't hear the TV when Mum "
         "is cleaning.",
         "v____m", "vacuum", "B2", None, "spelling (one c, double u)",
         "double-letters"),
        ("If I were a {}, I would buy an island and invite all my friends.",
         "m____o___r_", "millionaire", "B2", None,
         "spelling (double l, one n)", "double-letters"),
        ("The kitchen sink is leaking, so Mum has phoned a {}.", "p__m___",
         "plumber", "B2", None, "spelling (silent b)", "silent-letters"),
        ("What a {}! We were both wearing exactly the same T-shirt.",
         "c__n__d____", "coincidence", "C1", None, "spelling (-ence, -i-i-)",
         "ance-ence"),
        ("It was {} dark in the cave, so we switched on our torches.",
         "____h", "pitch", "C1", "collocation", "pitch dark", "collocation"),
        ("By the end of the bedtime story, my little brother was {} asleep.",
         "f___", "fast", "C1", "collocation", "fast asleep", "collocation"),
        ("Good luck in the competition: I'll keep my fingers {} for you!",
         "c___s__", "crossed", "B2", "idiom",
         "keep your fingers crossed; double s", "idiom"),
    ],
    "transform": [
        ("There wasn't enough time to finish the test.", "TOO",
         "We had {} the test.",
         "too little time to finish / too little time to complete / "
         "too little time to do", "B2", None,
         "too little + uncountable noun + to", "comparison"),
        ("Ola is the cleverest girl I know.", "CLEVER",
         "I do not know {} Ola.",
         "anyone as clever as / anyone so clever as / anybody as clever as / "
         "anybody so clever as / anyone more clever than / "
         "anybody more clever than / any girl as clever as / "
         "any girl so clever as / any girl more clever than / "
         "a girl as clever as / a girl more clever than", "C1", None,
         "superlative -> not ... anyone as + adjective + as, keyword "
         "unchanged (not *cleverer)", "comparison"),
        ("Dad got really angry when he saw the mess in the kitchen.",
         "TEMPER", "Dad {} when he saw the mess in the kitchen.",
         "lost his temper / really lost his temper / "
         "completely lost his temper / totally lost his temper", "B2",
         "collocation", "lose your temper", "collocation"),
        ("My sister and I didn't play on the computer at the same time: first "
         "she played, then I did.", "TURNS",
         "My sister and I {} on the computer.",
         "took turns playing / took turns to play / "
         "took it in turns to play / took turns at playing", "B2",
         "collocation", "take turns (doing / to do)", "collocation"),
        ("My sister is very tidy, but I'm not.", "UNLIKE",
         "{}, I am not tidy at all.", "Unlike my sister", "B2", None,
         "unlike + noun for a contrast", "linking-words"),
        ("We planned to go to the beach, but in the end we stayed at home "
         "because of the rain.", "ENDED",
         "We planned to go to the beach, but we {} at home because of the "
         "rain.", "ended up staying / ended up having to stay", "C1", None,
         "end up + -ing", "verb-patterns"),
        ("You can go to the party, but you must be home by ten.", "CONDITION",
         "You can go to the party {} home by ten.",
         "on condition that you are / on condition you are / "
         "on condition that you get / on condition you get / "
         "on condition that you come / on condition you come / "
         "on the condition that you are / on the condition that you get",
         "C1", None, "on condition that (= only if)", "conditionals"),
        ("I hate it when people interrupt me.", "BEING", "I hate {}.",
         "being interrupted / being interrupted by people / "
         "being interrupted by others", "C1", None, "passive -ing form",
         "passive"),
        ("'Well done for winning the race, Ola!' said the teacher.",
         "CONGRATULATED", "The teacher {} the race.",
         "congratulated Ola on winning / congratulated her on winning", "C1",
         None, "congratulate someone on + -ing", "reported-speech"),
        ("I learnt a bit of Italian on holiday without really trying.", "UP",
         "I {} a bit of Italian on holiday.", "picked up", "B2",
         "phrasal verb", "pick up (learn without trying)", "phrasal-verb"),
    ],
    "choice": [
        ("Can you {} the table for dinner, please? The plates are in the "
         "cupboard.", ["lay", "put", "make", "do"], "A", "B1", "collocation",
         "lay the table", "collocation"),
        ("When the last exam was over, we all {} a sigh of relief.",
         ["took", "breathed", "made", "blew"], "B", "C1", "collocation",
         "breathe a sigh of relief", "collocation"),
        ("My cousin and I look so alike that people say we're like two {} in "
         "a pod.", ["beans", "nuts", "seeds", "peas"], "D", "C1", "idiom",
         "like two peas in a pod", "idiom"),
        ("Let's {} off early tomorrow so we don't get stuck in traffic.",
         ["set", "put", "make", "give"], "A", "B2", "phrasal verb",
         "set off (start a journey)", "phrasal-verb"),
        ("This year's school show was every {} as good as last year's.",
         ["part", "piece", "bit", "way"], "C", "C1", None,
         "every bit as + adjective + as", "comparison"),
        ("The film was nearly three hours long. {}, I wasn't bored for a "
         "single minute.", ["Although", "Despite", "Nevertheless", "Because"],
         "C", "C1", None, "nevertheless for a contrast between sentences",
         "linking-words"),
        ("If you {} me, I would have helped you with your project.",
         ["asked", "had asked", "would ask", "have asked"], "B", "B2", None,
         "third conditional", "conditionals"),
        ("Nobody phoned while I was out, {}?",
         ["didn't they", "did he", "did they", "do they"], "C", "B2", None,
         "question tag after nobody (positive, they)", "tenses"),
        ("My bike, {} I got for my tenth birthday, is still as good as new.",
         ["that", "which", "what", "whose"], "B", "B2", None,
         "non-defining relative clause: which, not that", "relative-clauses"),
        ("Not {} what to say, I just smiled and nodded.",
         ["known", "know", "to know", "knowing"], "D", "C1", None,
         "negative participle clause", "participle-clauses"),
    ],
    "culture": [
        ("Why do the Yeomen of the Guard search the cellars of the Palace of "
         "Westminster before the State Opening of Parliament?",
         ["to find the Mace, which is locked away in the cellars overnight",
          "because of a tradition going back to 1605, when Guy Fawkes tried "
          "to blow up Parliament",
          "to check that the King's carriage, which is kept down there, is "
          "ready",
          "to make sure that no MP is hiding there to miss the King's Speech"],
         "B", "Political life: the State Opening, the Gunpowder Plot (1605)",
         "uk-politics"),
        ("Which of these is decided by the UK Parliament in Westminster for "
         "the whole country, and not by the Scottish Parliament?",
         ["schools", "health", "transport", "defence"], "D",
         "Political life: devolution", "uk-politics"),
        ("Who described the Great Fire of London in his famous diary, and "
         "even buried his cheese to save it from the flames?",
         ["Sir Christopher Wren", "Thomas Farriner", "Samuel Pepys",
          "Robert Hooke"], "C",
         "Historical events: the Great Fire of London (1666)", "uk-history"),
        ("In which year did women in the UK get the vote on the same terms "
         "as men?", ["1928", "1918", "1903", "1945"], "A",
         "Notable Britons: Emmeline Pankhurst, the votes of 1918 and 1928",
         "uk-people"),
        ("Why is the motto on the Royal Coat of Arms, 'Dieu et mon droit', "
         "in French?",
         ["It was a gift to an English king from a king of France.",
          "The first coat of arms was made in Paris.",
          "A French artist designed it for Queen Victoria.",
          "English kings spoke French for centuries after the Norman "
          "Conquest of 1066."], "D",
         "Symbols of the UK: the Royal Coat of Arms", "uk-symbols"),
    ],
}

# --------------------------------------------------------------------------
# Batch 07 (written 2026-10-31, with batch 06)
# --------------------------------------------------------------------------

T07 = {
    "formation": [
        ("Our {} to London was two hours late because of a storm.", "FLY",
         ["flight"], "B1", None, "stem change (fly -> flight)", "base-change"),
        ("In his {}, my grandad was a very good footballer.", "YOUNG",
         ["youth"], "B2", None, "stem change (young -> youth)", "base-change"),
        ("Because of the thick fog, {} on the motorway was very poor.",
         "VISIBLE", ["visibility"], "C1", None,
         "stem change (visible -> visibil-) + -ity", "base-change"),
        ("There are {} two ways to get to the castle: by bus or on foot.",
         "BASIC", ["basically"], "B2", None, "-ally (not *basicly)",
         "suffix-spelling"),
        ("Fresh fruit is cheap and {} in the summer.", "PLENTY",
         ["plentiful"], "C1", None, "y to i before -ful", "suffix-spelling"),
        ("After we scored the first goal, our team was {}: we won 6-0.",
         "STOP", ["unstoppable"], "C1", None, "un- + double p + -able",
         "double-letters"),
        ("The old map was {}: the bridge it showed had disappeared years ago.",
         "ACCURATE", ["inaccurate"], "C1", None, "in- (not *unaccurate)",
         "negative-prefix"),
        ("My uncle is a {} who writes books about the castles of Poland.",
         "HISTORY", ["historian"], "B2", None, "-ian for the person",
         "word-ending"),
        ("Our new classmate's {} is Ukrainian: she comes from Lviv.",
         "NATION", ["nationality"], "B2", None,
         "two steps (nation -> national -> nationality)", "two-steps"),
        ("To my {}, my little brother had eaten all the chocolate biscuits.",
         "ANNOY", ["annoyance"], "C1", None, "-ance, keeping the y",
         "ance-ence"),
    ],
    "hangman": [
        ("If you lose something at school, ask the school {} in the office.",
         "s_c____r_", "secretary", "B2", None,
         "spelling (-e-a-, not *secretery)", "vowels"),
        ("The fans' {} turned to joy when our team scored in the last minute.",
         "_____ir", "despair", "C1", None, "spelling (de-, not *dispair)",
         "vowels"),
        ("One {} of living in the countryside is the fresh air.", "____f_t",
         "benefit", "B1", None, "spelling (-e-e-i-)", "vowels"),
        ("Our street runs {} to the railway line, so we hear every train.",
         "______el", "parallel", "C1", None,
         "spelling (one r, double l in the middle, one l at the end)",
         "double-letters"),
        ("My little sister eats everything except {}: she says it looks like "
         "tiny trees.", "__o____i", "broccoli", "B2", None,
         "spelling (double c, one l)", "double-letters"),
        ("Our school has started a {} to collect old phones for recycling.",
         "___p___n", "campaign", "C1", None, "spelling (silent g)",
         "silent-letters"),
        ("Your handwriting is so messy that it's barely {}.", "l___b__",
         "legible", "C1", None, "spelling (-ible, not *legable)", "able-ible"),
        ("It's too early to {} any conclusions: we need more information "
         "first.", "d___", "draw", "C1", "collocation", "draw a conclusion",
         "collocation"),
        ("There is {} competition for places in the school football team.",
         "f___c_", "fierce", "B2", "collocation", "fierce competition; ie",
         "collocation"),
        ("The scientists {} out hundreds of experiments before they found the "
         "answer.", "____i_d", "carried", "B2", "phrasal verb",
         "carry out; double r, y to i", "phrasal-verb"),
    ],
    "transform": [
        ("My sister's bedroom is twice the size of mine.", "TWICE",
         "My sister's bedroom is {} mine.",
         "twice as big as / twice as large as", "B2", None,
         "twice as + adjective + as", "comparison"),
        ("The first film was bad, but the second one was worse.", "EVEN",
         "The second film was {} the first one.", "even worse than", "B2",
         None, "even + comparative", "comparison"),
        ("We should make good use of the sunshine while it lasts.",
         "ADVANTAGE", "We should {} the sunshine while it lasts.",
         "take advantage of / take full advantage of", "B2", "collocation",
         "take advantage of", "collocation"),
        ("Mr Nowak is responsible for the school trip to Gdańsk.", "CHARGE",
         "Mr Nowak {} the school trip to Gdańsk.",
         "is in charge of / is the teacher in charge of / "
         "is the person in charge of / is the one in charge of", "B2",
         "collocation", "be in charge of", "collocation"),
        ("I put on a thick coat because I didn't want to catch a cold.", "SO",
         "I put on a thick coat {} a cold.",
         "so as not to catch / so that I would not catch / "
         "so I would not catch / so that I did not catch / "
         "so I did not catch",
         "C1", None, "so as not to (a negative purpose)", "linking-words"),
        ("Living in a big city was new and strange to me at first.", "USED",
         "At first I {} in a big city.",
         "was not used to living / was not used to life / "
         "was not yet used to living / was not used to being", "C1", None,
         "be used to + -ing", "verb-patterns"),
        ("The film will start in a moment.", "ABOUT", "The film {} start.",
         "is about to / is just about to", "B2", None,
         "be about to for the very near future", "tenses"),
        ("'Please, please let me come with you!' my little brother said to "
         "me.", "BEGGED", "My little brother {} him come with me.",
         "begged me to let", "C1", None, "beg someone to + infinitive",
         "reported-speech"),
        ("He didn't say thank you even once.", "ONCE", "Not {} thank you.",
         "once did he say", "C1", None, "inversion after not once",
         "inversion"),
        ("Our school is very close to my house.", "THROW",
         "Our school is only {} my house.",
         "a stone's throw from / a stone's throw away from", "C1", "idiom",
         "a stone's throw", "idiom"),
    ],
    "choice": [
        ("My uncle {} a living by repairing old bikes.",
         ["wins", "earns", "gains", "takes"], "B", "B2", "collocation",
         "earn a living", "collocation"),
        ("It's {} to say that our class has the best football team in the "
         "school.", ["sure", "certain", "safe", "secure"], "C", "C1",
         "collocation", "it's safe to say", "collocation"),
        ("I've said I'm sorry, so now the ball is in your {}.",
         ["court", "field", "hands", "goal"], "A", "C1", "idiom",
         "the ball is in your court", "idiom"),
        ("We need to {} up with a name for our band before the concert.",
         ["think", "make", "come", "get"], "C", "B2", "phrasal verb",
         "come up with", "phrasal-verb"),
        ("Kraków is the {} biggest city in Poland, after Warsaw.",
         ["two", "second", "twice", "double"], "B", "B1", None,
         "the second + superlative", "comparison"),
        ("{} it was raining, we decided to stay at home and play board games.",
         ["Since", "Despite", "Unless", "However"], "A", "B2", None,
         "since for a reason", "linking-words"),
        ("I wish it {} raining: I want to go to the park!",
         ["stops", "will stop", "has stopped", "would stop"], "D", "C1", None,
         "wish + would for something you want to change", "conditionals"),
        ("Everything {} he told us turned out to be true.",
         ["what", "who", "whose", "that"], "D", "B2", None,
         "everything that (not *everything what)", "relative-clauses"),
        ("My little brother keeps {} my pens without asking!",
         ["take", "taking", "to take", "took"], "B", "B2", None,
         "keep + -ing", "verb-patterns"),
        ("The shop is closed, so we might as {} go home.",
         ["good", "well", "better", "soon"], "B", "C1", None, "might as well",
         "modals"),
    ],
    "culture": [
        ("Who runs the debates in the House of Commons and calls 'Order! "
         "Order!' when MPs get too noisy?",
         ["the Speaker", "Black Rod", "the Lord Speaker",
          "the Serjeant at Arms"], "A",
         "Political life: the House of Commons, the Speaker", "uk-politics"),
        ("Which country of the UK has no parliament or assembly of its own, "
         "so its laws are made by the UK Parliament?",
         ["Scotland", "Wales", "Northern Ireland", "England"], "D",
         "Political life: devolution", "uk-politics"),
        ("Why is the flag of Scotland a white X on a blue background?",
         ["The X stands for ten, the number of the old Scottish kingdoms.",
          "St Andrew was killed on an X-shaped cross.",
          "It shows the two swords of a famous Scottish king.",
          "It was copied from the flag of the Viking attackers."], "B",
         "The four countries: patron saints (St Andrew)", "uk-countries"),
        ("What is on top of the Monument, the column built to remember the "
         "Great Fire of London?",
         ["a statue of Sir Christopher Wren", "a stone lion",
          "a golden urn with flames", "a golden crown"], "C",
         "Landmarks of London: the Monument", "uk-london"),
        ("What is the Serpentine in Hyde Park?",
         ["a glass building from the Great Exhibition",
          "a long lake made in the 18th century",
          "a winding path for horse riders", "a very old oak tree"], "B",
         "London's Royal Parks: Hyde Park", "uk-parks"),
    ],
}

# --------------------------------------------------------------------------
# Batch 08 (written 2026-11-02, with batch 09). By then he had seen all 315
# items; the lean follows his record without the test he left after 23
# questions on 2026-11-01: base-change, vowels, suffix-spelling,
# double-letters, uk-politics, uk-people, uk-parks.
# --------------------------------------------------------------------------

T08 = {
    "formation": [
        ("Two cars were badly damaged in a {} at the crossroads.", "COLLIDE",
         ["collision"], "C1", None, "stem change (collide -> collis-) + -ion",
         "base-change"),
        ("The last ten minutes of the film were full of {}: we had no idea if "
         "the hero would survive.", "SUSPEND", ["suspense"], "B2", None,
         "stem change (suspend -> suspense)", "base-change"),
        ("Some of his jokes were so {} that he had to apologise.", "OFFEND",
         ["offensive"], "B2", None, "stem change (offend -> offens-) + -ive",
         "base-change"),
        ("I'm {} sorry, but I've lost the book you lent me.", "TERRIBLE",
         ["terribly"], "B1", None, "-le to -ly (not *terriblely)",
         "suffix-spelling"),
        ("Spring days in the mountains are very {}: sunny one minute and "
         "stormy the next.", "CHANGE", ["changeable"], "C1", None,
         "e kept before -able (not *changable)", "suffix-spelling"),
        ("Don't throw away the {} paper: we can use it again next "
         "Christmas.", "WRAP", ["wrapping"], "B2", None,
         "double p (not *wraping)", "double-letters"),
        ("As a teenager, my dad was quite {}: he never did what his parents "
         "told him.", "REBEL", ["rebellious"], "C1", None,
         "double l + -ious (not *rebelious)", "double-letters"),
        ("It was very {} of you to laugh when he fell off his bike.", "MATURE",
         ["immature"], "C1", None, "im- before m (not *unmature)",
         "negative-prefix"),
        ("If you need any {}, please ask at the reception desk.", "ASSIST",
         ["assistance"], "B2", None, "-ance (not *assistence)", "ance-ence"),
        ("The ballet dancer moved {} around the stage, as if she were flying.",
         "EFFORT", ["effortlessly"], "C1", None,
         "two steps (effort -> effortless -> effortlessly)", "two-steps"),
    ],
    "hangman": [
        ("Our English teacher says my {} is good, but my spelling needs work.",
         "g_____r", "grammar", "B1", None,
         "spelling (-ar, not *grammer; double m)", "vowels"),
        ("Pens, paper, rulers and other {} are sold in the little shop next "
         "to our school.", "_t__i___r_", "stationery", "C1", None,
         "spelling (-ery for paper and pens; stationary means not moving)",
         "vowels"),
        ("Don't worry, the pen washes off: the ink isn't {}.", "p__m____t",
         "permanent", "B2", None, "spelling (-a-e-, not *permenant)",
         "vowels"),
        ("We tied a red {} to the gate so our guests could find the house.",
         "b_____n", "balloon", "B1", None, "spelling (double l, double o)",
         "double-letters"),
        ("Pictures taken by a {} high above the Earth show where the storms "
         "are.", "s__e____e", "satellite", "B2", None,
         "spelling (one t, double l)", "double-letters"),
        ("My uncle sailed his {} all the way from Gdańsk to Sweden.", "y____",
         "yacht", "C1", None, "spelling (silent ch)", "silent-letters"),
        ("Don't make such a {} about a tiny scratch: it will heal in a day or "
         "two!", "_u__", "fuss", "C1", "collocation",
         "make a fuss; double s", "collocation"),
        ("There's only a {} chance that we'll win, but we'll do our best.",
         "_l__", "slim", "C1", "collocation", "a slim chance", "collocation"),
        ("I ran as quickly as I could and finally {} up with the others.",
         "c____t", "caught", "B2", "phrasal verb", "catch up with; -augh-",
         "phrasal-verb"),
        ("The problems we know about are only the tip of the {}: there are "
         "many more.", "i__b___", "iceberg", "C1", "idiom",
         "the tip of the iceberg", "idiom"),
    ],
    "transform": [
        ("Her first book was much, much better than her second one.",
         "NOWHERE", "Her second book was {} her first one.",
         "nowhere near as good as / nowhere near so good as", "C1", None,
         "nowhere near as + adjective + as", "comparison"),
        ("The red T-shirt costs more than the blue one.", "LESS",
         "The blue T-shirt {} the red one.",
         "costs less than / is less expensive than / is less costly than",
         "B2", None, "less + adjective + than", "comparison"),
        ("I had only just sat down when the phone rang.", "HARDLY",
         "{} down when the phone rang.", "Hardly had I sat", "C1", None,
         "hardly had I ... when (inversion)", "inversion"),
        ("I was enjoying the game so much that I didn't notice how late it "
         "was.", "TRACK",
         "I was enjoying the game so much that I {} time.",
         "lost track of / completely lost track of / totally lost track of",
         "C1", "collocation", "lose track of time", "collocation"),
        ("My brother never thanks Mum for cooking: he thinks it's normal that "
         "she does it.", "GRANTED", "My brother {} that Mum cooks for him.",
         "takes it for granted / just takes it for granted / "
         "simply takes it for granted", "B2", "collocation",
         "take it for granted (that)", "collocation"),
        ("We didn't go to the cinema; we stayed at home and played board "
         "games.", "INSTEAD",
         "We stayed at home and played board games {} to the cinema.",
         "instead of going", "B2", None, "instead of + -ing",
         "verb-patterns"),
        ("Tom didn't come to the party, and Ania didn't come either.",
         "NEITHER", "{} came to the party.",
         "Neither Tom nor Ania / Neither Ania nor Tom", "B2", None,
         "neither ... nor", "linking-words"),
        ("My advice is to say sorry to her.", "WERE", "{} say sorry to her.",
         "If I were you, I would / If I were you I would / "
         "Were I you, I would / Were I you I would", "B1", None,
         "if I were you for advice", "conditionals"),
        ("'If you don't stop talking, I'll keep you after school,' the "
         "teacher said to us.", "THREATENED",
         "The teacher {} us after school if we did not stop talking.",
         "threatened to keep", "C1", None, "threaten to + infinitive",
         "reported-speech"),
        ("I really admire my older cousin.", "UP",
         "I really {} my older cousin.", "look up to", "B2", "phrasal verb",
         "look up to (admire)", "phrasal-verb"),
    ],
    "choice": [
        ("My little brother {} a tantrum in the shop because Mum wouldn't buy "
         "him sweets.", ["threw", "made", "did", "took"], "A", "C1",
         "collocation", "throw a tantrum", "collocation"),
        ("Thanks for inviting me, but football isn't really my cup of {}.",
         ["coffee", "tea", "milk", "juice"], "B", "B2", "idiom",
         "not my cup of tea", "idiom"),
        ("Firefighters managed to {} out the fire before it reached the "
         "forest.", ["take", "turn", "give", "put"], "D", "B1",
         "phrasal verb", "put out (a fire)", "phrasal-verb"),
        ("Somebody will have to {} the news to Dad: his team has lost the "
         "final.", ["say", "speak", "break", "make"], "C", "C1", "collocation",
         "break the news (to someone)", "collocation"),
        ("My brother was still angry with me: not a single word {} to me "
         "during the whole journey.",
         ["he said", "said he", "did he say", "he did say"], "C", "C1",
         None, "not a single + inversion", "inversion"),
        ("It's {} colder today than yesterday, so take your warm coat.",
         ["very", "much", "more", "most"], "B", "B1", None,
         "much + comparative (not *very colder)", "comparison"),
        ("{} I need most right now is a long holiday.",
         ["That", "Which", "What", "It"], "C", "C1", None,
         "what = the thing that", "relative-clauses"),
        ("If I had practised more last year, I {} in the school orchestra "
         "now.", ["would be", "would have been", "will be", "am"], "A", "C1",
         None, "mixed conditional (past -> present)", "conditionals"),
        ("Would you mind {} me carry these heavy bags?",
         ["help", "helping", "to help", "helped"], "B", "B2", None,
         "mind + -ing", "verb-patterns"),
        ("You {} fallen and hurt yourself climbing on that wall! Luckily you "
         "only tore your jeans.", ["must have", "could have", "should have",
                         "needn't have"], "B", "B2", None,
         "could have for something possible that did not happen", "modals"),
    ],
    "culture": [
        ("Where does the Northern Ireland Assembly meet?",
         ["at Holyrood", "at Stormont", "in the Senedd", "at Westminster"],
         "B", "Political life: devolution, the Northern Ireland Assembly",
         "uk-politics"),
        ("In 2014 people in Scotland voted in a referendum on independence. "
         "What was the result?",
         ["Most voted Yes, so Scotland left the UK in 2016.",
          "Exactly half voted each way, so nothing changed.",
          "The vote was cancelled before it took place.",
          "Most voted No, so Scotland stayed in the UK."], "D",
         "Political life: devolution, the 2014 referendum (55% No)",
         "uk-politics"),
        ("Arthur Conan Doyle partly based Sherlock Holmes on one of his "
         "teachers at medical school, who could guess a lot about patients "
         "just by looking at them. Who was he?",
         ["Robert Hooke", "Charles Babbage", "Joseph Bell", "Samuel Pepys"],
         "C", "Notable Britons: Arthur Conan Doyle, Joseph Bell", "uk-people"),
        ("Which king opened Hyde Park to the public in 1637?",
         ["Henry VIII", "Charles I", "William III", "George II"], "B",
         "London's Royal Parks: Hyde Park (1536, 1637)", "uk-parks"),
        ("Which of these did NOT help the Great Fire of London of 1666 spread "
         "so quickly?",
         ["a hot, dry summer", "a strong wind",
          "wooden houses built very close together",
          "houses built of brick and stone"], "D",
         "Historical events: the Great Fire of London, its origins",
         "uk-history"),
    ],
}

# --------------------------------------------------------------------------
# Batch 09 (written 2026-11-02, with batch 08)
# --------------------------------------------------------------------------

T09 = {
    "formation": [
        ("Taking part in the school play is {}: nobody has to do it.",
         "VOLUNTEER", ["voluntary"], "C1", None,
         "stem change (volunteer -> volunt-) + -ary", "base-change"),
        ("You need your parents' {} to go on the school trip.", "PERMIT",
         ["permission"], "B2", None, "stem change (permit -> permiss-) + -ion",
         "base-change"),
        ("There was a loud {} in the science lab, but luckily nobody was "
         "hurt.", "EXPLODE", ["explosion"], "B2", None,
         "stem change (explode -> explos-) + -ion", "base-change"),
        ("The number of pupils at our school has grown {} over the years.",
         "STEADY", ["steadily"], "B2", None, "y to i before -ly",
         "suffix-spelling"),
        ("My little brother is celebrating his {} birthday on Saturday.",
         "NINE", ["ninth"], "B1", None, "e dropped (not *nineth)",
         "suffix-spelling"),
        ("Because of the storm, we got a text message about the {} of our "
         "train.", "CANCEL", ["cancellation"], "C1", None,
         "double l before -ation", "double-letters"),
        ("The village festival takes place {}, every June.", "ANNUAL",
         ["annually"], "C1", None, "double l (annual + -ly)",
         "double-letters"),
        ("A hundred years ago, many people in the village were {}: they could "
         "not read or write.", "LITERATE", ["illiterate"], "C1", None,
         "il- before l (not *unliterate)", "negative-prefix"),
        ("At the training school, dogs learn {}: to sit, to stay and to come "
         "when they are called.", "OBEY", ["obedience"], "C1", None,
         "-ence, with obey -> obedi- (not *obediance)", "ance-ence"),
        ("It's {} whether we'll finish the project on time: there's still so "
         "much to do.", "DOUBT", ["doubtful"], "B2", None,
         "silent b kept (doubt + -ful)", "silent-letters"),
    ],
    "hangman": [
        ("Carrots are my favourite {}: I eat one every day.", "v_g___b__",
         "vegetable", "B1", None, "spelling (-e-e-a-, not *vegtable)",
         "vowels"),
        ("Your answer is interesting, but it isn't {} to the question I "
         "asked.", "____v__t", "relevant", "C1", None,
         "spelling (-e-a-, not *relavent)", "vowels"),
        ("In the museum we saw the {} of a huge dinosaur.", "_k_____n",
         "skeleton", "B2", None, "spelling (-e-e-o-, not *skeliton)",
         "vowels"),
        ("Don't run in the school {}: walk!", "c____d__", "corridor", "B2",
         None, "spelling (double r, one d, -or)", "double-letters"),
        ("Someone has sprayed {} all over the wall of the sports hall.",
         "g______i", "graffiti", "B2", None, "spelling (double f, one t)",
         "double-letters"),
        ("In most fairy tales, the {} is punished at the end.", "v_____n",
         "villain", "C1", None, "spelling (double l, -ain)",
         "double-letters"),
        ("On the plane I like to sit by the {} so that I can stretch my "
         "legs.", "a____", "aisle", "C1", None, "spelling (silent s)",
         "silent-letters"),
        ("We had to learn the whole poem by {} for the school show.", "h____",
         "heart", "B2", "idiom", "learn by heart; -ea-", "idiom"),
        ("I'm exhausted after the match, so I'm going to hit the {} early "
         "tonight.", "_a__", "sack", "C1", "idiom", "hit the sack (go to bed)",
         "idiom"),
        ("Grandad's car is twenty years old, but it looks {} new.", "b____",
         "brand", "B1", "collocation", "brand new", "collocation"),
    ],
    "transform": [
        ("Ania swims a little better than Ola.", "QUITE", "Ola {} as Ania.",
         "does not swim quite as well / does not swim quite so well / "
         "cannot swim quite as well / is not quite as good / "
         "is not quite so good", "C1", None,
         "not quite as + adverb + as", "comparison"),
        ("We had expected more people at the concert.", "AS",
         "There were not {} we had expected at the concert.",
         "as many people as / so many people as", "B2", None,
         "not as many + noun + as", "comparison"),
        ("You must never open this door, whatever happens.", "CIRCUMSTANCES",
         "{} open this door.",
         "Under no circumstances must you / Under no circumstances should "
         "you / Under no circumstances are you to / In no circumstances "
         "must you / In no circumstances should you", "C1", None,
         "under no circumstances + inversion", "inversion"),
        ("Suddenly I saw a fox in our garden.", "SIGHT",
         "Suddenly I {} a fox in our garden.", "caught sight of",
         "C1", "collocation", "catch sight of", "collocation"),
        ("Don't worry, I'm only joking.", "LEG",
         "Don't worry, I am only {}.", "pulling your leg", "C1",
         "idiom", "pull someone's leg (joke)", "idiom"),
        ("On the way home we stopped because we wanted to buy some ice cream.",
         "STOPPED", "On the way home we {} some ice cream.",
         "stopped to buy / stopped to get / stopped to have", "B2", None,
         "stop to do (for a purpose), not stop doing", "verb-patterns"),
        ("She speaks German, and French too.", "WELL",
         "She speaks French {} German.", "as well as", "B2", None,
         "as well as for and also", "linking-words"),
        ("I didn't learn to swim when I was little, so I can't swim now.",
         "WOULD", "If I had learnt to swim when I was little, I {} now.",
         "would be able to swim / would be able to / would know how to swim",
         "C1", None, "mixed conditional (past -> present)", "conditionals"),
        ("'I'll tidy my room after dinner, Mum,' said Tom.", "PROMISED",
         "Tom {} his room after dinner.",
         "promised to tidy / promised he would tidy / "
         "promised that he would tidy / promised his mum he would tidy",
         "B2", None, "promise to + infinitive", "reported-speech"),
        ("The train is expected to arrive at five o'clock.", "DUE",
         "The train {} five o'clock.",
         "is due to arrive at / is due at / is due to get in at", "B2", None,
         "be due to (expected, by a timetable)", "modals"),
    ],
    "choice": [
        ("My grandma has a sweet {}: she can never say no to cake.",
         ["mouth", "tooth", "taste", "face"], "B", "C1", "idiom",
         "have a sweet tooth", "idiom"),
        ("My brothers had a {} argument about whose turn it was to wash up.",
         ["hot", "warm", "heated", "boiling"], "C", "C1", "collocation",
         "a heated argument", "collocation"),
        ("The teacher {} us off for talking during the test.",
         ["said", "told", "spoke", "shouted"], "B", "B2", "phrasal verb",
         "tell someone off", "phrasal-verb"),
        ("Could you {} an eye on the soup while I answer the door?",
         ["keep", "hold", "watch", "have"], "A", "B2", "collocation",
         "keep an eye on", "collocation"),
        ("So hot {} that I couldn't eat it.",
         ["the soup was", "was the soup", "did the soup", "the soup did"],
         "B", "C1", None, "so + adjective + inversion", "inversion"),
        ("My new trainers are the same colour {} yours.",
         ["like", "than", "that", "as"], "D", "B1", None,
         "the same + noun + as", "comparison"),
        ("I couldn't decide {} to laugh or cry.",
         ["if", "whether", "either", "unless"], "B", "B2", None,
         "whether + to-infinitive (not *if to)", "linking-words"),
        ("Let's go to the park after lunch, {}?",
         ["will we", "don't we", "shall we", "do we"], "C", "B2", None,
         "question tag after let's", "tenses"),
        ("{} from the top of the tower, the people below looked like ants.",
         ["Seen", "Seeing", "Having seen", "To see"], "A", "C1", None,
         "past participle clause with a passive meaning",
         "participle-clauses"),
        ("These tablets must {} after meals.",
         ["take", "be taken", "taken", "be taking"], "B", "B2", None,
         "passive after a modal", "passive"),
    ],
    "culture": [
        ("Who was the first woman to be Prime Minister of the UK, nicknamed "
         "'the Iron Lady'?",
         ["Theresa May", "Margaret Thatcher", "Emmeline Pankhurst",
          "Queen Victoria"], "B",
         "Political life: the Conservative Party, Margaret Thatcher",
         "uk-politics"),
        ("Who became Prime Minister of the UK in July 2024?",
         ["Rishi Sunak", "Boris Johnson", "Keir Starmer", "David Cameron"],
         "C", "Political life: the Labour Party, Keir Starmer (July 2024)",
         "uk-politics"),
        ("What did Ada Lovelace guess that machines like Charles Babbage's "
         "Analytical Engine could one day do?",
         ["travel into space", "work with music and pictures, not just "
          "numbers", "talk to each other by telephone",
          "run on electricity instead of steam"], "B",
         "Notable Britons: Ada Lovelace", "uk-people"),
        ("Which animals are shown carrying heavy loads through a gap in a "
         "wall on the Animals in War memorial?",
         ["two horses", "two dogs", "two elephants", "two mules"], "D",
         "London's Royal Parks: Hyde Park, the Animals in War memorial",
         "uk-parks"),
        ("Which famous man was executed because he refused to accept the Act "
         "of Supremacy?",
         ["Sir Thomas More", "Guy Fawkes", "Samuel Pepys",
          "Sir Christopher Wren"], "A",
         "Historical events: the Act of Supremacy (1534)", "uk-history"),
    ],
}

# --------------------------------------------------------------------------
# Batch 10 (written 2026-11-02, with batch 11). His record had not moved since
# 08-09 were written, so the lean is theirs, with more room for the next
# group: verb-patterns, linking-words, silent-letters, inversion.
# --------------------------------------------------------------------------

T10 = {
    "formation": [
        ("We tried for an hour, but nobody could find a {} to the puzzle.",
         "SOLVE", ["solution"], "B2", None,
         "stem change (solve -> solu-) + -tion", "base-change"),
        ("In the film, a group of children save the Earth from an alien {}.",
         "INVADE", ["invasion"], "C1", None,
         "stem change (invade -> invas-) + -ion (not *invadion)",
         "base-change"),
        ("Children under five get free {} to the zoo.", "ADMIT",
         ["admission"], "C1", None,
         "stem change (admit -> admiss-) + -ion (not *admition)",
         "base-change"),
        ("A {} parcel with no name on it was waiting outside our door.",
         "MYSTERY", ["mysterious"], "B2", None, "y to i before -ous",
         "suffix-spelling"),
        ("The museum is open {} from nine to five, even at weekends.", "DAY",
         ["daily"], "B1", None, "y to i (not *dayly)", "suffix-spelling"),
        ("The police found the thieves a day after the bank {}.", "ROB",
         ["robbery"], "B2", None, "double b (rob -> robbery)",
         "double-letters"),
        ("It is {} that the old cinema in our town has closed.", "REGRET",
         ["regrettable"], "C1", None, "double t before -able",
         "double-letters"),
        ("My fear of spiders is completely {}: they can't hurt me.",
         "RATIONAL", ["irrational"], "C1", None,
         "ir- before r (not *unrational)", "negative-prefix"),
        ("After the {}, the actors came back on stage three times to bow.",
         "PERFORM", ["performance"], "B2", None, "-ance (not *performence)",
         "ance-ence"),
        ("Our cousins arrived {}, so we had to cook dinner for six more "
         "people.", "EXPECT", ["unexpectedly"], "C1", None,
         "two steps (expect -> unexpected -> unexpectedly)", "two-steps"),
    ],
    "hangman": [
        ("The {} got in through an open window and took Dad's laptop.",
         "___g__r", "burglar", "B2", None, "spelling (-ar, not *burgler)",
         "vowels"),
        ("Put the letter in an {} and write the address on it.", "__v___p_",
         "envelope", "B2", None, "spelling (-e-o-e, not *envelop)", "vowels"),
        ("A {} landed on our windowsill and ate the breadcrumbs.", "p_g___",
         "pigeon", "C1", None, "spelling (-eon, not *pigion)", "vowels"),
        ("Please put your {} in the bin, not on the floor.", "r_____h",
         "rubbish", "B1", None, "spelling (double b)", "double-letters"),
        ("Can you {} a good book for the holidays?", "___o___nd",
         "recommend", "C1", None, "spelling (one c, double m)",
         "double-letters"),
        ("Can you speak any {} languages?", "___ei__", "foreign", "B2", None,
         "spelling (silent g)", "silent-letters"),
        ("It took my parents ten years to pay back the {} for our flat.",
         "d___", "debt", "C1", None, "spelling (silent b)", "silent-letters"),
        ("My uncle is a real couch {}: he watches TV all weekend.", "__t_t_",
         "potato", "B2", "idiom", "a couch potato; no e at the end", "idiom"),
        ("The film was so boring that Grandad {} off on the sofa.", "d____",
         "dozed", "C1", "phrasal verb", "doze off; -z-", "phrasal-verb"),
        ("We need a {} of bread for the sandwiches.", "___f", "loaf", "B2",
         "collocation", "a loaf of bread", "collocation"),
    ],
    "transform": [
        ("The school's old computers are not as good as the new ones.",
         "SUPERIOR", "The new computers {} the old ones.",
         "are superior to / are far superior to / are much superior to",
         "C1", None, "superior to (not *superior than)", "comparison"),
        ("I am not responsible for this mess at all.", "WAY",
         "{} responsible for this mess.", "In no way am I", "C1", None,
         "in no way + inversion", "inversion"),
        ("My parents are thinking about buying a dog.", "CONSIDERING",
         "My parents are {} a dog.",
         "considering buying / considering getting / considering having",
         "B2", None, "consider + -ing", "verb-patterns"),
        ("Leave now, or you might be late for school.", "RISK",
         "If you do not leave now, you {} late for school.",
         "risk being / run the risk of being / will risk being", "B2", None,
         "risk + -ing", "verb-patterns"),
        ("Ania plays the piano, and she plays the guitar too.", "BOTH",
         "Ania plays {} the guitar.", "both the piano and", "B2", None,
         "both ... and", "linking-words"),
        ("It doesn't matter what you say: I'm not going to change my mind.",
         "WHATEVER", "{}, I am not going to change my mind.",
         "Whatever you say / Whatever you may say", "B2", None,
         "whatever + clause (no matter what)", "linking-words"),
        ("It's our last sunny day by the sea, so let's enjoy every minute of "
         "it.", "MOST", "It is our last sunny day by the sea, so let's {} it.",
         "make the most of", "C1", "collocation", "make the most of",
         "collocation"),
        ("'I won't lend you my bike,' Ola said to me.", "REFUSED",
         "Ola {} me her bike.", "refused to lend", "B2", None,
         "refuse to + infinitive", "reported-speech"),
        ("We can't play outside because of the rain.", "FOR",
         "If it {} rain, we could play outside.",
         "were not for the / was not for the", "C1", None,
         "if it were not for (now)", "conditionals"),
        ("I have lots of books, and I have read most of them.", "WHICH",
         "I have lots of books, {} I have read.", "most of which", "C1", None,
         "most of which", "relative-clauses"),
    ],
    "choice": [
        ("I wanted to sing at the school concert, but at the last minute I "
         "got cold {}.", ["hands", "toes", "feet", "knees"], "C", "C1",
         "idiom", "get cold feet (lose courage)", "idiom"),
        ("If Mum sees this mess, we'll be in hot {}!",
         ["soup", "tea", "milk", "water"], "D", "C1", "idiom",
         "be in hot water (in trouble)", "idiom"),
        ("Could you {} room for Grandma on the sofa?",
         ["do", "take", "give", "make"], "D", "B2", "collocation",
         "make room (for someone)", "collocation"),
        ("My alarm clock {} off at six, but I didn't hear it.",
         ["came", "went", "got", "took"], "B", "B1", "phrasal verb",
         "go off (an alarm rings)", "phrasal-verb"),
        ("My brother is three years {} than me.",
         ["elder", "eldest", "oldest", "older"], "D", "B1", None,
         "older than (elder is not used with than)", "comparison"),
        ("I can hardly ride a bike, {} drive a car!",
         ["as well as", "let alone", "instead of", "apart from"], "B", "C1",
         None, "let alone (much less)", "linking-words"),
        ("When Mum came into the room, my brother pretended {} asleep.",
         ["being", "be", "to be", "been"], "C", "B2", None,
         "pretend + to-infinitive", "verb-patterns"),
        ("The reason {} I'm late is that I missed the bus.",
         ["why", "which", "what", "because"], "A", "B2", None,
         "the reason why", "relative-clauses"),
        ("{} to my grandma, there was only one shop in our village when she "
         "was little.", ["According", "Due", "Thanks", "Owing"], "A", "B2",
         None, "according to (as stated by)", "linking-words"),
        ("{} his surprise that he couldn't say a word.",
         ["So was", "Such was", "It was", "Such were"], "B", "C1", None,
         "such + be + inversion", "inversion"),
    ],
    "culture": [
        ("In which year did Scotland, Wales and Northern Ireland start making "
         "some of their own laws, after devolution?",
         ["1945", "1973", "1999", "2014"], "C",
         "Political life: devolution (1999)", "uk-politics"),
        ("How often must a general election take place in the UK?",
         ["every year", "at least every five years", "every ten years",
          "only when the King decides"], "B",
         "Political life: the House of Commons, general elections",
         "uk-politics"),
        ("Where did Arthur Conan Doyle make Sherlock Holmes 'die' in 1893?",
         ["at the Reichenbach Falls", "on Baker Street", "in the River Thames",
          "on a ship to America"], "A",
         "Notable Britons: Arthur Conan Doyle, the Reichenbach Falls",
         "uk-people"),
        ("Which king and queen turned a house next to Kensington Gardens into "
         "Kensington Palace in 1689?",
         ["Henry VIII and Anne Boleyn", "Charles I and Henrietta Maria",
          "George II and Caroline", "William III and Mary II"], "D",
         "London's Royal Parks: Kensington Gardens, Kensington Palace (1689)",
         "uk-parks"),
        ("What is on the national flag of Wales?",
         ["a gold harp", "a white X on blue", "a red dragon", "a red lion"],
         "C", "Symbols of the UK: Wales and the flags", "uk-symbols"),
    ],
}

# --------------------------------------------------------------------------
# Batch 11 (written 2026-11-02, with batch 10)
# --------------------------------------------------------------------------

T11 = {
    "formation": [
        ("Our teacher says that {} is the best way to learn new words.",
         "REPEAT", ["repetition"], "C1", None,
         "stem change (repeat -> repet-) + -ition (not *repeatition)",
         "base-change"),
        ("Don't forget to put an {} mark after 'What a surprise'.", "EXCLAIM",
         ["exclamation"], "C1", None,
         "stem change (exclaim -> exclam-) + -ation (not *exclaimation)",
         "base-change"),
        ("My grandma is full of {}: she always gives the best advice.", "WISE",
         ["wisdom"], "B2", None,
         "stem change (wise -> wis-) + -dom (not *wisedom)", "base-change"),
        ("I {} hope you feel better soon.", "SINCERE", ["sincerely"], "B2",
         None, "e kept before -ly (not *sincerly)", "suffix-spelling"),
        ("Our plants are {} because nobody has watered them for weeks.", "DIE",
         ["dying"], "B2", None, "ie to y before -ing (not *dieing)",
         "suffix-spelling"),
        ("The pictures of the flood on the news were very {}.", "UPSET",
         ["upsetting"], "B2", None, "double t before -ing", "double-letters"),
        ("I'm only a {}, so please be patient with me.", "BEGIN",
         ["beginner"], "B1", None, "double n before -er", "double-letters"),
        ("A true friend is never {}: they stay on your side even when things "
         "are hard.", "LOYAL", ["disloyal"], "C1", None,
         "dis- (not *unloyal)", "negative-prefix"),
        ("I don't mind which film we watch: I have no {}.", "PREFER",
         ["preference"], "C1", None, "-ence, one r (not *preferance)",
         "ance-ence"),
        ("My new jacket is {}: it's blue on one side and red on the other.",
         "REVERSE", ["reversible"], "C1", None,
         "-ible, e dropped (not *reversable)", "able-ible"),
    ],
    "hangman": [
        ("Your face looks {}: have we met before?", "f_m_____", "familiar",
         "B2", None, "spelling (-iar, not *familier)", "vowels"),
        ("If you're not sure how to spell a word, check it in a {}.",
         "d__t__n___", "dictionary", "B1", None,
         "spelling (-ary, not *dictionery)", "vowels"),
        ("She looked very {} in her long blue dress.", "e__g___", "elegant",
         "C1", None, "spelling (-e-a-, not *eligant)", "vowels"),
        ("A {} ran up the tree with a nut in its mouth.", "_q_____l",
         "squirrel", "B2", None, "spelling (double r, -el)", "double-letters"),
        ("Grandma's apple pie always smells of {}.", "c_____o_", "cinnamon",
         "C1", None, "spelling (double n, one m)", "double-letters"),
        ("Grandad always carries a cotton {} in his pocket.", "h____e_____f",
         "handkerchief", "C1", None, "spelling (silent d, -ie-)",
         "silent-letters"),
        ("We had grilled {} with rice and salad for dinner.", "___mo_",
         "salmon", "B2", None, "spelling (silent l)", "silent-letters"),
        ("Dad never takes sides when my sister and I argue: he always sits on "
         "the {}.",
         "f____", "fence", "C1", "idiom", "sit on the fence (not decide)",
         "idiom"),
        ("You've made great {} with your English this year!", "__og____",
         "progress", "B2", "collocation", "make progress; double s",
         "collocation"),
        ("Stop {} off: nobody cares about your new phone!", "s__w___",
         "showing", "B2", "phrasal verb", "show off", "phrasal-verb"),
    ],
    "transform": [
        ("Please come back as soon as you can.", "POSSIBLE",
         "Please come back {}.",
         "as soon as possible / as quickly as possible", "B1", None,
         "as ... as possible", "comparison"),
        ("I didn't suspect at all that he was lying.", "MOMENT",
         "Not for {} he was lying.",
         "a moment did I suspect that / a moment did I think that / "
         "a moment did I suspect / a moment did I think", "C1", None,
         "not for a moment + inversion", "inversion"),
        ("Mum was cooking dinner, so she couldn't answer the phone.", "BUSY",
         "Mum was {} dinner, so she could not answer the phone.",
         "busy cooking / busy making / busy preparing", "B2", None,
         "busy + -ing", "verb-patterns"),
        ("Someone should cut the grass in our garden: it's very long.",
         "NEEDS", "The grass in our garden {}: it is very long.",
         "needs cutting / needs to be cut / needs mowing / "
         "needs to be mowed / needs to be mown", "C1", None,
         "need + -ing (passive meaning)", "verb-patterns"),
        ("You can have pizza or pasta for dinner, but not both.", "EITHER",
         "You can have {} pasta for dinner.", "either pizza or", "B1", None,
         "either ... or", "linking-words"),
        ("My brother has left home, so I have my own room at last.", "NOW",
         "{} home, I have my own room at last.",
         "Now that my brother has left / Now my brother has left / "
         "Now that he has left / Now he has left", "C1", None,
         "now that (because now)", "linking-words"),
        ("We threw away our old toys before we moved.", "RID",
         "We {} our old toys before we moved.", "got rid of", "B2",
         "collocation", "get rid of", "collocation"),
        ("'I didn't eat the last biscuit,' said Tom.", "DENIED",
         "Tom {} the last biscuit.",
         "denied eating / denied having eaten / denied that he had eaten / "
         "denied he had eaten / denied that he ate / denied he ate", "B2",
         None, "deny + -ing", "reported-speech"),
        ("It's quite possible that it will snow tonight.", "WELL",
         "It {} tonight.", "may well snow / might well snow / could well snow",
         "C1", None, "may well (quite possibly)", "modals"),
        ("If the bus is on time, we'll be home by six.", "ASSUMING",
         "{} on time, we will be home by six.",
         "Assuming the bus is / Assuming that the bus is / "
         "Assuming the bus will be / Assuming that the bus will be", "C1",
         None, "assuming (that) for if", "conditionals"),
    ],
    "choice": [
        ("Don't worry about the test: we're all in the same {}.",
         ["boat", "ship", "car", "bus"], "A", "C1", "idiom",
         "be in the same boat", "idiom"),
        ("If we go to the bakery on the way to school, we'll kill two {} with "
         "one stone.", ["flies", "cats", "fish", "birds"], "D", "C1", "idiom",
         "kill two birds with one stone", "idiom"),
        ("Our class is {} money for the animal shelter.",
         ["rising", "raising", "lifting", "growing"], "B", "B2", "collocation",
         "raise money (raise, not rise)", "collocation"),
        ("Ola and I {} out last week, but now we're friends again.",
         ["fell", "went", "got", "came"], "A", "B2", "phrasal verb",
         "fall out (with someone)", "phrasal-verb"),
        ("My bedroom is only {} big as yours.",
         ["half", "as half", "half of", "half as"], "D", "C1", None,
         "half as + adjective + as", "comparison"),
        ("It was raining heavily; {}, the match was cancelled.",
         ["however", "although", "therefore", "because"], "C", "B2", None,
         "therefore (so, as a result)", "linking-words"),
        ("I really miss {} football with my old friends.",
         ["play", "to play", "playing", "played"], "C", "B2", None,
         "miss + -ing", "verb-patterns"),
        ("What would you do if you {} a wallet in the street?",
         ["find", "found", "will find", "would find"], "B", "B1", None,
         "second conditional (if + past)", "conditionals"),
        ("The man {} next to me on the bus was reading a newspaper.",
         ["sitting", "sit", "sits", "who sitting"], "A", "B2", None,
         "-ing participle for who was sitting", "participle-clauses"),
        ("Only by working hard {} pass the exam.",
         ["you can", "you could", "can you", "you will"], "C", "C1", None,
         "only by + inversion", "inversion"),
    ],
    "culture": [
        ("What is a constituency?",
         ["a group of laws passed together",
          "the area that one MP is elected to represent",
          "the room where the House of Lords meets",
          "a meeting of all the government ministers"], "B",
         "Political life: the House of Commons, constituencies",
         "uk-politics"),
        ("What can the House of Lords do with a new law that the House of "
         "Commons has passed?",
         ["stop it for ever", "sign it so that it becomes law",
          "check it, improve it and delay it, but not stop it in the end",
          "replace the Prime Minister who wrote it"], "C",
         "Political life: the House of Lords", "uk-politics"),
        ("In which city was Emmeline Pankhurst, the leader of the "
         "suffragettes, born?", ["London", "Liverpool", "Cardiff",
                                 "Manchester"], "D",
         "Notable Britons: Emmeline Pankhurst", "uk-people"),
        ("What happened to the Magna Carta a few weeks after King John sealed "
         "it?",
         ["The Pope cancelled it.", "It burnt in a fire in London.",
          "The barons tore it up.", "It was sent to France."], "A",
         "Historical events: the Magna Carta (1215)", "uk-history"),
        ("What does a legend say will happen if the ravens ever leave the "
         "Tower of London?",
         ["The Thames will flood.", "The Crown Jewels will disappear.",
          "The kingdom will fall.", "Big Ben will stop."], "C",
         "Landmarks of London: the Tower of London, the ravens", "uk-london"),
    ],
}

# --------------------------------------------------------------------------
# Wisielec batches 12-16, written 2026-11-11
# --------------------------------------------------------------------------
# Ten wisielec rows each, no other task (build_one_task_batch). By 10.11 he had
# seen all 495 items, and in wisielec he missed vowels (39% of his answers of
# that type wrong), double letters (29%) and silent letters (23%) most, so
# those lead; three idiom, collocation or phrasal verb items in each, as task
# 2 needs. Rows as in a full batch's "hangman".

T12 = {
    "hangman": [
        ("I bought a fridge magnet as a {} of our holiday in Kraków.",
         "___v___r", "souvenir", "B2", None,
         "spelling (-ou-, -enir, not *suvenir)", "vowels"),
        ("My new bed has a soft {}, so I sleep really well.",
         "m___r___", "mattress", "B2", None,
         "spelling (double t, double s)", "double-letters"),
        ("Grandma knocked on the door so hard that she hurt her {}.",
         "_nu_____", "knuckles", "C1", None, "spelling (silent k, -ckles)",
         "silent-letters"),
        ("In a wolf pack there is a strict {}: every wolf knows who is in "
         "charge.", "___r_r__y", "hierarchy", "C1", None,
         "spelling (-ie-, -archy)", "vowels"),
        ("The actress wore a {} silver dress to the film premiere.",
         "g__m____s", "glamorous", "C1", None,
         "u dropped before -ous (not *glamourous)", "suffix-spelling"),
        ("Check your essay before you hand it in: it's easy to {} a long "
         "word.", "m___p___", "misspell", "C1", None,
         "spelling (mis + spell: double s, double l)", "double-letters"),
        ("A {} has one or two horns on its nose and very thick grey skin.",
         "r_i__c____", "rhinoceros", "B2", None, "spelling (silent h, -os)",
         "silent-letters"),
        ("Wait until the {} is clear, then we can sneak into the kitchen for "
         "some biscuits.", "c____", "coast", "C1", "idiom",
         "the coast is clear (nobody is watching)", "idiom"),
        ("Can you pass me a pair of {}? I need to cut out this picture.",
         "__i__o__", "scissors", "B1", "collocation",
         "a pair of scissors; silent c, double s", "collocation"),
        ("It took the class ten minutes to {} down after the break.",
         "s___l_", "settle", "B2", "phrasal verb", "settle down; double t",
         "phrasal-verb"),
    ],
}

T13 = {
    "hangman": [
        ("Mum ordered a {} with lots of milky foam on top.",
         "c___u____o", "cappuccino", "B2", None,
         "spelling (double p, double c)", "double-letters"),
        ("When Queen Elizabeth II died in 2022, Charles became the British "
         "{}.", "_o__r___n", "sovereign", "C2", None,
         "spelling (-ei-, silent g)", "silent-letters"),
        ("My sister loves reading, so she wants to study English {} at "
         "university.", "l___r__u__", "literature", "B2", None,
         "spelling (-er-a-, not *litrature)", "vowels"),
        ("We stopped the car to admire the beautiful mountain {}.",
         "s__n___", "scenery", "B2", None, "spelling (silent c, -ery)",
         "silent-letters"),
        ("We don't have {} money to buy a new car this year.",
         "s___i____t", "sufficient", "C1", None,
         "spelling (double f, -cient)", "double-letters"),
        ("The music was so quiet that it was hardly {} at the back of the "
         "hall.", "__d_b__", "audible", "C1", None,
         "-ible (not *audable)", "able-ible"),
        ("The new puppy had to stay in {} for two weeks before it could come "
         "home.", "q____n___e", "quarantine", "C1", None,
         "spelling (-ua-, -antine)", "vowels"),
        ("I made the last bus by the skin of my {}: the doors closed right "
         "behind me.", "____h", "teeth", "C1", "idiom",
         "by the skin of your teeth (only just)", "idiom"),
        ("Dad gave Mum a big {} of flowers for her birthday.", "b____",
         "bunch", "B1", "collocation", "a bunch of flowers", "collocation"),
        ("Please {} up, or we'll miss the train!", "h____", "hurry", "B1",
         "phrasal verb", "hurry up; double r", "phrasal-verb"),
    ],
}

T14 = {
    "hangman": [
        ("Leave the butter out of the fridge for an hour to let it {}.",
         "s_f___", "soften", "C1", None, "spelling (silent t)",
         "silent-letters"),
        ("I made a salad with tomatoes, onions and fresh {}.",
         "le_____", "lettuce", "B2", None, "spelling (double t, -uce)",
         "double-letters"),
        ("There's a {} smell coming from the fridge: I think the cheese has "
         "gone off.", "w____", "weird", "B2", None,
         "spelling (-ei-, not *wierd)", "vowels"),
        ("The project looked huge at first, but with Dad's help it was quite "
         "{}.", "m___g___l_", "manageable", "C1", None,
         "e kept before -able (not *managable)", "suffix-spelling"),
        ("The bakery is on the {} side of the street, facing the bank.",
         "o__o____", "opposite", "B1", None, "spelling (double p, -ite)",
         "double-letters"),
        ("The {} and his dog led the sheep down from the hills before the "
         "storm.", "__ep____", "shepherd", "B2", None,
         "spelling (silent h, -erd)", "silent-letters"),
        ("Aunt Ewa knitted me a {} jumper with a green reindeer on it, but I "
         "said thank you anyway.", "h_d____", "hideous", "C1", None,
         "spelling (-eous)", "vowels"),
        ("Our class raised fifty zloty for the new playground, but that's "
         "just a drop in the {}.", "o____", "ocean", "C1", "idiom",
         "a drop in the ocean (far too little)", "idiom"),
        ("Can I have another {} of pizza, please? It's delicious!", "s____",
         "slice", "B1", "collocation", "a slice of pizza", "collocation"),
        ("Nobody {} up to breaking the window, so the whole class had to stay "
         "after school.", "_w___", "owned", "C1", "phrasal verb",
         "own up (admit)", "phrasal-verb"),
    ],
}

T15 = {
    "hangman": [
        ("The new statue in the town square is {}: it's taller than our "
         "school.", "___o___l", "colossal", "C2", None,
         "spelling (one l, double s)",
         "double-letters"),
        ("I told Mum that I had eaten the last biscuit, because I had a "
         "guilty {}.", "__n____nc_", "conscience", "C1", None,
         "spelling (silent c, -ience)", "silent-letters"),
        ("I always put some {} in my sandwich because it's cool and "
         "crunchy.", "__c__b__", "cucumber", "B1", None,
         "spelling (u-u-e, not *cucamber)", "vowels"),
        ("We were {} by the bright lights of the city at night.",
         "d___l__", "dazzled", "C1", None, "spelling (double z)",
         "double-letters"),
        ("I bought a {} with jam inside at the bakery.", "d_____u_",
         "doughnut", "B2", None, "spelling (-ough-)", "silent-letters"),
        ("The neighbours' dog looks {}, but it's actually very friendly.",
         "v_____s", "vicious", "C1", None, "spelling (-cious)", "vowels"),
        ("Every December we put a {} of holly and pine cones on our front "
         "door.", "____th", "wreath", "C1", None,
         "spelling (silent w, -ea-)", "silent-letters"),
        ("Don't worry, making pancakes isn't {} science: anyone can do it!",
         "r__k__", "rocket", "B2", "idiom",
         "it's not rocket science (it's easy)", "idiom"),
        ("I've got a {} headache, so I'm going to lie down in a dark room.",
         "_pli_____", "splitting", "C1", "collocation",
         "a splitting headache; double t", "collocation"),
        ("Our teacher {} out three mistakes in my story.", "_oi____",
         "pointed", "B2", "phrasal verb", "point out (show)", "phrasal-verb"),
    ],
}

T16 = {
    "hangman": [
        ("Prince William is the {} to the throne.", "___r", "heir", "C1",
         None, "spelling (silent h)", "silent-letters"),
        ("A {} can reach leaves at the very top of tall trees with its long "
         "neck.", "g__a___", "giraffe", "B1", None,
         "spelling (one r, double f)", "double-letters"),
        ("The letter was {}: nobody knew who had written it.", "a__n____s",
         "anonymous", "C1", None, "spelling (-y-, -ous)", "vowels"),
        ("The car began to {} as it went down the hill, so Dad put his foot "
         "on the brake.", "a____e___e", "accelerate", "C1", None,
         "spelling (double c, one l)", "double-letters"),
        ("The sailors dropped the {} and the ship stopped near the beach.",
         "a___o_", "anchor", "B2", None, "spelling (ch said as k)",
         "silent-letters"),
        ("The film was {}: we left the cinema after half an hour.", "__f__",
         "awful", "B1", None, "e dropped (awe -> awful, not *aweful)",
         "suffix-spelling"),
        ("Every morning Grandad eats a bowl of hot {} with honey.",
         "p___i___", "porridge", "B2", None, "spelling (double r, -idge)",
         "double-letters"),
        ("You look very quiet today. A {} for your thoughts?", "p____",
         "penny", "C1", "idiom",
         "a penny for your thoughts (what are you thinking?)", "idiom"),
        ("Our new neighbour is from Glasgow and speaks with a strong Scottish "
         "{}.", "a____t", "accent", "B2", "collocation",
         "a strong accent; double c", "collocation"),
        ("My favourite band {} up last year, and I'm still sad about it.",
         "s____", "split", "B2", "phrasal verb",
         "split up (stop being together)", "phrasal-verb"),
    ],
}

# --------------------------------------------------------------------------
# One-task batches 17-29, written 2026-11-11
# --------------------------------------------------------------------------
# 100 items for the four tasks that had no unseen item left, one task per
# batch (build_one_task_batch): word formation 17-19, transformations 20-21,
# choice 22-23, UK culture 24-29. His record that day, without the three
# tests he left early (13, 14 and 16 of 45): UK politics 44% of his answers
# of that type wrong, UK parks 39%, base change 35%, UK people 30%, suffix
# spelling 28%, inversion 28%, UK history 24%, double letters 22%. Those
# lead each task. Rows as in a full batch.

T17 = {
    "formation": [
        ("When I asked who had eaten my chocolate, my brother got very {} and "
         "started shouting.", "DEFEND", ["defensive"], "B2", None,
         "stem change (defend -> defens-) + -ive (not *defendive)",
         "base-change"),
        ("Our school is very {}: every pupil feels welcome, whatever their "
         "background.", "INCLUDE", ["inclusive"], "B2", None,
         "stem change (include -> inclus-) + -ive (not *includive)",
         "base-change"),
        ("My little brother is still not very good at {} his shoelaces.",
         "TIE", ["tying"], "B2", None, "ie to y before -ing (not *tieing)",
         "suffix-spelling"),
        ("The older boys laughed {} at the new pupil's old trainers, which "
         "made her cry.", "CRUEL", ["cruelly"], "B2", None, "double l: cruel + -ly",
         "double-letters"),
        ("Laughing at someone whose pet has just died is really {}.",
         "SENSITIVE", ["insensitive"], "B2", None, "in- (not *unsensitive)",
         "negative-prefix"),
        ("Our teacher explains maths with great {}, so everyone understands "
         "it.", "CLEAR", ["clarity"], "C1", None,
         "stem change (clear -> clar-) + -ity (not *clearity)", "base-change"),
        ("This is {} the best pizza in town, although some people prefer the "
         "one near the station.", "ARGUE", ["arguably"], "C1", None,
         "e dropped before -ably (not *argueably)", "suffix-spelling"),
        ("Mum says my {} gets me into trouble: I never change my mind, even "
         "when I'm wrong.", "STUBBORN", ["stubbornness"], "C1", None,
         "double n: stubborn + -ness", "double-letters"),
        ("Rice is easily {}, so it is good food when you have a stomach ache.",
         "DIGEST", ["digestible"], "C1", None, "-ible (not *digestable)",
         "able-ible"),
        ("Our team won the cup thanks to hard work and {}: we never gave up, "
         "even when we were losing.", "PERSIST", ["persistence"], "C1", None,
         "-ence (not *persistance)", "ance-ence"),
    ],
}

T18 = {
    "formation": [
        ("They say that money can't buy {}.", "HAPPY", ["happiness"], "B1",
         None, "y to i before -ness (not *happyness)", "suffix-spelling"),
        ("After a lot of {}, my parents finally agreed to let me go to the "
         "camp.", "PERSUADE", ["persuasion"], "B2", None,
         "stem change (persuade -> persuas-) + -ion (not *persuadion)",
         "base-change"),
        ("Everyone in the class was {} of Ola's new bike: it was the best one "
         "at school.", "ENVY", ["envious"], "B2", None,
         "y to i before -ous (not *envyous)", "suffix-spelling"),
        ("The school has bought new sports {}: balls, nets and mats.", "EQUIP",
         ["equipment"], "B2", None,
         "one p before -ment (not *equippment; compare equipped)",
         "double-letters"),
        ("Our old car is slow, but it's very {}: it starts every time, even on "
         "the coldest mornings.", "DEPEND", ["dependable"], "B2", None,
         "-able (not *dependible)", "able-ible"),
        ("Despite all his success, the famous footballer is known for his {}: "
         "he never boasts about it.", "HUMBLE", ["humility"], "C1", None,
         "stem change (humble -> humil-) + -ity (not *humblity)",
         "base-change"),
        ("Speaking two languages can be very {} when you look for a job.",
         "ADVANTAGE", ["advantageous"], "C1", None,
         "e kept before -ous (not *advantagous)", "suffix-spelling"),
        ("Our new drone is easily {} from a phone app.", "CONTROL",
         ["controllable"], "C1", None,
         "double l before -able (not *controlable)", "double-letters"),
        ("The referee was so {} that he didn't see the most obvious foul of "
         "the match.", "COMPETENT", ["incompetent"], "C1", None,
         "in- (not *uncompetent)", "negative-prefix"),
        ("The village is very {}, with old stone houses and flowers everywhere.",
         "PICTURE", ["picturesque"], "C1", None,
         "-esque (not *picturous, *pictureful)", "word-ending"),
    ],
}

T19 = {
    "formation": [
        ("The magazine has an {} interview with the singer: no other magazine "
         "has spoken to her.", "EXCLUDE", ["exclusive"], "B2", None,
         "stem change (exclude -> exclus-) + -ive (not *excludive)",
         "base-change"),
        ("The story ended {}: the hero died in the last chapter.", "TRAGIC",
         ["tragically"], "B2", None, "-ally after -ic (not *tragicly)",
         "suffix-spelling"),
        ("Stop {}! We still have ten minutes to get to the station.", "PANIC",
         ["panicking"], "B2", None, "k added before -ing (not *panicing)",
         "suffix-spelling"),
        ("Our school has zero {} for bullying.", "TOLERATE", ["tolerance"],
         "B2", None, "-ance (not *tolerence)", "ance-ence"),
        ("Every November, people in Britain wear red poppies as a sign of {}.",
         "REMEMBER", ["remembrance"], "C1", None,
         "stem change (remember -> remembr-) + -ance (not *rememberance)",
         "base-change"),
        ("Doctors say that half an hour of {} exercise a day keeps you healthy.",
         "VIGOUR", ["vigorous"], "C2", None,
         "-our to -or- before -ous (not *vigourous)", "base-change"),
        ("The {} of the storm surprised everyone: one minute the sky was blue, "
         "the next it was pouring.", "SUDDEN", ["suddenness"], "C1", None,
         "double n: sudden + -ness", "double-letters"),
        ("The school sports hall is too small and {} for 500 pupils.",
         "ADEQUATE", ["inadequate"], "C1", None, "in- (not *unadequate)",
         "negative-prefix"),
        ("Tom tried {} to open the jar, so in the end he gave it to Dad.",
         "SUCCESS", ["unsuccessfully"], "C1", None,
         "two steps: success -> successful -> un- + -ly", "two-steps"),
        ("The instructions were written in such bad English that they were "
         "hardly {}.", "COMPREHEND", ["comprehensible"], "C1", None,
         "-ible, d to s (not *comprehendable)", "able-ible"),
    ],
}

T20 = {
    "transform": [
        ("My bike and your bike look almost the same.", "SIMILAR",
         "My bike looks {} yours.",
         "very similar to / similar to / quite similar to / really similar to "
         "/ so similar to", "B1", None, "similar to (not *similar like)",
         "comparison"),
        ("It snowed so much that the match was cancelled.", "IF",
         "The match would not have been cancelled {} so much.",
         "if it had not snowed / if it had not been snowing", "B2", None,
         "third conditional (if + had not + past participle)", "conditionals"),
        ("My best friend moved to Spain three years ago, and we don't write or "
         "talk to each other any more.", "TOUCH",
         "Since my best friend moved to Spain three years ago, we {}.",
         "have lost touch / have lost touch with each other / "
         "have not kept in touch / have not been in touch / "
         "have been out of touch / have not stayed in touch", "B2",
         "collocation", "lose touch (with someone)", "collocation"),
        ("I asked my brother to fix my bike, and he did.", "GOT",
         "I {} my bike.",
         "got my brother to fix / got my brother to repair / got him to fix / "
         "got him to repair", "B2", None, "get someone to do something",
         "verb-patterns"),
        ("'Have you ever been to London?' Ola asked me.", "EVER",
         "Ola asked me {} to London.",
         "if I had ever been / whether I had ever been", "B2", None,
         "reported question: if + had ever been", "reported-speech"),
        ("As soon as we got to the beach, it started to rain.", "SCARCELY",
         "{} to the beach when it started to rain.",
         "Scarcely had we got / Scarcely had we come / Scarcely had we gone",
         "C1", None, "scarcely had ... when + inversion", "inversion"),
        ("I have never tasted such delicious soup.", "NEVER",
         "{} such delicious soup.",
         "Never have I tasted / Never before have I tasted", "C1", None,
         "never + inversion (have I tasted)", "inversion"),
        ("If you want to catch the early train, you have to get up at five.",
         "MEANS", "Catching the early train {} at five.",
         "means getting up / means having to get up / "
         "means you have to get up / means waking up", "C1", None,
         "mean + -ing (involve)", "verb-patterns"),
        ("Is it possible that they have already left?", "COULD",
         "{} already left?", "Could they have / Could they possibly have",
         "C1", None, "could have (possibility in the past), as a question",
         "modals"),
        ("Although I really like pizza, I can't eat it every day.", "MUCH",
         "{} pizza, I cannot eat it every day.",
         "Much as I like / Much as I love / Much as I really like / "
         "Much as I enjoy / As much as I like / As much as I love / "
         "As much as I really like / As much as I enjoy", "C2", None,
         "much as (although); as much as accepted 2026-11-15", "linking-words"),
    ],
}

T21 = {
    "transform": [
        ("If you hadn't helped me, I would never have finished my project.",
         "WITHOUT", "I would never have finished my project {}.",
         "without your help / without you / without you helping me / "
         "without you helping", "B2", None, "without (if ... had not)",
         "conditionals"),
        ("I really hate waiting for the bus in the rain.", "STAND",
         "I {} for the bus in the rain.",
         "cannot stand waiting / really cannot stand waiting / "
         "just cannot stand waiting", "B2", None, "cannot stand + -ing",
         "verb-patterns"),
        ("We finally decided where to go on holiday.", "DECISION",
         "We finally {} where to go on holiday.",
         "made a decision about / came to a decision about / "
         "reached a decision about / took a decision about / "
         "made a decision on / came to a decision on / "
         "reached a decision on / made our decision about", "B2",
         "collocation", "make / come to / reach a decision", "collocation"),
        ("I was too scared to tell Mum about my bad mark.", "DARE",
         "I {} Mum about my bad mark.",
         "did not dare to tell / did not dare tell", "B2",
         None, "dare (did not dare to)", "modals"),
        ("I can't swim, and my brother can't swim either.", "NOR",
         "I cannot swim, and {} my brother.", "nor can", "B2", None,
         "nor + inversion (nor can my brother)", "inversion"),
        ("Whatever happens, don't tell Ola about the surprise party.",
         "ACCOUNT", "On {} Ola about the surprise party.",
         "no account must you tell / no account should you tell / "
         "no account are you to tell", "C1", None,
         "on no account + inversion", "inversion"),
        ("You can watch the film only if you finish your homework first.",
         "ALLOWED", "Only if you finish your homework first {} the film.",
         "will you be allowed to watch / are you allowed to watch / "
         "will you be allowed to see / are you allowed to see", "C1", None,
         "only if + inversion", "inversion"),
        ("I'm not good at maths, so I didn't win the maths competition.",
         "GOOD", "If I {} maths, I would have won the maths competition.",
         "were good at / was good at / had been good at / were any good at / "
         "was any good at", "C1", None,
         "mixed conditional (if + past, would have)", "conditionals"),
        ("The new tablet costs exactly the same as the old one.", "NO",
         "The new tablet is {} than the old one.",
         "no more expensive / no cheaper / no dearer", "C1", None,
         "no + comparative (no more expensive than)", "comparison"),
        ("Tom passed all his exams. This surprised everybody.", "WHICH",
         "Tom passed all his exams, {} everybody.",
         "which surprised / which was a surprise to / "
         "which came as a surprise to", "C1", None,
         "which for a whole clause", "relative-clauses"),
    ],
}

T22 = {
    "choice": [
        ("Take an umbrella: it's raining cats and {}!",
         ["mice", "dogs", "birds", "horses"], "B", "B2", "idiom",
         "rain cats and dogs (rain very heavily)", "idiom"),
        ("After the long test, we ran around the playground to let off {}.",
         ["smoke", "air", "steam", "gas"], "C", "C1", "idiom",
         "let off steam (get rid of energy or strong feelings)", "idiom"),
        ("The police believe the man {} the crime on Friday night.",
         ["committed", "made", "caused", "took"], "A", "B2", "collocation",
         "commit a crime", "collocation"),
        ("Ola was counting on me, and I {} her down by forgetting her birthday.",
         ["put", "turned", "took", "let"], "D", "B2", "phrasal verb",
         "let someone down (disappoint)", "phrasal-verb"),
        ("All {} I want for my birthday is a new bike.",
         ["what", "that", "which", "who"], "B", "B2", None,
         "all that (not *all what)", "relative-clauses"),
        ("For {} information, please visit the school website.",
         ["farther", "farthest", "further", "furthest"], "C", "B2", None,
         "further (more), not farther (distance)", "comparison"),
        ("If Tomek weren't so slow, he {} picked for the relay team last year.",
         ["would have been", "would be", "will be", "had been"], "A", "C1",
         None, "mixed conditional (if + past, would have been)",
         "conditionals"),
        ("Never again {} so much ice cream before a long bus journey!",
         ["I will eat", "I am eating", "will I eat", "I would eat"], "C", "C1",
         None, "never again + inversion", "inversion"),
        ("'You must be bored at home all day.' '{}, I'm having a great time!'",
         ["On the other hand", "On the contrary", "In contrast", "Otherwise"],
         "B", "C1", None, "on the contrary (no, the opposite is true)",
         "linking-words"),
        ("Dad objects to {} so much for a cinema ticket.",
         ["pay", "be paid", "have paid", "paying"], "D", "C1", None,
         "object to + -ing", "verb-patterns"),
    ],
}

T23 = {
    "choice": [
        ("At the start of the party nobody was talking, so Ola told a joke to "
         "break the {}.", ["glass", "ice", "snow", "wall"], "B", "B2", "idiom",
         "break the ice", "idiom"),
        ("Could you {} a photo of us in front of the castle, please?",
         ["make", "do", "take", "create"], "C", "B1", "collocation",
         "take a photo (not *make a photo)", "collocation"),
        ("My little sister has a very {} imagination: she says a dragon lives "
         "under her bed.", ["vivid", "bright", "loud", "sharp"], "A", "C1",
         "collocation", "a vivid imagination", "collocation"),
        ("If we had left home ten minutes earlier, we {} the start of the "
         "film.", ["might not miss", "would not miss", "had not missed",
                   "might not have missed"],
         "D", "B2", None, "third conditional with might have",
         "conditionals"),
        ("The tickets were really expensive. {}, we had a fantastic time at "
         "the concert.", ["Even though", "Even so", "Although", "Despite"],
         "B", "B2", None, "even so (but still), not even though",
         "linking-words"),
        ("If you {} see a ghost, what would you do?",
         ["were to", "are to", "will", "would"], "A", "C1", None,
         "if + were to (an unlikely future)", "conditionals"),
        ("Only later {} that the 'ghost' was my brother in a sheet.",
         ["I found out", "I did find out", "did I find out", "had I found out"],
         "C", "C1", None, "only later + inversion", "inversion"),
        ("Ola and Kasia are twins, but Ola is the {} of the two.",
         ["tallest", "taller", "highest", "higher"], "B", "C1", None,
         "the + comparative of the two", "comparison"),
        ("{} about the test only the day before, we spent the whole evening "
         "revising.", ["Having told", "To tell", "Having been told", "Telling"],
         "C", "C1", None,
         "perfect passive participle (having been + past participle)",
         "participle-clauses"),
        ("Barely had the film started {} the lights went out.",
         ["than", "when", "then", "that"], "B", "C2", None,
         "barely ... when (not than, which goes with no sooner)", "inversion"),
    ],
}

T24 = {
    "culture": [
        ("What does it mean that the UK is a constitutional monarchy?",
         ["The King makes all the laws himself.",
          "There is no king or queen, only a president.",
          "There is a king, but the country is run by the government and the "
          "MPs that people elect.",
          "The King and the Prime Minister take turns to rule the country."],
         "C", "Political life: the UK Parliament, constitutional monarchy",
         "uk-politics"),
        ("Who runs the debates in the House of Lords?",
         ["the Lord Speaker", "Black Rod", "the Prime Minister",
          "the Serjeant at Arms"], "A",
         "Political life: the House of Lords, the Lord Speaker", "uk-politics"),
        ("How many Royal Parks are there in London?",
         ["two", "five", "twelve", "eight"], "D", "London's Royal Parks",
         "uk-parks"),
        ("Which programming language is named after Ada Lovelace?",
         ["Python", "Ada", "Java", "Byron"], "B",
         "Notable Britons: Ada Lovelace", "uk-people"),
        ("Why did the barons rebel against King John before the Magna Carta?",
         ["He wanted to close all the monasteries.",
          "He had made peace with France without asking them.",
          "He had lost English lands in France, quarrelled with the Pope and "
          "made them pay very high taxes.",
          "He wanted to move the capital from London to Winchester."], "C",
         "Historical events: the Magna Carta (1215), origins", "uk-history"),
    ],
}

T25 = {
    "culture": [
        ("In which decade did the Conservative Party take its name?",
         ["the 1660s", "the 1830s", "the 1900s", "the 1940s"], "B",
         "Political life: two major political parties", "uk-politics"),
        ("Who becomes Prime Minister after a general election?",
         ["the leader of the party with the most MPs",
          "the oldest MP in the House of Commons",
          "the person chosen by the House of Lords",
          "the MP who got the most votes in London"], "A",
         "Political life: the government and the Prime Minister",
         "uk-politics"),
        ("From whom did Henry VIII take the land of Hyde Park in 1536?",
         ["the Lord Mayor of London", "the Duke of Westminster",
          "the monks of Westminster Abbey", "the people of Kensington"], "C",
         "London's Royal Parks: Hyde Park, history", "uk-parks"),
        ("Which organisation did Emmeline Pankhurst found in 1903?",
         ["the Labour Party", "the Women's Social and Political Union",
          "the National Health Service", "the Royal Society"], "B",
         "Notable Britons: Emmeline Pankhurst", "uk-people"),
        ("What did Henry VIII do with the monasteries after the Act of "
         "Supremacy?",
         ["He turned them all into schools.", "He gave them to the Pope.",
          "He made them pay a new tax.",
          "He closed them and took their land and money."], "D",
         "Historical events: the Act of Supremacy (1534), significance",
         "uk-history"),
    ],
}

T26 = {
    "culture": [
        ("Why is the senior official of the House of Lords called Black Rod?",
         ["because the first Black Rod was a blacksmith",
          "because of the black ebony rod the official carries",
          "because the official always wears a black wig",
          "because the official guards a black door"], "B",
         "Political life: parliamentary officials, Black Rod", "uk-politics"),
        ("What is the name of the body in Cardiff that makes some of the laws "
         "for Wales?",
         ["Holyrood", "Stormont", "the Senedd", "the Woolsack"], "C",
         "Political life: devolution", "uk-politics"),
        ("Where in Hyde Park is Speakers' Corner?",
         ["on an island in the Serpentine", "next to the Albert Memorial",
          "at the gate of Kensington Palace",
          "in the north-east corner, near Marble Arch"], "D",
         "London's Royal Parks: Hyde Park, Speakers' Corner", "uk-parks"),
        ("Which book by Arthur Conan Doyle is about dinosaurs surviving in "
         "South America?",
         ["The Lost World", "The Hound of the Baskervilles",
          "A Study in Scarlet", "On the Origin of Species"], "A",
         "Notable Britons: Arthur Conan Doyle", "uk-people"),
        ("About how many houses did the Great Fire of London destroy?",
         ["130", "1,300", "13,000", "130,000"], "C",
         "Historical events: the Great Fire of London (1666)", "uk-history"),
    ],
}

T27 = {
    "culture": [
        ("Which agreement of 1998 helped to create the Northern Ireland "
         "Assembly?",
         ["the Act of Union", "the Magna Carta", "the Good Friday Agreement",
          "the Act of Supremacy"], "C", "Political life: devolution",
         "uk-politics"),
        ("What is the symbol of the Labour Party?",
         ["a red rose", "a blue lion", "a white unicorn", "a green shamrock"],
         "A", "Political life: two major political parties", "uk-politics"),
        ("What were Kensington Gardens before they became the gardens of "
         "Kensington Palace?",
         ["a royal vineyard", "the western part of Hyde Park",
          "a lake for royal boats", "the garden of Westminster Abbey"], "B",
         "London's Royal Parks: Kensington Gardens, history", "uk-parks"),
        ("What is Christopher Nolan's film Oppenheimer about?",
         ["the rescue of British soldiers from France in 1940",
          "a detective who lives at 221B Baker Street",
          "a journey through space to find a new home for people",
          "the scientist who led the building of the atomic bomb"], "D",
         "Notable Britons: Christopher Nolan", "uk-people"),
        ("Where can you see the Royal Coat of Arms?",
         ["only on the King's crown",
          "on British passports, in courts and on government documents",
          "only on the flag of England", "only inside Buckingham Palace"], "B",
         "Symbols of the UK: the Royal Coat of Arms", "uk-symbols"),
    ],
}

T28 = {
    "culture": [
        ("Which Conservative Prime Minister led Britain during World War II?",
         ["Clement Attlee", "Anthony Eden", "Margaret Thatcher",
          "Winston Churchill"], "D",
         "Political life: the Conservative Party", "uk-politics"),
        ("For about a hundred years, which parties has the Prime Minister come "
         "from?",
         ["Labour or the Conservatives", "the Liberal Democrats or Labour",
          "the Scottish National Party or the Conservatives",
          "Reform UK or Labour"], "A",
         "Political life: two major political parties", "uk-politics"),
        ("Which building does the Albert Memorial face?",
         ["Buckingham Palace", "the Royal Albert Hall", "Westminster Abbey",
          "the Tower of London"], "B",
         "London's Royal Parks: Kensington Gardens, the Albert Memorial",
         "uk-parks"),
        ("Why has Christopher Nolan been called 'Sir Christopher' since 2024?",
         ["He became an MP.", "He won an Oscar.", "He was knighted.",
          "He married into the royal family."], "C",
         "Notable Britons: Christopher Nolan", "uk-people"),
        ("Which country planned the attack on Egypt together with Britain and "
         "France in 1956?",
         ["the United States", "the Soviet Union", "Israel", "Argentina"], "C",
         "Historical events: the Suez Crisis (1956)", "uk-history"),
    ],
}

T29 = {
    "culture": [
        ("What happened in Argentina after it lost the Falklands War?",
         ["The army took even more power.",
          "The military government fell and democracy returned.",
          "Argentina joined the Commonwealth.",
          "Argentina gave up its claim to the islands for ever."], "B",
         "Historical events: the Falklands War (1982), significance",
         "uk-history"),
        ("What can you get at the bottom of the Monument after climbing its "
         "311 steps?",
         ["a certificate", "a free ticket to the Tower of London",
          "a piece of the old St Paul's Cathedral", "a golden urn"], "A",
         "Landmarks of London: the Monument", "uk-london"),
        ("How many ravens live at the Tower of London?",
         ["exactly two", "at least six", "exactly twelve",
          "at least a hundred"], "B",
         "Landmarks of London: the Tower of London, the ravens", "uk-london"),
        ("What stands for Scotland on the Royal Standard?",
         ["three gold lions", "a gold harp",
          "a red lion standing on its back legs", "a white unicorn"], "C",
         "Symbols of the UK: the Royal Standard", "uk-symbols"),
        ("According to a legend, what did St Patrick use the shamrock to "
         "explain?",
         ["why Ireland is green", "the Holy Trinity", "the four seasons",
          "how to find water"], "B",
         "The four countries: the saints and their stories", "uk-countries"),
    ],
}

# --------------------------------------------------------------------------
# One-task batches 30-33, written 2026-11-11
# --------------------------------------------------------------------------
# A second round of transformations (30-31) and choice (32-33), 20 of each,
# because the new items of 20-23 run out around 13.11. His record per task
# that day, without the three tests he left early: in transformations
# inversion 5 of 15 wrong, collocation 8/33, modals 3/14, idiom 2/9,
# comparison 7/35, verb patterns 5/25; in choice inversion 3/13,
# conditionals 5/24 (mixed conditionals and "But for"), linking words 2/15,
# collocation 4/34, relative clauses 2/21 ("what" for "that"). Those lead
# each task.

T30 = {
    "transform": [
        ("The puzzle was so difficult that nobody in our class could solve it.",
         "SO", "{} that nobody in our class could solve it.",
         "So difficult was the puzzle / So hard was the puzzle / "
         "So difficult was that puzzle / So hard was that puzzle", "C1", None,
         "so + adjective + inversion (So difficult was the puzzle)",
         "inversion"),
        ("My brother is really interested in the stars and planets.",
         "INTEREST", "My brother {} the stars and planets.",
         "takes a keen interest in / has a keen interest in / "
         "takes a great interest in / has a great interest in / "
         "takes a real interest in / has a real interest in / "
         "has a strong interest in / has a deep interest in / "
         "takes a lot of interest in", "C1",
         "collocation", "take / have a keen interest in (in, not *for)",
         "collocation"),
        ("Last weekend we went to see our grandparents in Kraków.", "PAID",
         "Last weekend we {} in Kraków.",
         "paid our grandparents a visit / paid a visit to our grandparents",
         "B2", "collocation", "pay someone a visit / pay a visit to someone",
         "collocation"),
        ("It was a mistake to eat so many sweets before dinner.", "OUGHT",
         "I {} so many sweets before dinner.",
         "ought not to have eaten / ought not to have had", "C1", None,
         "ought not to have + past participle (not *ought not have)",
         "modals"),
        ("My cousin from Canada phoned me one evening when I was not expecting "
         "it at all.", "BLUE", "My cousin from Canada phoned me {} one evening.",
         "out of the blue / completely out of the blue / "
         "totally out of the blue / right out of the blue / "
         "quite out of the blue", "C1", "idiom",
         "out of the blue (suddenly, without warning)", "idiom"),
        ("No other mountain in Poland is as high as Rysy.", "OTHER",
         "Rysy is higher {} in Poland.",
         "than any other mountain / than all the other mountains / "
         "than any other peak / than all the other peaks / "
         "than every other mountain / than every other peak / "
         "than the other mountains / than the other peaks", "B2", None,
         "than any other + singular noun (not *any other mountains)",
         "comparison"),
        ("Ola won the school talent show, and years later she became a famous "
         "actress.", "WENT",
         "After winning the school talent show, Ola {} a famous actress.",
         "went on to become / later went on to become / went on to be",
         "C1", None, "go on to do (do next), not go on doing",
         "verb-patterns"),
        ("I don't know the answer now because I wasn't listening in class.",
         "LISTENED", "If I {} in class, I would know the answer now.",
         "had listened / had listened carefully / had listened more carefully "
         "/ had listened properly / had listened to the teacher", "B2", None,
         "mixed conditional: if + had + past participle, would + verb now",
         "conditionals"),
        ("My old bike was much slower than my new one.", "LOT",
         "My new bike is {} my old one.",
         "a lot faster than / a lot quicker than", "B1", None,
         "a lot + comparative + than", "comparison"),
        ("All visitors to the museum must leave their bags in the cloakroom.",
         "REQUIRED", "All visitors to the museum {} their bags in the cloakroom.",
         "are required to leave", "B2", None,
         "be required to (a rule: must)", "modals"),
    ],
}

T31 = {
    "transform": [
        ("The last time I laughed so much was on my sixth birthday.", "SINCE",
         "Not {} laughed so much.",
         "since my sixth birthday have I / since I was six have I / "
         "since I turned six have I", "C2",
         None, "not since + inversion (have I + past participle)",
         "inversion"),
        ("This door must not be used except in an emergency.", "EMERGENCY",
         "Only {} this door.",
         "in an emergency may you use / in an emergency can you use / "
         "in an emergency should you use / in an emergency may you open / "
         "in an emergency can you open / in an emergency should you open",
         "C1", None,
         "only + phrase + inversion (may you use)", "inversion"),
        ("I'm not going to apologise to him: he started the argument!",
         "INTENTION", "I have {} to him: he started the argument!",
         "no intention of apologising / no intention of apologizing / "
         "no intention of saying sorry / absolutely no intention of apologising "
         "/ absolutely no intention of apologizing / "
         "absolutely no intention of saying sorry", "C1", "collocation",
         "have no intention of + -ing", "collocation"),
        ("I couldn't understand the instructions for the new board game at all.",
         "SENSE", "I could not {} the instructions for the new board game at all.",
         "make sense of / make any sense of", "B2", "collocation",
         "make sense of (understand)", "collocation"),
        ("Pupils should hand in their homework on Mondays, but Tom always "
         "forgets.", "MEANT",
         "Pupils {} their homework on Mondays, but Tom always forgets.",
         "are meant to hand in / are meant to give in / are meant to bring in "
         "/ are meant to bring / are meant to submit", "B2", None,
         "be meant to (should: what is expected)", "modals"),
        ("I'm slowly learning how to ride my new skateboard.", "HANG",
         "I am slowly {} my new skateboard.",
         "getting the hang of riding / getting the hang of / "
         "getting the hang of using", "B2", "idiom",
         "get the hang of (learn how to do)", "idiom"),
        ("All the other tasks in the test were harder than this one.", "LEAST",
         "This task was {} all the tasks in the test.",
         "the least difficult of / the least hard of / "
         "the least challenging of / the least tricky of", "B2", None,
         "the least + adjective + of", "comparison"),
        ("My dad always reads the newspaper at breakfast.", "HABIT",
         "My dad {} the newspaper at breakfast.",
         "is in the habit of reading / has a habit of reading / "
         "has the habit of reading", "C1", None,
         "be in the habit of + -ing", "verb-patterns"),
        ("It started to rain, but we didn't stop playing football.", "CARRIED",
         "It started to rain, but we {} football.",
         "carried on playing / just carried on playing / "
         "still carried on playing", "B2", None,
         "carry on + -ing (not *carry on to play)", "verb-patterns"),
        ("If we hadn't had the map, we would have got lost in the forest.",
         "BUT", "{}, we would have got lost in the forest.",
         "But for the map / But for our map / But for that map", "C1", None,
         "but for + noun (if it had not been for)", "conditionals"),
    ],
}

T32 = {
    "choice": [
        ("Ever since he was five, Tom has had a {} ambition to become a pilot.",
         ["burning", "boiling", "hot", "flaming"], "A", "C1", "collocation",
         "a burning ambition (a very strong wish)", "collocation"),
        ("As the oldest, you should {} a good example to your little brothers.",
         ["give", "set", "make", "put"], "B", "B2", "collocation",
         "set an example", "collocation"),
        ("When my parents said we could get a puppy, I was on cloud {} for a "
         "week.", ["seven", "nine", "ten", "one"], "B", "B2", "idiom",
         "on cloud nine (extremely happy)", "idiom"),
        ("Only recently {} to enjoy reading.",
         ["I have started", "have I started", "I did start", "I started"], "B",
         "C1", None, "only recently + inversion (have I started)",
         "inversion"),
        ("If I had done my homework yesterday, I {} it now.",
         ["wouldn't have to do", "wouldn't have had to do", "won't have to do",
          "hadn't had to do"], "A", "C1", None,
         "mixed conditional: if + had done (past), would + verb (now)",
         "conditionals"),
        ("If the bus {} on time, we wouldn't have missed the first lesson.",
         ["would have come", "had come", "came", "has come"], "B", "B2", None,
         "third conditional: if + had + past participle (not *if ... would "
         "have)", "conditionals"),
        ("{} playing the piano, Ola plays the guitar in the school band.",
         ["Moreover", "In addition to", "Furthermore", "Also"], "B", "C1", None,
         "in addition to + -ing (moreover and furthermore join sentences)",
         "linking-words"),
        ("I have three cousins, none of {} lives in Poland.",
         ["who", "whom", "which", "whose"], "B", "C1", None,
         "none of whom (not *none of who)", "relative-clauses"),
        ("Great-grandma Zofia is the oldest person {} our family: she is 97.",
         ["of", "in", "at", "on"], "B", "B1", None,
         "superlative + in + a group or place", "comparison"),
        ("{} you've finished your homework, you can go out and play.",
         ["Unless", "Once", "Until", "While"], "B", "B2", None,
         "once (as soon as, after)", "linking-words"),
    ],
}

T33 = {
    "choice": [
        ("The school trip to London is a {} opportunity to practise your "
         "English.", ["golden", "silver", "shiny", "sunny"], "A", "C1",
         "collocation", "a golden opportunity", "collocation"),
        ("Dad has a terrible sense of {}: he gets lost even in our own town.",
         ["way", "direction", "route", "road"], "B", "B2", "collocation",
         "a sense of direction", "collocation"),
        ("Tom has been grumpy all morning: he must have got out of bed on the "
         "wrong {}.", ["side", "foot", "leg", "way"], "A", "C1", "idiom",
         "get out of bed on the wrong side (be in a bad mood all day)",
         "idiom"),
        ("'I've never tried sushi.' '{}. Shall we try it together?'",
         ["So have I", "Neither have I", "Neither I have", "I have neither"],
         "B", "B2", None, "neither + inversion after a negative (not *so have "
         "I)", "inversion"),
        ("No longer {} to share a room with my brother: we've moved to a bigger "
         "flat.", ["I have", "do I have", "I do have", "am I having"], "B",
         "C1", None, "no longer + inversion (do I have)", "inversion"),
        ("If I {} my glasses at school, I could read this letter now.",
         ["didn't leave", "hadn't left", "wouldn't have left", "haven't left"],
         "B", "C1", None,
         "mixed conditional: if + had not + past participle, could + verb now",
         "conditionals"),
        ("{} fire, do not use the lift.", ["In case of", "In case", "If",
                                           "Unless"], "A", "B2", None,
         "in case of + noun (if there is), as on a sign", "conditionals"),
        ("Grandma always buys the best butter for her cakes, {} the price.",
         ["regardless of", "even though", "although", "unless"], "A", "C1",
         None, "regardless of + noun (not caring about)", "linking-words"),
        ("The only thing {} matters is that everyone got home safely.",
         ["what", "that", "whose", "whom"], "B", "B2", None,
         "the only thing that (not *what)", "relative-clauses"),
        ("Tom isn't so much lazy {} tired: he goes to bed far too late.",
         ["than", "as", "but", "that"], "B", "C2", None,
         "not so much ... as (rather than)", "comparison"),
    ],
}

# --------------------------------------------------------------------------
# One-task batches 34-47, written 2026-11-15
# --------------------------------------------------------------------------
# 120 items, the day before the real test, when he had seen all 685: word
# formation 34-35, wisielec 36-38, transformations 39-41, choice 42-43, UK
# culture 44-47. The split follows his last eight tests (12-15.11): wisielec
# 26% of his answers wrong and transformations 24% got 30 items each, word
# formation 11% and choice 5% got 20 each, culture 13% got 20. Within each
# task the batches lean on his weak types that day: UK politics 43%, UK parks
# 38%, vowels 34%, inversion 30%, base change 29%, UK people 29%. In
# transformations he misses inversion most, by not inverting ("hardly sat",
# "Never had I tasted"), so every inversion stem here fixes the opening word
# and the answer has to invert; and dependent prepositions in collocations
# ("no intention in", "had an interest in").

T34 = {
    "formation": [
        ("My little sister is very {}: she screams and cries whenever she "
         "doesn't get her way.", "THEATRE", ["theatrical"], "C1", None,
         "stem change (theatre -> theatr-) + -ical (not *theatreical)",
         "base-change"),
        ("Eating too much sugar is bad for you, so our family has cut down its "
         "{} of sweets.", "CONSUME", ["consumption"], "C1", None,
         "stem change (consume -> consump-) + -tion (not *consumation)",
         "base-change"),
        ("My brother is celebrating his {} birthday next week.", "TWELVE",
         ["twelfth"], "B2", None, "v to f + -th (not *twelveth)",
         "base-change"),
        ("On Sunday we went {} in the park with our cousins.", "PICNIC",
         ["picnicking"], "C1", None, "k added before -ing (not *picnicing)",
         "suffix-spelling"),
        ("His excuse was hardly {}: who would believe that the dog ate his "
         "phone?", "BELIEVE", ["believable"], "B2", None,
         "e dropped before -able (not *believeable)", "suffix-spelling"),
        ("I couldn't believe his {}: he didn't even buy his own mother a "
         "birthday present.", "MEAN", ["meanness"], "C1", None,
         "double n: mean + -ness", "double-letters"),
        ("Is it {} to wear trainers to a wedding?", "ACCEPT", ["acceptable"],
         "B2", None, "-able (not *acceptible)", "able-ible"),
        ("Our PE teacher says that {} matters more than winning.", "FIT",
         ["fitness"], "B2", None, "double t before -ness (not *fitnes)",
         "double-letters"),
        ("Tom is the best {} in our school: he wins every race.", "RUN",
         ["runner"], "B1", None, "double n before -er (not *runer)",
         "double-letters"),
        ("Tom was very {} about breaking our window and offered to pay for it.",
         "APOLOGY", ["apologetic"], "C1", None,
         "stem change (apology -> apologet-) + -ic (not *apologic)",
         "base-change"),
    ],
}

T35 = {
    "formation": [
        ("His recovery after the accident was {}: the doctors couldn't explain "
         "it.", "MIRACLE", ["miraculous"], "C1", None,
         "stem change (miracle -> miracul-) + -ous (not *miracleous)",
         "base-change"),
        ("Our new library is a {} building with no corners at all.", "CIRCLE",
         ["circular"], "B2", None,
         "stem change (circle -> circul-) + -ar (not *circlar)", "base-change"),
        ("Last summer we went {} on the river and saw a family of beavers.",
         "CANOE", ["canoeing"], "C1", None, "e kept before -ing (not *canoing)",
         "suffix-spelling"),
        ("The children played {} in the garden all afternoon.", "HAPPY",
         ["happily"], "B1", None, "y to i before -ly (not *happyly)",
         "suffix-spelling"),
        ("The {} team was cheered by thousands of fans in the town square.",
         "VICTORY", ["victorious"], "B2", None,
         "y to i before -ous (not *victoryous)", "suffix-spelling"),
        ("It would be {} to leave early and avoid the traffic.", "PREFER",
         ["preferable"], "C1", None,
         "one r before -able (not *preferrable; compare preferred)",
         "double-letters"),
        ("My little brother has thrown these toy cars everywhere, but they "
         "still work: they're almost {}.", "DESTROY", ["indestructible"], "C1",
         None, "destroy -> destruct- + -ible, with in- (not *indestroyable)",
         "able-ible"),
        ("Fifteen is {} by three and by five.", "DIVIDE", ["divisible"], "C1",
         None, "stem change (divide -> divis-) + -ible (not *dividable)",
         "able-ible"),
        ("A referee has to be {}: he can't support either team.", "PARTIAL",
         ["impartial"], "C2", None, "im- (not *unpartial)", "negative-prefix"),
        ("My aunt always wears {} clothes: she looks like a model.", "STYLE",
         ["stylish"], "B2", None, "e dropped before -ish (not *styleish)",
         "word-ending"),
    ],
}

T36 = {
    "hangman": [
        ("What do you like doing in your {} time?", "l__s___", "leisure",
         "B2", None, "spelling (-ei-, -sure)", "vowels"),
        ("The {} who operated on my knee said I could play football again in a "
         "month.", "s_r____", "surgeon", "C1", None,
         "spelling (-eon, not *surgen)", "vowels"),
        ("The dog looked {}, but it was actually very friendly.", "f_r_____s",
         "ferocious", "C1", None, "spelling (-ocious, not *ferotious)",
         "vowels"),
        ("The documentary about sharks was absolutely {}.", "f____n____g",
         "fascinating", "B2", None, "spelling (sc, not *facinating)",
         "silent-letters"),
        ("Would you like ketchup or {} on your chips?", "m_y_____s_",
         "mayonnaise", "C1", None, "spelling (double n, -aise)",
         "double-letters"),
        ("Baby birds are very {}: they can't fly away from cats.", "v_l__r____",
         "vulnerable", "C1", None, "-able (not *vulnerible)", "able-ible"),
        ("I have a bowl of {} with milk every morning.", "c_r___", "cereal",
         "B1", None, "spelling (-ea-, not *serial)", "vowels"),
        ("Finding my earring in the sand was like looking for a {} in a "
         "haystack.", "n___l_", "needle", "C1", "idiom",
         "a needle in a haystack (almost impossible to find); -ee-, -dle",
         "idiom"),
        ("Add a {} of salt to the soup.", "_i___", "pinch", "B2", "collocation",
         "a pinch of salt", "collocation"),
        ("Ola has {} up for the school drama club.", "s____d", "signed", "B2",
         "phrasal verb", "sign up (join); silent g", "phrasal-verb"),
    ],
}

T37 = {
    "hangman": [
        ("A {} has yellow fur with black spots and can climb trees.",
         "l__p___", "leopard", "B2", None, "spelling (-eo-, not *lepard)",
         "vowels"),
        ("What an {} idea! Nobody else would have thought of it.", "i_g_____s",
         "ingenious", "C1", None, "spelling (-enious, not *ingenuous)",
         "vowels"),
        ("Eggs, fish and beans contain a lot of {}.", "p__t___", "protein",
         "C1", None, "spelling (-ei-, not *protien)", "vowels"),
        ("My cousin is studying {} because she wants to understand how people "
         "think.", "_s_c__l___", "psychology", "C1", None,
         "spelling (silent p, y)", "silent-letters"),
        ("My uncle has a {} of a dragon on his arm.", "ta____", "tattoo", "B2",
         None, "spelling (double t, double o)", "double-letters"),
        ("I can't eat peanuts: I'm {} to them.", "a____g__", "allergic", "B2",
         None, "spelling (double l)", "double-letters"),
        ("The police stopped every {} on the road to check the drivers.",
         "v___c__", "vehicle", "B2", None, "spelling (silent h)",
         "silent-letters"),
        ("After our argument, Ola gave me the cold {} for a week: she didn't "
         "speak to me at all.", "s___l___", "shoulder", "C1", "idiom",
         "give someone the cold shoulder (ignore them); -ou-", "idiom"),
        ("After Tom's joke nobody laughed, and there was an {} silence.",
         "a_____d", "awkward", "C1", "collocation",
         "an awkward silence; aw-kw-", "collocation"),
        ("Ola {} up her room before her friends came.", "t_d___", "tidied",
         "B2", "phrasal verb", "tidy up; y to i before -ed", "phrasal-verb"),
    ],
}

T38 = {
    "hangman": [
        ("A {} can change the colour of its skin to hide from its enemies.",
         "c__m_l___", "chameleon", "B2", None,
         "spelling (ch- said k, -eon)", "vowels"),
        ("When the goalkeeper slipped, Tom {} his chance and scored.",
         "s__z__", "seized", "C1", None, "spelling (-ei-, not *siezed)",
         "vowels"),
        ("Our trip to the seaside was completely {}: we decided to go at "
         "breakfast.", "sp__t______", "spontaneous", "C1", None,
         "spelling (-eous, not *spontanious)", "vowels"),
        ("Grandma is {} me a warm scarf for the winter.", "_n_____g",
         "knitting", "B2", None, "spelling (silent k, double t)",
         "silent-letters"),
        ("If you lose your passport abroad, go to the Polish {}.", "e_b____",
         "embassy", "C1", None, "spelling (double s)", "double-letters"),
        ("This charger isn't {} with my phone: it doesn't fit.", "c_m__t____",
         "compatible", "C1", None, "-ible (not *compatable)", "able-ible"),
        ("The farmer has a big herd of {}.", "c____e", "cattle", "B2",
         "collocation", "a herd of cattle; double t", "collocation"),
        ("In a {}, the film is about a boy who saves his village from a "
         "dragon.", "n__s____", "nutshell", "C1", "idiom",
         "in a nutshell (in a few words); double l", "idiom"),
        ("Our teacher {} out the test papers and told us to start.", "h_n___",
         "handed", "B2", "phrasal verb", "hand out (give to everyone)",
         "phrasal-verb"),
        ("The children ran {} out of the classroom when the bell rang.",
         "n__s___", "noisily", "B2", None, "y to i before -ly (not *noisyly)",
         "suffix-spelling"),
    ],
}

T39 = {
    "transform": [
        ("Ola sang so beautifully that everyone in the hall cried.",
         "BEAUTIFULLY", "So {} that everyone in the hall cried.",
         "beautifully did Ola sing / beautifully did she sing", "C2", None,
         "so + adverb + inversion (So beautifully did Ola sing)", "inversion"),
        ("I have been to London only once.", "ONCE", "Only {} to London.",
         "once have I been / once have I ever been / once have I travelled / "
         "once have I traveled / once have I gone", "C1", None,
         "only once + inversion (have I been)", "inversion"),
        ("Tom has finished the test, and I have finished it too.", "SO",
         "Tom has finished the test, and {}.", "so have I", "B1", None,
         "so + auxiliary + subject (so have I)", "inversion"),
        ("Most pupils in our class support the idea of a longer lunch break.",
         "FAVOUR", "Most pupils in our class are {} a longer lunch break.",
         "in favour of / all in favour of / strongly in favour of / "
         "very much in favour of", "B2", "collocation",
         "be in favour of (in, not *for)", "collocation"),
        ("We had to walk home because the last bus had already gone.",
         "CHOICE", "We had {} walk home because the last bus had already gone.",
         "no choice but to / no other choice but to", "C1", "collocation",
         "have no choice but to", "collocation"),
        ("Grandma is still as full of energy as she always was.", "EVER",
         "Grandma is as full of energy {}.",
         "as ever / as she ever was / as she has ever been", "C1", None,
         "as ... as ever", "comparison"),
        ("Instead of taking the bus, let's walk to school.", "RATHER",
         "Let's walk to school {} the bus.",
         "rather than take / rather than taking / rather than catch / "
         "rather than catching / rather than go by / rather than going by / "
         "rather than get / rather than getting", "B2", None,
         "rather than (instead of)", "linking-words"),
        ("When I was little, Grandpa often told me stories before bed.", "WOULD",
         "When I was little, Grandpa {} me stories before bed.",
         "would often tell / would tell / would always tell / "
         "would usually tell", "B2", None, "would for a past habit",
         "modals"),
        ("'OK, I'll help you with your maths homework,' my sister said to me.",
         "AGREED", "My sister {} with my maths homework.",
         "agreed to help me / agreed that she would help me", "B2", None,
         "agree to + verb", "reported-speech"),
        ("Why don't you put some ice on your knee? It might help.", "TRY",
         "{} some ice on your knee: it might help.",
         "Try putting / Why not try putting / You could try putting / "
         "You should try putting / You might try putting", "C1", None,
         "try + -ing (do it and see if it helps), not try to", "verb-patterns"),
    ],
}

T40 = {
    "transform": [
        ("We had only just sat down at the table when the phone rang.", "DOWN",
         "Barely {} at the table when the phone rang.",
         "had we sat down / had we just sat down", "C1", None,
         "barely had ... when + inversion (had we sat down)", "inversion"),
        ("I only noticed the spelling mistake in my test at the very end.",
         "END", "Only {} the spelling mistake in my test.",
         "at the end did I notice / at the end did I see / "
         "at the end did I spot", "C1", None,
         "only + phrase + inversion (did I notice)", "inversion"),
        ("Tom finally accepted that his team had lost the final.", "TERMS",
         "Tom finally {} his team's defeat in the final.",
         "came to terms with / managed to come to terms with", "C1",
         "collocation", "come to terms with (accept something sad)",
         "collocation"),
        ("Stop laughing at my new glasses!", "FUN", "Stop {} my new glasses!",
         "making fun of / poking fun at", "B2", "collocation",
         "make fun of (of, not *about)", "collocation"),
        ("I have never been as nervous as I am today.", "THAN",
         "Today I am {} been.", "more nervous than I have ever", "C1", None,
         "comparative + than I have ever been", "comparison"),
        ("It was cold yesterday, and it is just as cold today.", "ANY",
         "It is {} today than it was yesterday.",
         "not any warmer / not any less cold", "B2", None,
         "not any + comparative", "comparison"),
        ("Although I was very tired, I finished all my homework.", "AS",
         "{}, I finished all my homework.",
         "Tired as I was / Tired as I felt / Very tired as I was / "
         "Exhausted as I was", "C1", None,
         "adjective + as + clause (although)", "linking-words"),
        ("Because of your help, I passed the test.", "THANKS",
         "{}, I passed the test.", "Thanks to your help / Thanks to you", "B1",
         None, "thanks to (because of)", "linking-words"),
        ("I'm tired of waiting for the bus every morning.", "FED",
         "I am {} for the bus every morning.",
         "fed up with waiting / really fed up with waiting / "
         "so fed up with waiting", "B2", None, "fed up with + -ing",
         "verb-patterns"),
        ("'You should enter the singing competition, Ola,' said our teacher.",
         "ENCOURAGED", "Our teacher {} the singing competition.",
         "encouraged Ola to enter / encouraged her to enter / "
         "encouraged Ola to take part in / encouraged her to take part in",
         "B2", None, "encourage someone to do", "reported-speech"),
    ],
}

T41 = {
    "transform": [
        ("We only managed to finish the project because Dad helped us.", "HELP",
         "Only {} to finish the project.",
         "with Dad's help did we manage / with Dad's help were we able", "C1",
         None, "only with + inversion (did we manage)", "inversion"),
        ("I have never once been late for school.", "OCCASION",
         "On {} late for school.",
         "no occasion have I been / no occasion have I ever been", "C1", None,
         "on no occasion + inversion (have I been)", "inversion"),
        ("I don't mind whether we go by bus or by train.", "DIFFERENCE",
         "It makes {} me whether we go by bus or by train.",
         "no difference to / no difference at all to / "
         "absolutely no difference to", "B2", "collocation",
         "make no difference to (to, not *for)", "collocation"),
        ("After running up the stairs, I could hardly breathe.", "BREATH",
         "After running up the stairs, I {}.",
         "was out of breath / was completely out of breath / "
         "was totally out of breath / was really out of breath / "
         "was short of breath / could not catch my breath / "
         "could hardly catch my breath", "B2", "collocation",
         "be out of breath", "collocation"),
        ("My new school isn't like my old one at all.", "DIFFERENT",
         "My new school is {} my old one.",
         "completely different from / totally different from / "
         "very different from / quite different from / different from / "
         "completely different to / totally different to / "
         "very different to / quite different to / different to", "B1", None,
         "different from / to (not *different of)", "comparison"),
        ("Although the film was very long, I enjoyed it.", "SAME",
         "The film was very long, but I enjoyed it {}.",
         "all the same / just the same", "B2", None,
         "all the same (even so)", "linking-words"),
        ("Do you want me to carry your bag?", "SHALL", "{} your bag?",
         "Shall I carry / Shall I take", "B1", None,
         "shall I for an offer", "modals"),
        ("My sister is afraid of horses because she fell off one when she was "
         "six.", "FALLEN",
         "My sister would not be afraid of horses now {} off one when she was "
         "six.", "if she had not fallen / had she not fallen", "C1", None,
         "mixed conditional: would + verb now, if + had not + past participle",
         "conditionals"),
        ("There's absolutely no way you can stay up until midnight.",
         "QUESTION", "Staying up until midnight is {}.",
         "out of the question / completely out of the question / "
         "absolutely out of the question / totally out of the question / "
         "quite out of the question", "C1", "idiom",
         "out of the question (not possible)", "idiom"),
        ("We got on the train, but only just.", "NICK",
         "We got on the train {}.",
         "in the nick of time / just in the nick of time", "C1", "idiom",
         "in the nick of time (only just)", "idiom"),
    ],
}

T42 = {
    "choice": [
        ("Grandpa usually {} a nap after lunch.",
         ["makes", "takes", "does", "sleeps"], "B", "B2", "collocation",
         "take a nap (not *make a nap)", "collocation"),
        ("My little brother always has his head in the {}: he never listens "
         "to what people say.", ["sky", "stars", "clouds", "trees"], "C", "B2",
         "idiom", "have your head in the clouds (be dreaming)", "idiom"),
        ("Our plans for a picnic fell {} because of the rain.",
         ["behind", "over", "in", "through"], "D", "C1", "phrasal verb",
         "fall through (not happen)", "phrasal-verb"),
        ("{} to popular belief, bats are not blind.",
         ["Contrary", "Unlike", "Against", "Different"], "A", "C1", None,
         "contrary to (the opposite of what)", "linking-words"),
        ("The test looked easy, {} nobody in the class got full marks.",
         ["so", "yet", "because", "unless"], "B", "B2", None,
         "yet (but even so)", "linking-words"),
        ("If I weren't afraid of heights, I {} to the top of the tower with you "
         "yesterday.",
         ["would climb", "will climb", "would have climbed", "had climbed"],
         "C", "C1", None,
         "mixed conditional: if + past (true now), would have (yesterday)",
         "conditionals"),
        ("If you {} to see Ola, tell her I said hello.",
         ["will happen", "would happen", "are happening", "happen"], "D", "B2",
         None, "if you happen to (by chance)", "conditionals"),
        ("Here {} the bus! Quick, get your bag.",
         ["comes", "is coming", "come", "does come"], "A", "B1", None,
         "here + verb + subject (Here comes the bus)", "inversion"),
        ("We regret {} you that the school trip has been cancelled.",
         ["informing", "to inform", "inform", "having informed"], "B", "C1",
         None, "regret to (be sorry to say), not regret + -ing",
         "verb-patterns"),
        ("{} in the 13th century, the castle is now a museum.",
         ["Building", "Having built", "Built", "To build"], "C", "B2", None,
         "past participle for a passive (Built = which was built)",
         "participle-clauses"),
    ],
}

T43 = {
    "choice": [
        ("I can't decide whether to go to the party: I'm in two {} about it.",
         ["heads", "minds", "thoughts", "ideas"], "B", "B2", "idiom",
         "be in two minds (not sure)", "idiom"),
        ("I think I'm coming {} with a cold: I've been sneezing all morning.",
         ["up", "over", "out", "down"], "D", "C1", "phrasal verb",
         "come down with (start to have an illness)", "phrasal-verb"),
        ("When our team came home with the cup, the fans gave them a {} "
         "welcome.", ["warm", "hot", "heated", "burning"], "A", "B2",
         "collocation", "a warm welcome", "collocation"),
        ("{} you look in the old town, there are beautiful churches.",
         ["Whatever", "Whoever", "Wherever", "Whichever"], "C", "B2", None,
         "wherever (in any place)", "linking-words"),
        ("The museum was closed, so we went to the zoo {}.",
         ["rather", "instead", "otherwise", "besides"], "B", "B2", None,
         "instead at the end of a sentence (in its place)", "linking-words"),
        ("{} wins the race will get a gold medal.",
         ["Who", "Whom", "Whose", "Whoever"], "D", "C1", None,
         "whoever (the person who)", "relative-clauses"),
        ("We're thinking of {} a dog.", ["getting", "to get", "get", "got"],
         "A", "B1", None, "think of + -ing", "verb-patterns"),
        ("{} we set off half an hour earlier, we would not have missed the "
         "train.",
         ["If", "Had", "Should", "Were"], "B", "C1", None,
         "inverted third conditional (Had we left = If we had left)",
         "conditionals"),
        ("Not until the lights came on {} that the cake had disappeared.",
         ["we saw", "we did see", "did we see", "had we seen"], "C", "C1", None,
         "not until + inversion (did we see)", "inversion"),
        ("Imagine {} in a castle with a hundred rooms!",
         ["to live", "living", "live", "lived"], "B", "B2", None,
         "imagine + -ing", "verb-patterns"),
    ],
}

T44 = {
    "culture": [
        ("Which part of the UK Parliament is the most powerful?",
         ["the House of Lords", "the House of Commons", "the monarch",
          "the Lord Speaker"], "B",
         "Political life: the three components", "uk-politics"),
        ("What has happened to MPs who grabbed the Mace in protest?",
         ["They have been made Speaker.",
          "They have been sent to the House of Lords.",
          "They have been suspended.", "They have been given a new seat."],
         "C", "Political life: the Mace", "uk-politics"),
        ("On the Animals in War memorial, which animals stand on the other "
         "side of the wall?",
         ["two elephants", "a lion and a unicorn", "a cat and a goat",
          "a horse and a dog"], "D",
         "London's Royal Parks: Hyde Park, the Animals in War memorial",
         "uk-parks"),
        ("What was Arthur Conan Doyle's job, apart from writing?",
         ["a police detective", "a doctor", "a teacher", "a ship's captain"],
         "B", "Notable Britons: Arthur Conan Doyle", "uk-people"),
        ("How many original copies of the Magna Carta survive?",
         ["one", "four", "twelve", "none"], "B",
         "Historical events: the Magna Carta (1215), significance",
         "uk-history"),
    ],
}

T45 = {
    "culture": [
        ("Why is the Lord Speaker's seat, the Woolsack, stuffed with wool?",
         ["Wool keeps the Lord Speaker warm in winter.",
          "The first Lord Speaker was a sheep farmer.",
          "Wool was the only material that would not burn.",
          "Wool was England's most important trade in the 14th century."], "D",
         "Political life: the Woolsack", "uk-politics"),
        ("Which queen redesigned Kensington Gardens in the 1720s?",
         ["Queen Victoria", "Queen Mary II", "Queen Caroline", "Queen Anne"],
         "C", "London's Royal Parks: Kensington Gardens, history", "uk-parks"),
        ("Which famous people went to Speakers' Corner in Hyde Park?",
         ["William Shakespeare and Christopher Wren",
          "Karl Marx and George Orwell", "Henry VIII and Anne Boleyn",
          "Isaac Newton and Samuel Pepys"], "B",
         "London's Royal Parks: Hyde Park, Speakers' Corner", "uk-parks"),
        ("Which women in the UK got the vote in 1918?",
         ["all women over 18", "some women over 30",
          "only women who were MPs", "only women in Scotland"], "B",
         "Notable Britons: Emmeline Pankhurst", "uk-people"),
        ("Which new kind of company appeared in London because of the Great "
         "Fire?",
         ["railway companies", "telephone companies",
          "fire insurance companies", "bus companies"], "C",
         "Historical events: the Great Fire of London (1666), significance",
         "uk-history"),
    ],
}

T46 = {
    "culture": [
        ("Which Labour Prime Minister led the country from 1997 to 2007?",
         ["Tony Blair", "Clement Attlee", "Keir Starmer", "Winston Churchill"],
         "A", "Political life: two major political parties", "uk-politics"),
        ("Which crown does the King wear at the State Opening of Parliament?",
         ["St Edward's Crown", "the Imperial State Crown",
          "the Crown of Scotland", "a crown of flowers"], "B",
         "Political life: the State Opening of Parliament", "uk-politics"),
        ("What do the sculptures around the Albert Memorial represent?",
         ["the four countries of the UK", "the four seasons", "four continents",
          "Prince Albert's four children"], "C",
         "London's Royal Parks: Kensington Gardens, the Albert Memorial",
         "uk-parks"),
        ("What are Christopher Nolan's films known for?",
         ["songs and dancing", "cartoons made by hand",
          "being very short, never more than an hour",
          "complicated stories told out of time order, and real effects "
          "instead of computer graphics"], "D",
         "Notable Britons: Christopher Nolan", "uk-people"),
        ("Which motto is on the Garter, the belt around the shield on the "
         "Royal Coat of Arms?",
         ["Dieu et mon droit", "Deeds, not words", "Honi soit qui mal y pense",
          "Do the little things"], "C",
         "Symbols of the UK: the Royal Coat of Arms", "uk-symbols"),
    ],
}

T47 = {
    "culture": [
        ("When was Margaret Thatcher Prime Minister?",
         ["1945-1951", "1959-1964", "1979-1990", "2010-2016"], "C",
         "Political life: two major political parties", "uk-politics"),
        ("Why does the Peter Pan statue stand where it does in Kensington "
         "Gardens?",
         ["It is the spot where Peter lands in the story.",
          "J. M. Barrie was born there.", "Queen Victoria chose the place.",
          "It is where Peter Pan was first performed."], "A",
         "London's Royal Parks: Kensington Gardens, the Peter Pan statue",
         "uk-parks"),
        ("What happened to Charles Babbage's Analytical Engine?",
         ["It won a prize at the Great Exhibition.", "It was never finished.",
          "It was destroyed in the Great Fire of London.",
          "It is still used by scientists today."], "B",
         "Notable Britons: Ada Lovelace", "uk-people"),
        ("In 2013 the people of the Falkland Islands voted on their future. "
         "What did almost all of them choose?",
         ["to become part of Argentina", "to become an independent country",
          "to stay British", "to join Scotland"], "C",
         "Historical events: the Falklands War (1982), significance",
         "uk-history"),
        ("Which of these has the Tower of London also been, over the "
         "centuries?",
         ["a football stadium", "a railway station", "a theatre", "a zoo"],
         "D", "Landmarks of London: the Tower of London", "uk-london"),
    ],
}

# --------------------------------------------------------------------------
# One-task batches 48-61, written 2026-11-15, evening
# --------------------------------------------------------------------------
# 120 more items the same evening, before he had seen any of 34-47 (the
# deploy came six minutes after his last test): word formation 48-49,
# wisielec 50-52, transformations 53-55, choice 56-57, UK culture 58-61, the
# split of 34-47. His share wrong since 12.11 by then: wisielec 19%,
# transformations 18%, word formation 11%, culture 9%, choice 4%; his weak
# types UK politics 39%, UK parks 36%, vowels 33%, base change 27%, UK people
# 27%, inversion 26%. His last misses were dependent prepositions in
# collocations ("no intention in", "had an interest in"), so eight
# transformations test one (an influence on, crazy about, jealous of, take no
# notice of, ashamed of, a reputation for, addicted to, pressure on). Every
# inversion stem again fixes the opening words. By then the common points
# were nearly all used: each point here was checked against every item in
# the app and the vault with its gap filled (tools/ojaj/tr_points.py).

T48 = {
    "formation": [
        ("Copying out all the poems in the book by hand was a long and {} job.",
         "LABOUR", ["laborious"], "C1", None,
         "stem change (labour -> labor-) + -ious (not *labourious)",
         "base-change"),
        ("Spending an hour in front of the mirror every morning is pure {}.",
         "VAIN", ["vanity"], "C1", None,
         "stem change (vain -> van-) + -ity (not *vainity)", "base-change"),
        ("Don't throw that spray can into the fire: it's {}.", "EXPLODE",
         ["explosive"], "B2", None,
         "stem change (explode -> explos-) + -ive (not *explodive)",
         "base-change"),
        ("Our trip to Rome was the most {} holiday of my life.", "MEMORY",
         ["memorable"], "B2", None,
         "stem change (memory -> memor-) + -able (not *memoriable)",
         "base-change"),
        ("Is it {} to use a calculator in the maths competition?", "PERMIT",
         ["permissible"], "C2", None,
         "t to ss + -ible (not *permitable)", "able-ible"),
        ("When the lift suddenly stopped, Tom {} and started shouting.",
         "PANIC", ["panicked"], "B2", None,
         "k added before -ed (not *paniced)", "suffix-spelling"),
        ("The cat stretched {} in the warm sun.", "LAZY", ["lazily"], "B1",
         None, "y to i before -ly (not *lazyly)", "suffix-spelling"),
        ("In Greek myths, the gods are {}: they never die.", "MORTAL",
         ["immortal"], "B2", None, "im- (not *unmortal)", "negative-prefix"),
        ("Despite his {}, Tom agreed to sing at the school concert.",
         "RELUCTANT", ["reluctance"], "C1", None,
         "-ance (not *reluctence)", "ance-ence"),
        ("Ola is {} the best player in our team: nobody could say otherwise.",
         "DENY", ["undeniably"], "C1", None,
         "un- + y to i + -able + -ly (not *undenyably)", "two-steps"),
    ],
}

T49 = {
    "formation": [
        ("The {} of her name from the list of winners was a mistake.",
         "OMIT", ["omission"], "C1", None,
         "t to ss + -ion (not *omition)", "base-change"),
        ("The plane began its {} towards Warsaw airport.", "DESCEND",
         ["descent"], "C1", None,
         "stem change (descend -> descent), not *descendence",
         "base-change"),
        ("The weightlifter has very {} arms.", "MUSCLE", ["muscular"], "B2",
         None, "stem change (muscle -> muscul-) + -ar (not *musclar)",
         "base-change"),
        ("Good English is a highly {} skill for anyone looking for a job.",
         "DESIRE", ["desirable"], "B2", None,
         "e dropped before -able (not *desireable, *desirible)", "able-ible"),
        ("It is {} to swim straight after a big meal.", "ADVISE",
         ["inadvisable"], "C1", None,
         "in- (not *unadvisable); e dropped before -able", "negative-prefix"),
        ("The pupils' {} with the new canteen food was obvious: nobody ate "
         "it.", "SATISFY", ["dissatisfaction"], "C1", None,
         "dis- (double s) + satisf- + -action", "two-steps"),
        ("His {} of geography surprised everyone: he thought Paris was in "
         "Spain.", "IGNORE", ["ignorance"], "B2", None,
         "-ance (not *ignorence)", "ance-ence"),
        ("My grandparents were {} people who worked from dawn to dusk.",
         "INDUSTRY", ["industrious"], "C1", None,
         "-ious (hard-working), not *industrial", "word-ending"),
        ("The {} of the soil this summer killed most of our tomatoes.", "DRY",
         ["dryness"], "B2", None, "y kept before -ness (not *driness)",
         "suffix-spelling"),
        ("I like Ola's {}: she always says what she thinks.", "OPEN",
         ["openness"], "B2", None, "double n: open + -ness (not *openess)",
         "double-letters"),
    ],
}

T50 = {
    "hangman": [
        ("Ola is my sister's daughter, so she is my {}.", "n____", "niece",
         "B1", None, "spelling (-ie-, not *neice)", "vowels"),
        ("There's a big spider on the {} right above my bed!", "c_____g",
         "ceiling", "B2", None, "spelling (-ei- after c, not *cieling)",
         "vowels"),
        ("Don't let his friendly smile {} you: he can't be trusted.",
         "d____v_", "deceive", "C1", None,
         "spelling (-ei- after c, not *decieve)", "vowels"),
        ("My cousin studies {}: she digs up old pots and coins.",
         "a______l__y", "archaeology", "C1", None, "spelling (-ae-, -eo-)",
         "vowels"),
        ("Is it {} to bring a passport on the school trip?", "n_____a_y",
         "necessary", "B2", None, "spelling (one c, double s)",
         "double-letters"),
        ("There's no {} that Ola is the best singer in our class.", "d____",
         "doubt", "B2", None, "spelling (silent b)", "silent-letters"),
        ("His excuse sounded {}, so the teacher believed him.", "pl__s____",
         "plausible", "C1", None, "-ible (not *plausable)", "able-ible"),
        ("Keep your {} up! You'll do better in the next match.", "c___",
         "chin", "C1", "idiom", "keep your chin up (stay cheerful)", "idiom"),
        ("A {} of bees flew out of the hollow tree.", "s____", "swarm", "B2",
         "collocation", "a swarm of bees", "collocation"),
        ("The baby finally {} down when Dad started singing.", "c____d",
         "calmed", "B2", "phrasal verb", "calm down; silent l",
         "phrasal-verb"),
    ],
}

T51 = {
    "hangman": [
        ("Our football team is top of the {} this season.", "l__g__",
         "league", "B1", None, "spelling (-ea-, -gue)", "vowels"),
        ("After the marathon, many athletes were suffering from {}.",
         "f_t____", "fatigue", "C1", None, "spelling (-gue, not *fatig)",
         "vowels"),
        ("The waiter was very {}: he held the door open and smiled at "
         "everyone.", "c___t___s", "courteous", "C1", None,
         "spelling (-eous, not *courtious)", "vowels"),
        ("Scientists are working on a new {} against the flu.", "v____n_",
         "vaccine", "B2", None, "spelling (double c)", "double-letters"),
        ("I don't want to {} my parents, so I'm studying hard.",
         "d__a____n_", "disappoint", "B2", None,
         "spelling (one s, double p)", "double-letters"),
        ("Grandma can't {} down easily because her legs hurt.", "_n___",
         "kneel", "B2", None, "spelling (silent k, -ee-)", "silent-letters"),
        ("With our new goalkeeper, we felt {}: nobody could beat us.",
         "i_v_n_____", "invincible", "C1", None, "-ible (not *invincable)",
         "able-ible"),
        ("There is so much red {} that getting a new passport takes months.",
         "t___", "tape", "C1", "idiom",
         "red tape (too many official rules)", "idiom"),
        ("There is still a {} of hope that our lost dog will come home.",
         "g_____r", "glimmer", "C1", "collocation",
         "a glimmer of hope; double m", "collocation"),
        ("Ola and her sister had a big argument, but they {} it out in the "
         "end.", "s____d", "sorted", "B2", "phrasal verb",
         "sort out (solve)", "phrasal-verb"),
    ],
}

T52 = {
    "hangman": [
        ("The two concerts were {}, so I couldn't go to both.",
         "s_m__t______", "simultaneous", "C2", None,
         "spelling (-eous, not *simultanious)", "vowels"),
        ("A long {} train full of coal went slowly past our house.",
         "f___g__", "freight", "C1", None, "spelling (-eigh-)", "vowels"),
        ("I fell off my bike and got a big purple {} on my knee.", "b___s_",
         "bruise", "B2", None, "spelling (-ui-, not *broose)", "vowels"),
        ("Her ring has a blue {} in the middle.", "s_____r_", "sapphire",
         "C1", None, "spelling (double p, then h)", "double-letters"),
        ("If you don't clean under your bed, dust soon begins to {} there.",
         "a_____l__e", "accumulate", "C1", None,
         "spelling (double c, one m)", "double-letters"),
        ("I'd like a {} ice cream, please.", "r___b___y", "raspberry", "B2",
         None, "spelling (silent p, double r)", "silent-letters"),
        ("Nobody noticed the teacher's {} for the first ten minutes of the "
         "lesson.", "ab_____", "absence", "B2", None,
         "-ence (not *absense, *absance)", "ance-ence"),
        ("Winning the cup was great, and scoring the winning goal myself was "
         "the {} on the cake.", "i____", "icing", "C1", "idiom",
         "the icing on the cake (makes a good thing even better)", "idiom"),
        ("A sudden {} of wind blew my hat into the river.", "g___", "gust",
         "B2", "collocation", "a gust of wind", "collocation"),
        ("After all the excitement of the trip, the class finally {} down "
         "and started working.", "s_____d", "settled", "B2", "phrasal verb",
         "settle down (become calm); double t", "phrasal-verb"),
    ],
}

T53 = {
    "transform": [
        ("I have never been so frightened in my whole life.", "LIFE",
         "Never in {} so frightened.",
         "my life have I been / my whole life have I been / "
         "my life have I felt / my whole life have I felt / "
         "all my life have I been", "C1", None,
         "never in my life + inversion (have I been)", "inversion"),
        ("Ola didn't enjoy the film, and I didn't enjoy it either.",
         "NEITHER", "Ola did not enjoy the film, and {}.", "neither did I",
         "B1", None, "neither + auxiliary + subject (neither did I)",
         "inversion"),
        ("My grandfather has influenced my choice of career a lot.",
         "INFLUENCE", "My grandfather has had {} my choice of career.",
         "an influence on / a big influence on / a great influence on / "
         "a huge influence on / "
         "a strong influence on / a major influence on / "
         "an enormous influence on / a lot of influence on / "
         "a real influence on", "B2", "collocation",
         "have an influence on (on, not *for or *to)", "collocation"),
        ("My little sister loves horses more than anything.", "CRAZY",
         "My little sister is {} horses.",
         "crazy about / completely crazy about / absolutely crazy about / "
         "totally crazy about / really crazy about / just crazy about",
         "B2", "collocation", "be crazy about (about, not *on or *for)",
         "collocation"),
        ("Ola wishes she had long hair like her sister.", "JEALOUS",
         "Ola is {} long hair.",
         "jealous of her sister's / a bit jealous of her sister's / "
         "really jealous of her sister's / very jealous of her sister's / "
         "so jealous of her sister's", "B2", "collocation",
         "be jealous of (of, not *on or *about)", "collocation"),
        ("Ola kept quiet about the accident because she didn't want to get "
         "into trouble.", "FEAR",
         "Ola kept quiet about the accident {} into trouble.",
         "for fear of getting / for fear that she would get / "
         "for fear that she might get / for fear she would get / "
         "for fear she might get", "C1", None,
         "for fear of + -ing (so as not to)", "linking-words"),
        ("Ola should get the prize: she has worked so hard.", "DESERVES",
         "Ola {} the prize: she has worked so hard.",
         "deserves to get / deserves to win / deserves to be given / "
         "really deserves to get / really deserves to win / "
         "deserves to receive", "B2", None, "deserve to + verb",
         "verb-patterns"),
        ("'Please, please go and see a doctor,' Tom's mum said to him.",
         "URGED", "Tom's mum {} a doctor.",
         "urged him to see / urged Tom to see / urged him to go and see / "
         "urged Tom to go and see / urged him to go to / "
         "urged Tom to go to / urged him to visit / urged Tom to visit",
         "C1", None, "urge someone to do (ask very strongly)",
         "reported-speech"),
        ("This summer is much cooler than last summer.", "NOTHING",
         "This summer is {} as last summer.",
         "nothing like as hot / nothing like as warm / nothing like so hot / "
         "nothing like so warm", "C1", None,
         "nothing like as + adjective (not nearly as)", "comparison"),
        ("I wanted to go to the concert, but I couldn't.", "LIKED",
         "I {} to the concert, but I could not.",
         "would have liked to go / would have liked to have gone / "
         "would really have liked to go / would have really liked to go",
         "C1", None, "would have liked to (a past wish that did not happen)",
         "modals"),
    ],
}

T54 = {
    "transform": [
        ("Tom didn't say a single word all evening.", "WORD",
         "Not {} all evening.",
         "a word did Tom say / a single word did Tom say / "
         "a word did he say / a single word did he say / "
         "one word did Tom say / one word did he say", "C1", None,
         "not a word + inversion (did Tom say)", "inversion"),
        ("The pupils were never in any danger during the storm.", "POINT",
         "At no {} in any danger during the storm.",
         "point were the pupils / point were they", "C1", None,
         "at no point + inversion (were the pupils)", "inversion"),
        ("Don't pay any attention to what he says.", "NOTICE",
         "Take {} what he says.", "no notice of / no notice at all of", "C1",
         "collocation", "take no notice of (of, not *on)", "collocation"),
        ("Tom felt bad because he had lied to his parents.", "ASHAMED",
         "Tom was {} to his parents.",
         "ashamed of lying / ashamed of having lied / "
         "ashamed that he had lied / ashamed because he had lied / "
         "ashamed of himself for lying / really ashamed of lying", "B2",
         "collocation", "be ashamed of + -ing (of, not *for)",
         "collocation"),
        ("Our school is well known for its excellent sports teams.",
         "REPUTATION", "Our school has {} its excellent sports teams.",
         "a reputation for / a good reputation for / "
         "a great reputation for / an excellent reputation for / "
         "a strong reputation for / a fine reputation for / "
         "quite a reputation for", "B2", "collocation",
         "have a reputation for (for, not *of)", "collocation"),
        ("As soon as I saw the puppy, I knew I wanted it.", "MOMENT",
         "{} the puppy, I knew I wanted it.",
         "The moment I saw / The moment that I saw / The very moment I saw / "
         "From the moment I saw / The moment I set eyes on", "B2", None,
         "the moment (as soon as)", "linking-words"),
        ("If I take the job, I will have to move to London.", "MEAN",
         "Taking the job will {} to London.",
         "mean moving / mean having to move / mean that I have to move / "
         "mean I have to move / mean I will have to move / "
         "mean that I must move", "C1", None,
         "mean + -ing (involve)", "verb-patterns"),
        ("What would you buy if you won the lottery?", "WERE",
         "If you {} the lottery, what would you buy?", "were to win", "C1",
         None, "if + were to (an unlikely future)", "conditionals"),
        ("The organisers gave every player a medal.", "GIVEN",
         "Every player {} by the organisers.",
         "was given a medal / was given a medal each", "B2", None,
         "passive of give (was given a medal)", "passive"),
        ("Tom will probably be late again.", "LIKELY", "Tom {} late again.",
         "is likely to be / is very likely to be / is quite likely to be / "
         "is most likely to be", "B2", None, "be likely to (probably)",
         "modals"),
    ],
}

T55 = {
    "transform": [
        ("I didn't realise until now how lucky I am.", "REALISE",
         "Only now {} how lucky I am.",
         "do I realise / do I really realise / do I finally realise / "
         "do I fully realise", "C1", None,
         "only now + inversion (do I realise)", "inversion"),
        ("We only understood the joke after Tom explained it.", "UNDERSTAND",
         "Only after Tom had explained the joke {} it.",
         "did we understand / did we really understand / "
         "did we finally understand / did we fully understand", "C1", None,
         "only after + inversion (did we understand)", "inversion"),
        ("You can only go skiing here in winter.", "SKIING",
         "Only in winter {} here.",
         "can you go skiing / can people go skiing / can one go skiing / "
         "is it possible to go skiing / are you able to go skiing", "C1",
         None, "only in + inversion (can you go)", "inversion"),
        ("My brother can't stop playing computer games.", "ADDICTED",
         "My brother is {} computer games.",
         "addicted to / addicted to playing / completely addicted to / "
         "totally addicted to / really addicted to / "
         "completely addicted to playing / totally addicted to playing / "
         "really addicted to playing", "B2", "collocation",
         "be addicted to (to, not *on or *of)", "collocation"),
        ("My parents keep pushing me to get better marks.", "PRESSURE",
         "My parents keep {} me to get better marks.",
         "putting pressure on / putting a lot of pressure on / "
         "putting more pressure on", "B2", "collocation",
         "put pressure on someone (on, not *to)", "collocation"),
        ("Because of the storm, the match was cancelled.", "VIEW",
         "{} the storm, the match was cancelled.", "In view of", "C1",
         None, "in view of (because of)", "linking-words"),
        ("'Don't forget to bring your swimming things,' the teacher said to "
         "us.", "REMINDED", "The teacher {} our swimming things.",
         "reminded us to bring / reminded us to take", "B2", None,
         "remind someone to do", "reported-speech"),
        ("I wrote down her phone number so that I wouldn't forget it.",
         "LEST", "I wrote down her phone number {} it.",
         "lest I forget / lest I should forget", "C2", None,
         "lest (so that ... not), formal", "linking-words"),
        ("It's a pity you didn't tell me you were coming: I would have met "
         "you at the station.", "COULD",
         "You {} you were coming: I would have met you at the station.",
         "could have told me / could have let me know / "
         "could at least have told me / could have said", "B2", None,
         "could have + past participle (you should have, but did not)",
         "modals"),
        ("I'll finish reading the book before Friday.", "FINISHED",
         "By Friday I {} the book.",
         "will have finished / will have finished reading / "
         "will already have finished / will have already finished / "
         "will already have finished reading / "
         "will have already finished reading", "B2", None,
         "future perfect (will have finished)", "tenses"),
    ],
}

T56 = {
    "choice": [
        ("Nobody believed Tom when he really was ill, because he had cried "
         "{} too many times.", ["fox", "wolf", "bear", "sheep"], "B", "C1",
         "idiom", "cry wolf (call for help when you do not need it)",
         "idiom"),
        ("Sorry, the hotel is {} booked for the whole of August.",
         ["totally", "wholly", "fully", "complete"], "C", "B2",
         "collocation", "fully booked", "collocation"),
        ("When the factory lost its biggest customer, it {} off two hundred "
         "workers.", ["put", "set", "took", "laid"], "D", "C1",
         "phrasal verb", "lay off (stop employing)", "phrasal-verb"),
        ("To {} should I give this letter?",
         ["whom", "who", "which", "whose"], "A", "C1", None,
         "whom after a preposition (To whom)", "relative-clauses"),
        ("If I {} a dog, I would take it for a walk every day.",
         ["have", "would have", "had", "will have"], "C", "B1", None,
         "second conditional: if + past, would + verb", "conditionals"),
        ("{} you do, don't tell Mum what happened to the vase.",
         ["However", "Whatever", "Whoever", "Whenever"], "B", "B2", None,
         "whatever (no matter what)", "linking-words"),
        ("I remember {} this film at the cinema years ago.",
         ["to watch", "watch", "to have watched", "watching"], "D", "B2",
         None, "remember + -ing (a memory), not remember to",
         "verb-patterns"),
        ("My bike needs {}: the brakes don't work.",
         ["repairing", "to repair", "repaired", "repair"], "A", "C1", None,
         "need + -ing with a passive meaning (needs to be repaired)",
         "passive"),
        ("You {} touch that plate: it's very hot!",
         ["don't have to", "needn't", "mustn't", "haven't"], "C", "B1", None,
         "mustn't (it is not allowed), not don't have to", "modals"),
        ("I'm older than you, {} I?",
         ["am not", "aren't", "isn't", "don't"], "B", "C1", None,
         "question tag after I am: aren't I", "tenses"),
    ],
}

T57 = {
    "choice": [
        ("My brother fell head over {} in love with a girl from his class.",
         ["toes", "feet", "heels", "knees"], "C", "C1", "idiom",
         "head over heels (completely)", "idiom"),
        ("It was midnight, but the children were still {} awake.",
         ["wide", "broad", "large", "high"], "A", "B2", "collocation",
         "wide awake (fully awake)", "collocation"),
        ("Grandpa {} away most of his books to the school library.",
         ["let", "put", "threw", "gave"], "D", "B2", "phrasal verb",
         "give away (give to someone for free)", "phrasal-verb"),
        ("He lent me three books, {} I have already read.",
         ["all of them", "all of which", "which all", "all that"], "B", "C1",
         None, "all of which (in a relative clause)", "relative-clauses"),
        ("You {} have warned me about the test! I would have studied.",
         ["must", "can", "will", "might"], "D", "C1", None,
         "might have + past participle (complaining that someone did not)",
         "modals"),
        ("{} you're here, could you help me move this table?",
         ["Unless", "Although", "Since", "Until"], "C", "B2", None,
         "since (because)", "linking-words"),
        ("The test was {} easier than I expected.",
         ["very", "far", "too", "so"], "B", "B2", None,
         "far + comparative (much easier)", "comparison"),
        ("{} the letter, Ola burst into tears.",
         ["Having read", "Read", "To read", "Being read"], "A", "C1", None,
         "having + past participle (after she had read)",
         "participle-clauses"),
        ("Tom asked me what time {}.",
         ["was it", "is it", "it was", "did it be"], "C", "B2", None,
         "reported question: no inversion (what time it was)",
         "reported-speech"),
        ("Next month we {} in this flat for ten years.",
         ["will live", "have lived", "are living", "will have lived"], "D",
         "C1", None, "future perfect with for (will have lived)", "tenses"),
    ],
}

T58 = {
    "culture": [
        ("Before the House of Commons can meet or pass laws, what must be "
         "lying on the table in front of the Speaker?",
         ["the King's Speech", "the Mace", "Black Rod's rod",
          "a copy of the Magna Carta"], "B",
         "Political life: the Mace", "uk-politics"),
        ("In the reign of which king was the Woolsack first placed in the "
         "House of Lords?",
         ["Alfred the Great", "George III", "Richard III", "Edward III"],
         "D", "Political life: the Woolsack", "uk-politics"),
        ("What did Henry VIII hunt in Hyde Park?",
         ["foxes", "wolves", "deer", "rabbits"], "C",
         "London's Royal Parks: Hyde Park, history", "uk-parks"),
        ("What does Darwin's idea of natural selection say?",
         ["Living things that are best suited to their environment survive "
          "and have young.",
          "Farmers choose which of their animals will have young.",
          "Every species was made at the same time and never changes.",
          "The biggest and strongest animal in each group becomes its leader."],
         "A",
         "Notable Britons: Charles Darwin", "uk-people"),
        ("Which two seas does the Suez Canal connect?",
         ["the North Sea and the Baltic Sea", "the Black Sea and the Caspian Sea",
          "the Atlantic and the Pacific", "the Mediterranean and the Red Sea"],
         "D", "Historical events: the Suez Crisis (1956), origins",
         "uk-history"),
    ],
}

T59 = {
    "culture": [
        ("Where does the King sit during the State Opening of Parliament?",
         ["in the Speaker's chair in the House of Commons", "on the Woolsack",
          "on the throne in the House of Lords",
          "in a gallery above the House of Commons"], "C",
         "Political life: the State Opening of Parliament", "uk-politics"),
        ("What do people speaking at Speakers' Corner often stand on?",
         ["a horse", "a box", "the roof of a bus", "a stone column"], "B",
         "London's Royal Parks: Hyde Park, Speakers' Corner", "uk-parks"),
        ("On which London street is the Animals in War memorial?",
         ["Oxford Street", "Abbey Road", "Fleet Street", "Park Lane"], "D",
         "London's Royal Parks: Hyde Park, the Animals in War memorial",
         "uk-parks"),
        ("How did many suffragettes protest when they were sent to prison?",
         ["They went on hunger strike.",
          "They sang the national anthem all night.",
          "They wrote letters to the Pope.", "They refused to wear shoes."],
         "A", "Notable Britons: Emmeline Pankhurst", "uk-people"),
        ("How did the Falklands War change things for Margaret Thatcher?",
         ["She resigned the same year and left politics.",
          "She lost the 1983 election to the Labour Party.",
          "She became much more popular and won the 1983 election.",
          "She moved to the Falkland Islands to govern them."],
         "C", "Historical events: the Falklands War (1982), significance",
         "uk-history"),
    ],
}

T60 = {
    "culture": [
        ("What does the King's Speech at the State Opening of Parliament list?",
         ["the new laws planned for the coming session",
          "the names of all the new MPs",
          "the results of the general election",
          "the King's visits abroad for the year"], "A",
         "Political life: the State Opening of Parliament", "uk-politics"),
        ("Which religious leaders have seats in the House of Lords?",
         ["the Pope's cardinals", "the leaders of every church in London",
          "no religious leaders at all", "bishops of the Church of England"],
         "D", "Political life: the three components", "uk-politics"),
        ("Who designed the Albert Memorial?",
         ["Christopher Wren", "Prince Albert himself", "George Gilbert Scott",
          "Charles Dickens"], "C",
         "London's Royal Parks: Kensington Gardens, the Albert Memorial",
         "uk-parks"),
        ("Which was the first Sherlock Holmes story?",
         ["The Hound of the Baskervilles", "A Study in Scarlet",
          "Treasure Island", "Oliver Twist"], "B",
         "Notable Britons: Arthur Conan Doyle", "uk-people"),
        ("What stands for England on the Royal Standard?",
         ["three gold lions", "one white horse", "two silver swans",
          "a golden crown"], "A", "Symbols of the UK: the Royal Standard",
         "uk-symbols"),
    ],
}

T61 = {
    "culture": [
        ("Which of these was a Conservative Prime Minister?",
         ["Harold Wilson", "Gordon Brown", "Ramsay MacDonald",
          "David Cameron"], "D",
         "Political life: two major political parties", "uk-politics"),
        ("What is the Peter Pan statue in Kensington Gardens standing on?",
         ["a tree stump", "a ship", "a rock in the Serpentine", "a clock"],
         "A", "London's Royal Parks: Kensington Gardens, the Peter Pan statue",
         "uk-parks"),
        ("Which superhero did Christopher Nolan make three films about?",
         ["Superman", "Spider-Man", "Batman", "Iron Man"], "C",
         "Notable Britons: Christopher Nolan", "uk-people"),
        ("What does the most famous rule of the Magna Carta say?",
         ["The king can take any land he wants without asking the barons.",
          "No free man can be put in prison or punished except by the law of "
          "the land.",
          "Every man must fight in the king's army for forty days a year.",
          "Only barons and bishops are allowed to own land in England."], "B",
         "Historical events: the Magna Carta (1215), significance",
         "uk-history"),
        ("What colours are the uniforms of the Yeoman Warders at the Tower of "
         "London?",
         ["green and gold", "black and white", "orange and purple",
          "red and dark blue"], "D",
         "Landmarks of London: the Tower of London", "uk-london"),
    ],
}

# --------------------------------------------------------------------------
# The semi-final pool (etap polfinalowy, czesc I), written from 2026-11-18
# --------------------------------------------------------------------------
# The semi-final's online test (7.12.2026) has etap I's shape: 45 questions in
# 45 minutes, generated for each student from a pool, the same four task
# types, and culture from the USA mind map (programme 2026/27, section 2.1).
# Its batches are full batches of 45, numbered S01 up, to SEMI_LEVEL_RANGE:
# harder than etap I's, with rarer words like the etap II czesc I sample
# (ojaj_e2p1_*: lapels, stye, next of kin) and more of the inversion and
# mixed conditionals the programme names. Task 5 asks about the USA; every
# culture fact was checked against the source named in its row's note.
# Rows as in the etap I batches. S01 leans on his weakest types after the
# real etap I test (16.11): vowels, base-change, inversion, double letters,
# linking words, suffix spelling, collocations, silent letters.

S01 = {
    "formation": [
        ("During his eight-year {}, he visited more than forty countries.",
         "PRESIDENT", ["presidency"], "C1", None,
         "t -> cy (not *presidentship, *presidentcy)", "base-change"),
        ("The fire was caused by the {} of a worker who left a heater on all "
         "night.", "NEGLECT", ["negligence"], "C2", None,
         "neglect -> neglig- + -ence (not *neglectance)", "base-change"),
        ("Some people still believe in the {} theory that the Moon landing was "
         "filmed in a studio.", "CONSPIRE", ["conspiracy"], "C1", None,
         "conspire -> conspir- + -acy (not *conspiration)", "base-change"),
        ("In the USA, the Supreme Court is at the head of the {} branch of "
         "government.", "JUDGE", ["judicial", "judiciary"], "C2", None,
         "judge -> judic- + -ial (not *judgial)", "base-change"),
        ("The best man's {} at the wedding was so funny that everyone was in "
         "tears.", "SPEAK", ["speech"], "B2", None,
         "speak -> speech (not *speaking)", "base-change"),
        ("The {} between the two schools goes back more than a hundred years.",
         "RIVAL", ["rivalry"], "C1", None, "-ry (not *rivalness, *rivality)",
         "word-ending"),
        ("The name of the Welsh village was so long that it was almost {} for "
         "the tourists.", "PRONOUNCE", ["unpronounceable"], "C1", None,
         "e kept after c before -able (not *unpronouncable)",
         "suffix-spelling"),
        ("The film was {} long: it could easily have finished an hour "
         "earlier.", "NECESSARY", ["unnecessarily"], "C1", None,
         "un- and -ly, y to i (not *unnecessaryly)", "two-steps"),
        ("The lawyer found {} evidence that her client had been at home that "
         "night.", "COMPEL", ["compelling"], "C1", None,
         "double l before -ing", "double-letters"),
        ("My surname was {} on the certificate, so I had to send it back.",
         "SPELL", ["misspelt", "misspelled"], "B2", None,
         "mis- + spell: double s", "double-letters"),
    ],
    "hangman": [
        ("The monks have lived in this {} high in the mountains for over six "
         "hundred years.", "m___s___y", "monastery", "C1", None,
         "spelling (-a-, -ery, not *monestary)", "vowels"),
        ("Grandma keeps her best {} cups in a glass cabinet and never uses "
         "them.", "_o___l__n", "porcelain", "C1", None,
         "spelling (-e-, -ain, not *porceline)", "vowels"),
        ("He joined the army at eighteen and was promoted to {} three years "
         "later.", "l____e___t", "lieutenant", "C2", None,
         "spelling (lieu-, -ant, not *leutenant)", "vowels"),
        ("The food in the school canteen was {}: cold, greasy and completely "
         "tasteless.", "a__a____g", "appalling", "B2", None,
         "spelling (double p, double l)", "double-letters"),
        ("In the USA, a lawyer who speaks for people in court is often called "
         "an {}.", "____rn__", "attorney", "C1", None,
         "spelling (double t, -ey)", "double-letters"),
        ("Politicians from all parties were quick to {} the attack on the "
         "journalist, calling it a disgrace.", "c__d___", "condemn", "C1", None,
         "spelling (silent n after m)", "silent-letters"),
        ("Roasted {} are sold on street corners all over London in winter.",
         "_h_s_n___", "chestnuts", "B2", None, "spelling (silent t)",
         "silent-letters"),
        ("Don't take their quarrel too seriously: it's just a storm in a {}.",
         "__a__p", "teacup", "C2", "idiom",
         "a storm in a teacup (a lot of fuss about nothing)", "idiom"),
        ("The election was {} contested: the winner got only a few hundred "
         "votes more than his rival.", "f___c___", "fiercely", "C1",
         "collocation", "fiercely contested; ie", "collocation"),
        ("In the end, the whole argument {} down to one thing: money.",
         "b____", "boils", "C1", "phrasal verb",
         "boil down to (be in the end about)", "phrasal-verb"),
    ],
    "transform": [
        ("The film was so frightening that my little brother hid under the "
         "blanket.", "SO", "{} that my little brother hid under the blanket.",
         "So frightening was the film", "C2", None,
         "so + adjective + was + subject (inversion)", "inversion"),
        ("We didn't learn the truth until many years later.", "LATER",
         "Only {} the truth.",
         "many years later did we learn / years later did we learn / "
         "many years later did we discover / years later did we discover",
         "C1", None, "only + time phrase + did (inversion)", "inversion"),
        ("I didn't take the job in London, so I still live with my parents.",
         "HAD", "{} in London, I would not be living with my parents now.",
         "Had I taken the job / Had I accepted the job", "C1", None,
         "mixed conditional, inverted (Had I taken ..., I would not be ...)",
         "conditionals"),
        ("She is very shy, which is why she didn't ask the teacher for help.",
         "WOULD", "If she were less shy, {} the teacher for help.",
         "she would have asked", "C1", None,
         "mixed conditional (present cause, past result)", "conditionals"),
        ("Although she tried very hard, she couldn't remember the password.",
         "TRY", "{}, she could not remember the password.",
         "Try as she might / Try as she did", "C2", None,
         "try as she might (however hard she tried)", "linking-words"),
        ("I would never expect Tom to lie to me.", "LAST",
         "Tom is the {} to lie to me.",
         "last person I would expect / last person I would ever expect",
         "C1", None, "the last person I would expect to", "comparison"),
        ("It makes me angry when people treat me like a child.", "RESENT",
         "I {} like a child.",
         "resent being treated / resent people treating me / "
         "resent it when people treat me", "C1", None,
         "resent + being + past participle", "verb-patterns"),
        ("Someone had warned us about the roadworks, so we left home early.",
         "HAVING", "{} the roadworks, we left home early.",
         "Having been warned about", "C1", None,
         "perfect passive participle clause", "participle-clauses"),
        ("A professional photographer is going to take our wedding photos.",
         "TAKEN", "We are going to {} by a professional photographer.",
         "have our wedding photos taken / get our wedding photos taken",
         "B2", None, "have something done", "passive"),
        ("I know her name, but I just can't remember it right now.", "TIP",
         "Her name is {} tongue.", "on the tip of my", "B2", "idiom",
         "on the tip of my tongue", "idiom"),
    ],
    "choice": [
        ("Nobody knew it at the time, but the shy boy in the back row {} one "
         "of the most famous writers of his generation.",
         ["was to become", "would have become", "had become", "has become"],
         "A", "C1", None, "was to + infinitive: the future seen from the past",
         "tenses"),
        ("{} the weather forecast, we would never have set off without our "
         "raincoats.",
         ["Had we checked", "If we checked", "Should we check", "Did we check"],
         "A", "C1", None, "inverted third conditional (Had we ...)",
         "conditionals"),
        ("Nowhere {} such kindness as in that small mountain village.",
         ["have I ever experienced", "I have ever experienced",
          "ever I have experienced", "I ever experienced"],
         "A", "C1", None, "inversion after nowhere", "inversion"),
        ("The new stadium is {} the old one: it holds three times as many "
         "fans.",
         ["three times the size of", "three times as big than",
          "three times bigger as", "three times more big than"],
         "A", "B2", None, "three times the size of", "comparison"),
        ("{} his wealth, he never seemed truly happy.",
         ["For all", "In spite", "Although", "However"], "A", "C1", None,
         "for all + noun (despite)", "linking-words"),
        ("The government has {} a ban on plastic bags in all supermarkets.",
         ["imposed", "forced", "laid", "thrown"], "A", "C1", "collocation",
         "impose a ban", "collocation"),
        ("The film received {} reviews: one critic called it 'a complete waste "
         "of time'.", ["scathing", "scolding", "scorching", "scalding"], "A",
         "C2", "collocation", "scathing reviews (very critical)",
         "collocation"),
        ("He has been {} the midnight oil all week to finish his history "
         "project.", ["burning", "lighting", "heating", "boiling"], "A", "C1",
         "idiom", "burn the midnight oil (work late into the night)", "idiom"),
        ("The government plans to {} out coal power stations over the next ten "
         "years.", ["phase", "face", "stage", "pace"], "A", "C2",
         "phrasal verb", "phase out (stop using gradually)", "phrasal-verb"),
        ("The police officer asked us {} outside so late at night.",
         ["what we were doing", "what were we doing", "what we are doing",
          "what did we do"], "A", "B2", None,
         "word order and tense in a reported question", "reported-speech"),
    ],
    "culture": [
        ("Which US Army officer was killed, together with all the soldiers "
         "under his direct command, at the Battle of the Little Bighorn in "
         "1876?",
         ["Ulysses S. Grant", "Robert E. Lee", "George Armstrong Custer",
          "William T. Sherman"], "C",
         "Native American history: the Battle of the Little Bighorn (1876); "
         "source: Britannica, Battle of the Little Bighorn", "usa-native"),
        ("What does 'E pluribus unum', the motto on the Great Seal of the "
         "United States, mean?",
         ["Out of many, one", "In God we trust", "United we stand",
          "Liberty for all"], "A",
         "National emblems: the Great Seal; source: National Archives, "
         "original design of the Great Seal", "usa-symbols"),
        ("Under the system of checks and balances, how can Congress still pass "
         "a law that the President has vetoed?",
         ["with a simple majority vote in the Senate alone",
          "by asking the Supreme Court to sign it into law",
          "by holding a national referendum on the new law",
          "by a two-thirds vote in both the House and the Senate"], "D",
         "Politics: the Constitution, checks and balances; source: US "
         "Constitution, Article I, Section 7; CRS report 98-157",
         "usa-constitution"),
        ("Why did Poland not receive any help from the Marshall Plan after the "
         "Second World War?",
         ["The USA did not invite Poland to take part.",
          "The Soviet Union made Poland refuse it.",
          "Poland had already joined NATO.",
          "Poland had no war damage to repair."], "B",
         "The Cold War: the policy of containment, the Marshall Plan (1948); "
         "source: PAP, 'Under Russian pressure Poland rejects Marshall Plan'",
         "usa-cold-war"),
        ("Which President signed the Civil Rights Act of 1964 into law?",
         ["John F. Kennedy", "Richard Nixon", "Dwight D. Eisenhower",
          "Lyndon B. Johnson"], "D",
         "The Civil Rights Movement: the Civil Rights Act (1964); source: "
         "National Archives, Center for Legislative Archives, 'The Civil "
         "Rights Act of 1964'", "usa-civil-rights"),
    ],
}

# --------------------------------------------------------------------------
# Builders: rows -> the paper shape scoreTest already reads
# --------------------------------------------------------------------------


def pattern_of(compact):
    """'w_a_h_r' -> 'w __ a __ h __ r (7)', the 2024/25 paper's shape."""
    slots = " ".join("__" if c == "_" else c.lower() for c in compact)
    return f"{slots} ({len(compact)})"


def tagged(item, level, focus, mistake_type):
    item["level"] = level
    if focus:
        item["focus"] = focus
    item["mistakeType"] = mistake_type
    return item


ROW_KINDS = ("formation", "hangman", "transform", "choice", "culture")
# Each kind of row: its task's id and type, the number of its first question
# and its count of items, in a full batch. A batch of one task alone keeps
# them, so its items read as they would in a full batch.
TASK_OF = {
    "formation": ("1", "word_formation", 1, 10),
    "hangman": ("2", "word_spelling", 11, 10),
    "transform": ("3", "sentence_transformation", 21, 10),
    "choice": ("4", "multiple_choice", 31, 10),
    "culture": ("5", "knowledge_questions", 41, 5),
}
ONE_TASK_LABEL = {"formation": "Slowotworstwo", "hangman": "Wisielec",
                  "transform": "Transformacje", "choice": "Wybor",
                  "culture": "Kultura"}


def hangman_items(rows):
    """Wisielec rows as items, without ids. A row is (sentence with {} where
    the pattern goes, compact pattern, answer, level, focus, what it tests,
    mistake type)."""
    return [tagged({"sentence": s.format(pattern_of(p)), "hint": pattern_of(p),
                    "answer": [a]}, lvl, foc, mt)
            for s, p, a, lvl, foc, _, mt in rows]


def numbered(items, first):
    """Items with their question numbers as ids, the id first."""
    return [{"id": str(n), **it} for n, it in enumerate(items, start=first)]


def task_items(kind, rows):
    """One kind of row as items, without ids."""
    if kind == "formation":
        return [tagged({"sentence": s.format(BLANK), "wordBase": base,
                        "answer": answers}, lvl, foc, mt)
                for s, base, answers, lvl, foc, _, mt in rows]
    if kind == "hangman":
        return hangman_items(rows)
    if kind == "transform":
        return [tagged({"original": o, "keyword": kw,
                        "transformed": tr.format(GAP), "answer": a}, lvl, foc, mt)
                for o, kw, tr, a, lvl, foc, _, mt in rows]
    if kind == "choice":
        return [tagged({"stem": s.format(BLANK),
                        "options": [f"{l}) {o}" for l, o in zip("ABCD", opts)],
                        "answer": ans}, lvl, foc, mt)
                for s, opts, ans, lvl, foc, _, mt in rows]
    assert kind == "culture", kind
    return [{"question": q,
             "options": [f"{l}. {o}" for l, o in zip("ABCD", opts)],
             "answer": ans, "mistakeType": mt}
            for q, opts, ans, _, mt in rows]


def build_one_task_batch(test_id, kind, rows):
    """A batch of one task alone: that task of a full batch without the other
    four, its questions numbered as there. Added 2026-11-11 for wisielec, when
    he had seen every item in the vault, and later the same day for the other
    tasks, so that his next tests get new items of a task while the rest
    repeat items he has seen."""
    task_id, task_type, first, _ = TASK_OF[kind]
    return {
        "competition": "ojaj",
        "kind": "online",
        "id": test_id,
        "label": f"{ONE_TASK_LABEL[kind]} {test_id}",
        "maxPoints": len(rows),
        "timeMinutes": 45,
        "tasks": [{"id": task_id, "type": task_type, "points": len(rows),
                   "instruction": INSTR[task_type],
                   "items": numbered(task_items(kind, rows), first)}],
    }


def one_task_kind(test):
    """The kind of row a batch of one task alone holds; None for a full batch."""
    if len(test["tasks"]) != 1:
        return None
    task_id = test["tasks"][0]["id"]
    return next(k for k, spec in TASK_OF.items() if spec[0] == task_id)


def is_hangman_batch(test):
    return one_task_kind(test) == "hangman"


def build_test(test_id, rows, label=None):
    """A batch as a test: all five tasks, or one alone. `label` names it in
    the printout (default "Test online NN")."""
    if len(rows) == 1:
        (kind, kind_rows), = rows.items()
        assert kind in TASK_OF, f"batch {test_id}: rows for {kind}"
        return build_one_task_batch(test_id, kind, kind_rows)
    assert set(rows) == set(ROW_KINDS), (
        f"batch {test_id}: rows for {sorted(rows)}; a batch has all five tasks "
        "or one alone")
    # Item ids are the question numbers, 1-45 straight through the test: the
    # renderers print the id beside each item, and the platform numbers its
    # questions the same way.
    out = []
    number = 1
    for kind in ROW_KINDS:
        task_id, task_type, _, _ = TASK_OF[kind]
        items = task_items(kind, rows[kind])
        out.append({"id": task_id, "type": task_type, "points": len(items),
                    "instruction": INSTR[task_type],
                    "items": numbered(items, number)})
        number += len(items)
    return {
        "competition": "ojaj",
        "kind": "online",
        "id": test_id,
        "label": label or f"Test online {test_id}",
        "maxPoints": sum(t["points"] for t in out),
        "timeMinutes": 45,
        "tasks": out,
    }


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

CONTRACTION = re.compile(r"n't\b|'(re|ve|ll|d|m)\b", re.I)


def check_formation(task, where):
    for item in task["items"]:
        assert len(re.findall(r"_{2,}", item["sentence"])) == 1, (
            f"{where} {item['id']}: not exactly one blank")
        assert item["wordBase"].isupper(), f"{where} {item['id']}: base case"
        for a in item["answer"]:
            assert a.lower() != item["wordBase"].lower(), (
                f"{where} {item['id']}: answer is the base word")


def given_letters(n):
    """How many letters the published papers give in a wisielec word of n
    letters: the median at each length over their 70 items (2026-10-31)."""
    return 1 if n <= 5 else 2 if n <= 8 else 3 if n <= 12 else 4


def check_given_letters(task, where):
    for item in task["items"]:
        n = len(item["answer"][0])
        slots = item["hint"][: item["hint"].rindex("(")].split()
        shown = sum(1 for s in slots if s != "__")
        assert shown == given_letters(n), (
            f"{where} {item['id']}: {shown} given letters in a word of {n}, "
            f"the papers give {given_letters(n)}")


def check_transform(task, where):
    for item in task["items"]:
        assert item["transformed"].count(GAP) == 1 and "__________" not in (
            item["transformed"]), f"{where} {item['id']}: gap is not nine"
        assert item["keyword"].isupper(), f"{where} {item['id']}: keyword case"
        for alt in item["answer"].split(" / "):
            words = alt.lower().split()
            assert item["keyword"].lower() in words, (
                f"{where} {item['id']}: {item['keyword']} not in '{alt}'")
            assert len(words) <= 6, f"{where} {item['id']}: '{alt}' over six"
            assert not CONTRACTION.search(alt), (
                f"{where} {item['id']}: contraction in '{alt}'")


def check_profile(task, where, level_range=LEVEL_RANGE):
    """The level target for tasks 1-4 (the pool's: LEVEL_RANGE or
    SEMI_LEVEL_RANGE), and the idiom count for 2 and 4."""
    levels = Counter(it["level"] for it in task["items"])
    assert set(levels) <= set(LEVELS), f"{where}: levels {dict(levels)}"
    assert len(task["items"]) == 10, f"{where}: {len(task['items'])} items"
    for level, (lo, hi) in level_range.items():
        assert lo <= levels[level] <= hi, f"{where}: {levels[level]} {level}"
    foci = [it["focus"] for it in task["items"] if it.get("focus")]
    assert set(foci) <= FOCI, f"{where}: focus {foci}"
    if task["type"] in FOCUS_TASKS:
        lo, hi = FOCUS_RANGE
        assert lo <= len(foci) <= hi, f"{where}: {len(foci)} focus items"


def check_types(test, where, culture=ETAP1_CULTURE):
    """One known mistake type per item, allowed in its task; an item with a
    focus (idiom, collocation, phrasal verb) has that as its type, and only
    such an item has one of those three. A task's id is its number in a full
    batch, also in a wisielec batch. Culture items carry the pool's culture
    (`culture`, the prefix of its types: UK for etap I, USA for the
    semi-final)."""
    for task in test["tasks"]:
        n = int(task["id"])
        for item in task["items"]:
            mt = item.get("mistakeType")
            at = f"{where} {item['id']}"
            assert mt in MISTAKE_TYPES, f"{at}: mistake type {mt!r}"
            assert n in MISTAKE_TYPES[mt]["tasks"], f"{at}: {mt} in task {n}"
            if task["type"] == "knowledge_questions":
                assert mt.startswith(culture), f"{at}: {mt} in a {culture} pool"
            focus = item.get("focus")
            if focus:
                assert mt == FOCUS_TYPE[focus], f"{at}: focus {focus}, type {mt}"
            else:
                assert mt not in FOCUS_TYPE.values(), f"{at}: {mt}, no focus"


def prompt_of(item):
    for field in ("stem", "sentence", "original", "question", "context",
                  "statement", "prompt"):
        if item.get(field):
            return re.sub(r"\s+", " ", item[field]).strip().lower()
    return None


def app_docs():
    """(name, document) for every file of tasks in the app outside the vault."""
    for path in sorted(glob.glob(f"{DATA}/**/*.json", recursive=True)):
        name = os.path.relpath(path, DATA)
        if name.startswith("ojaj/online/"):
            continue
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(doc, dict) and "tasks" in doc:
            yield name, doc


def existing_items():
    """Every item already in the app, outside the vault itself."""
    prompts, words, pairs = {}, {}, {}
    for name, doc in app_docs():
        add_items((prompts, words, pairs), doc, name)
    return prompts, words, pairs


def add_items(existing, doc, name):
    """Record a document's items in `existing`, as existing_items does."""
    prompts, words, pairs = existing
    for task in doc["tasks"]:
        for item in task.get("items") or []:
            where = f"{name} {item.get('id')}"
            p = prompt_of(item)
            if p:
                prompts[p] = where
            ans = item.get("answer")
            if task["type"] in ("word_formation", "word_spelling"):
                for a in ans if isinstance(ans, list) else [ans]:
                    words[str(a).lower()] = where
            if task["type"] == "sentence_transformation":
                for alt in str(ans).lower().split(" / "):
                    pairs[(str(item.get("keyword")).lower(), alt)] = where


def check_unseen_elsewhere(test, existing):
    """No item in this test already exists in the app, as the same prompt, the
    same derived or spelt word, or the same keyword with the same answer."""
    prompts, words, pairs = existing
    found = []
    for task in test["tasks"]:
        for item in task["items"]:
            p = prompt_of(item)
            if p in prompts:
                found.append(f"{item['id']}: prompt also at {prompts[p]}")
            if task["type"] in ("word_formation", "word_spelling"):
                for a in item["answer"]:
                    if a.lower() in words:
                        found.append(f"{item['id']}: '{a}' also at {words[a.lower()]}")
            if task["type"] == "sentence_transformation":
                for alt in item["answer"].lower().split(" / "):
                    key = (item["keyword"].lower(), alt)
                    if key in pairs:
                        found.append(f"{item['id']}: '{alt}' also at {pairs[key]}")
    return found


def check_hangman_task(task, where, level_range=LEVEL_RANGE):
    """A wisielec task: patterns that fit their words, the papers' number of
    given letters, and the level and idiom profile of task 2."""
    check_spelling(task, where)
    check_given_letters(task, where)
    check_profile(task, f"{where} task {task['id']}", level_range)


def check_task(task, where, level_range=LEVEL_RANGE):
    """One task's own checks, the same in a full batch and alone: its items'
    shape, and for tasks 1-4 the level and idiom profile."""
    kind = task["type"]
    if kind == "word_formation":
        check_formation(task, where)
    elif kind == "word_spelling":
        check_hangman_task(task, where, level_range)
        return
    elif kind == "sentence_transformation":
        check_transform(task, where)
    else:
        check_choice(task, where, letters="ABCD")
    if kind == "knowledge_questions":
        assert len(task["items"]) == 5, f"{where}: task 5 has {len(task['items'])}"
    else:
        check_profile(task, f"{where} task {task['id']}", level_range)


def check_test(test, existing, level_range=LEVEL_RANGE, culture=ETAP1_CULTURE):
    """A batch's checks; a semi-final batch passes its pool's level profile
    and culture (SEMI_LEVEL_RANGE, SEMI_CULTURE)."""
    where = f"online {test['id']}"
    kind = one_task_kind(test)
    if kind:
        _, _, first, size = TASK_OF[kind]
        ids = [it["id"] for it in test["tasks"][0]["items"]]
        assert ids == [str(n) for n in range(first, first + size)], (
            f"{where}: ids are not {first}-{first + size - 1} but "
            f"{ids[0]}-{ids[-1]}")
    else:
        assert [t["type"] for t in test["tasks"]] == list(INSTR), "task order"
        assert test["maxPoints"] == 45, f"{where}: {test['maxPoints']} points"
        ids = [it["id"] for t in test["tasks"] for it in t["items"]]
        assert ids == [str(n) for n in range(1, 46)], f"{where}: ids are not 1-45"
    for task in test["tasks"]:
        check_task(task, where, level_range)
    check_types(test, where, culture)
    # One test, no answer twice.
    answers = [a.lower() for t in test["tasks"]
               if t["type"] in ("word_formation", "word_spelling")
               for it in t["items"] for a in it["answer"]]
    assert len(answers) == len(set(answers)), f"{where}: an answer repeats"
    found = check_unseen_elsewhere(test, existing)
    assert not found, f"{where}: already in the app:\n  " + "\n  ".join(found)


def own_hangman_task(rows):
    """An own wisielec exercise's rows as a task 2, numbered from 1."""
    return {"id": "2", "type": "word_spelling",
            "items": numbered(hangman_items(rows), 1)}


def check_own_hangman(ex_id, rows, exercise):
    """One of the app's own wisielec exercises in the online test's shape
    (ojaj_own.HANGMAN_ONLINE): its rows keep the rules of a vault wisielec
    task, and the exercise written from them shows the same patterns."""
    task = own_hangman_task(rows)
    check_hangman_task(task, ex_id)
    check_types({"tasks": [task]}, ex_id)
    written = exercise["tasks"][0]["items"]
    assert ([(it["sentence"], it["hint"], it["answer"]) for it in written] ==
            [(it["sentence"], it["hint"], it["answer"]) for it in task["items"]]), (
        f"{ex_id}: the exercise does not show its rows' patterns")


def check_own_exercises():
    """Every own wisielec exercise in the online test's shape: checked as a
    vault wisielec task, and no answer word used twice among them or anywhere
    else in the app or the vault."""
    exercises = dict(OWN.EXERCISES)
    places = {}
    for name, doc in app_docs():
        for task in doc["tasks"]:
            if task["type"] not in ("word_formation", "word_spelling"):
                continue
            for item in task.get("items") or []:
                ans = item.get("answer")
                for a in ans if isinstance(ans, list) else [ans]:
                    places.setdefault(str(a).lower(), set()).add(name)
    for _, rows in TESTS:
        for r in rows.get("formation", []):
            for a in r[2]:
                places.setdefault(a.lower(), set()).add("the vault")
        for r in rows.get("hangman", []):
            places.setdefault(r[2].lower(), set()).add("the vault")
    own = [r[2].lower() for _, rows in OWN.HANGMAN_ONLINE for r in rows]
    assert len(own) == len(set(own)), (
        f"own wisielec: {sorted(w for w, n in Counter(own).items() if n > 1)} twice")
    for ex_id, rows in OWN.HANGMAN_ONLINE:
        check_own_hangman(ex_id, rows, exercises[ex_id])
        mine = f"ojaj/practice/{ex_id}.json"
        for r in rows:
            elsewhere = places.get(r[2].lower(), set()) - {mine}
            assert not elsewhere, f"{ex_id}: '{r[2]}' also in {sorted(elsewhere)}"


# --------------------------------------------------------------------------
# The printout
# --------------------------------------------------------------------------

TASK_TITLES = [
    "Zadanie 1: słowotwórstwo (word formation)",
    "Zadanie 2: wisielec",
    "Zadanie 3: transformacje ze słowem kluczem (oceniane przez AI)",
    "Zadanie 4: gramatyka i słownictwo, wybór",
    "Zadanie 5: kultura Wielkiej Brytanii, wybór",
]
SEMI_TASK_TITLES = TASK_TITLES[:4] + ["Zadanie 5: kultura USA, wybór"]


def level_line(task):
    levels = Counter(it["level"] for it in task["items"])
    counts = ", ".join(f"{levels[l]} {l}" for l in LEVELS)
    foci = Counter(it["focus"] for it in task["items"] if it.get("focus"))
    focus = (", ".join(f"{n} {f}" for f, n in sorted(foci.items()))
             if foci else "none")
    return f"Levels: {counts}. Idiom / collocation / phrasal verb items: {focus}."


def bold_gap(text):
    return re.sub(r"_{2,}", lambda m: f"`{m.group(0)}`", text)


def hangman_printout(title, intro, task, rows):
    """A printout of wisielec items alone: a wisielec batch or an own
    exercise, laid out as task 2 of a full batch's printout."""
    out = [f"# {title}: review printout", "", intro, ""]
    out += ["> " + line if line else ">" for line in
            task["instruction"].split("\n")]
    out += ["", level_line(task), ""]
    for item, row in zip(task["items"], rows):
        tag = item["level"] + (f", {item['focus']}" if item.get("focus") else "")
        out += [f"**{item['id']}.** ({tag}, type {item['mistakeType']}) "
                f"{item['sentence']}",
                f"  - Key: {item['answer'][0]}",
                f"  - Tests: {row[5]}", ""]
    return "\n".join(out).rstrip() + "\n"


def printout(test, rows, titles=TASK_TITLES, intro=None):
    """A batch's review printout: a full batch, or one task alone other than
    wisielec (hangman_printout prints that). A semi-final batch passes its
    task titles and its own intro."""
    # Where each kind of row keeps its note on what the item tests.
    note_at = {"formation": 5, "hangman": 5, "transform": 6, "choice": 5,
               "culture": 3}
    tests_notes = {TASK_OF[k][1]: [r[note_at[k]] for r in rows[k]] for k in rows}
    alone = one_task_kind(test)
    if intro is None and alone:
        task_id, _, first, size = TASK_OF[alone]
        intro = (f"{test['maxPoints']} items of task {task_id} alone, for the "
                 f"vault: they join task {task_id} of the online tests. Every "
                 f"item is the app's own. Questions are numbered {first}-"
                 f"{first + size - 1}, as task {task_id} is in a full batch.")
    elif intro is None:
        intro = (f"{test['maxPoints']} items, {test['timeMinutes']} minutes, one "
                 "point each, all or nothing. Every item is the app's own. "
                 "Questions are numbered 1-45, as in the player and the JSON.")
    out = [f"# OJAJ {test['label']}: review printout", "", intro, ""]
    for task in test["tasks"]:
        out += [f"## {titles[int(task['id']) - 1]}", ""]
        out += ["> " + line if line else ">" for line in
                task["instruction"].split("\n")]
        out += [""]
        if task["type"] != "knowledge_questions":
            out += [level_line(task), ""]
        for item, note in zip(task["items"], tests_notes[task["type"]]):
            tag = item.get("level", "")
            if item.get("focus"):
                tag += f", {item['focus']}"
            tag = f"{tag}, type {item['mistakeType']}".lstrip(", ")
            head = f"**{item['id']}.**" + (f" ({tag})" if tag else "")
            if task["type"] == "word_formation":
                out += [f"{head} {bold_gap(item['sentence'])} "
                        f"**{item['wordBase']}**",
                        f"  - Key: {' / '.join(item['answer'])}",
                        f"  - Tests: {note}"]
            elif task["type"] == "word_spelling":
                out += [f"{head} {item['sentence']}",
                        f"  - Key: {item['answer'][0]}",
                        f"  - Tests: {note}"]
            elif task["type"] == "sentence_transformation":
                out += [f"{head} {item['original']}",
                        f"  - **{item['keyword']}**: "
                        f"{bold_gap(item['transformed'])}",
                        f"  - Key: {item['answer']}",
                        f"  - Tests: {note}"]
            elif task["type"] == "multiple_choice":
                out += [f"{head} {bold_gap(item['stem'])}",
                        f"  - {'   '.join(item['options'])}",
                        f"  - Key: {item['answer']}",
                        f"  - Tests: {note}"]
            else:
                out += [f"{head} {item['question']}",
                        *[f"  - {o}" for o in item["options"]],
                        f"  - Key: {item['answer']}",
                        f"  - Mind map: {note}"]
            out += [""]
    if alone:
        return "\n".join(out).rstrip() + "\n"
    total = Counter(it["level"] for t in test["tasks"][:4] for it in t["items"])
    out += ["## Whole test, tasks 1-4", "",
            "Levels: " + ", ".join(f"{total[l]} {l}" for l in LEVELS) +
            f" (C1 or above: {total['C1'] + total['C2']} of 40).", ""]
    return "\n".join(out).rstrip() + "\n"


def item_brief(task, item):
    """One line naming an item by what is asked and its key."""
    kind = task["type"]
    if kind == "word_formation":
        return f"{item['answer'][0]} ({item['wordBase']})"
    if kind == "word_spelling":
        return item["answer"][0]
    if kind == "sentence_transformation":
        return f"{item['keyword']}: {item['answer'].split(' / ')[0]}"
    chosen = next(o for o in item["options"] if o[0] == item["answer"])[3:]
    if kind == "multiple_choice":
        return re.sub(r"_{2,}", f"**{chosen}**", item["stem"])
    return f"{item['question']} **{chosen}**"


def types_printout(tests):
    """The mistake types with every item of the vault under its type."""
    by_type = {key: [] for key in MISTAKE_TYPES}
    for test in tests:
        for task in test["tasks"]:
            for item in task["items"]:
                by_type[item["mistakeType"]].append(
                    (int(task["id"]), f"{test['id']}/{item['id']}",
                     item_brief(task, item)))
    total = sum(len(v) for v in by_type.values())
    out = ["# OJAJ online tests: mistake types, review printout", "",
           f"{len(MISTAKE_TYPES)} types, {total} items (Tests "
           f"{', '.join(t['id'] for t in tests)}). Each item has exactly one "
           "type: the point that makes it hard. A miss counts against the "
           "item's type, and the next tests draw more unseen items of the "
           "types he misses. The label is what the OJAJ page shows in the "
           "list of weak points. Items are named test/question.", "",
           "| Type | Label shown on the page | Covers | T1 | T2 | T3 | T4 | T5 "
           "| All |", "|---|---|---|---|---|---|---|---|---|"]
    for key, info in MISTAKE_TYPES.items():
        per = Counter(n for n, _, _ in by_type[key])
        counts = " | ".join(str(per[n] or "") for n in range(1, 6))
        out.append(f"| `{key}` | {info['label']} | {info['covers']} | "
                   f"{counts} | {len(by_type[key])} |")
    out += ["", "T1-T5: tasks 1-5 (word formation, wisielec, transformations, "
            "choice, UK culture).", ""]
    for key, info in MISTAKE_TYPES.items():
        out += [f"## `{key}`: {info['label']}", "",
                f"Link: {info['link'] or 'none'}", ""]
        if not by_type[key]:
            out += ["No item yet.", ""]
            continue
        out += [f"- {where} (task {n}): {brief}"
                for n, where, brief in by_type[key]]
        out += [""]
    return "\n".join(out).rstrip() + "\n"


# The batches of 45 items, each written and approved as one test. Tests 01-03
# were served as fixed tests until 2026-10-25; since then the app puts every
# test together from all of them (build_vault). Batches 04 and 05 were
# written on 2026-10-31, after he had seen every item of 01-03; 06 and 07
# the same day, from the same record. 08 and 09 on 2026-11-02, after he had
# seen all 315; 10 and 11 the same day, from the same record. 12-16 hold
# wisielec alone, written on 2026-11-11 after he had seen all 495; 17-29
# each hold one of the other tasks alone, written later the same day; 30-33
# a second round of transformations and choice, the same evening.
TESTS = [("01", T01), ("02", T02), ("03", T03), ("04", T04), ("05", T05),
         ("06", T06), ("07", T07), ("08", T08), ("09", T09), ("10", T10),
         ("11", T11), ("12", T12), ("13", T13), ("14", T14), ("15", T15),
         ("16", T16), ("17", T17), ("18", T18), ("19", T19), ("20", T20),
         ("21", T21), ("22", T22), ("23", T23), ("24", T24), ("25", T25),
         ("26", T26), ("27", T27), ("28", T28), ("29", T29), ("30", T30),
         ("31", T31), ("32", T32), ("33", T33), ("34", T34), ("35", T35),
         ("36", T36), ("37", T37), ("38", T38), ("39", T39), ("40", T40),
         ("41", T41), ("42", T42), ("43", T43), ("44", T44), ("45", T45),
         ("46", T46), ("47", T47), ("48", T48), ("49", T49), ("50", T50),
         ("51", T51), ("52", T52), ("53", T53), ("54", T54), ("55", T55),
         ("56", T56), ("57", T57), ("58", T58), ("59", T59), ("60", T60),
         ("61", T61)]


# The semi-final pool's batches of 45 (S01 written 2026-11-18).
SEMI_TESTS = [("S01", S01)]


def pool_types(culture):
    """The mistake types a pool carries: every language type and its own
    culture's (`culture` is the prefix, ETAP1_CULTURE or SEMI_CULTURE)."""
    return [key for key, info in MISTAKE_TYPES.items()
            if info["tasks"] != (5,) or key.startswith(culture)]


def built_semi_tests(tests):
    """The semi-final batches, built and checked to the semi-final profile and
    USA culture. Each is checked against the rest of the app, every etap I
    batch (`tests`, from built_tests) and the semi-final batches before it, so
    no item repeats across the two pools either."""
    existing = existing_items()
    for test in tests:
        add_items(existing, test, f"ojaj/online/{test['id']}.json")
    semi = [build_test(test_id, rows, label=f"Polfinal {test_id}")
            for test_id, rows in SEMI_TESTS]
    for test in semi:
        assert not one_task_kind(test), f"{test['id']}: a semi-final batch has all five tasks"
        check_test(test, existing, SEMI_LEVEL_RANGE, SEMI_CULTURE)
        add_items(existing, test, f"ojaj/online/semi/{test['id']}.json")
    return semi


def built_tests():
    """Every test in the vault, built and checked; the JSON gen_ojaj.py writes.

    Each test is checked against the rest of the app and against the vault
    tests before it, so no item repeats inside the vault either."""
    existing = existing_items()
    tests = [build_test(test_id, rows) for test_id, rows in TESTS]
    for test in tests:
        check_test(test, existing)
        add_items(existing, test, f"ojaj/online/{test['id']}.json")
    return tests


UK_NOTEBOOK = os.path.join(ROOT, "site", "public", "ojaj_uk.html")
STUDY_DIR = os.path.join(ROOT, "site", "public", "ojaj_study")


def vault_link(key, link, notebook):
    """The link the vault carries for a type: a section of the UK notebook,
    which must exist, or a study page, carried only once its file is in
    site/public/ojaj_study/. The study pages are written on another branch, and
    a link to one not there yet would open an error page in the app; re-running
    gen_ojaj.py after they are merged puts their links in."""
    if link is None:
        return None
    if link.startswith("/ojaj_uk#"):
        anchor = link.split("#", 1)[1]
        assert f'id="{anchor}"' in notebook, f"{key}: no #{anchor} in the notebook"
        return link
    page = re.fullmatch(r"/ojaj_study/([a-z-]+)", link)
    assert page, f"{key}: link {link}"
    return link if os.path.isfile(os.path.join(STUDY_DIR, page[1] + ".html")) else None


def vault_links():
    """Each type's key -> the link the vault carries for it (vault_link)."""
    notebook = open(UK_NOTEBOOK, encoding="utf-8").read()
    return {key: vault_link(key, info["link"], notebook)
            for key, info in MISTAKE_TYPES.items()}


def build_vault(tests):
    """The vault the app draws from, online/vault.json.

    Every item of every batch under its task, its id the batch and the
    question number ("02-14"), so the answers saved by the old fixed tests,
    keyed by question number, still find their items. Each task says how many
    items a test takes from it and, for tasks 1-4, the profile those must meet;
    the mistake types carry the labels the OJAJ page shows. The items of a
    batch of one task alone join that task, after those of the batches before
    it."""
    links = vault_links()

    def shape(task):
        return task["id"], task["type"], task["instruction"], len(task["items"])

    first = next(t for t in tests if not one_task_kind(t))
    for test in tests:
        if one_task_kind(test):
            task = test["tasks"][0]
            assert shape(task) == shape(first["tasks"][int(task["id"]) - 1]), (
                f"batch {test['id']}: not task {task['id']} of a full batch")
        else:
            assert ([shape(t) for t in test["tasks"]] ==
                    [shape(t) for t in first["tasks"]]), f"batch {test['id']}: tasks differ"
    tasks = []
    for task in first["tasks"]:
        spec = {"id": task["id"], "type": task["type"],
                "instruction": task["instruction"], "count": len(task["items"])}
        if task["type"] != "knowledge_questions":
            spec["levels"] = {lvl: list(r) for lvl, r in LEVEL_RANGE.items()}
        if task["type"] in FOCUS_TASKS:
            spec["focus"] = list(FOCUS_RANGE)
        spec["items"] = [{**item, "id": f"{test['id']}-{item['id']}"}
                         for test in tests for t in test["tasks"]
                         if t["id"] == task["id"] for item in t["items"]]
        tasks.append(spec)
    # The draw relies on this: no answer word twice in the vault means no test
    # put together from it can hold one twice. built_tests already refuses a
    # batch that repeats an earlier one's answer; this says it of the whole.
    words = [a.lower() for t in tasks[:2] for it in t["items"]
             for a in it["answer"]]
    assert len(words) == len(set(words)), "an answer word repeats in the vault"
    return {
        "competition": "ojaj",
        "kind": "online-vault",
        "label": "Test online",
        "timeMinutes": first["timeMinutes"],
        "mistakeTypes": [{"key": key, "label": MISTAKE_TYPES[key]["label"],
                          "link": links[key]}
                         for key in pool_types(ETAP1_CULTURE)],
        "tasks": tasks,
    }


def own_printout():
    """The own wisielec exercises in the online test's shape, for review."""
    parts = []
    for ex_id, rows in OWN.HANGMAN_ONLINE:
        ex = dict(OWN.EXERCISES)[ex_id]
        task = {**own_hangman_task(rows),
                "instruction": ex["tasks"][0]["instruction"]}
        parts.append(hangman_printout(
            f"{ex_id}, {ex['title']}",
            "Practice exercise on the OJAJ page, 10 items, the online test's "
            "shape. Its words are in no other exercise and not in the vault.",
            task, rows))
    return "\n".join(parts)


def main():
    os.makedirs(TMP, exist_ok=True)
    tests = built_tests()
    for test, (test_id, rows) in zip(tests, TESTS):
        path = os.path.join(TMP, f"ojaj_online_{test_id}_review.md")
        with open(path, "w", encoding="utf-8") as fh:
            if is_hangman_batch(test):
                fh.write(hangman_printout(
                    f"OJAJ {test['label']}", "10 wisielec items for the vault, "
                    "drawn into task 2 of the online tests; questions 11-20, as "
                    "task 2 is numbered in a full batch.",
                    test["tasks"][0], rows["hangman"]))
            else:
                fh.write(printout(test, rows))
        print(f"online {test_id}: checks pass, printout at {os.path.relpath(path, ROOT)}")
    semi = built_semi_tests(tests)
    for test, (test_id, rows) in zip(semi, SEMI_TESTS):
        path = os.path.join(TMP, f"ojaj_semi_{test_id}_review.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(printout(
                test, rows, SEMI_TASK_TITLES,
                f"{test['maxPoints']} items for the semi-final pool, "
                f"{test['timeMinutes']} minutes, one point each, all or "
                "nothing. Every item is the app's own. Questions are numbered "
                "1-45. Harder than the etap I pool: per 10-item task no B1, 2-3 "
                "B2, 5-6 C1, 1-2 C2. Task 5 asks about the USA mind map."))
        print(f"semi-final {test_id}: checks pass, printout at "
              f"{os.path.relpath(path, ROOT)}")
    path = os.path.join(TMP, "ojaj_mistake_types_review.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(types_printout(tests))
    print(f"mistake types: printout at {os.path.relpath(path, ROOT)}")
    check_own_exercises()
    path = os.path.join(TMP, "ojaj_own_wisielec_review.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(own_printout())
    print(f"own wisielec: {len(OWN.HANGMAN_ONLINE)} exercises pass, printout at "
          f"{os.path.relpath(path, ROOT)}")
    vault = build_vault(tests)
    sizes = ", ".join(f"{len(t['items'])}" for t in vault["tasks"])
    print(f"vault: {len(tests)} batches, items per task {sizes}")
    held = sorted({MISTAKE_TYPES[t["key"]]["link"] for t in vault["mistakeTypes"]
                   if MISTAKE_TYPES[t["key"]]["link"] and not t["link"]})
    if held:
        print(f"vault: links held back until the study page exists: {', '.join(held)}")


if __name__ == "__main__":
    main()
