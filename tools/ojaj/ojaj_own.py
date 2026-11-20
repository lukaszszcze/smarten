#!/usr/bin/env python3
"""School-stage practice for OJAJ 2026/27, written for this app.

Imported by tools/ojaj/ojaj_new.py, which appends GROUPS to its own; tools/ojaj/gen_ojaj.py
then writes and checks these exercises with no further edit.

Every OJAJ paper with a published key is already converted, so these items are
not from a paper. They follow the 2026/27 programme for the school stage, which
lists four task types (multiple choice, word formation, key word
transformations and hangman):

    https://ojaj.wsjo.pl/wp-content/uploads/2026/09/Zalacznik-do-Regulaminu-OJAJ-program-OJAJ-edycja-2026-2027.pdf

The first batch covers the two types the papers lean on and students find
hardest: hangman and key word transformations, two exercises of ten each. The
formats are the 2023/24 paper's, built with the same helpers
(tools/ojaj/ojaj_2324.py).

Hangman (3)-(7), added 2026-11-11, are in the 2024/25 paper's shape, the one
the online tests use: given letters in lower case, the letter count in
brackets, and as many given letters as the papers give. Their rows are vault
wisielec rows (level, focus, what it tests, mistake type), and
tools/ojaj/ojaj_online.py checks them with a vault wisielec task's rules
(check_own_exercises); their words are in no other exercise and not in the
vault. They lean on the spelling types Tadzio misses most: vowels, double
letters, silent letters.

Writing rules the items keep to:
  - hangman: the sentence must pin the word down on its own, and the given
    letters must rule out any other word of that length (stingy shows its I and
    G because s__n__ also fits "skinny"). No word already used by another
    hangman exercise.
  - transformations: the keyword appears unchanged in every accepted answer,
    every answer is six words or fewer with no contractions, and accepted
    alternatives are joined with " / ". These are graded by the AI checker
    against the key, so the key lists the phrasings a marker would accept.

Every exercise title says the items are the app's own.
"""

import ojaj_2324 as T2324

SRC = (
    "https://ojaj.wsjo.pl/wp-content/uploads/2026/09/"
    "Zalacznik-do-Regulaminu-OJAJ-program-OJAJ-edycja-2026-2027.pdf"
)

NOTE = "Zadania wlasne w formacie etapu szkolnego (nie z arkusza olimpiady). "

# (sentence with {} where the word goes, compact pattern, answer)
HANGMAN_1 = [
    ("After the long drought the river was so {} that we could walk across it.",
     "s__l__w", "shallow"),
    ("Please do not touch the paintings: they are {}, and no amount of money "
     "could replace them.", "p____l__s", "priceless"),
    ("Our flight was {} for three hours because of a storm, so we spent the "
     "whole afternoon at the airport.", "d__a__d", "delayed"),
    ("I can't stand people who {} about everything: the weather, the food, "
     "the traffic...", "c___l__n", "complain"),
    ("The two sisters look so {} that even their parents sometimes mix them "
     "up.", "a__k_", "alike"),
    ("The court found him {} of stealing the car, and he spent two years in "
     "prison.", "g___t_", "guilty"),
    ("The teacher reminded us that using a phone during the exam would count "
     "as {}.", "c__a___g", "cheating"),
    ("The children were {} when they heard a strange noise upstairs, and they "
     "hid under the blankets.", "t___i___d", "terrified"),
    ("Thousands of people lost their homes in the giant wave, a {}, that hit "
     "the coast after the earthquake.", "t___a_i", "tsunami"),
    ("You must {} your seatbelt before the plane takes off.",
     "f__t__", "fasten"),
]

HANGMAN_2 = [
    ("The firefighters managed to {} everyone from the burning building just "
     "in time.", "e__c___e", "evacuate"),
    ("Her handwriting is so {} that the teacher asked her to type her essays "
     "instead.", "i___g___e", "illegible"),
    ("Scientists carried out an {} to find out whether the new medicine really "
     "works.", "e___r___n_", "experiment"),
    ("The volcano had been {} for centuries, so nobody expected it to erupt.",
     "d__m__t", "dormant"),
    ("He is so {} that he has never once bought his friends a drink.",
     "s_i_g_", "stingy"),
    ("Pieces of {} from the crashed plane were found many kilometres away.",
     "w___k__e", "wreckage"),
    ("Wearing a helmet is {} on building sites: you cannot go in without one.",
     "c___u___r_", "compulsory"),
    ("After the accident he had to learn to walk again, and his {} took almost "
     "a year.", "r__o___y", "recovery"),
    ("The new law will {} plastic bags, so shops will no longer be allowed to "
     "hand them out.", "p__h___t", "prohibit"),
    ("My little brother is very {}: he always wants to know how everything "
     "works.", "c__i__s", "curious"),
]

# (original, keyword, transformed with {} for the gap, answer)
TRANSFORM_1 = [
    ("It wasn't necessary for you to buy flowers.", "NEED",
     "You {} flowers.", "need not have bought / did not need to buy"),
    ("I'm sure he didn't take your money.", "CANNOT",
     "He {} your money.", "cannot have taken"),
    ("It's a pity I didn't go to the party.", "WISH",
     "I {} to the party.", "wish I had gone"),
    ("People say that the castle is haunted.", "SAID",
     "The castle {} haunted.", "is said to be"),
    ("She started learning Spanish three years ago.", "BEEN",
     "She {} Spanish for three years.",
     "has been learning / has been studying"),
    ("I'd prefer you not to smoke in here.", "RATHER",
     "I {} smoke in here.", "would rather you did not"),
    ("Perhaps Tom forgot about the meeting.", "MAY",
     "Tom {} about the meeting.", "may have forgotten"),
    ("Although it was raining, we went for a walk.", "DESPITE",
     "We went for a walk {} raining.",
     "despite it / despite the fact that it was / despite the fact it was"),
    ("A mechanic repaired my bike yesterday.", "GOT",
     "I {} yesterday.", "got my bike repaired"),
    ("The last time I saw Anna was in May.", "SEEN",
     "I {} May.", "have not seen Anna since"),
]

TRANSFORM_2 = [
    ("I haven't been to the cinema for ages.", "AGES",
     "It {} I went to the cinema.", "has been ages since / is ages since"),
    ("He regrets not studying harder.", "ONLY",
     "If {} harder.", "only he had studied / only he had worked"),
    ("It took me two hours to finish the report.", "SPENT",
     "I {} the report.",
     "spent two hours finishing / spent two hours on / spent two hours writing"),
    ("They cancelled the match because of the snow.", "CALLED",
     "The match {} because of the snow.", "was called off"),
    ("It isn't worth repairing this old radio.", "POINT",
     "There {} this old radio.", "is no point repairing / is no point in repairing"),
    ("Ewa was late because she missed the bus.", "IF",
     "Ewa would have arrived on time {} the bus.", "if she had not missed"),
    ("My parents don't let me stay out after ten.", "ALLOWED",
     "I {} stay out after ten.", "am not allowed to"),
    ("Everyone was surprised that she won the race.", "CAME",
     "Her victory in the race {} everyone.", "came as a surprise to"),
    ("He probably won't come to the party.", "UNLIKELY",
     "He {} to the party.", "is unlikely to come"),
    ("'I'll help you with your homework,' said Dad.", "OFFERED",
     "Dad {} with my homework.", "offered to help me"),
]


# The 2024/25 paper's wisielec instruction, without diacritics as practice
# instructions are written.
INSTR_HANGMAN_ONLINE = (
    "Wpisz slowo poprawnie uzupelniajace kazde ze zdan. Liczba kreseczek "
    "odpowiada liczbie liter w slowie. Wymagana jest pelna poprawnosc "
    "gramatyczna i ortograficzna wpisywanych slow."
)


def online_pattern(compact):
    """'w_a_h_r' -> 'w __ a __ h __ r (7)', the 2024/25 paper's shape (the
    vault's pattern_of; check_own_hangman holds the two to the same output)."""
    slots = " ".join("__" if c == "_" else c.lower() for c in compact)
    return f"{slots} ({len(compact)})"


def hangman_online_exercise(ex_id, title, rows, source):
    """rows: vault wisielec rows, (sentence with {} where the word goes,
    compact pattern, answer, level, focus, what it tests, mistake type); the
    exercise keeps the first three."""
    items = [{"id": f"1.{i}", "sentence": s.format(online_pattern(p)),
              "hint": online_pattern(p), "answer": [a]}
             for i, (s, p, a, *_) in enumerate(rows, start=1)]
    return ex_id, {
        "title": title,
        "type": "practice",
        "source": source,
        "tasks": [{"id": "1", "type": "word_spelling", "points": len(items),
                   "instruction": INSTR_HANGMAN_ONLINE, "items": items}],
    }


HANGMAN_3 = [
    ("My little brother knows the name of every {} that ever lived.",
     "d_n_____", "dinosaur", "B1", None, "spelling (-saur, not *dinosour)",
     "vowels"),
    ("Grandad's old watch is his most precious {}.", "po______o_",
     "possession", "C1", None, "spelling (double s, double s)",
     "double-letters"),
    ("There were {} all over the sofa after the boys had eaten their "
     "sandwiches.", "__um__", "crumbs", "B2", None, "spelling (silent b)",
     "silent-letters"),
    ("The police {} asked us a lot of questions about the accident.",
     "s__g____", "sergeant", "C1", None, "spelling (-er-, -eant)", "vowels"),
    ("The children loved jumping in every {} on the way home from school.",
     "p___l_", "puddle", "B2", None, "spelling (double d)", "double-letters"),
    ("The ceremony was very {}: nobody laughed or talked.", "__l_m_",
     "solemn", "C1", None, "spelling (silent n)", "silent-letters"),
    ("Be {}: if you keep trying, you will get there in the end.",
     "p__s_____t", "persistent", "C1", None, "-ent (not *persistant)",
     "ance-ence"),
    ("When I got the main part in the school play, I was on {} nine for a "
     "week.", "___u_", "cloud", "C1", "idiom", "on cloud nine (very happy)",
     "idiom"),
    ("I've got a sore {}, so I can't sing in the concert tonight.",
     "_h___t", "throat", "B2", "collocation", "a sore throat; -oa-",
     "collocation"),
    ("The teacher left the room and told us to {} on with our work.",
     "_a___", "carry", "B1", "phrasal verb", "carry on; double r",
     "phrasal-verb"),
]

HANGMAN_4 = [
    ("My phone's {} is almost dead: can I borrow your charger?", "b_____y",
     "battery", "B1", None, "spelling (double t)", "double-letters"),
    ("My cousin does {} at school: he can lift me off the ground!",
     "__es_l___", "wrestling", "B2", None, "spelling (silent w, silent t)",
     "silent-letters"),
    ("The hotel was so {} that it had a swimming pool on the roof.",
     "__x_r___s", "luxurious", "C1", None, "spelling (-urious)", "vowels"),
    ("The library has an {} collection of old books: more than a million!",
     "i__e___", "immense", "C1", None, "spelling (double m, -se)",
     "double-letters"),
    ("I like my boiled eggs with a runny {}.", "y___", "yolk", "B2", None,
     "spelling (silent l)", "silent-letters"),
    ("What a {} view from the top of the mountain!", "g__g____", "gorgeous",
     "B2", None, "spelling (-geous)", "vowels"),
    ("We had three days of {} sunshine at the seaside.", "g__r____",
     "glorious", "B2", None, "y to i before -ous (glory -> glorious)",
     "suffix-spelling"),
    ("I hate going to the dentist, but I'll have to bite the {} and book an "
     "appointment.", "b____t", "bullet", "C1", "idiom",
     "bite the bullet (do something unpleasant); double l", "idiom"),
    ("A {} of sheep was blocking the road, so we had to wait.", "____k",
     "flock", "B2", "collocation", "a flock of sheep", "collocation"),
    ("Tom wanted to go on the highest slide, but he {} out at the last "
     "minute.", "c___k___d", "chickened", "C1", "phrasal verb",
     "chicken out (get scared and not do it)", "phrasal-verb"),
]

HANGMAN_5 = [
    ("I hit my {} with the hammer, and it really hurt.", "___m_", "thumb",
     "B1", None, "spelling (silent b)", "silent-letters"),
    ("I really {} your help with my science project.", "a___e___t_",
     "appreciate", "B2", None, "spelling (double p, -ciate)",
     "double-letters"),
    ("Only pupils under fifteen are {} for the competition.", "___g_b__",
     "eligible", "C1", None, "-ible (not *eligable)", "able-ible"),
    ("In the Middle Ages, the {} killed millions of people in Europe.",
     "p__g__", "plague", "C1", None, "spelling (-gue)", "silent-letters"),
    ("Don't forget your swimming {}: the water in the pool stings your eyes.",
     "g___l__", "goggles", "B2", None, "spelling (double g)",
     "double-letters"),
    ("My favourite subject at school is {}: I love solving problems with "
     "numbers.", "m____m___c_", "mathematics", "B1", None,
     "spelling (-the-, not *mathmatics)", "vowels"),
    ("This cake is made with ground {} instead of flour.", "__m__d_",
     "almonds", "B2", None, "spelling (silent l)", "silent-letters"),
    ("It's my first week at the new club, so I'm still learning the {}.",
     "__p__", "ropes", "C1", "idiom",
     "learn the ropes (learn how things are done)", "idiom"),
    ("We have a very tight {}: the bus leaves at seven and we have three "
     "museums to see.", "____d__e", "schedule", "C1", "collocation",
     "a tight schedule; sch-, -ule", "collocation"),
    ("I {} into my old teacher at the supermarket yesterday.", "b__p__",
     "bumped", "B2", "phrasal verb", "bump into (meet by chance)",
     "phrasal-verb"),
]

HANGMAN_6 = [
    ("Workers put up {} around the church so they could repair the tower.",
     "_c___o___n_", "scaffolding", "C2", None, "spelling (double f)",
     "double-letters"),
    ("There is a funny garden {} with a red hat next to our pond.", "_n___",
     "gnome", "B2", None, "spelling (silent g)", "silent-letters"),
    ("This is only a {} classroom: we'll move back to ours when the painters "
     "finish.", "t_m____r_", "temporary", "B2", None,
     "spelling (-orary, not *tempory)", "vowels"),
    ("We filled the {} with food for the whole week.", "t_o____", "trolley",
     "B2", None, "spelling (double l, -ey)", "double-letters"),
    ("After the storm, the beach was covered in {} from broken boats.",
     "d__r__", "debris", "C1", None, "spelling (silent s)", "silent-letters"),
    ("Don't worry about the old mug: it's cheap and easily {}.",
     "r__l____b__", "replaceable", "C1", None,
     "e kept after c before -able (not *replacable)", "suffix-spelling"),
    ("Washing your hands before meals is a basic rule of {}.", "h_g____",
     "hygiene", "C1", None, "spelling (-y-, -ie-)", "vowels"),
    ("My dog goes {} every time someone rings the doorbell.", "__n_n__",
     "bananas", "C1", "idiom", "go bananas (get very excited)", "idiom"),
    ("Could you do me a {} and feed my cat while I'm away?", "f_v___",
     "favour", "B1", "collocation", "do someone a favour; -our",
     "collocation"),
    ("We bought Ola some flowers to {} her up after she broke her arm.",
     "_h___", "cheer", "B1", "phrasal verb", "cheer up", "phrasal-verb"),
]

HANGMAN_7 = [
    ("Please {}: the baby is asleep in the next room.", "___sp__", "whisper",
     "B1", None, "spelling (wh-)", "silent-letters"),
    ("A {} was looking for food in our dustbin last night.", "r_____n",
     "raccoon", "B2", None, "spelling (double c, double o)", "double-letters"),
    ("Gymnasts have to be strong and very {}.", "___x___e", "flexible", "B2",
     None, "-ible (not *flexable)", "able-ible"),
    ("Our kitchen table {} because one leg is shorter than the others.",
     "wo_____", "wobbles", "C1", None, "spelling (double b)",
     "double-letters"),
    ("The {} fixed our car in less than an hour.", "m______c", "mechanic",
     "B1", None, "spelling (ch said as k)", "silent-letters"),
    ("The river forms the {} between the two countries.", "___n___y",
     "boundary", "C1", None, "spelling (-ary, not *boundry)", "vowels"),
    ("At Christmas, people in Britain hang {} above the door and kiss "
     "underneath it.", "m___le___", "mistletoe", "C1", None,
     "spelling (silent t, -toe)", "silent-letters"),
    ("Grandma is eighty, but she's as fit as a {}: she walks ten kilometres "
     "every day.", "f___l_", "fiddle", "C1", "idiom",
     "as fit as a fiddle (very healthy); double d", "idiom"),
    ("Those new headphones must have cost a {}!", "f___u__", "fortune", "B2",
     "collocation", "cost a fortune", "collocation"),
    ("You can always {} on me if you need help.", "__u__", "count", "B2",
     "phrasal verb", "count on (rely on)", "phrasal-verb"),
]

HANGMAN_ONLINE = [
    ("ojaj_own_wisielec_03", HANGMAN_3),
    ("ojaj_own_wisielec_04", HANGMAN_4),
    ("ojaj_own_wisielec_05", HANGMAN_5),
    ("ojaj_own_wisielec_06", HANGMAN_6),
    ("ojaj_own_wisielec_07", HANGMAN_7),
]


def own(pair):
    """Mark an exercise as the app's own: title suffix and instruction note."""
    ex_id, ex = pair
    ex["title"] += " (zadania wlasne)"
    ex["tasks"][0]["instruction"] = NOTE + ex["tasks"][0]["instruction"]
    return ex_id, ex


HEAD = "OJAJ etap szkolny 2026/27"

EXERCISES = [own(p) for p in [
    T2324.hangman_exercise("ojaj_own_wisielec_01", f"{HEAD}: wisielec (1)",
                           HANGMAN_1, SRC),
    T2324.hangman_exercise("ojaj_own_wisielec_02", f"{HEAD}: wisielec (2)",
                           HANGMAN_2, SRC),
] + [
    hangman_online_exercise(ex_id, f"{HEAD}: wisielec ({int(ex_id[-2:])})",
                            rows, SRC)
    for ex_id, rows in HANGMAN_ONLINE
] + [
    T2324.transform_exercise("ojaj_own_transformacje_01",
                             f"{HEAD}: transformacje (1)", TRANSFORM_1, SRC),
    T2324.transform_exercise("ojaj_own_transformacje_02",
                             f"{HEAD}: transformacje (2)", TRANSFORM_2, SRC),
]]

for _, ex in EXERCISES:
    for item in ex["tasks"][0]["items"]:
        if "keyword" in item:
            for alt in item["answer"].split(" / "):
                assert item["keyword"].lower() in alt.split(), (
                    f"{item['id']}: keyword {item['keyword']} not in '{alt}'")
                assert len(alt.split()) <= 6, f"{item['id']}: '{alt}' over 6"
                assert "'" not in alt, f"{item['id']}: contraction in '{alt}'"

# --------------------------------------------------------------------------
# What ojaj_new.py consumes
# --------------------------------------------------------------------------

GROUPS = [
    ("Etap szkolny 2026/27 - zadania wlasne", EXERCISES),
]
