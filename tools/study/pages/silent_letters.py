"""Study page: silent-letters (Silent letters). Data for tools/study/gen_study.py."""

KEY = "silent-letters"
TITLE = "Silent letters"
HEAD_TITLE = "Silent Letters"
INDEX_TITLE = "Silent letters"
BODY = "wordpage"
EYEBROW = "Word formation and wisielec"
LEDE = ("Many English words have letters you do not hear: the k in knee, the b in doubt, the "
        "u in guess. They are left over from the way the words were said hundreds of years "
        "ago. Most of them follow a pattern, such as k before n or b after m, so learn them in "
        "groups.")

MISTAKES_INTRO = ""
WIDE = False
MISTAKES = [
    {"wrong": "garantee", "right": "guarantee", "why": "A silent u after g, as in guard and guess."},
    {"wrong": "concientious", "right": "conscientious",
     "why": "It comes from conscience: con-sci-en-tious."},
    {"wrong": "goverment", "right": "government", "why": "govern + ment: the n stays."},
    {"wrong": "enviroment", "right": "environment", "why": "environ + ment: the n stays."},
    {"wrong": "Febuary", "right": "February", "why": "Many people do not say the first r, but it is written."},
]

RULE_TITLE = "The rule"
RULE_HTML = """    <div class="fact">
      <p>A silent letter is often heard in a word from the same family. If you know the other word, you know the letter is there: sign &rarr; signature, resign &rarr; resignation, muscle &rarr; muscular, bomb &rarr; bombard, crumb &rarr; crumble, autumn &rarr; autumnal, condemn &rarr; condemnation, column &rarr; columnist, solemn &rarr; solemnity.</p>
    </div>"""
LEGEND = "The silent letters are in <b>green</b>."

GROUPS = [
    ("Silent consonants", None, [
        ("b after m, and before t", [
            "clim{b}", "com{b}", "bom{b}", "lam{b}", "lim{b}", "num{b}", "thum{b}", "tom{b}",
            "crum{b}", "plum{b}er", "de{b}t", "dou{b}t", "su{b}tle",
        ]),
        ("c after s", [
            "s{c}ience", "s{c}ene", "s{c}enery", "s{c}issors", "mus{c}le", "fas{c}inate",
            "des{c}end", "dis{c}ipline", "cons{c}ious", "cons{c}ience", "cons{c}ientious",
            "cres{c}ent", "s{c}ent", "adoles{c}ent",
        ]),
        ("d", ["We{d}nesday", "han{d}some", "han{d}kerchief", "san{d}wich"]),
        ("g before n", [
            "si{g}n", "desi{g}n", "forei{g}n", "rei{g}n", "campai{g}n", "{g}nome", "{g}naw",
            "champa{g}ne", "resi{g}n", "assi{g}n", "ali{g}n",
        ]),
        ("gh", [
            "hi{gh}", "li{gh}t", "ni{gh}t", "dau{gh}ter", "cau{gh}t", "thou{gh}t", "throu{gh}",
            "thou{gh}", "nei{gh}bour", "wei{gh}", "ei{gh}t", "hei{gh}t", "strai{gh}t",
            "fri{gh}ten", "nau{gh}ty", "bou{gh}t", "brou{gh}t", "ou{gh}t", "dou{gh}",
        ]),
        ("h", [
            "{h}onest", "{h}onour", "{h}our", "{h}eir", "g{h}ost", "r{h}yme", "r{h}inoceros",
            "ex{h}austed", "ex{h}ibition", "ve{h}icle", "shep{h}erd", "w{h}ether", "w{h}ile",
        ]),
        ("h after c, when ch sounds like k", [
            "sc{h}ool", "c{h}aracter", "c{h}emistry", "c{h}orus", "c{h}aos", "c{h}oir",
            "ec{h}o", "stomac{h}", "tec{h}nology", "mec{h}anic", "arc{h}itect", "orc{h}estra",
            "ac{h}e", "anc{h}or", "monarc{h}",
        ]),
        ("k before n", [
            "{k}nee", "{k}nife", "{k}nock", "{k}now", "{k}nowledge", "{k}not", "{k}nit",
            "{k}night", "{k}nuckle", "{k}neel", "{k}nob",
        ]),
        ("l", [
            "ca{l}m", "pa{l}m", "ha{l}f", "ca{l}f", "ta{l}k", "wa{l}k", "cha{l}k", "cou{l}d",
            "shou{l}d", "wou{l}d", "sa{l}mon", "yo{l}k", "fo{l}k",
        ]),
        ("n after m", ["autum{n}", "colum{n}", "condem{n}", "solem{n}", "hym{n}"]),
        ("n and r you hardly hear", [
            "gover{n}ment", "enviro{n}ment", "Feb{r}uary", "lib{r}ary", "su{r}prise",
        ]),
        ("p", [
            "{p}sychology", "{p}sychologist", "recei{p}t", "cu{p}board", "ras{p}berry",
            "{p}neumonia",
        ]),
        ("s", ["i{s}land", "i{s}le", "ai{s}le"]),
        ("t", [
            "lis{t}en", "cas{t}le", "whis{t}le", "fas{t}en", "of{t}en", "Chris{t}mas",
            "mor{t}gage", "balle{t}", "sof{t}en", "glis{t}en", "has{t}en", "mois{t}en",
            "bus{t}le", "hus{t}le", "this{t}le", "apos{t}le",
        ]),
        ("w", [
            "{w}rite", "{w}rong", "{w}rap", "{w}rist", "{w}reck", "{w}rinkle", "{w}restle",
            "{w}reath", "play{w}right", "ans{w}er", "s{w}ord", "t{w}o", "{w}hole", "{w}ho",
            "{w}hom", "{w}hose",
        ]),
    ]),
    ("A silent u",
     "After g, a silent u keeps the g hard, as in guess (without it, you would read \"jess\"). "
     "At the end of a word, -gue and -que are said like g and k.", [
         ("u after g", [
             "g{u}arantee", "g{u}ess", "g{u}est", "g{u}ide", "g{u}ilty", "g{u}itar", "g{u}ard",
             "disg{u}ise", "leag{ue}", "catalog{ue}", "dialog{ue}", "colleag{ue}", "fatig{ue}",
             "intrig{ue}", "plag{ue}", "vag{ue}", "rog{ue}", "vog{ue}",
         ]),
         ("u after q", [
             "q{ueue}", "uniq{ue}", "antiq{ue}", "techniq{ue}", "cheq{ue}", "mosq{ue}",
             "pictures{que}",
         ]),
         ("u you do not hear in the middle", ["b{u}ild", "b{u}ilt", "bisc{u}it", "circ{u}it"]),
     ]),
]

WATCH = [
    "In cough, laugh, enough, rough and tough, gh is not silent: it sounds like f.",
    "<b>whose</b> (whose bag is this?) and <b>who's</b> (who is) sound the same.",
    "<b>knew</b> (from know) and <b>new</b> sound the same; so do <b>knight</b> and "
    "<b>night</b>, and <b>write</b> and <b>right</b>.",
    "The silent letters stay when an ending is added: knowledgeable, doubtful, listening, "
    "designer.",
]

CHECK_INTRO = ("Type the whole word, then press Check or Enter. The word must fit the letters "
               "given, as in wisielec. The spelling has to be exact, as on the test.")
TYPED = [
    ("My cousin wants to study ___ so that she can help people with their problems.",
     "psychology", "the p is silent: psy-cho-lo-gy.", "_ s y c h _ l _ g y"),
    ("The ___ rode a white horse into the castle.", "knight",
     "k is silent before n, and gh is silent too.", "_ n _ g h t"),
    ("I hit my ___ with the hammer, and now it really hurts.", "thumb",
     "b is silent after m.", "t h u _ _"),
    ("In ___ the leaves turn red and gold.", "autumn", "n is silent after m.", "a u t u _ _"),
    ("Our football team is top of the ___.", "league", "a silent -ue after g.", "l e a g _ _"),
    ("Only one ___ can park in front of the gate.", "vehicle", "the h is silent.", "v e _ i c l e"),
    ("After the long walk we were completely ___.", "exhausted",
     "ex-h-austed: the h is silent.", "e x _ a u s t e d"),
    ("I would love to learn a ___ language.", "foreign", "g is silent before n.", "f o r e i _ _"),
]
CHECK_TIP = 'All eight right? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_2324_wisielec_02", "SmartEn: wisielec, OJAJ 2023/24"),
    ("/ojaj/cwiczenia/ojaj_e3_wisielec_02", "SmartEn: wisielec, stage 3"),
]

# Shown in each list's "Advanced" box: C1-C2, formal or rare words (judged by hand, 2026-10-25).
ADVANCED = """
    limb numb subtle crescent scent adolescent reign gnome gnaw assign align dough heir knob
    condemn solemn hymn pneumonia isle aisle mortgage glisten hasten moisten bustle hustle
    wreath playwright fatigue intrigue rogue vogue picturesque
""".split()
