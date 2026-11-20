"""Study page: ance-ence (-ance or -ence?). Data for tools/study/gen_study.py."""

KEY = "ance-ence"
TITLE = "-ance or -ence?"
HEAD_TITLE = "-ance or -ence?"
INDEX_TITLE = "-ance or -ence?"
BODY = "wordpage"
EYEBROW = "Word formation and wisielec"
LEDE = ("-ance and -ence sound exactly the same, and so do -ant and -ent. You cannot hear the "
        "difference, but a word from the same family usually tells you which one it is. Where "
        "nothing helps, the lists below are the words to learn.")

MISTAKES_INTRO = ""
WIDE = False
MISTAKES = [
    {"wrong": "resemblence", "right": "resemblance", "why": "resemble takes -ance."},
    {"wrong": "perseverence", "right": "perseverance", "why": "persevere takes -ance."},
    {"wrong": "existance", "right": "existence", "why": "exist, insist and persist take -ence."},
    {"wrong": "independant", "right": "independent", "why": "independent, independence: e every time."},
    {"wrong": "relevent", "right": "relevant", "why": "relevant, relevance: a every time."},
]

RULE_TITLE = "The rule"
RULE_HTML = ""
LEGEND = "The letter to watch is in <b>green</b>."

GROUPS = [
    ("The -ant or -ent word tells you",
     "If you know the adjective, you know the noun: important &rarr; importance, different "
     "&rarr; difference. The letter stays the same in the whole family. And listen to the c or "
     "g before the ending: a hard one (k, g) goes with -ance (significance, elegance), a soft "
     "one (s, j) with -ence (innocence, intelligence).", [
         ("-ant becomes -ance", [
             "important > import{a}nce", "relevant > relev{a}nce", "elegant > eleg{a}nce",
             "distant > dist{a}nce", "ignorant > ignor{a}nce", "tolerant > toler{a}nce",
             "brilliant > brilli{a}nce", "arrogant > arrog{a}nce", "abundant > abund{a}nce",
             "significant > signific{a}nce", "reluctant > reluct{a}nce",
             "extravagant > extravag{a}nce", "fragrant > fragr{a}nce", "dominant > domin{a}nce",
             "radiant > radi{a}nce",
         ]),
         ("-ent becomes -ence", [
             "absent > abs{e}nce", "confident > confid{e}nce", "convenient > conveni{e}nce",
             "different > differ{e}nce", "evident > evid{e}nce", "excellent > excell{e}nce",
             "independent > independ{e}nce", "innocent > innoc{e}nce",
             "intelligent > intellig{e}nce", "magnificent > magnific{e}nce",
             "obedient > obedi{e}nce", "patient > pati{e}nce", "permanent > perman{e}nce",
             "present > pres{e}nce", "silent > sil{e}nce", "violent > viol{e}nce",
             "competent > compet{e}nce", "adolescent > adolesc{e}nce",
             "prominent > promin{e}nce",
         ]),
         ("-ent becomes -ency", [
             "frequent > frequ{e}ncy", "urgent > urg{e}ncy", "fluent > flu{e}ncy",
             "efficient > effici{e}ncy", "decent > dec{e}ncy", "consistent > consist{e}ncy",
         ]),
     ]),
    ("The verb tells you",
     "Most verbs take -ance: perform &rarr; performance. Verbs that end in a stressed -er or "
     "-ur (pre-FER, oc-CUR) or in -ere take -ence, and so do exist, insist and persist. "
     "The other -ence verbs below have to be learnt.", [
         ("-ance", [
             "perform > perform{a}nce", "accept > accept{a}nce", "allow > allow{a}nce",
             "annoy > annoy{a}nce", "assist > assist{a}nce", "attend > attend{a}nce",
             "avoid > avoid{a}nce", "disturb > disturb{a}nce", "endure > endur{a}nce",
             "guide > guid{a}nce", "insure > insur{a}nce", "resemble > resembl{a}nce",
             "rely > reli{a}nce", "resist > resist{a}nce", "persevere > persever{a}nce",
             "acquaint > acquaint{a}nce", "admit > admitt{a}nce", "clear > clear{a}nce",
             "comply > compli{a}nce", "defy > defi{a}nce", "ally > alli{a}nce",
             "govern > govern{a}nce", "inherit > inherit{a}nce", "utter > utter{a}nce",
             "grieve > griev{a}nce",
             "enter > entr{a}nce | the base word changes too",
             "hinder > hindr{a}nce | the base word changes too",
             "remember > remembr{a}nce | the base word changes too",
             "maintain > mainten{a}nce | the base word changes too",
         ]),
         ("-ence", [
             "exist > exist{e}nce", "insist > insist{e}nce", "persist > persist{e}nce",
             "depend > depend{e}nce", "prefer > prefer{e}nce", "refer > refer{e}nce",
             "confer > confer{e}nce", "infer > infer{e}nce", "interfere > interfer{e}nce",
             "occur > occurr{e}nce", "recur > recurr{e}nce", "emerge > emerg{e}nce",
             "coincide > coincid{e}nce", "correspond > correspond{e}nce",
             "adhere > adher{e}nce", "reside > resid{e}nce", "indulge > indulg{e}nce",
         ]),
     ]),
    ("Learn by heart", None, [
        ("-ance", [
            "nuis{a}nce", "ambul{a}nce", "bal{a}nce", "fin{a}nce", "inst{a}nce", "rom{a}nce",
            "subst{a}nce", "circumst{a}nce", "appli{a}nce", "adv{a}nce", "enh{a}nce",
        ]),
        ("-ence", [
            "audi{e}nce", "consci{e}nce", "consequ{e}nce", "experi{e}nce", "sci{e}nce",
            "sent{e}nce", "sequ{e}nce", "influ{e}nce", "ess{e}nce",
            "lic{e}nce | the noun; to license is the verb", "off{e}nce", "def{e}nce",
            "pret{e}nce",
        ]),
        ("-ant", [
            "assist{a}nt", "attend{a}nt", "serv{a}nt", "inhabit{a}nt", "applic{a}nt",
            "particip{a}nt", "account{a}nt", "descend{a}nt", "pleas{a}nt", "const{a}nt",
            "vac{a}nt", "inst{a}nt", "redund{a}nt", "hesit{a}nt",
        ]),
        ("-ent", [
            "appar{e}nt", "transpar{e}nt", "curr{e}nt", "rec{e}nt", "suffici{e}nt",
            "persist{e}nt", "depend{e}nt", "coher{e}nt", "inher{e}nt", "oppon{e}nt",
            "stud{e}nt", "presid{e}nt", "resid{e}nt",
        ]),
    ]),
]

WATCH = [
    "assist and resist take -ance (assistance, resistance), but exist, insist and persist "
    "take -ence (existence, insistence, persistence).",
    "prefer &rarr; preference and refer &rarr; reference: the stress moves to the front, so "
    "the r does not double. occur &rarr; occurrence keeps the stress, so it does.",
    "<b>independent</b> never has an a: independence, independently.",
    "In British spelling <b>licence</b> is the noun and <b>license</b> the verb; "
    "<b>practice</b> and <b>practise</b> work the same way.",
    "maintain &rarr; maintenance and hinder &rarr; hindrance also change inside: see "
    "<a href=\"/ojaj_study/base-change\">When the base word changes</a>.",
]

CHECK_INTRO = ("Type the word made from the word in capitals, then press Check or Enter. The "
               "spelling has to be exact, as on the test.")
TYPED = [
    ("I don't see the ___ (RELEVANT) of this question to our topic.", "relevance",
     "-ant gives -ance.", None),
    ("Do you believe in the ___ (EXIST) of ghosts?", "existence",
     "exist, insist and persist take -ence.", None),
    ("The actors were cheered at the end of their ___ (PERFORM).", "performance",
     "perform takes -ance.", None),
    ("Thank you for your ___ (ASSIST) with the heavy bags.", "assistance",
     "assist and resist take -ance.", None),
    ("My aunt's ___ (INSIST) on paying for everyone was very kind.", "insistence",
     "exist, insist and persist take -ence.", None),
    ("There is a big ___ (DIFFER) between the two plans.", "difference",
     "different gives difference.", None),
    ("Running a marathon needs a lot of ___ (ENDURE).", "endurance",
     "endure takes -ance.", None),
    ("My ___ (PREFER) is for a seat by the window.", "preference",
     "pre-FER takes -ence, and the stress moves, so one r.", None),
]
CHECK_TIP = 'All eight right? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_2324_slowotworstwo_02", "SmartEn: word formation, OJAJ 2023/24"),
    ("/ojaj/cwiczenia/ojaj_e3_slowotworstwo", "SmartEn: word formation, stage 3"),
]

# No Advanced boxes on this page (Lukasz, 2026-10-25); the words below stay marked.
SPLIT = False

# Shown in each list's "Advanced" box: C1-C2, formal or rare words (judged by hand, 2026-10-25).
ADVANCED = """
    brilliance arrogance abundance reluctance extravagance fragrance dominance radiance
    magnificence permanence competence adolescence prominence decency consistency avoidance
    reliance admittance clearance compliance defiance alliance governance utterance
    grievance insistence persistence inference recurrence emergence correspondence adherence
    indulgence enhance essence pretence descendant redundant hesitant coherent inherent
""".split()
