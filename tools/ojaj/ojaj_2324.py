#!/usr/bin/env python3
"""The fourth batch of OJAJ material: the 2023/24 etap szkolny paper.

Imported by tools/ojaj/ojaj_new.py, which appends GROUPS to its own; tools/ojaj/gen_ojaj.py
then writes and checks these exercises with no further edit.

Where the text came from
------------------------
Both papers and both keys are scans with no text layer. OCR (tesseract, eng)
reads the words but scrambles the two-column option layout and the hangman
letter boxes, so every item below was read off page images instead:

    pdftoppm -r 300 -png tools/ojaj/pdfs/t2324_A.pdf tools/ojaj/pdfs/hi_A

Sources, prefixed with https://ojaj.wsjo.pl/wp-content/uploads/2025/06/:
    Test-A-—-6.11.2023-bez-hasa.pdf         Test-A-Klucz-—-6.11.2023-bez-hasla.pdf
    Test-B-—-6.11.2023-bez-hasla.pdf        Test-B-Klucz-—-6.11.2023-bez-hasla.pdf

Wersja B holds the same ninety items as wersja A with its tasks in a different
order (its key is A's key re-lettered, and its culture questions are word for
word A's), so only wersja A is converted.

The paper has five tasks: A multiple choice grammar (20), B hangman (20),
C word formation (20), D key word transformations (20), E UK culture multiple
choice (10). Every twenty-item task is split into two exercises of ten, so the
paper gives nine exercises.

The hangman task prints the word's length in brackets after each sentence; the
app's pattern already has one slot per letter, so the bracket is dropped. The
"sister-in-law" item keeps its hyphens as given slots, as the paper does.
"""

SRC = "https://ojaj.wsjo.pl/wp-content/uploads/2025/06"
SRC_A = f"{SRC}/Test-A-—-6.11.2023-bez-hasa.pdf"

GAP = "_________"          # exactly nine, which is what GrammarGaps and
#                            SentenceTransformation split on
BLANK = "__________"       # word_formation splits on any run of two or more

INSTR_MC = (
    "Z podanych odpowiedzi wybierz poprawna. Tylko jedna jest prawidlowa."
)
INSTR_HANGMAN = (
    "Uzupelnij brakujace litery. Liczba kreseczek odpowiada liczbie liter w "
    "wyrazie. Wymagana jest pelna poprawnosc ortograficzna."
)
INSTR_FORMATION = (
    "Uzupelnij kazde zdanie slowem utworzonym od wyrazu podanego wielkimi "
    "literami. Wymagana jest pelna poprawnosc ortograficzna i gramatyczna."
)
INSTR_TRANSFORM = (
    "Wykorzystujac slowa podane wielkimi literami, uzupelnij luki w zdaniach "
    "tak, aby zachowac sens zdania wyjsciowego. W kazda luke mozesz wpisac do "
    "6 wyrazow lacznie z wyrazem podanym. Nie wolno zmieniac form podanych "
    "slow. Niedopuszczalne sa formy skrocone (isn't, won't, would've itd.). "
    "Wymagana jest pelna poprawnosc gramatyczna i ortograficzna."
)
INSTR_CULTURE = (
    "Pytania o kulture i historie Wielkiej Brytanii. Z podanych odpowiedzi "
    "wybierz poprawna. Tylko jedna jest prawidlowa."
)


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------

def _exercise(ex_id, title, source, task):
    return ex_id, {
        "title": title,
        "type": "practice",
        "source": source,
        "tasks": [task],
    }


def mc_exercise(ex_id, title, instruction, rows, source):
    """rows: (stem, [four options], answer letter a-d as on the key)."""
    items = []
    for i, (stem, opts, answer) in enumerate(rows, start=1):
        assert len(opts) == 4, f"{ex_id} {i}: {len(opts)} options"
        items.append({
            "id": f"1.{i}",
            "stem": stem,
            "options": [f"{l}) {o}" for l, o in zip("ABCD", opts)],
            "answer": answer.upper(),
        })
    return _exercise(ex_id, title, source, {
        "id": "1",
        "type": "multiple_choice",
        "points": len(items),
        "instruction": instruction,
        "items": items,
    })


def pattern_of(compact):
    """'_o__' -> '__ O __ __': one slot per character, given letters shown."""
    return " ".join("__" if c == "_" else c.upper() for c in compact)


def hangman_exercise(ex_id, title, rows, source):
    """rows: (sentence with {} where the word goes, compact pattern, answer)."""
    items = []
    for i, (sentence, compact, answer) in enumerate(rows, start=1):
        pattern = pattern_of(compact)
        items.append({
            "id": f"1.{i}",
            "sentence": sentence.format(pattern),
            "hint": pattern,
            "answer": [answer],
        })
    return _exercise(ex_id, title, source, {
        "id": "1",
        "type": "word_spelling",
        "points": len(items),
        "instruction": INSTR_HANGMAN,
        "items": items,
    })


def formation_exercise(ex_id, title, rows, source):
    """rows: (sentence with {} for the blank, base word, answer)."""
    return _exercise(ex_id, title, source, {
        "id": "1",
        "type": "word_formation",
        "points": len(rows),
        "instruction": INSTR_FORMATION,
        "items": [
            {"id": f"1.{i}", "sentence": s.format(BLANK),
             "wordBase": base.upper(), "answer": [a]}
            for i, (s, base, a) in enumerate(rows, start=1)
        ],
    })


def transform_exercise(ex_id, title, rows, source):
    """rows: (original, keyword, transformed with {} for the gap, answer).

    Alternatives the key gives with a slash are written out in full and joined
    with " / ", which is how the scorer reads accepted phrasings."""
    return _exercise(ex_id, title, source, {
        "id": "1",
        "type": "sentence_transformation",
        "points": len(rows),
        "instruction": INSTR_TRANSFORM,
        "items": [
            {"id": f"1.{i}", "original": o, "keyword": k.upper(),
             "transformed": t.format(GAP), "answer": a}
            for i, (o, k, t, a) in enumerate(rows, start=1)
        ],
    })


def paper_exercises(tag, label, source, mc, hangman, formation, transform,
                    culture):
    """Nine exercises from one paper: each twenty-item task split in two."""
    for name, rows in [("mc", mc), ("hangman", hangman),
                       ("formation", formation), ("transform", transform)]:
        assert len(rows) == 20, f"{tag} {name}: {len(rows)} rows"
    assert len(culture) == 10, f"{tag} culture: {len(culture)} rows"
    pre = f"ojaj_2324{tag}"
    head = f"OJAJ 2023/24{label}"
    return [
        mc_exercise(f"{pre}_gramatyka_01", f"{head}: gramatyka (1)",
                    INSTR_MC, mc[:10], source),
        mc_exercise(f"{pre}_gramatyka_02", f"{head}: gramatyka (2)",
                    INSTR_MC, mc[10:], source),
        hangman_exercise(f"{pre}_wisielec_01", f"{head}: wisielec (1)",
                         hangman[:10], source),
        hangman_exercise(f"{pre}_wisielec_02", f"{head}: wisielec (2)",
                         hangman[10:], source),
        formation_exercise(f"{pre}_slowotworstwo_01",
                           f"{head}: slowotworstwo (1)", formation[:10], source),
        formation_exercise(f"{pre}_slowotworstwo_02",
                           f"{head}: slowotworstwo (2)", formation[10:], source),
        transform_exercise(f"{pre}_transformacje_01",
                           f"{head}: transformacje (1)", transform[:10], source),
        transform_exercise(f"{pre}_transformacje_02",
                           f"{head}: transformacje (2)", transform[10:], source),
        mc_exercise(f"{pre}_kultura", f"{head}: Wielka Brytania",
                    INSTR_CULTURE, culture, source),
    ]


# --------------------------------------------------------------------------
# Wersja A
# --------------------------------------------------------------------------

A_MC = [
    (f"By this time next year, she {GAP} as an engineer for 10 years.",
     ["will be working", "will work", "have worked", "will have been working"],
     "d"),
    (f"Could you tell me what {GAP}?",
     ["time is it", "is the time", "time it is", "the time"], "c"),
    (f"{GAP} dress does she prefer, the pink one or the red one?",
     ["what", "who", "which", "whose"], "c"),
    (f"Please pass me the salt, {GAP}?",
     ["do you", "don't you", "are you", "will you"], "d"),
    (f"I {GAP} ever drink tea with lemon. I simply don't like the taste.",
     ["hard", "harden", "hardiness", "hardly"], "d"),
    (f"I don't recommend {GAP} this film. It's extremely boring.",
     ["watch", "to watch", "watching", "to watching"], "c"),
    (f"I leaned the bike {GAP} the wall and entered the building.",
     ["of", "to", "on", "against"], "d"),
    (f"Our maths teacher is married {GAP} a physics teacher.",
     ["with", "of", "from", "to"], "d"),
    (f"I am keen {GAP} all football matches on TV.",
     ["on watching", "on looking", "to watching", "to seeing"], "a"),
    (f"They arrived {GAP} the airport just in time.",
     ["at", "to", "on", "in"], "a"),
    (f"Do you expect me {GAP} it to you a third time?",
     ["explaining", "explain", "to explain", "having explain"], "c"),
    (f"He wishes he {GAP} more about basketball.",
     ["knows", "will know", "known", "knew"], "d"),
    (f"They worked {GAP} to complete the project on time.",
     ["hardly", "hard", "hardily", "harden"], "b"),
    (f"I can't find my phone. I {GAP} it at home.",
     ["must leave", "must leaving", "must have left", "must left"], "c"),
    (f"Susan {GAP} her homework when the phone rang.",
     ["has been doing", "done", "was doing", "was to be doing"], "c"),
    (f"He would visit his friend in the USA if he {GAP} more money.",
     ["has", "have", "had", "would have"], "c"),
    (f"Unless it {GAP} tomorrow, we can go to the beach.",
     ["will rain", "rains", "doesn't rain", "would rain"], "b"),
    (f"She's allergic {GAP} cats.",
     ["in", "on", "at", "to"], "d"),
    (f"She'll be back {GAP} a few hours.",
     ["about", "in", "on", "at"], "b"),
    (f"{GAP} car is blocking the driveway?",
     ["Whose", "Who", "Whom", "Whilst"], "a"),
]

A_HANGMAN = [
    ("{} of the bikes broke at the same time, so we couldn't finish the race.",
     "_o__", "both"),
    ("He {} the instructions and didn't complete the task.",
     "m___n__r_____", "misunderstood"),
    ("Susan, have you gone {} any painful experience in your life recently?",
     "__r____", "through"),
    ("{} of my parents likes my girl-friend. It makes me feel depressed.",
     "__i__e_", "neither"),
    ("My {} is amazing. She married my brother only a month ago but we are "
     "already getting on very well.",
     "_i____-__-_a_", "sister-in-law"),
    ("{} of the guests arrived on time. Everybody was late.",
     "___e", "none"),
    ("Her {} speech left a lasting impact on the audience.",
     "_m__e__i__", "impressive"),
    ("Don't worry. I'm sure you'll make {} meet.",
     "___s", "ends"),
    ("During the pandemic remember to wash your hands with soap and wear {} "
     "gloves.",
     "d___o_a___", "disposable"),
    ("Mark's {} to the project was priceless. We wouldn't have done it "
     "without him.",
     "__n__i___i__", "contribution"),
    ("Many animals are {} during the daytime and hunt during the night.",
     "_n___i__", "inactive"),
    ("All my students were exhausted during the last lecture, so they did not "
     "understand a word of my {} of this complex theory.",
     "_x__a_a_i__", "explanation"),
    ("The authorities {} warnings and gave instructions as how to prepare for "
     "the flood.",
     "___u_d", "issued"),
    ("You usually wear very {} colours. Why don't you start wearing bright "
     "colours for a change?",
     "_u__", "dull"),
    ("I need another lamp. I can't read in here. The light is too {}.",
     "_i_", "dim"),
    ("The rise in oil prices is {} as oil supplies have been running out "
     "across the world.",
     "__e_i_____", "inevitable"),
    ("There was {} chaos in the city centre during the transport strike. Many "
     "people had problems getting to work.",
     "___e_", "utter"),
    ("Instead of going to Greece, my parents decided to go on a luxury {} "
     "around the Mediterranean.",
     "___i__", "cruise"),
    ("My family buy {} furniture, restore it and then sell online.",
     "___i_u_", "antique"),
    ("Recently it has been announced that crimes like {} and burglary are on "
     "the increase.",
     "_h___", "theft"),
]

A_FORMATION = [
    ("Trains in Poland are very {}. They are never on time.",
     "rely", "unreliable"),
    ("Students were blocking the {} to the school and didn't let anyone in.",
     "enter", "entrance"),
    ("{}, it is raining today so we can't go out and sunbathe.",
     "fortune", "unfortunately"),
    ("The doctor {} me to stop eating so much sugar.",
     "advice", "advised"),
    ("My first {} was that our new teacher was a very friendly person.",
     "impress", "impression"),
    ("Susan had a(n) {} visit from a friend who usually avoids her.",
     "expect", "unexpected"),
    ("You must {} your TikTok account before uploading any content.",
     "active", "activate"),
    ("Our teacher took us to an art {} which we really loved.",
     "exhibit", "exhibition"),
    ("It was a very peaceful place. Living there meant that I could actually "
     "go wherever I {}.",
     "please", "pleased"),
    ("After her parents died, she could not get over it and felt blue and {}.",
     "misery", "miserable"),
    ("Employers have recently complained that they can't find reliable {}.",
     "employ", "employees"),
    ("She is {} for the job as she cannot swim, which is absolutely essential "
     "to become a lifeguard.",
     "suit", "unsuitable"),
    ("I didn't pass my final exam although I had studied so hard. The only "
     "thing I felt was deep {}.",
     "disappoint", "disappointment"),
    ("My new mobile is much bigger than the previous one which makes it {}. "
     "I can't put it in any of my pockets.",
     "convenient", "inconvenient"),
    ("Mobile phones nowadays have {} capabilities, such as sending and "
     "receiving e-mails or using instant messaging.",
     "end", "endless"),
    ("King Arthur was considered to be an exceptionally {} leader, who feared "
     "nobody.",
     "courage", "courageous"),
    ("It is said that {} killed the cat. Don't be too nosy.",
     "curious", "curiosity"),
    ("Airlines shouldn't employ such young and {} people for pilot positions. "
     "It is simply irresponsible.",
     "experience", "inexperienced"),
    ("He said he loved me and looked at me in {}.",
     "amaze", "amazement"),
    ("I came back home after 10 years of absence. All my friends prepared for "
     "me a surprise party full of {} and affection.",
     "warm", "warmth"),
]

A_TRANSFORM = [
    ("Nobody can do all that work in one single day. It's impossible.",
     "capable", "Nobody {} all that work in one single day.",
     "is capable of doing"),
    ("I wish I hadn't eaten so much cake.",
     "eating", "I {} much cake.",
     "regret eating so"),
    ("Did the teacher give you the handout yesterday?",
     "provide", "Did the teacher {} the handout yesterday?",
     "provide you with"),
    ("I'm not interested in what you think about me.",
     "care", "I {} your opinion of me.",
     "do not care about"),
    ("I can't afford to buy a new house.",
     "enough", "I {} buy a new house.",
     "do not have enough money to"),
    ("The concert hall is close to the hotel, so we can walk there.",
     "foot", "The concert hall is close to the hotel, so we can {}.",
     "go there on foot / get there on foot"),
    ("She is not interested in sports.",
     "no", "She {} in sports.",
     "has no interest"),
    ("The podcast was too boring for me to finish.",
     "that", "The podcast was {} finish it.",
     "so boring that I could not / so boring that I did not"),
    ("He didn't understand the instructions, so he made a mistake.",
     "had", "{}, he wouldn't have made a mistake.",
     "If he had understood the instructions"),
    ("After the show, they introduced us to the leading actor.",
     "we", "After the show, {} to the leading actor.",
     "we were introduced"),
    ("Would you like to have some ice cream?",
     "feel", "Do you {} some ice cream?",
     "feel like having"),
    ("We have arranged to meet in the city centre at 5 p.m.",
     "are", "We {} 5 p.m. in the city centre.",
     "are meeting at"),
    ("When I was younger, I dyed my hair green every summer.",
     "used", "When I was younger, I {} green.",
     "used to dye my hair"),
    ("She hadn't eaten snails before.",
     "first", "It was the {} snails.",
     "first time she had eaten"),
    ("After he reached the foot of the mountain, he realised that he didn't "
     "have his mobile.",
     "had", "He {} the foot of the mountain when he realised he didn't have "
     "his mobile.",
     "had reached"),
    ("Jack collected his diploma and then we left the ceremony.",
     "until", "We didn't leave the ceremony {} his diploma.",
     "until Jack collected / until Jack had collected"),
    ("Mary and John are both 15 years old.",
     "same", "Mary {} John.",
     "is the same age as"),
    ("Take your umbrella, Susie, because it might rain in the evening.",
     "case", "Take your umbrella, Susie, {} in the evening.",
     "in case it rains"),
    ("Although she tries hard, she never manages to finish marathons.",
     "matter", "She never manages to finish marathons {} she tries.",
     "no matter how hard"),
    ("You will never lose weight if you don't exercise more regularly.",
     "unless", "You won't lose weight {} more regularly.",
     "unless you exercise"),
]

A_CULTURE = [
    ("What are the national symbols of Wales?",
     ["daffodil and shamrock", "daffodil and rose", "daffodil and leek",
      "daffodil and thistle"], "c"),
    ("What is the protagonist's name in Charles Dickens' Christmas Carol?",
     ["Ebenezer Scrooge", "Martin Chuzzlewit", "David Copperfield", "Alfi"],
     "a"),
    ("Which of the following novels was not authored by Jane Austen?",
     ["Pride and Prejudice", "Northanger Abbey", "Emma", "Jane Eyre"], "d"),
    ("What is the nickname often used to refer to the group of ravens that "
     "reside at the Tower of London due to an ancient superstition?",
     ["The Crown's Crows", "The Tower's Terrors", "The Monarch's Magpies",
      "The Guardians of the Tower"], "d"),
    ("What is the name of the circular space which stands at the heart of the "
     "British Museum, in the centre of the Great Court?",
     ["The Roundhouse", "The Oval Office", "The Circular Quay",
      "The Reading Room"], "d"),
    ("What happened to the original Globe Theatre in 1613?",
     ["It was destroyed by fire during a performance of Henry VIII.",
      "It was dismantled and moved to a different location.",
      "It was sold to a rival theatre company.",
      "It was abandoned and fell into disrepair."], "a"),
    ("What is the significance of the Magna Carta?",
     ["It established the Church of England as the official state religion.",
      "It was a treaty that ended the Hundred Years' War.",
      "It was a document in English constitutional history, limiting the "
      "powers of the monarch.",
      "It granted voting rights to common citizens in medieval England."],
     "c"),
    ("What was the primary purpose of the Act of Supremacy passed by the "
     "English Parliament in 1534?",
     ["To grant religious freedom to all citizens.",
      "To establish the Church of England and declare the monarch as its "
      "supreme head.",
      "To abolish the monarchy in England.",
      "To ratify the Magna Carta."], "b"),
    ("What is the nickname often used to refer to Queen Elizabeth I of "
     "England due to her long and successful reign?",
     ['"Bloody Mary"', '"Gloriana"', '"The Iron Lady"', '"The Tudor Rose"'],
     "b"),
    ("Which World War II squadron, composed mainly of Polish pilots, was one "
     "of the most successful during the Battle of Britain?",
     ["The Royal Navy Squadron", "The Spitfire Squadron", "The 303 Squadron",
      "The Eagle Squadron"], "c"),
]

A_EXERCISES = paper_exercises("", "", SRC_A, A_MC, A_HANGMAN, A_FORMATION,
                              A_TRANSFORM, A_CULTURE)


# --------------------------------------------------------------------------
# What ojaj_new.py consumes
# --------------------------------------------------------------------------

GROUPS = [
    ("Etap szkolny 2023/24", A_EXERCISES),
]
