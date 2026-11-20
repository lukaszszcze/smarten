"""Study page: negative-prefix (Negative prefixes). Data for tools/study/gen_study.py."""

KEY = "negative-prefix"
TITLE = "Negative prefixes"
HEAD_TITLE = "Negative Prefixes"
INDEX_TITLE = "Negative prefixes"
BODY = "wordpage"
EYEBROW = "Word formation and wisielec"
LEDE = ("un-, in-, im-, il-, ir- and dis- all turn a word into its opposite. Three of them "
        "are chosen by the first letter of the word, so they are easy. The choice between "
        "un-, in- and dis- has no rule that always works, so the lists below are the words to "
        "learn. And when the sentence means the opposite, do not leave the prefix off.")

MISTAKES_INTRO = ""
WIDE = False
MISTAKES = [
    {"wrong": "unaccessible", "right": "inaccessible", "why": "accessible takes in-."},
    {"wrong": "undistinguishable", "right": "indistinguishable",
     "why": "distinguishable takes in-."},
    {"wrong": "undispensable", "right": "indispensable", "why": "dispensable takes in-."},
    {"wrong": "unseparated", "right": "inseparable",
     "why": "separable takes in-; and the sentence needs -able: cannot be separated."},
    {"wrong": "deniable", "right": "undeniable",
     "why": "The sentence meant that nobody could deny it, so the prefix is needed."},
]

RULE_TITLE = "The rule"
RULE_HTML = ""
LEGEND = "The prefixes are in <b>green</b>."

GROUPS = [
    ("il-, im- and ir-: chosen by the first letter",
     "Before l write il-, before b, m and p write im-, before r write ir-. That is why these "
     "words have a double letter: il + legal = illegal.", [
         ("il- before l", [
             "legal > {il}legal", "logical > {il}logical", "literate > {il}literate",
             "legible > {il}legible", "legitimate > {il}legitimate",
         ]),
         ("im- before b, m and p", [
             "balance > {im}balance", "mature > {im}mature", "mortal > {im}mortal",
             "moral > {im}moral", "measurable > {im}measurable", "mobile > {im}mobile",
             "modest > {im}modest", "possible > {im}possible", "patient > {im}patient",
             "polite > {im}polite", "perfect > {im}perfect", "practical > {im}practical",
             "probable > {im}probable", "partial > {im}partial | fair to everyone",
             "personal > {im}personal", "pure > {im}pure", "proper > {im}proper",
             "patience > {im}patience", "passable > {im}passable",
         ]),
         ("ir- before r", [
             "regular > {ir}regular", "relevant > {ir}relevant",
             "responsible > {ir}responsible", "rational > {ir}rational",
             "replaceable > {ir}replaceable", "reversible > {ir}reversible",
             "respective > {ir}respective", "{ir}resistible",
             "repair > {ir}reparable | the base word changes too",
         ]),
     ]),
    ("in-",
     "in- goes with many longer words that came into English from Latin. They often end in "
     "-ible, -ent, -ant, -ate, -ive or -ion.", [
         (None, [
             "accessible > {in}accessible", "capable > {in}capable", "complete > {in}complete",
             "correct > {in}correct", "convenient > {in}convenient",
             "dependent > {in}dependent", "direct > {in}direct", "visible > {in}visible",
             "formal > {in}formal", "expensive > {in}expensive",
             "experienced > {in}experienced", "accurate > {in}accurate",
             "adequate > {in}adequate", "appropriate > {in}appropriate",
             "competent > {in}competent", "consistent > {in}consistent",
             "credible > {in}credible", "curable > {in}curable", "decisive > {in}decisive",
             "definite > {in}definite", "different > {in}different | not interested",
             "dispensable > {in}dispensable | very much needed",
             "distinguishable > {in}distinguishable", "effective > {in}effective",
             "efficient > {in}efficient", "{in}evitable", "finite > {in}finite",
             "sane > {in}sane", "secure > {in}secure", "sensitive > {in}sensitive",
             "separable > {in}separable", "significant > {in}significant",
             "sufficient > {in}sufficient", "tolerable > {in}tolerable",
             "tolerant > {in}tolerant", "considerate > {in}considerate",
             "hospitable > {in}hospitable", "humane > {in}humane", "ability > {in}ability",
             "active > {in}active", "attentive > {in}attentive",
             "comprehensible > {in}comprehensible", "conceivable > {in}conceivable",
             "destructible > {in}destructible", "excusable > {in}excusable",
             "explicable > {in}explicable", "frequent > {in}frequent",
             "justice > {in}justice", "equality > {in}equality", "edible > {in}edible",
             "famous > {in}famous | famous for something bad",
             "valuable > {in}valuable | extremely valuable",
         ]),
     ]),
    ("un-",
     "un- is the most common. It goes with ordinary English words, and nearly always with "
     "words ending in -ed and -ing: unexpected, unconvincing.", [
         ("Adjectives", [
             "happy > {un}happy", "able > {un}able", "aware > {un}aware",
             "believable > {un}believable", "comfortable > {un}comfortable",
             "common > {un}common", "conscious > {un}conscious", "employed > {un}employed",
             "expected > {un}expected", "fair > {un}fair", "familiar > {un}familiar",
             "fortunate > {un}fortunate", "forgettable > {un}forgettable",
             "friendly > {un}friendly", "healthy > {un}healthy", "important > {un}important",
             "kind > {un}kind", "known > {un}known", "likely > {un}likely", "lucky > {un}lucky",
             "necessary > {un}necessary", "pleasant > {un}pleasant", "popular > {un}popular",
             "predictable > {un}predictable", "recognisable > {un}recognisable",
             "reliable > {un}reliable", "safe > {un}safe", "successful > {un}successful",
             "tidy > {un}tidy", "usual > {un}usual", "{un}deniable",
             "even > {un}even", "acceptable > {un}acceptable",
             "avoidable > {un}avoidable", "bearable > {un}bearable", "certain > {un}certain",
             "convincing > {un}convincing", "decided > {un}decided", "equal > {un}equal",
             "exciting > {un}exciting", "fit > {un}fit", "foreseen > {un}foreseen",
             "grateful > {un}grateful", "helpful > {un}helpful",
             "inhabited > {un}inhabited | nobody lives there", "limited > {un}limited",
             "natural > {un}natural", "official > {un}official",
             "professional > {un}professional", "qualified > {un}qualified",
             "suitable > {un}suitable", "stable > {un}stable", "sure > {un}sure",
             "true > {un}true", "wise > {un}wise", "interested > {un}interested | bored",
             "available > {un}available", "attractive > {un}attractive",
             "balanced > {un}balanced",
         ]),
         ("Verbs: un- means doing the opposite", [
             "lock > {un}lock", "tie > {un}tie", "do > {un}do", "pack > {un}pack",
             "wrap > {un}wrap", "fold > {un}fold", "load > {un}load", "plug > {un}plug",
             "zip > {un}zip", "dress > {un}dress",
         ]),
     ]),
    ("dis-", "dis- goes with many verbs, and with some adjectives and nouns.", [
        (None, [
            "agree > {dis}agree", "approve > {dis}approve", "approval > {dis}approval",
            "honest > {dis}honest", "loyal > {dis}loyal", "obey > {dis}obey",
            "obedient > {dis}obedient", "like > {dis}like", "advantage > {dis}advantage",
            "comfort > {dis}comfort", "connect > {dis}connect", "continue > {dis}continue",
            "courage > {dis}courage", "honour > {dis}honour", "organised > {dis}organised",
            "order > {dis}order", "pleased > {dis}pleased", "qualify > {dis}qualify",
            "satisfied > {dis}satisfied", "similar > {dis}similar", "trust > {dis}trust",
            "ability > {dis}ability", "{dis}abled", "agreeable > {dis}agreeable",
            "belief > {dis}belief", "respect > {dis}respect", "respectful > {dis}respectful",
            "prove > {dis}prove",
        ]),
    ]),
    ("non- and mis-",
     "non- simply means not: non-stop, non-fiction. mis- means wrongly, not \"not\": to "
     "misunderstand is to understand wrongly.", [
         ("non-", ["{non}sense", "{non}-fiction", "{non}-smoker", "{non}-existent", "{non}-stop"]),
         ("mis-", [
             "understand > {mis}understand", "behave > {mis}behave", "spell > {mis}spell",
             "lead > {mis}lead", "use > {mis}use", "judge > {mis}judge",
             "interpret > {mis}interpret", "place > {mis}place", "print > {mis}print",
             "pronounce > {mis}pronounce",
         ]),
     ]),
]

WATCH = [
    "<b>inhabitable</b> means a place can be lived in; <b>uninhabitable</b> means it cannot.",
    "<b>invaluable</b> means extremely valuable, not without value.",
    "<b>infamous</b> means famous for something bad.",
    "<b>disinterested</b> means fair, not taking sides; <b>uninterested</b> means bored.",
    "<b>flammable</b> and <b>inflammable</b> both mean that something burns easily.",
    "<b>unable</b> and <b>inability</b> come from the same word, but take different prefixes. "
    "Learn each word on its own.",
]

CHECK_INTRO = ("Type the word made from the word in capitals, then press Check or Enter. The "
               "spelling has to be exact, as on the test.")
TYPED = [
    ("It is ___ (POLITE) to talk with your mouth full.", "impolite", "im- before p.", None),
    ("His plan was completely ___ (LOGIC): it could never work.", "illogical",
     "logic → logical → illogical: il- before l.", None),
    ("Leaving the door unlocked was very ___ (RESPONSIBLE) of you.", "irresponsible",
     "ir- before r.", None),
    ("The difference between the twins is almost ___ (VISIBLE).", "invisible",
     "in-, as in incredible.", None),
    ("I ___ (AGREE) with you: I think the film was great.", "disagree",
     "dis- with a verb.", None),
    ("The bus was late again, and the passengers were getting ___ (PATIENT).", "impatient",
     "im- before p.", None),
    ("Copying someone else's homework is ___ (HONEST).", "dishonest",
     "dis-, as in dislike.", None),
    ("Some of the dates in the article were ___ (ACCURATE).", "inaccurate",
     "in-, as in inaccessible.", None),
]
CHECK_TIP = 'All eight right? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_2324_slowotworstwo_01", "SmartEn: word formation, OJAJ 2023/24"),
    ("/ojaj/cwiczenia/ojaj_formation_001", "SmartEn: word formation, sample test"),
]

# Shown in each list's "Advanced" box: C1-C2, formal or rare words (judged by hand, 2026-10-25).
ADVANCED = """
    illiterate illegible illegitimate imbalance immeasurable immobile immodest improbable
    impartial impersonal impure improper impassable irrational irreplaceable irreversible
    irrespective irreparable inadequate incompetent inconsistent indefinite indifferent
    inevitable insufficient intolerable intolerant inhospitable inhumane inattentive
    incomprehensible inconceivable indestructible inexcusable inexplicable infrequent
    inedible infamous invaluable unforeseen uninhabited discontinue dishonour displeased
    dissimilar disagreeable disprove non-existent misjudge misinterpret misprint
    unconvincing unequal unexciting ungrateful unofficial unprofessional unqualified unstable unwise
    uninterested unbalanced unnatural unavoidable uneven unbearable undecided unfit unattractive
""".split()
