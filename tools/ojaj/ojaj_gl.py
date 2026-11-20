#!/usr/bin/env python3
"""The third batch of OJAJ material: the two gramatyczno-leksykalny papers.

Imported by tools/ojaj/ojaj_new.py, which appends these groups to the ones the second
batch defines; tools/ojaj/gen_ojaj.py then writes them with no further edit.

Where the text came from
------------------------
Unlike every other paper in this app, these two lose whole words in extraction
-- their fonts are subsetted with incomplete character maps, so pdftotext drops
runs of characters rather than just the Polish diacritics. Every item below was
read off page images instead:

    pdftoppm -png -r 120 tools/ojaj/pdfs/e1gl_key.pdf tools/ojaj/pdfs/e1gl

Each paper is published twice, with and without the key, and both versions are
needed. The key version marks its answers (bold in etap I tasks 1, 2, 5, 6, 7
and in all of etap II; italic in etap I task 4; a bracketed letter in etap I
tasks 3 and 8) but prints them in place of the blanks, so it does not show
where the blanks are, and it drops the etap I word bank and both papers' base
words. The no-key version carries all of those. Where the two disagree the
no-key version wins: the key version bolds "were you doing" as well as "rang"
in etap I task 5 item 1, and numbers etap II task 6 from 2 to 11 where the
paper numbers it 1 to 10.

Repairs
-------
Two, both recorded at their item:
  - etap II task 4 item 10 prints "you tea" for "your tea";
  - the etap II picture task's photo is a licensed stock image the app does not
    reproduce, so its instruction says what the photo shows instead. All five
    blanks are grammar or vocabulary and stay answerable without it.

Left as printed: etap I task 6 item 4 says "thanks" twice ("How is your mother?
Thanks, she's ....., thanks."). It reads oddly but the answer does not depend
on it.
"""

SRC = "https://ojaj.wsjo.pl/wp-content/uploads"
E1GL_SRC = f"{SRC}/2025/06/Test-gramatyczno-leksykalny-etap-I.pdf"
E2GL_SRC = f"{SRC}/2025/06/Test-gramatyczno-leksykalny-etap-II.pdf"

GAP = "_________"          # exactly nine, which is what GrammarGaps splits on
BLANK = "__________"       # word_formation splits on any run of two or more


# --------------------------------------------------------------------------
# Builders. One exercise per task on the paper, since each task is already one
# coherent type; the only task split in two is the fifteen-item etap II
# vocabulary block, which is longer than anything else here.
# --------------------------------------------------------------------------

def _exercise(ex_id, title, source, task):
    return ex_id, {
        "title": title,
        "type": "practice",
        "source": source,
        "tasks": [task],
    }


def mc_exercise(ex_id, title, instruction, rows, source, start=1):
    """rows: (stem, [options without letters], answer letter)."""
    items = []
    for i, (stem, opts, answer) in enumerate(rows, start=start):
        letters = "ABCD"[: len(opts)]
        items.append({
            "id": f"1.{i}",
            "stem": stem,
            "options": [f"{l}) {o}" for l, o in zip(letters, opts)],
            "answer": answer,
        })
    return _exercise(ex_id, title, source, {
        "id": "1",
        "type": "multiple_choice",
        "points": len(items),
        "instruction": instruction,
        "items": items,
    })


def matching_exercise(ex_id, title, instruction, statements, options, source):
    letters = [chr(ord("A") + i) for i in range(len(options))]
    return _exercise(ex_id, title, source, {
        "id": "1",
        "type": "matching",
        "points": len(statements),
        "instruction": instruction,
        "options": [{"letter": l, "text": t} for l, t in zip(letters, options)],
        "items": [
            {"id": f"1.{i}", "statement": s, "answer": a}
            for i, (s, a) in enumerate(statements, start=1)
        ],
    })


def formation_exercise(ex_id, title, instruction, rows, source):
    """rows: (sentence with a blank, BASE WORD, answer)."""
    return _exercise(ex_id, title, source, {
        "id": "1",
        "type": "word_formation",
        "points": len(rows),
        "instruction": instruction,
        "items": [
            {"id": f"1.{i}", "sentence": s, "wordBase": base, "answer": [a]}
            for i, (s, base, a) in enumerate(rows, start=1)
        ],
    })


def gaps_exercise(ex_id, title, instruction, rows, source):
    """rows: (context with one nine-underscore gap, answer string)."""
    return _exercise(ex_id, title, source, {
        "id": "1",
        "type": "grammar_gaps",
        "points": len(rows),
        "instruction": instruction,
        "items": [
            {"id": f"1.{i}", "context": c, "answer": a}
            for i, (c, a) in enumerate(rows, start=1)
        ],
    })


def spelling_exercise(ex_id, title, instruction, rows, source):
    """rows: (Polish prompt, letter pattern, answer)."""
    return _exercise(ex_id, title, source, {
        "id": "1",
        "type": "word_spelling",
        "points": len(rows),
        "instruction": instruction,
        "items": [
            {"id": f"1.{i}", "sentence": f"{pl} - {pattern}",
             "hint": pattern, "answer": [a]}
            for i, (pl, pattern, a) in enumerate(rows, start=1)
        ],
    })


# --------------------------------------------------------------------------
# Etap I
# --------------------------------------------------------------------------

E1_LETTER = (
    "Dear Max,\n"
    f"I'm writing to you to ask 1. {BLANK} advice. I have been 2. {BLANK} for a "
    f"job for 2 months but the only one I've found is 3. {BLANK} L.A. It will "
    f"mean moving far 4. {BLANK} here. I really don't know what to do, I need "
    f"5. {BLANK} advice from you as soon as possible.\n"
    "Please, help me.\n"
    "Ann"
)

E1_LIST = _exercise(
    "ojaj_e1gl_list", "OJAJ etap I gram.-leks.: list do kolegi", E1GL_SRC,
    {
        "id": "1",
        "type": "word_formation",
        "points": 5,
        "instruction": (
            "Uzupelnij list wyrazami z ramki. Kilka wyrazow jest dodatkowych i "
            "nie pasuje do zadnej luki."
        ),
        "wordBank": ["SEARCH", "FROM", "LOOKING", "ONE", "FOR",
                     "IN", "SOME", "AWAY", "ABOUT", "AN"],
        "text": E1_LETTER,
        "items": [
            {"id": "1.1", "answer": ["for"]},
            {"id": "1.2", "answer": ["looking"]},
            {"id": "1.3", "answer": ["in"]},
            {"id": "1.4", "answer": ["from"]},
            {"id": "1.5", "answer": ["some"]},
        ],
    },
)

# The prompt words keep their Polish diacritics: "laka" is a different word
# from "laka", so folding them would change what is being asked. The
# instructions stay ASCII, which is the convention these files follow.
E1_SPELLING = spelling_exercise(
    "ojaj_e1gl_slowka", "OJAJ etap I gram.-leks.: slowka po angielsku",
    "Podaj angielski odpowiednik podanego slowa. Kazda kreska odpowiada jednej "
    "literze, a podane litery stoja na swoich miejscach.",
    [
        ("fiołek", "V __ __ __ __ __", "violet"),
        ("stokrotka", "D __ __ __ Y", "daisy"),
        ("trawnik", "__ __ W __", "lawn"),
        ("łąka", "M __ __ __ __ __", "meadow"),
        ("widelec", "__ __ R __", "fork"),
    ],
    E1GL_SRC,
)

E1_HEADINGS = matching_exercise(
    "ojaj_e1gl_naglowki", "OJAJ etap I gram.-leks.: praca na lotnisku",
    "Do kazdego akapitu dopasuj wlasciwy naglowek (A-F). Jeden naglowek jest "
    "dodatkowy - dopasuj go do ostatniego wiersza.",
    [
        ("I deal with all kinds of things - including passenger complaints, VIP "
         "and celebrities visits, air conditioning failures and terminal staff "
         "contracts. You'll see me walking around the airport and talking to "
         "people on my mobile.", "E"),
        ("I have to be really fit doing this job, because I have to carry a lot "
         "of bags and suitcases every day and put them on the baggage trucks. I "
         "like people I work with, but I can't stand shift work - I hate "
         "working at nights.", "B"),
        ("There are many different problems I have to manage - ventilation, "
         "escalators, lifts - I get really busy sometimes. I don't fix it all "
         "by myself, of course - I have to manage a team of manual workers.",
         "D"),
        ("It's not as interesting or dangerous as people think. There are many "
         "rules and procedures I have to follow when we check people's "
         "documents and baggage. My work can be quite physical - sometimes I "
         "have to deal with passengers who are drunk or violent and that's not "
         "nice.", "C"),
        ("I work shifts, but it's ok with me. We often get super busy, "
         "especially when there's a delay and many hungry and thirsty people "
         "come over to kill time and their hunger.", "F"),
        ("This heading does not match any of the paragraphs.", "A"),
    ],
    ["Cleaner", "Baggage handler", "Security guard", "Engineer",
     "Terminal duty manager", "Waiter"],
    E1GL_SRC,
)

E1_REPLIES = mc_exercise(
    "ojaj_e1gl_reakcje", "OJAJ etap I gram.-leks.: reakcje jezykowe",
    "Wybierz poprawna odpowiedz do zasugerowanej sytuacji.",
    [
        ("Przepros nauczyciela za spoznienie.",
         ["I'm sorry for I'm late.", "I'm sorry I'm late.",
          "I'm sorry to being late."], "B"),
        ("Jestes z rodzicami u znajomych. Zasugeruj powrot do domu.",
         ["Shall we go home now?", "Can I ask you to me to go home now?",
          "Do you think we must to go home now?"], "A"),
        ("Dzwonisz do kolegi. Odbiera jego mama - jak zaczniesz rozmowe?",
         ["Could I speak to Daniel, please?", "Ask Daniel to speak to me.",
          "I want Daniel to speak to me."], "A"),
        ("Chcesz dojsc na najblizszy przystanek autobusowy. Spytaj o droge.",
         ["Can you tell me the nearest bus?",
          "Can you tell me how to get to the nearest bus?",
          "Where I go to the nearest bus?"], "B"),
        ("Chcesz powiedziec, ze masz dobry kontakt ze swoja siostra.",
         ["I get up well with my sister.", "I get in well with my sister.",
          "I get on well with my sister."], "C"),
        ("Jestes w kawiarni. Chcesz powiedziec kolezance, ze to ty placisz "
         "rachunek.",
         ["It's on me.", "It's for me.", "It's by me."], "A"),
    ],
    E1GL_SRC,
)

E1_VERBS = gaps_exercise(
    "ojaj_e1gl_czasowniki", "OJAJ etap I gram.-leks.: formy czasownika",
    "Uzupelnij zdania poprawnymi formami czasownikow podanych w nawiasach. "
    "Uzywaj pelnych form, np. does not zamiast doesn't.",
    [
        (f"What were you doing when the boss {GAP} you at noon? (ring)",
         "rang"),
        (f"When we got to the party, everybody {GAP} and the place was "
         "completely quiet. (already leave)", "had already left"),
        (f"I don't know, why he {GAP} - it's so simple! (not understand)",
         "does not understand"),
        (f"{GAP} Polish in our Spanish class is strictly forbidden. (speak)",
         "Speaking"),
        (f"I {GAP} 4 coffees today, that's enough, thanks. (already have)",
         "have already had"),
        (f"I didn't realize how difficult it is {GAP} in England. (drive)",
         "to drive"),
        (f"Karen hates it when her husband {GAP} in the shower. (whistle)",
         "whistles"),
        (f"She {GAP} the attic all morning and that's why she is so tired. "
         "(cleaning)", "has been cleaning"),
        (f"I can't give you the soup. It {GAP} . (still/prepare)",
         "is still being prepared"),
        (f"I'm sure I {GAP} decorating the Christmas tree by 5p.m. (finish)",
         "will have finished"),
        (f"More and more people {GAP} their lifestyles, e.g. a lot of my "
         "friends have stopped eating sweets. (change)", "are changing"),
        (f"I wish I {GAP} some rest just after I finished my exams - now I'm "
         "so tired! (have)", "had had"),
    ],
    E1GL_SRC,
)

E1_GRAMMAR = mc_exercise(
    "ojaj_e1gl_gramatyka", "OJAJ etap I gram.-leks.: gramatyka",
    "W kazdym zdaniu znajduje sie luka. Wybierz jedyna poprawna odpowiedz.",
    [
        (f"I have {GAP} good news for you!", ["the", "a", "some"], "C"),
        (f"Meet Tanya - she's my {GAP}.",
         ["brother's wife", "wife's brother", "wife of the brother"], "A"),
        (f"My best friend Tom is not as tall as {GAP}.", ["I", "me", "my"],
         "B"),
        (f"How is your mother? Thanks, she's {GAP}, thanks.",
         ["much better", "a lot good", "a lot of better"], "A"),
        (f"How much coffee {GAP} every day?",
         ["he drinks", "he drink", "does he drink"], "C"),
        (f"Have you finished doing the research {GAP}?",
         ["yet", "still", "so far"], "A"),
        (f"When she grows up she wants {GAP} a ballet dancer.",
         ["become", "becoming", "to become"], "C"),
        (f"That new teacher of yours is so funny! He always makes {GAP}.",
         ["me laugh", "me to laugh", "my laughing"], "A"),
        (f"When he realized I {GAP} at him, he {GAP}.",
         ["looked, turned away", "was looking, was turning away",
          "was looking, turned away"], "C"),
        (f"{GAP} men escaped from {GAP} yesterday after overpowering the guard "
         "and using dynamite to destroy the wall.",
         ["A few, prison", "Few, the prison", "A few, the prison"], "A"),
    ],
    E1GL_SRC,
)

E1_FORMATION = formation_exercise(
    "ojaj_e1gl_slowotworstwo", "OJAJ etap I gram.-leks.: slowotworstwo",
    "Wstaw wyraz podany wielkimi literami w odpowiedniej formie gramatycznej, "
    "np. BIG - bigger, WATCH - watched, BEAUTY - beautiful.",
    [
        (f"{BLANK} speaking, I don't believe any of his promises.",
         "HONEST", "Honestly"),
        (f"This film is really violent, it's not {BLANK} for children.",
         "SUIT", "suitable"),
        (f"Three {BLANK} paintings were stolen from The National Gallery "
         "yesterday.", "PRICE", "priceless"),
        (f"I don't really like girls with short hair, I prefer medium {BLANK} "
         "hair.", "LONG", "length"),
        (f"He grew up without parents, it was a difficult {BLANK}.",
         "CHILD", "childhood"),
        (f"My cousin Laura is really good at {BLANK}.", "SING", "singing"),
        (f"Our youngest son is in hospital, so we've had some {BLANK} nights "
         "recently.", "SLEEP", "sleepless"),
        (f"Would you believe that he's already had 5 {BLANK}?", "WIFE",
         "wives"),
        (f"It's {BLANK} outside, you'd better put on your scarf and gloves.",
         "FREEZE", "freezing"),
        (f"I can't stand this {BLANK}, 42 degrees is too much for me.",
         "HOT", "heat"),
    ],
    E1GL_SRC,
)

E1_ANSWERS = matching_exercise(
    "ojaj_e1gl_odpowiedzi", "OJAJ etap I gram.-leks.: pytania i odpowiedzi",
    "Przyporzadkuj do kazdego pytania jedna z podanych odpowiedzi (A-F). Jedna "
    "odpowiedz jest dodatkowa - dopasuj ja do ostatniego wiersza.",
    [
        ("How much was the coat?", "B"),
        ("Are you enjoying yourself?", "E"),
        ("Can I try on this dress?", "D"),
        ("Do you like my new shoes?", "F"),
        ("How was the party?", "A"),
        ("This answer does not match any of the questions.", "C"),
    ],
    ["It was fantastic!", "Half price, can you believe it?",
     "I bought it yesterday.", "Of course, changing rooms are over there.",
     "Not really, I'm bored.", "Yes, are they Italian?"],
    E1GL_SRC,
)

E1GL_EXERCISES = [
    E1_LIST, E1_SPELLING, E1_HEADINGS, E1_REPLIES,
    E1_VERBS, E1_GRAMMAR, E1_FORMATION, E1_ANSWERS,
]


# --------------------------------------------------------------------------
# Etap II
# --------------------------------------------------------------------------

E2_PARK_TEXT = (
    "Come face to face with life size dinosaurs both great and small lurking "
    "in the woods on our Trail. Help our ranger discover how many T-Rex roam "
    "the woodland, using our radio and lookout towers to accomplish your "
    "mission. Pretending to be an archaeologist with brush in hand, enjoy "
    "unearthing the dinosaur fossil and discover which dinosaur you think it "
    "is. Have fun climbing, sliding, swinging and scrambling in our fantastic "
    "adventure play area set in parkland. There's plenty for all ages "
    "including our Tiny 'Terror'saurs for the under 5's. For a small "
    "additional charge, climb aboard and get close to our deer herd on our "
    "fascinating guided safari (subject to availability)."
)

E2_PARK = _exercise(
    "ojaj_e2gl_dinozaury", "OJAJ etap II gram.-leks.: park dinozaurow",
    E2GL_SRC,
    {
        "id": "1",
        "type": "true_false_ni",
        "points": 5,
        "instruction": (
            "Przeczytaj reklame parku dinozaurow. Zdecyduj, czy ponizsze zdania "
            "sa prawdziwe (T) czy falszywe (F)."
        ),
        # The paper offers only T and F; the renderer shows a third column
        # unless the task says which options it has.
        "options": ["T", "F"],
        "title": "DINOSAUR PARK - A MONSTER DAY OUT",
        "text": E2_PARK_TEXT,
        "items": [
            {"id": "1.1",
             "statement": "The Dinosaur Park is only for children above 5 "
                          "years of age.", "answer": "F"},
            {"id": "1.2",
             "statement": "There are a lot of activities and tasks for children "
                          "to accomplish.", "answer": "T"},
            {"id": "1.3",
             "statement": "There is a special area with a playground just "
                          "outside the park.", "answer": "F"},
            {"id": "1.4",
             "statement": "You can go on a guided safari and see a herd of deer "
                          "for free.", "answer": "F"},
            {"id": "1.5",
             "statement": "The guided safari may not be available if there are "
                          "too many people signing up for this activity.",
             "answer": "T"},
        ],
    },
)

E2_CLIMATE_TEXT = (
    "The world's top scientists have concluded that our climate is changing "
    "and they have issued urgent warnings about our future we can't afford to "
    "ignore. The IPCC (Intergovernmental Panel on Climate Change) reports "
    "leave no room for doubt: global warming is a fact. And human activity "
    "including the burning of fossil fuels, industrial emissions, and "
    "deforestation are the main cause of climate change and its most dangerous "
    "side effects. The dramatic rise in greenhouse gases over the last 250 "
    "years, particularly carbon dioxide, has caused temperatures to rise "
    "across the globe and this warming is projected to accelerate at an "
    "alarming and dangerous pace. Science is a powerful witness. Our world is "
    "undergoing a dramatic transformation. Dangerous atmospheric changes "
    "already observed and measured will continue for decades.\n\n"
    "A fragment of \"A Way Forward: Facing Climate Change\" - a video produced "
    "by the National Geographic Society."
)

E2_CLIMATE_ID, E2_CLIMATE_EX = mc_exercise(
    "ojaj_e2gl_klimat", "OJAJ etap II gram.-leks.: zmiany klimatu",
    "Przeczytaj tekst, a nastepnie wybierz poprawna odpowiedz.",
    [
        ("According to the article the warnings presented by top scientists:",
         ["are exaggerated.", "should be taken seriously.",
          "have been misinterpreted by the media."], "B"),
        ("Climate change has been caused mainly by:",
         ["people's actions.", "Intergovernmental Panel on Climate Change.",
          "the existence of too many forests."], "A"),
        ("Increased production of greenhouse gasses has resulted in:",
         ["disappearance of fossil fuels.",
          "higher temperatures all over the world.",
          "local changes in the amount of carbon dioxide."], "B"),
        ("Scientists predict that the changes in atmosphere:",
         ["were most dangerous 250 years ago.",
          "will take place at a slower rate.",
          "will remain a major problem in years to come."], "C"),
    ],
    E2GL_SRC,
)
E2_CLIMATE_EX["tasks"][0]["text"] = E2_CLIMATE_TEXT
E2_CLIMATE = (E2_CLIMATE_ID, E2_CLIMATE_EX)

# The paper prints a licensed stock photo above this description. The app does
# not reproduce it, so the instruction says what it shows; all five blanks are
# grammar or vocabulary and are answerable from the description alone.
E2_PHOTO_TEXT = (
    f"In this photo there are two dogs and a girl playing. The dog 1. {GAP} "
    f"the girl is white and is wearing a blue 2. {GAP}. 3. {GAP} dog is black. "
    f"Neither dog 4. {GAP} standing on all four legs. The dogs are trying to "
    f"get the stick the girl is holding in 5. {GAP} hand."
)

E2_PHOTO_ID, E2_PHOTO_EX = mc_exercise(
    "ojaj_e2gl_opis", "OJAJ etap II gram.-leks.: opis zdjecia",
    "Ponizszy opis dotyczy zdjecia, na ktorym dziewczynka bawi sie z dwoma "
    "psami nad strumieniem. Uzupelnij opis tak, aby byl poprawny gramatycznie "
    "i logiczny.",
    [
        (f"The dog {GAP} the girl is white.", ["next", "close", "nearest"],
         "C"),
        (f"... and is wearing a blue {GAP}.", ["necklace", "leash", "collar"],
         "C"),
        (f"{GAP} dog is black.", ["The other", "Another", "A"], "A"),
        (f"Neither dog {GAP} standing on all four legs.",
         ["are", "has been", "is"], "C"),
        (f"The dogs are trying to get the stick the girl is holding in {GAP} "
         "hand.", ["the", "her", "a"], "B"),
    ],
    E2GL_SRC,
)
E2_PHOTO_EX["tasks"][0]["text"] = E2_PHOTO_TEXT
E2_PHOTO = (E2_PHOTO_ID, E2_PHOTO_EX)

E2_FORMATION = formation_exercise(
    "ojaj_e2gl_slowotworstwo", "OJAJ etap II gram.-leks.: slowotworstwo",
    "Wstaw wyraz podany wielkimi literami w odpowiedniej formie gramatycznej, "
    "np. BIG - bigger, WATCH - watched. Wyrazu nie mozna wstawic w formie "
    "niezmienionej.",
    [
        (f"I try to speak English fluently and build sentences that are "
         f"{BLANK} correct.", "GRAMMAR", "grammatically"),
        (f"The words in the dictionary are in the {BLANK} order.",
         "ALPHABET", "alphabetical"),
        (f"In {BLANK} with Tokyo, life in Warsaw and Prague is cheap.",
         "COMPARE", "comparison"),
        (f"The headmaster's speech was so long that I almost died of {BLANK}.",
         "BORE", "boredom"),
        (f"Paula and Jack have three children. Paula also has a daughter from "
         f"a previous {BLANK}.", "MARRY", "marriage"),
        (f"It is {BLANK} in Poland to sell alcohol to people under 18.",
         "LEGAL", "illegal"),
        (f"She didn't realize that {BLANK} films from the Internet is illegal.",
         "DOWNLOAD", "downloading"),
        (f"Mark is very {BLANK}. He wants to be the best at everything.",
         "COMPETE", "competitive"),
        (f"The last Batman movie was so {BLANK} - you knew exactly how it was "
         "going to end.", "PREDICT", "predictable"),
        # The paper prints "you tea"; the possessive is the obvious slip.
        (f"You can {BLANK} your tea with honey instead of sugar.",
         "SWEET", "sweeten"),
    ],
    E2GL_SRC,
)

E2_VOCAB_ROWS = [
    ("I've got a {gap} throat. I must have caught a cold.",
     ["red", "sore", "sour", "painful"], "B"),
    ("My father's second wife has got two daughters, so I have two {gap}.",
     ["foster sisters", "semi-sisters", "stepsisters", "in-law sisters"], "C"),
    ("Remember, never leave your wallet or bag {gap}. Someone may steal it.",
     ["open", "unattended", "obvious", "lonely"], "B"),
    ("I'm not good at taking decisions. I sometimes {gap} a coin.",
     ["drop", "throw", "spin", "toss"], "D"),
    ("WWW stands for {gap}.",
     ["World Wild Web", "Wide Worldly Web", "World Wide Web",
      "World Web of Words"], "C"),
    ("This light, {gap} blouse is perfect for the summer.",
     ["silk", "velvet", "woolen", "corduroy"], "A"),
    ("{gap} are large birds with beautiful tail feathers with eye-like "
     "patterns.", ["pigeons", "peacocks", "hedgehogs", "hares"], "B"),
    ("Being a doctor is a {gap} job.",
     ["profiting", "well-paid", "good-paid", "wealthy"], "B"),
    ("Tom and Ann don't love each other any more. They have just {gap}.",
     ["split off", "split with", "split up", "split on"], "C"),
    ("Water was {gap} slowly from the pipe.",
     ["filtering", "spilling", "gushing", "leaking"], "D"),
    ("Patrick lost his job so he couldn't pay off his {gap}. That's why the "
     "bank took his house.", ["mortgage", "salary", "taxes", "rates"], "A"),
    ("When the {gap} blew his whistle, he finally put an end to this "
     "embarrassing performance.", ["fan", "referee", "judge", "trainer"], "B"),
    ("The room in our hotel was really {gap}. It was the size of a shoebox.",
     ["filthy", "humongous", "tiny", "moody"], "C"),
    ("My dog is really wild, I must always keep it on a {gap}.",
     ["line", "cord", "rope", "lead"], "D"),
    ("I need to see the dentist, one of my {gap} has just fallen out.",
     ["tooth", "fillings", "holes", "gums"], "B"),
]

E2_VOCAB_ROWS = [(stem.format(gap=GAP), opts, key)
                 for stem, opts, key in E2_VOCAB_ROWS]

INSTR_E2_VOCAB = "W kazdym zdaniu znajduje sie luka. Wybierz poprawna odpowiedz."

E2_VOCAB_01 = mc_exercise(
    "ojaj_e2gl_slownictwo_01", "OJAJ etap II gram.-leks.: slownictwo (1)",
    INSTR_E2_VOCAB, E2_VOCAB_ROWS[:8], E2GL_SRC,
)
E2_VOCAB_02 = mc_exercise(
    "ojaj_e2gl_slownictwo_02", "OJAJ etap II gram.-leks.: slownictwo (2)",
    INSTR_E2_VOCAB, E2_VOCAB_ROWS[8:], E2GL_SRC, start=9,
)

E2_VERBS = gaps_exercise(
    "ojaj_e2gl_czasowniki", "OJAJ etap II gram.-leks.: formy czasownika",
    "Uzupelnij zdania poprawnymi formami czasownikow podanych w nawiasach. "
    "Uzywaj pelnych form, np. does not zamiast doesn't.",
    [
        (f"I'm used to {GAP} on the left because I've lived in England for "
         "some time. (drive)", "driving"),
        (f"She tried to be serious but she couldn't help {GAP}. (laugh)",
         "laughing"),
        (f"I wish I {GAP} something to read. It's so boring sitting in this "
         "waiting-room with nothing to do. (have)", "had"),
        (f"My parents never let me {GAP} after 10. (stay out)", "stay out"),
        (f"It's high time you {GAP} a job. I'm fed up with supporting you! "
         "(find)", "found"),
        (f"I had great difficulty {GAP} a good nanny for my two-year-old. "
         "(find)", "finding"),
        (f"What {GAP} like? Is he tall? (he/look)", "does he look"),
        (f"If I {GAP} about the meeting, I'd definitely have attended it. "
         "(inform)", "had been informed"),
        (f"It's time we stopped {GAP} about our next move. We need to have a "
         "clear plan. (think)", "to think"),
        (f"Byron is said to {GAP} on vinegar and potatoes. (live)",
         "have lived"),
    ],
    E2GL_SRC,
)

E2_GRAMMAR = mc_exercise(
    "ojaj_e2gl_gramatyka", "OJAJ etap II gram.-leks.: gramatyka",
    "W kazdym zdaniu sa dwie luki. Wybierz pare wyrazow, ktora pasuje do obu.",
    [
        (f"She broke her toe when she {GAP} {GAP} her bike.",
         ["had fallen / down", "was falling / of", "fell / off"], "C"),
        (f"There {GAP} furniture in this office, we need to remove {GAP}.",
         ["are too many / them", "is too many / some", "is too much / it"],
         "C"),
        (f"I have a dentist appointment {GAP}. Can you give me {GAP}?",
         ["tomorrow in the morning / the lift", "tomorrow morning / a lift",
          "in tomorrow's morning / the lift"], "B"),
        (f"As long as you {GAP} when you {GAP}, I will meet you at the "
         "airport.",
         ["let me know / will arrive", "will let me know / arrive",
          "let me know / arrive"], "A"),
        (f"I don't know this word. I {GAP} look it {GAP} in a dictionary.",
         ["need / on", "need to / on", "need to / up"], "C"),
    ],
    E2GL_SRC,
)

E2GL_EXERCISES = [
    E2_PARK, E2_CLIMATE, E2_PHOTO, E2_FORMATION,
    E2_VOCAB_01, E2_VOCAB_02, E2_VERBS, E2_GRAMMAR,
]


# --------------------------------------------------------------------------
# What ojaj_new.py consumes
# --------------------------------------------------------------------------

GROUPS = [
    ("Test gramatyczno-leksykalny, etap I", E1GL_EXERCISES),
    ("Test gramatyczno-leksykalny, etap II", E2GL_EXERCISES),
]
