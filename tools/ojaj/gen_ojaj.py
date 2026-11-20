#!/usr/bin/env python3
"""Build the OJAJ data tree from the published papers.

OJAJ = Olimpiada Jezyka Angielskiego dla Juniorow (ojaj.wsjo.pl), a national
English olympiad for primary school, harder than the Mazowieckie kuratoryjny
competition the rest of this app covers (B2-C1+ against B1-C1).

Source PDFs (downloaded from ojaj.wsjo.pl/kompendium-26-27/):
  - OJAJ_202425_etap_szkolny1_testB.pdf + _klucz.pdf  -> the test
  - OJAJ-Przykladowy-test-*.pdf (4 type-specific samples, answers in the PDF
    itself) -> the practice exercises

The test and the exercises share no items, so a student never meets the same
question twice.

Run:  python3 tools/ojaj/gen_ojaj.py
Then: node tools/ojaj/val_ojaj.mjs && bash tools/ojaj/render_ojaj.sh &&
      python3 tools/ojaj/audit_ojaj.py

Converted in the second batch (see tools/ojaj/ojaj_new.py). Download with
`curl -sSL -o tools/ojaj/pdfs/<name>.pdf <url>`, prefixing every path with
https://ojaj.wsjo.pl/wp-content, then run tools/ojaj/ojaj_extract.py:

  klucz_2223_A  .../uploads/2025/09/KLUCZ_I-ETAP_-CZESC-I_TEST_GRUPA_A.pdf
  klucz_2223_B  .../uploads/2025/09/KLUCZ_I-ETAP_-CZESC-I_TEST_GRUPA_B.pdf
  e1c2_key      .../uploads/2025/06/etap-I-czesc-II-1.pdf
  e2c1_key      .../uploads/2025/06/etap-II-czesc-I.pdf
  e3z1_key      .../uploads/2025/06/Zestaw-I-z-kluczami.pdf

The four etap III "zestawy" (Zestaw-I/II/III-z-kluczami.pdf and etap-III.pdf)
turned out to be the same 75 items in four different orders -- their key sets
are byte-identical once sorted -- so only Zestaw I was converted.

Converted in the third batch (see tools/ojaj/ojaj_gl.py): the two
Test-gramatyczno-leksykalny papers, etap I and etap II. They lose whole words in
extraction, so every item was read off page images; both are published with and
without the key and both versions are needed, since the key version drops the
word bank and the base words while the no-key version drops the answers.

Converted in the fourth batch: the 2023/24 etap szkolny paper, read off page
images (tools/ojaj/ojaj_2324.py), and self-written UK-culture sets for the 2026/27
mind map (tools/ojaj/ojaj_uk.py).

Also written here, from tools/ojaj/ojaj_online.py: the vault (online/vault.json),
the own items the app puts each online test together from, the app's
rehearsals of etap I, czesc II. Their items are not from any paper;
ojaj_online.py holds and checks them, in batches of 45. The three fixed tests
the app served before 2026-10-25 (online/01-03.json) are no longer written;
their items are the vault's first three batches.

Still not usable:
  - the 2025/26 final (.../uploads/2026/04/OJAJ-Test-finalowy-2025_2026-Grupa-{A,B}.pdf)
    has no published answer key.
  - listening and the final's oral part have no material to work from at all.
"""

import json
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ojaj_new as NEW  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA = os.path.join(ROOT, "pub", "konkursy", "angielski", "data", "ojaj")


def write(path, obj):
    full = os.path.join(DATA, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"wrote {os.path.relpath(full, ROOT)}")


# --------------------------------------------------------------------------
# Test: 2024/2025, etap szkolny (czesc 1), wersja B
# 45 minutes, 45 points, 5 tasks. Instructions kept as printed on the paper.
# --------------------------------------------------------------------------

TASK_1 = {
    "id": "1",
    "type": "word_formation",
    "points": 10,
    "instruction": (
        "W każdą z luk wpisz odpowiednie słowo przekształcając wyraz podany na końcu "
        "zdania drukowanymi literami. Wymagana jest pełna poprawność gramatyczna "
        "i ortograficzna wpisywanych słów.\n\n"
        "Przykład: The __________ (SERVE) in this restaurant was absolutely appalling. "
        "— prawidłowa odpowiedź: SERVICE"
    ),
    "items": [
        {
            "id": "1.1",
            "sentence": "He showed __________ for the warning signs and continued hiking up the mountain despite the approaching storm.",
            "wordBase": "REGARD",
            "answer": ["disregard"],
        },
        {
            "id": "1.2",
            "sentence": "The factory workers complained that their tasks were too __________, doing the same thing over and over again every day.",
            "wordBase": "REPEAT",
            "answer": ["repetitive"],
        },
        {
            "id": "1.3",
            "sentence": "The results of the experiment were __________ successful, showing no errors in any of the trials.",
            "wordBase": "QUESTION",
            "answer": ["unquestionably"],
        },
        {
            "id": "1.4",
            "sentence": "They've put forward a number of __________ to the problem we're currently facing, but none of them is really satisfactory.",
            "wordBase": "SOLVE",
            "answer": ["solutions"],
        },
        {
            "id": "1.5",
            "sentence": "Being __________ wealthy, my uncle can purchase any car he desires.",
            "wordBase": "BELIEVE",
            "answer": ["unbelievably"],
        },
        {
            "id": "1.6",
            "sentence": "The __________ spent their first week of marriage exploring a charming seaside town on their honeymoon.",
            "wordBase": "WED",
            "answer": ["newlyweds"],
        },
        {
            "id": "1.7",
            "sentence": "As a __________ person, she often volunteers at the local shelter and regularly donates money to various causes.",
            "wordBase": "CHARITY",
            "answer": ["charitable"],
        },
        {
            "id": "1.8",
            "sentence": "The old lady's __________ was evident when she donated a substantial portion of her savings to support the local children's home.",
            "wordBase": "GENEROUS",
            "answer": ["generosity"],
        },
        {
            "id": "1.9",
            "sentence": "The noise from the construction site was loud, but with earplugs, it was __________ enough to focus on work.",
            "wordBase": "TOLERATE",
            "answer": ["tolerable"],
        },
        {
            "id": "1.10",
            "sentence": "As a child, she spent hours creating adventures with her __________ friend, who always helped her explore new worlds.",
            "wordBase": "IMAGINE",
            "answer": ["imaginary"],
        },
    ],
}

TASK_2 = {
    "id": "2",
    "type": "word_spelling",
    "points": 10,
    "instruction": (
        "Wpisz słowo poprawnie uzupełniające każde ze zdań. Liczba kreseczek odpowiada "
        "liczbie liter w słowie. Wymagana jest pełna poprawność gramatyczna "
        "i ortograficzna wpisywanych słów.\n\n"
        "Przykład: She asked for a(n) __ __ e __ __ __ i __ (8) type of flower for her "
        "bouquet. — prawidłowa odpowiedź: SPECIFIC"
    ),
    "items": [
        {
            "id": "2.1",
            "sentence": "When the device started overheating, he immediately u __ __ l __ __ g __ __ (9) it from the socket to prevent any potential damage.",
            "hint": "u __ __ l __ __ g __ __ (9)",
            "answer": ["unplugged"],
        },
        {
            "id": "2.2",
            "sentence": "The criminals threatened to harm the hostages if their demand for a hefty r __ __ __ o __ (6) was not met within 24 hours.",
            "hint": "r __ __ __ o __ (6)",
            "answer": ["ransom"],
        },
        {
            "id": "2.3",
            "sentence": "The roller coaster rapidly rushed d __ w __ __ __ r __ __ (9), causing everyone on board to shout with excitement.",
            "hint": "d __ w __ __ __ r __ __ (9)",
            "answer": ["downwards"],
        },
        {
            "id": "2.4",
            "sentence": "The book my teacher recommended turned out to be so t __ __ __ o __ __ (7) that I actually lost count how many times I fell asleep attempting to read it.",
            "hint": "t __ __ __ o __ __ (7)",
            "answer": ["tedious"],
        },
        {
            "id": "2.5",
            "sentence": "The mansion, f __ __ m __ __ l __ (8) owned by a famous artist, is now a popular museum showcasing his work.",
            "hint": "f __ __ m __ __ l __ (8)",
            "answer": ["formerly"],
        },
        {
            "id": "2.6",
            "sentence": "During the meeting, I had a sudden f __ a __ __ b __ __ __ (9) to my childhood, remembering how my father used to give similar advice.",
            "hint": "f __ a __ __ b __ __ __ (9)",
            "answer": ["flashback"],
        },
        {
            "id": "2.7",
            "sentence": "The soldiers were instructed to protect the c __ v __ __ __ a __ __ (9) during the conflict, ensuring their safety above all else.",
            "hint": "c __ v __ __ __ a __ __ (9)",
            "answer": ["civilians"],
        },
        {
            "id": "2.8",
            "sentence": "He showed up at the party in a c __ s __ __ __ (6) outfit, wearing jeans and a t-shirt, while everyone else was dressed formally.",
            "hint": "c __ s __ __ __ (6)",
            "answer": ["casual"],
        },
        {
            "id": "2.9",
            "sentence": "The actor's performance on stage was f __ a __ __ __ s __ (8), earning him a standing ovation from the audience.",
            "hint": "f __ a __ __ __ s __ (8)",
            "answer": ["flawless"],
        },
        {
            "id": "2.10",
            "sentence": "The heat during the summer was so intense that it became u __ b __ __ __ __ __ l __ (10), driving everyone indoors to seek relief.",
            "hint": "u __ b __ __ __ __ __ l __ (10)",
            "answer": ["unbearable"],
        },
    ],
}

# grammar_gaps is AI-graded. `answer` must be a STRING per gap (an array is read
# as one entry per gap), so the paper's alternative keys go in one string
# separated by "/", the way the kuratoryjny papers store theirs.
TASK_3 = {
    "id": "3",
    "type": "grammar_gaps",
    "points": 10,
    "instruction": (
        "Uzupełnij każde ze zdań wyrazami z nawiasów w odpowiedniej formie. Nie wolno "
        "zmieniać kolejności słów w nawiasie, natomiast w niektórych przypadkach należy "
        "dodać brakujące słowo lub słowa, tak aby zdania były poprawne i logiczne. "
        "Wymagana jest pełna poprawność gramatyczna i ortograficzna wpisywanych słów. "
        "Każde rozwiązanie ma od 3 do 6 słów. Formy skrócone typu: don't, isn't, that's "
        "etc. są liczone jako jedno słowo.\n\n"
        "Przykład: She __________ (not / see) the film yet. — prawidłowa odpowiedź: hasn't seen"
    ),
    "items": [
        {
            "id": "3.1",
            "context": "I have arranged with the shop that my new _________ (furniture / deliver) flat between 6 and 7 p.m. tonight. This way I don't need to take a day-off from work.",
            "answer": "furniture is being delivered to my",
        },
        {
            "id": "3.2",
            "context": "As I walked through the park, I _________ (see / child / play) joyfully on the swings, laughing at the top of their lungs.",
            "answer": "could see children playing / saw children playing",
        },
        {
            "id": "3.3",
            "context": "They will consider your application, _________ (provide / you / submit) all the required documents.",
            "answer": "provided that you submit / providing that you submit / provided you submit / providing you submit",
        },
        {
            "id": "3.4",
            "context": "This is _________ (five / time / I / be) to England and I still can't help being totally amazed by the beauty of this country.",
            "answer": "the fifth time I have ('ve) been",
        },
        {
            "id": "3.5",
            "context": "Hearing how unfairly my teacher criticized the project I presented yesterday _________ (make / I / think / change) my school.",
            "answer": "made me think of changing / made me think about changing / made me think I should change",
        },
        {
            "id": "3.6",
            "context": "A boy living next door _________ (rumor / steal) groceries from the corner shop for at least a month. The shop's owner is now determined to catch the suspect red-handed.",
            "answer": "is rumored to have been stealing / is rumoured to have been stealing",
        },
        {
            "id": "3.7",
            "context": "My sister won't listen to anybody's advice so it _________ (use / try) talk her out of consuming fast food.",
            "answer": "is no use trying to",
        },
        {
            "id": "3.8",
            "context": "If I were you, I would get aunt Betty _________ (organise / Sandra / father-in-law) farewell party because she has amazing organizational skills.",
            "answer": "to organise Sandra's father-in-law's / to organize Sandra's father-in-law's",
        },
        {
            "id": "3.9",
            "context": "The day Ben started working in the same office as me I realized we _________ (already / bump) each other several times in the local gym.",
            "answer": "had already bumped into",
        },
        {
            "id": "3.10",
            "context": "I'd rather you _________ (bring / girlfriend) to my party. On top of looking totally bored all the time, she had the guts to criticize the food and the music.",
            "answer": "hadn't brought your girlfriend / had not brought your girlfriend",
        },
    ],
}

TASK_4 = {
    "id": "4",
    "type": "multiple_choice",
    "points": 10,
    "instruction": (
        "Uzupełnij lukę w każdym ze zdań, wybierając jedną poprawną odpowiedź "
        "z zaproponowanych możliwości A) – D)."
    ),
    "items": [
        {
            "id": "4.1",
            "stem": "Your clothes are filthy! As soon as you __________ home, throw them all into the laundry.",
            "options": ["A) will have arrived", "B) will arrive", "C) arrived", "D) arrive"],
            "answer": "D",
        },
        {
            "id": "4.2",
            "stem": "__________ surprised the teacher the most was the top students' poor performance in the final exams.",
            "options": ["A) Which", "B) That", "C) What", "D) Who"],
            "answer": "C",
        },
        {
            "id": "4.3",
            "stem": "Our parents agreed to __________ us repaint the walls of our room if we use neutral colours.",
            "options": ["A) allow", "B) have", "C) let", "D) permit"],
            "answer": "C",
        },
        {
            "id": "4.4",
            "stem": "The more she practised speaking in public, __________ she became, until eventually she found herself looking forward to giving presentations.",
            "options": ["A) the more nervous", "B) the less nervous", "C) the least nervous", "D) the most nervous"],
            "answer": "B",
        },
        {
            "id": "4.5",
            "stem": "Despite the heavy traffic, we __________ reach the airport on time.",
            "options": ["A) were able to", "B) could", "C) have been able to", "D) had been able to"],
            "answer": "A",
        },
        {
            "id": "4.6",
            "stem": "Citizens under the age of 18 are not __________ to vote in elections.",
            "options": ["A) accessible", "B) eligible", "C) advisable", "D) admissible"],
            "answer": "B",
        },
        {
            "id": "4.7",
            "stem": "Marrion had a __________ escape when she had a head-on collision with a truck.",
            "options": ["A) near", "B) close", "C) narrow", "D) tight"],
            "answer": "C",
        },
        {
            "id": "4.8",
            "stem": "Nancy was happy that she __________ a new mobile phone and was able to save a lot of money as she had won the latest model of the I-phone in a lottery.",
            "options": ["A) didn't need to buy", "B) needn't have bought", "C) couldn't have bought", "D) shouldn't have bought"],
            "answer": "A",
        },
        {
            "id": "4.9",
            "stem": "__________ details concerning the tournament's opening ceremony __________ so far.",
            "options": ["A) Only a few / weren't revealed", "B) Quite little / have revealed", "C) Only a little / haven't been revealed", "D) Very few / have been revealed"],
            "answer": "D",
        },
        {
            "id": "4.10",
            "stem": "When the president gave his statement he asked if there were any questions. Only one journalist __________ his hand.",
            "options": ["A) raised", "B) rose", "C) risen", "D) rise"],
            "answer": "A",
        },
    ],
}

TASK_5 = {
    "id": "5",
    "type": "knowledge_questions",
    "points": 5,
    "instruction": (
        "Odpowiedz na pytania wybierając jedną poprawną odpowiedź z zaproponowanych "
        "możliwości A) – D)."
    ),
    "items": [
        {
            "id": "5.1",
            "question": "Which of the statements about the Act of Supremacy is false?",
            "options": [
                "A. It was passed by the Parliament of England in 1543.",
                "B. The passing of the law marked the beginning of the English Reformation.",
                "C. One of the reasons for its passing was the king's personal interest.",
                "D. It gave the monarch an additional function he had not possessed earlier.",
            ],
            "answer": "A",
        },
        {
            "id": "5.2",
            "question": "What actions earned Queen Mary I of England the nickname 'Bloody Mary'?",
            "options": [
                "A. She cursed a lot and 'bloody' was her favorite swearword.",
                "B. She enjoyed watching bloody fights between her subjects.",
                "C. She suffered from a disease affecting her blood vessels.",
                "D. She gave an order to persecute Protestant heretics.",
            ],
            "answer": "D",
        },
        {
            "id": "5.3",
            "question": "Who is the patron saint of Wales?",
            "options": ["A. Saint Richard", "B. Saint George", "C. Saint David", "D. Saint Steven"],
            "answer": "C",
        },
        {
            "id": "5.4",
            "question": "Which of Henry VIII's wives outlived him?",
            "options": ["A. Catherine Howard", "B. Catherine Parr", "C. Anne of Cleves", "D. Catherine of Aragon"],
            "answer": "B",
        },
        {
            "id": "5.5",
            "question": "How many crosses does the Union Jack include?",
            "options": ["A. one", "B. two", "C. three", "D. four"],
            "answer": "C",
        },
    ],
}

TEST_2425_SZKOLNY = {
    "competition": "ojaj",
    "year": "2024/2025",
    "stage": "szkolny",
    "part": "1",
    "variant": "B",
    "maxPoints": 45,
    "timeMinutes": 45,
    "source": "https://ojaj.wsjo.pl/wp-content/uploads/2025/10/OJAJ_202425_etap_szkolny1_testB.pdf",
    "tasks": [TASK_1, TASK_2, TASK_3, TASK_4, TASK_5],
}


# --------------------------------------------------------------------------
# Practice exercises, from the four type-specific sample papers OJAJ publishes.
# Instructions in ASCII, matching the rest of the practice content.
# --------------------------------------------------------------------------

EX_FORMATION = {
    "title": "OJAJ: Slowotworstwo (test przykladowy)",
    "type": "practice",
    "source": "https://ojaj.wsjo.pl/wp-content/uploads/2025/06/OJAJ-Przykladowy-test-—-slowotworstwo.pdf",
    "tasks": [{
        "id": "1",
        "type": "word_formation",
        "points": 10,
        "instruction": (
            "Dla kazdego ze zdan utworz slowo pochodne od slowa bazowego zapisanego "
            "wielkimi literami. Wymagana jest pelna poprawnosc ortograficzna."
        ),
        "items": [
            {"id": "1.1", "sentence": "He __________ ignored the speed limit sign and had to pay a huge fine.", "wordBase": "CARE", "answer": ["carelessly"]},
            {"id": "1.2", "sentence": "__________ twins have to share every aspect of their life, including working together.", "wordBase": "SEPARATE", "answer": ["inseparable"]},
            {"id": "1.3", "sentence": "__________, a natural response of your body to stress, is a feeling of fear or apprehension about future events.", "wordBase": "ANXIOUS", "answer": ["anxiety"]},
            {"id": "1.4", "sentence": "\"Not in a million years\" — the idiom is used to talk about something which is __________ to happen.", "wordBase": "LIKE", "answer": ["unlikely"]},
            {"id": "1.5", "sentence": "Children and teenagers have a natural __________ about things related to science.", "wordBase": "CURIOUS", "answer": ["curiosity"]},
            {"id": "1.6", "sentence": "An entirely vegan diet is claimed to be __________ better for the environment than the Mediterranean one.", "wordBase": "SIGNIFY", "answer": ["significantly"]},
            {"id": "1.7", "sentence": "What is the most __________ building you have ever visited?", "wordBase": "IMPRESS", "answer": ["impressive"]},
            {"id": "1.8", "sentence": "Being a highly __________ person, she hardly ever gets bored.", "wordBase": "IMAGINE", "answer": ["imaginative"]},
            {"id": "1.9", "sentence": "Our calculations are based on the __________ that the prices will rise.", "wordBase": "ASSUME", "answer": ["assumption"]},
            {"id": "1.10", "sentence": "A serious __________ of cybersecurity experts might result in enormous losses of many companies.", "wordBase": "SHORT", "answer": ["shortage"]},
        ],
    }],
}

EX_SPELLING = {
    "title": "OJAJ: Wisielec (test przykladowy)",
    "type": "practice",
    "source": "https://ojaj.wsjo.pl/wp-content/uploads/2025/06/OJAJ-Przykladowy-test-—-wisielec.pdf",
    "tasks": [{
        "id": "1",
        "type": "word_spelling",
        "points": 10,
        "instruction": (
            "Przeczytaj zdania i uzupelnij brakujace litery w wyrazach. Liczba kreseczek "
            "odpowiada liczbie brakujacych liter. Wymagana jest pelna poprawnosc "
            "ortograficzna."
        ),
        # The paper prints the given letters in a grid of boxes, whose positions
        # plain-text extraction drops. They were recovered from the PDF's word
        # coordinates (a fixed-width column split into one cell per letter);
        # every recovered position matches the letter the answer has there.
        "items": [
            {"id": "1.1", "sentence": "__ L __ __ __ chocolate, also called dark chocolate, contains 65% to 99% cocoa mass and 1% to 40% sugar.", "hint": "__ L __ __ __", "answer": ["plain"]},
            {"id": "1.2", "sentence": "A gamer can be G __ __ __ D to the screen for hours, but gets tired of reading after a few minutes.", "hint": "G __ __ __ D", "answer": ["glued"]},
            {"id": "1.3", "sentence": "You must let your friends know that you can be __ __ L I __ __ upon not to gossip behind their backs.", "hint": "__ __ L I __ __", "answer": ["relied"]},
            {"id": "1.4", "sentence": "Decorators should never I __ __ I __ __ on throwing out everything the client has. Even when they are far from perfect, loved possessions add personality. (Billy Baldwin, a furniture advisor)", "hint": "I __ __ I __ __", "answer": ["insist"]},
            {"id": "1.5", "sentence": "If you have ever had food P __ __ S __ __ __ __ __ when eating out, any slightly undercooked meat will horrify you.", "hint": "P __ __ S __ __ __ __ __", "answer": ["poisoning"]},
            {"id": "1.6", "sentence": "She has D __ __ __ her hair blue. Her fans love her new look.", "hint": "D __ __ __", "answer": ["dyed"]},
            {"id": "1.7", "sentence": "Footballers or runners have human opponents. If you do an __ __ __ __ __ M __ sport, danger is your opponent.", "hint": "__ __ __ __ __ M __", "answer": ["extreme"]},
            {"id": "1.8", "sentence": "The mountain is definitely worth the long trek. The view from the __ __ M __ __ __ is breathtaking.", "hint": "__ __ M __ __ __", "answer": ["summit"]},
            {"id": "1.9", "sentence": "The model is an economical vehicle suitable for everyday C __ __ M __ __ __ __ S.", "hint": "C __ __ M __ __ __ __ S", "answer": ["commuters"]},
            {"id": "1.10", "sentence": "I overslept and __ __ __ S __ __ an important meeting because the battery on my mobile died.", "hint": "__ __ __ S __ __", "answer": ["missed"]},
        ],
    }],
}

EX_TRANSFORM = {
    "title": "OJAJ: Transformacje (test przykladowy)",
    "type": "practice",
    "source": "https://ojaj.wsjo.pl/wp-content/uploads/2025/06/OJAJ-Przykladowy-test-—-transformacje.pdf",
    "tasks": [{
        "id": "1",
        "type": "sentence_transformation",
        "points": 10,
        "instruction": (
            "Wykorzystujac slowa podane wielkimi literami, uzupelnij luki w zdaniach tak, "
            "aby zachowac sens zdania wyjsciowego. W kazda luke mozesz wpisac do 6 wyrazow "
            "lacznie z wyrazem juz podanym. Nie wolno zmieniac form podanych slow. Wymagana "
            "jest pelna poprawnosc gramatyczna i ortograficzna."
        ),
        "items": [
            {"id": "1.1", "original": "I could not leave the island because of the strike of air traffic controllers.", "keyword": "PREVENTED", "transformed": "I _________ the island because of the strike of air traffic controllers.", "answer": "was prevented from leaving"},
            {"id": "1.2", "original": "\"They stole my recipe,\" Ann said.", "keyword": "ACCUSED", "transformed": "Ann _________ recipe.", "answer": "accused them of stealing her"},
            {"id": "1.3", "original": "We will not get there in less than an hour.", "keyword": "LEAST", "transformed": "It _________ an hour to get there.", "answer": "will take us at least"},
            {"id": "1.4", "original": "Despite knowing the city quite well I got lost.", "keyword": "EVEN", "transformed": "_________ the city quite well, I got lost.", "answer": "Even though I knew"},
            {"id": "1.5", "original": "\"We can watch any of these films,\" she said.", "keyword": "MATTER", "transformed": "She told us that _________ which film we saw.", "answer": "it did not (didn't) matter to her"},
            {"id": "1.6", "original": "Whenever I hear this song, I remember our holiday by the lake.", "keyword": "REMINDS", "transformed": "Whenever I hear this song, _________ our holiday by the lake.", "answer": "it reminds me of"},
            {"id": "1.7", "original": "I watched it because you had told me it was really good.", "keyword": "IF", "transformed": "I _________ you had not told me it was really good.", "answer": "would not (wouldn't) have watched it if"},
            {"id": "1.8", "original": "He did not talk to anybody before he made the decision.", "keyword": "SHOULD", "transformed": "He _________ before he made the decision.", "answer": "should have talked to someone / should have talked to somebody"},
            {"id": "1.9", "original": "I cannot draw landscapes as well as they can.", "keyword": "BETTER", "transformed": "They are _________.", "answer": "better at drawing landscapes than me / better at drawing landscapes than I am"},
            {"id": "1.10", "original": "The information I got from them was so unclear that I had no idea what to do.", "keyword": "SUCH", "transformed": "They gave me _________ information that I had no idea what to do.", "answer": "such unclear"},
        ],
    }],
}

EX_CHOICE = {
    "title": "OJAJ: Test jednokrotnego wyboru (test przykladowy)",
    "type": "practice",
    "source": "https://ojaj.wsjo.pl/wp-content/uploads/2025/06/OJAJ-Przykladowy-test-—-test-jednokrotnego-wyboru.pdf",
    "tasks": [{
        "id": "1",
        "type": "multiple_choice",
        "points": 10,
        "instruction": (
            "W kazdym z ponizszych zdan znajduje sie luka. Wybierz odpowiedz, ktora "
            "najlepiej pasuje do kazdego ze zdan. Wez pod uwage zarowno znaczenie, "
            "jak i gramatyke."
        ),
        "items": [
            {"id": "1.1", "stem": "You are not going to school tomorrow if your temperature _________.", "options": ["A) will not have gone down", "B) will not go down", "C) has not gone down", "D) had not gone down"], "answer": "C"},
            {"id": "1.2", "stem": "If he was there yesterday, he _________ what they were talking about.", "options": ["A) might hear", "B) would heard", "C) might have heard", "D) might be hearing"], "answer": "C"},
            {"id": "1.3", "stem": "Let me know as soon as you _________ the book you ordered.", "options": ["A) will receive", "B) have received", "C) will be receiving", "D) received"], "answer": "B"},
            {"id": "1.4", "stem": "Since early morning, the police _________ all the people in our neighbourhood about the accident.", "options": ["A) are questioning", "B) is questioning", "C) has been questioning", "D) have been questioning"], "answer": "D"},
            {"id": "1.5", "stem": "She _________ since that accident.", "options": ["A) does not want to go cycling", "B) has not wanted to cycle", "C) does not want to cycle", "D) has not wanted cycling"], "answer": "B"},
            {"id": "1.6", "stem": "Hopes are _________ for those missing in a cruise ship disaster.", "options": ["A) darkening", "B) weakening", "C) fading", "D) losing"], "answer": "C"},
            {"id": "1.7", "stem": "More _________ controls of heavy metal emissions are coming into effect in the whole region.", "options": ["A) stringent", "B) blatant", "C) flagrant", "D) lurid"], "answer": "A"},
            {"id": "1.8", "stem": "In _________ cases, infection can result in death.", "options": ["A) reimbursed", "B) protuberant", "C) convex", "D) severe"], "answer": "D"},
            {"id": "1.9", "stem": "Apart from her most _________ friends, she avoided telling anyone that her father was a well-known CEO.", "options": ["A) close", "B) trustee", "C) intimate", "D) initiate"], "answer": "C"},
            {"id": "1.10", "stem": "Journalists face many attacks each year, ranging from online harassment to _________ murder.", "options": ["A) straight", "B) outright", "C) gasping", "D) freight"], "answer": "B"},
        ],
    }],
}

EXERCISES = [
    ("ojaj_formation_001", EX_FORMATION),
    ("ojaj_spelling_001", EX_SPELLING),
    ("ojaj_transform_001", EX_TRANSFORM),
    ("ojaj_choice_001", EX_CHOICE),
] + NEW.EXERCISES


def build_index():
    """The OJAJ index: the papers and the exercises. The online tests are not
    listed; the OJAJ page reads the vault (online/vault.json) itself."""
    exercises = []
    for ex_id, ex in EXERCISES:
        task = ex["tasks"][0]
        entry = {
            "id": ex_id,
            "title": ex["title"],
            "taskType": task["type"],
            "taskCount": len(ex["tasks"]),
            "points": sum(t["points"] for t in ex["tasks"]),
        }
        group = NEW.GROUP_OF.get(ex_id)
        if group:
            entry["group"] = group
        exercises.append(entry)

    return {
        "competition": {
            "id": "ojaj",
            "name": "Olimpiada Jezyka Angielskiego dla Juniorow",
            "shortName": "OJAJ",
            "level": "B2-C1+",
            "url": "https://ojaj.wsjo.pl/",
        },
        "editions": [
            NEW.EDITION_2223,
            {
                "year": "2024/2025",
                "yearPath": "2024-2025",
                "stages": [
                    {
                        "stage": "szkolny",
                        "part": "1",
                        "variant": "B",
                        "maxPoints": TEST_2425_SZKOLNY["maxPoints"],
                        "timeMinutes": TEST_2425_SZKOLNY["timeMinutes"],
                    }
                ],
            }
        ],
        "exercises": exercises,
    }


def check_spelling(task, where):
    """A hangman clue is wrong in a way nothing downstream catches: the answer
    still marks correct, but the pattern the student reads is unsolvable. So
    check every given letter against the answer, and the slot count against its
    length."""
    for item in task["items"]:
        answer = item["answer"][0].upper()
        pattern = item["hint"]
        # OJAJ prints the word's length after the boxes: "u __ __ l ... (9)".
        stated_len = re.search(r"\((\d+)\)\s*$", pattern)
        if stated_len:
            assert int(stated_len.group(1)) == len(answer), (
                f"{where} {item['id']}: says ({stated_len.group(1)}) letters, "
                f"{answer} has {len(answer)}"
            )
            pattern = pattern[: stated_len.start()]
        slots = pattern.split()
        assert len(slots) == len(answer), (
            f"{where} {item['id']}: pattern has {len(slots)} slots, "
            f"{answer} has {len(answer)} letters"
        )
        for i, (slot, letter) in enumerate(zip(slots, answer), start=1):
            if slot == "__":
                continue
            assert slot.upper() == letter, (
                f"{where} {item['id']}: pattern gives {slot} at position {i}, "
                f"{answer} has {letter}"
            )
        assert pattern in item["sentence"], (
            f"{where} {item['id']}: pattern not present in the sentence"
        )
        assert answer.lower() not in item["sentence"].lower(), (
            f"{where} {item['id']}: the sentence gives the answer away"
        )


def check_choice(task, where, letters=None):
    """Every option letter present once, and the key pointing at a real one.

    Papers vary between three and four options, so the default is the item's
    own count; pass `letters` where the count itself is what needs pinning."""
    for item in task["items"]:
        opts = item["options"]
        want = letters or "ABCD"[: len(opts)]
        assert len(opts) == len(want), f"{where} {item['id']}: {len(opts)} options"
        for opt, letter in zip(opts, want):
            assert opt.startswith(letter), f"{where} {item['id']}: {opt!r} is not {letter}"
        assert item["answer"] in want, f"{where} {item['id']}: key {item['answer']!r}"


def check_word_bank(task, where):
    """The word-bank shape has no sentence per item: the gaps live in one shared
    text and the answers have to come from the bank on offer. A gap count that
    does not match the item count shifts every later answer onto the wrong
    input, which renders fine and marks wrong."""
    gaps = re.findall(r"(?:(\d+)\.\s*)?_{2,}", task["text"])
    assert len(gaps) == len(task["items"]), (
        f"{where}: {len(gaps)} gaps in the text, {len(task['items'])} items"
    )
    bank = {w.lower() for w in task["wordBank"]}
    for item, label in zip(task["items"], gaps):
        # parseGapText maps the label "3" onto the item whose id ends ".3".
        assert not label or item["id"].endswith("." + label), (
            f"{where} {item['id']}: gap labelled {label}"
        )
        for answer in item["answer"]:
            assert answer.lower() in bank, (
                f"{where} {item['id']}: {answer!r} is not in the word bank"
            )
    assert len(bank) > len(task["items"]), (
        f"{where}: the bank has no extra words, so the last gap is free"
    )


def check_true_false(task, where):
    """The renderer shows T, F and NI unless the task lists its own options, so
    a paper that only offers T and F has to say so or the student is given a
    third column that is never the answer."""
    options = task.get("options") or ["T", "F", "NI"]
    for item in task["items"]:
        assert item["answer"] in options, (
            f"{where} {item['id']}: key {item['answer']!r} is not offered"
        )
    assert set(options) <= {"T", "F", "NI"}, f"{where}: options {options}"


def check_gaps(task, where):
    """GrammarGaps splits the context on a run of exactly nine underscores, and
    a string answer means one gap. Eight or ten underscores renders the
    sentence with its input stranded at the end and nothing errors."""
    for item in task["items"]:
        context = item["context"]
        assert context.count("_________") == 1, (
            f"{where} {item['id']}: {context.count('_________')} nine-underscore gaps"
        )
        assert not re.search(r"_{10,}", context), (
            f"{where} {item['id']}: a run of ten or more underscores"
        )
        assert isinstance(item["answer"], str), (
            f"{where} {item['id']}: a list answer means one answer per gap"
        )
        assert re.search(r"\([^)]+\)", context), (
            f"{where} {item['id']}: no bracketed prompt, so the gap is unanswerable"
        )


def check_matching(task, where):
    """Every key points at a real option, and no option is claimed twice."""
    letters = [o["letter"] for o in task["options"]]
    assert len(set(letters)) == len(letters), f"{where}: duplicate option letters"
    used = []
    for item in task["items"]:
        assert item["answer"] in letters, f"{where} {item['id']}: key {item['answer']!r}"
        used.append(item["answer"])
    assert len(set(used)) == len(used), f"{where}: an option is the answer twice"


def main():
    write("2024-2025/szkolny.json", TEST_2425_SZKOLNY)
    for path, test in NEW.TESTS:
        write(path, test)
    for ex_id, ex in EXERCISES:
        write(f"practice/{ex_id}.json", ex)
    # Imported here: ojaj_online borrows this module's choice and spelling
    # checks, so a top-level import would be circular. built_tests() checks
    # each batch against the papers and exercises just written;
    # check_own_exercises() holds the own wisielec exercises in the online
    # test's shape to a vault wisielec task's rules.
    import ojaj_online as ONLINE
    write("online/vault.json", ONLINE.build_vault(ONLINE.built_tests()))
    ONLINE.check_own_exercises()
    write("index.json", build_index())

    total = sum(t["points"] for t in TEST_2425_SZKOLNY["tasks"])
    assert total == TEST_2425_SZKOLNY["maxPoints"], f"{total} != maxPoints"
    for task in TEST_2425_SZKOLNY["tasks"]:
        assert len(task["items"]) == task["points"], f"task {task['id']}: items != points"
        ids = [it["id"] for it in task["items"]]
        assert len(set(ids)) == len(ids), f"task {task['id']}: duplicate item ids"

    check_spelling(TASK_2, "test 2024/25 zad. 2")
    check_choice(TASK_4, "test 2024/25 zad. 4", letters="ABCD")
    check_choice(TASK_5, "test 2024/25 zad. 5", letters="ABCD")
    check_spelling(EX_SPELLING["tasks"][0], "ojaj_spelling_001")
    check_choice(EX_CHOICE["tasks"][0], "ojaj_choice_001", letters="ABCD")

    # A word_formation answer that is already in its own sentence is a giveaway.
    # Whole words only: the etap III paper asks for "fame" in a sentence that
    # says "famous", which hints at the root without handing over the answer.
    formation = [("test zad. 1", TASK_1), ("ojaj_formation_001", EX_FORMATION["tasks"][0])]
    formation += [(ex_id, ex["tasks"][0]) for ex_id, ex in NEW.EXERCISES
                  if ex["tasks"][0]["type"] == "word_formation"]
    for label, task in formation:
        # A word-bank task shows every answer on purpose, and its answers are
        # function words that recur in any passage, so the check does not apply.
        if task.get("wordBank"):
            continue
        for item in task["items"]:
            assert not re.search(rf"\b{re.escape(item['answer'][0])}\b",
                                 item["sentence"], re.I), \
                f"{label} {item['id']}: the sentence gives the answer away"

    # knowledge_questions is scored A-D by letter, so the options must carry the
    # "A." prefix its renderer parses.
    for item in TASK_5["items"]:
        for opt, letter in zip(item["options"], "ABCD"):
            assert opt.startswith(letter + "."), f"zad. 5 {item['id']}: {opt!r}"

    # The second batch, checked the same way its shape allows.
    for path, test in NEW.TESTS:
        total_new = sum(t["points"] for t in test["tasks"])
        assert total_new == test["maxPoints"], f"{path}: {total_new} != maxPoints"
        for task in test["tasks"]:
            assert len(task["items"]) == task["points"], f"{path}: items != points"
            check_choice(task, path, letters="ABCD")

    for ex_id, ex in NEW.EXERCISES:
        task = ex["tasks"][0]
        assert len(task["items"]) == task["points"], f"{ex_id}: items != points"
        ids = [it["id"] for it in task["items"]]
        assert len(set(ids)) == len(ids), f"{ex_id}: duplicate item ids"
        if task["type"] == "multiple_choice":
            check_choice(task, ex_id)
        elif task["type"] == "word_spelling":
            check_spelling(task, ex_id)
        elif task["type"] == "matching":
            check_matching(task, ex_id)
        elif task["type"] == "true_false_ni":
            check_true_false(task, ex_id)
        elif task["type"] == "grammar_gaps":
            check_gaps(task, ex_id)
        elif task["type"] == "word_formation" and task.get("wordBank"):
            check_word_bank(task, ex_id)

    # No item may appear both as a test question and as practice.
    def stems(task):
        """The text a student reads, for whichever field this type puts it in."""
        out = set()
        for it in task["items"]:
            text = it.get("stem") or it.get("sentence") or it.get("statement")
            if text:
                out.add(text)
        return out

    test_stems = set()
    for _, test in [("", TEST_2425_SZKOLNY)] + NEW.TESTS:
        for task in test["tasks"]:
            test_stems |= stems(task)
    for ex_id, ex in EXERCISES:
        for task in ex["tasks"]:
            clash = stems(task) & test_stems
            assert not clash, f"{ex_id}: also a test question: {sorted(clash)[:1]}"

    keys = [it["answer"] for it in TASK_4["items"]]
    print(f"\ntest: {total} pkt across {len(TEST_2425_SZKOLNY['tasks'])} tasks, "
          f"{sum(len(t['items']) for t in TEST_2425_SZKOLNY['tasks'])} items")
    print(f"zad. 4 key spread: {''.join(keys)}")
    print(f"exercises: {len(EXERCISES)}, "
          f"{sum(len(e['tasks'][0]['items']) for _, e in EXERCISES)} items")
    print("all checks passed")


if __name__ == "__main__":
    main()
