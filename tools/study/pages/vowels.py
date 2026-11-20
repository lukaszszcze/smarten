"""Study page: vowels (Vowels you cannot hear clearly). Data for tools/study/gen_study.py."""

KEY = "vowels"
TITLE = "Vowels you cannot hear clearly"
HEAD_TITLE = "Vowels You Cannot Hear Clearly"
INDEX_TITLE = "Vowels you cannot hear clearly"
BODY = "wordpage"
EYEBROW = "Word formation and wisielec"
LEDE = ("In many English words a vowel is said so quickly that it sounds like a short "
        "\"uh\", whatever letter it is written with. In others, two vowel letters make one "
        "sound and you cannot hear which two. Saying these words aloud will not tell you how "
        "to spell them, so this page shows ways to work the spelling out, and lists the words "
        "to learn.")

MISTAKES_INTRO = ""
WIDE = False
MISTAKES = [
    {"wrong": "mischevious", "right": "mischievous",
     "why": "ie, as in chief. And there is no i before -ous."},
    {"wrong": "emberrassment", "right": "embarrassment", "why": "Think of a bar: em-BAR-rass-ment."},
    {"wrong": "percieving", "right": "perceiving", "why": "After c it is ei: receive, perceive."},
    {"wrong": "refrigirator", "right": "refrigerator", "why": "re-frig-er-a-tor: -er- in the middle."},
    {"wrong": "compertitive", "right": "competitive",
     "why": "Think of compete: com-pet-i-tive, with no r."},
]

RULE_TITLE = "The rule"
RULE_HTML = ""
LEGEND = "There is no single rule, but these six things help. The letters to watch are in <b>green</b>."

GROUPS = [
    ("ie or ei",
     "Write i before e (believe, chief) except after c (receive, ceiling). This works when you "
     "hear \"ee\". When you hear \"ay\" or \"eye\", it is usually ei (eight, height).", [
         ("ie", [
             "bel{ie}ve", "ach{ie}ve", "ch{ie}f", "f{ie}ld", "p{ie}ce", "n{ie}ce", "br{ie}f",
             "gr{ie}f", "rel{ie}f", "th{ie}f", "sh{ie}ld", "y{ie}ld", "pr{ie}st", "s{ie}ge",
             "f{ie}rce", "p{ie}rce", "retr{ie}ve",
         ]),
         ("ei after c", [
             "rec{ei}ve", "rec{ei}pt", "dec{ei}ve", "dec{ei}t", "perc{ei}ve", "conc{ei}ve",
             "conc{ei}t", "c{ei}ling",
         ]),
         ("ei when you hear \"ay\" or \"eye\"", [
             "{ei}ght", "w{ei}gh", "w{ei}ght", "n{ei}ghbour", "r{ei}gn", "v{ei}n", "v{ei}l",
             "r{ei}ndeer", "b{ei}ge", "sl{ei}gh", "h{ei}ght", "{ei}ther", "n{ei}ther",
         ]),
         ("Words that break the rule", [
             "s{ei}ze", "w{ei}rd", "prot{ei}n", "caff{ei}ne", "l{ei}sure", "for{ei}gn",
             "th{ei}r", "h{ei}r", "fr{ie}nd",
             "sc{ie}nce | c + ie, because the c sounds like s or sh",
             "spec{ie}s", "anc{ie}nt", "effic{ie}nt", "suffic{ie}nt", "consc{ie}nce",
             "soc{ie}ty",
         ]),
     ]),
    ("Find a relative where the vowel is clear",
     "Look for a word from the same family where the vowel you cannot hear is stressed. Then "
     "you can hear it.", [
         (None, [
             "defin{i}te | think of finite, define",
             "comp{e}tition, comp{e}titive | think of compete",
             "rep{e}tition | think of repeat",
             "prep{a}ration | think of prepare",
             "inv{i}tation | think of invite",
             "opp{o}site | think of oppose",
             "comp{o}sition | think of compose",
             "comp{a}rison | think of compare",
             "def{i}nition | think of define",
             "adm{i}ration | think of admire",
             "insp{i}ration | think of inspire",
             "imag{i}nation | think of imagine",
             "rel{a}tive | think of relation",
             "hist{o}ry | think of historic",
             "mem{o}ry | think of memorial",
             "fam{i}ly | think of familiar",
             "simil{a}r | think of similarity",
             "gramm{a}r | think of grammatical",
             "categ{o}ry | think of categorical",
             "secret{a}ry | think of secretarial",
             "com{e}dy | think of comedian",
             "democr{a}cy | think of democratic",
             "acad{e}my | think of academic",
             "med{i}cine | think of medicinal",
             "phot{o}graph | think of photography",
             "pol{i}tics | think of political",
             "libr{a}ry | think of librarian",
             "auth{o}r | think of authority",
             "min{o}r | think of minority",
             "maj{o}r | think of majority",
             "popul{a}r | think of popularity",
             "regul{a}r | think of regularity",
             "cel{e}brate | think of celebrity",
         ]),
     ]),
    ("Endings that sound the same",
     "If there is a related word ending in -er or -or, it usually helps: bake &rarr; baker "
     "&rarr; bakery, direct &rarr; director &rarr; directory.", [
         ("-ar, not -er", [
             "calend{ar}", "doll{ar}", "particul{ar}", "famili{ar}", "peculi{ar}", "cell{ar}",
             "coll{ar}", "burgl{ar}", "li{ar}", "begg{ar}", "vineg{ar}", "sug{ar}",
             "schol{ar}", "pill{ar}",
         ]),
         ("-or, not -er", [
             "act{or}", "doct{or}", "visit{or}", "edit{or}", "invent{or}", "govern{or}",
             "sail{or}", "tail{or}", "mirr{or}", "err{or}", "conduct{or}", "direct{or}",
             "translat{or}", "investigat{or}", "operat{or}", "spectat{or}", "competit{or}",
             "profess{or}", "surviv{or}", "creat{or}", "ancest{or}", "calculat{or}",
         ]),
         ("-our, in British spelling", [
             "col{our}", "fav{our}", "flav{our}", "hon{our}", "harb{our}", "lab{our}",
             "behavi{our}", "rum{our}", "od{our}", "glam{our}", "arm{our}",
             "vig{our}", "endeav{our}",
         ]),
         ("-ary", [
             "diction{ary}", "necess{ary}", "ordin{ary}", "tempor{ary}", "vocabul{ary}",
             "prim{ary}", "bound{ary}", "summ{ary}", "sal{ary}", "Janu{ary}", "Febru{ary}",
             "annivers{ary}", "contempor{ary}", "imagin{ary}", "milit{ary}", "volunt{ary}",
             "document{ary}", "extraordin{ary}", "liter{ary}",
             "station{ary} | not moving",
         ]),
         ("-ery", [
             "bak{ery}", "brav{ery}", "deliv{ery}", "discov{ery}", "gall{ery}",
             "myst{ery}", "nurs{ery}", "recov{ery}", "scen{ery}", "surg{ery}", "machin{ery}",
             "jewell{ery}", "cook{ery}", "batt{ery}", "lott{ery}", "pott{ery}", "robb{ery}",
             "cel{ery}", "flatt{ery}",
             "station{ery} | paper and pens",
         ]),
         ("-ory", [
             "fact{ory}", "territ{ory}", "laborat{ory}", "invent{ory}", "direct{ory}",
             "vict{ory}", "the{ory}", "satisfact{ory}", "compuls{ory}", "obligat{ory}",
             "introduct{ory}", "access{ory}", "dormit{ory}", "observat{ory}",
         ]),
     ]),
    ("Vowels you hardly hear at all",
     "Say these words slowly, the way they are written: dif-fer-ent, in-ter-est-ing, "
     "veg-e-ta-ble.", [
         (None, [
             "diff{e}rent", "int{e}resting", "veg{e}table", "fav{ou}rite", "sev{e}ral",
             "choc{o}late", "ev{e}ry", "temp{e}rature", "cam{e}ra", "gen{e}ral",
             "mis{e}rable", "comf{o}rtable", "bus{i}ness", "math{e}matics", "rest{au}rant",
             "lit{e}rature", "av{e}rage", "sep{a}rate", "desp{e}rate", "defin{i}tely",
             "p{o}lice", "s{u}ppose", "p{e}rhaps", "prob{a}bly", "vet{e}rinary",
         ]),
     ]),
    ("The u sound, written o or ou",
     "In these words you hear u, as in cup, but you write o or ou.", [
         ("ou", [
             "c{ou}rage", "enc{ou}rage", "c{ou}sin", "d{ou}ble", "tr{ou}ble", "c{ou}ntry",
             "en{ou}gh", "y{ou}ng", "t{ou}ch", "s{ou}thern", "n{ou}rish", "fl{ou}rish",
             "r{ou}gh", "t{ou}gh", "c{ou}ple",
         ]),
         ("o", [
             "am{o}ng", "m{o}ney", "h{o}ney", "m{o}nth", "w{o}nder", "{o}ven", "gl{o}ve",
             "g{o}vernment", "c{o}ver", "disc{o}ver", "fr{o}nt", "n{o}thing", "w{o}rry",
             "{o}nion", "M{o}nday", "br{o}ther", "m{o}ther", "l{o}ve", "ab{o}ve", "d{o}zen",
         ]),
     ]),
    ("Words to learn by heart", None, [
        (None, [
            "misch{ie}vous | no i before -ous",
            "gen{ui}ne | ends in -ine",
            "hilar{iou}s",
            "emb{a}rrassment | think of a bar",
            "cemet{e}ry | three e's",
            "serg{ea}nt",
            "hyg{ie}ne",
            "min{u}scule | think of minus",
            "vac{uu}m | two u's",
            "h{y}pocrite",
            "consc{iou}s",
            "prec{iou}s",
            "del{i}cious",
            "{a}mateur",
            "b{eau}tiful",
            "ex{e}rcise | ex-er-cise",
            "refrig{e}rator | -er- in the middle",
        ]),
    ]),
]

WATCH = [
    "<b>mischievous</b> has three parts, mis-chie-vous. There is no i before -ous.",
    "<b>stationary</b> means not moving; <b>stationery</b> is paper and pens (e for envelope).",
    "<b>lose</b> is the opposite of win; <b>loose</b> is the opposite of tight.",
    "<b>quite</b> means fairly; <b>quiet</b> means not loud.",
    "<b>principal</b> is the head of a school; a <b>principle</b> is a rule you believe in.",
    "A <b>compliment</b> is something nice you say; to <b>complement</b> is to go well with "
    "something.",
    "Use British spelling: colour, favourite, behaviour (American English writes color).",
]

CHECK_INTRO = ("Type the word, then press Check or Enter. Where letters are given, the word must "
               "fit them, as in wisielec. The spelling has to be exact, as on the test.")
TYPED = [
    ("I can't stop eating this ___ cake!", "chocolate",
     "choc-o-late: say it slowly, the way it is written.", "c h _ c _ l _ t e"),
    ("Thank you for the present. I ___ it yesterday.", "received",
     "e before i after c.", "r e c _ _ v e d"),
    ("Our new ___ helped us carry the boxes upstairs.", "neighbour",
     "ei, because you hear \"ay\"; and British -our.", "n _ _ g h b _ _ r"),
    ("Please ___ the white clothes from the coloured ones before you wash them.", "separate",
     "sep-a-rate: there is a rat in separate.", "s e p _ r _ t e"),
    ("The ___ (PREPARE) for the school trip took two whole weeks.", "preparation",
     "think of prepare: prep-a-ration.", None),
    ("Sixty pupils took part in the maths ___ (COMPETE).", "competition",
     "think of compete: comp-e-tition.", None),
    ("The ___ (DIRECT) of the school play was very proud of us.", "director",
     "-or, as in direct → director.", None),
    ("There is a ___ (BAKE) on the corner that sells fresh bread every morning.", "bakery",
     "baker + y.", None),
]
CHECK_TIP = 'All eight right? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_own_wisielec_01", "SmartEn: wisielec (1)"),
    ("/ojaj/cwiczenia/ojaj_own_wisielec_02", "SmartEn: wisielec (2)"),
]

# Shown in each list's "Advanced" box: C1-C2, formal or rare words (judged by hand, 2026-10-25).
ADVANCED = """
    yield siege pierce retrieve deceit perceive conceive conceit reign vein veil heir
    peculiar cellar beggar scholar pillar investigator odour vigour endeavour contemporary
    literary stationary flattery stationery inventory obligatory introductory dormitory
    observatory nourish flourish sergeant minuscule hypocrite
""".split()
