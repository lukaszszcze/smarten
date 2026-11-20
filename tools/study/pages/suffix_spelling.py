"""Study page: suffix-spelling (Adding an ending). Data for tools/study/gen_study.py."""

KEY = "suffix-spelling"
TITLE = "Adding an ending"
HEAD_TITLE = "Adding an Ending"
INDEX_TITLE = "Adding an ending"
BODY = "wordpage"
EYEBROW = "Word formation and wisielec"
LEDE = ("When an ending goes onto a word, the last letter of the word sometimes changes: a "
        "silent e drops or stays, a y becomes i, and -ic needs -ally. A few rules cover almost "
        "every word. (A letter that doubles, as in forgettable, is on the double letters page.)")

MISTAKES_INTRO = ""
WIDE = False
MISTAKES = [
    {"wrong": "knowledgable", "right": "knowledgeable",
     "why": "The e stays after g, so the g still sounds like j."},
    {"wrong": "unrecogniseable", "right": "unrecognisable",
     "why": "recognise loses its e before -able."},
    {"wrong": "accidentaly", "right": "accidentally", "why": "accidental + ly: keep both l's."},
    {"wrong": "truely", "right": "truly", "why": "true loses its e, although -ly starts with a consonant."},
    {"wrong": "arguement", "right": "argument",
     "why": "argue loses its e, although -ment starts with a consonant."},
]

RULE_TITLE = "The rule"
RULE_HTML = ""
LEGEND = ("The letters that go are <s>crossed out</s> and the letters that come in, or stay "
          "where you might drop them, are <b>green</b>.")

GROUPS = [
    ("A silent e at the end",
     "Drop the e before an ending that starts with a vowel (-able, -ing, -ous, -al, -ity, "
     "-ion, -y). Keep it before an ending that starts with a consonant (-ment, -ful, -less, "
     "-ly, -ness).", [
         ("The e drops before a vowel", [
             "recognis[e] > recognisable, unrecognisable", "lov[e] > lovable",
             "believ[e] > believable", "us[e] > usable", "excit[e] > exciting",
             "hop[e] > hoping", "writ[e] > writing", "desir[e] > desirable",
             "debat[e] > debatable", "valu[e] > valuable", "fam[e] > famous",
             "nerv[e] > nervous", "adventur[e] > adventurous", "glob[e] > global",
             "natur[e] > natural", "arriv[e] > arrival", "refus[e] > refusal",
             "sens[e] > sensible", "creat[e] > creation, creative", "educat[e] > education",
             "pur[e] > purity", "secur[e] > security", "scarc[e] > scarcity",
             "imagin[e] > imaginative", "continu[e] > continuous", "pleas[e] > pleasure",
             "ston[e] > stony", "nois[e] > noisy", "ic[e] > icy", "tast[e] > tasty",
         ]),
         ("The e stays before a consonant", [
             "excite > excit{e}ment", "hope > hop{e}ful, hop{e}less", "care > car{e}ful, car{e}less",
             "use > us{e}ful, us{e}less", "love > lov{e}ly", "safe > saf{e}ly, saf{e}ty",
             "complete > complet{e}ly", "polite > polit{e}ness", "encourage > encourag{e}ment",
             "manage > manag{e}ment", "replace > replac{e}ment", "achieve > achiev{e}ment",
             "measure > measur{e}ment", "nice > nic{e}ly", "home > hom{e}less",
             "state > stat{e}ment", "move > mov{e}ment", "amuse > amus{e}ment",
             "settle > settl{e}ment", "advertise > advertis{e}ment", "peace > peac{e}ful",
             "grace > grac{e}ful", "lone > lon{e}ly", "extreme > extrem{e}ly",
             "immediate > immediat{e}ly", "entire > entir{e}ly", "sincere > sincer{e}ly",
             "severe > sever{e}ly", "rare > rar{e}ly", "waste > wast{e}ful",
             "shame > sham{e}ful", "late > lat{e}ness", "rude > rud{e}ness",
         ]),
         ("But in these words the e drops before a consonant", [
             "argu[e] > argument", "tru[e] > truly, truth", "du[e] > duly",
             "whol[e] > wholly", "nin[e] > ninth", "wis[e] > wisdom", "aw[e] > awful",
         ]),
         ("The e stays after c and g, so they stay soft", [
             "knowledge > knowledg{e}able", "notice > notic{e}able", "change > chang{e}able",
             "manage > manag{e}able", "replace > replac{e}able", "trace > trac{e}able",
             "service > servic{e}able", "enforce > enforc{e}able", "courage > courag{e}ous",
             "outrage > outrag{e}ous", "advantage > advantag{e}ous",
         ]),
         ("The e stays after ee, oe and ye", [
             "agree > agr{ee}able", "see > s{ee}ing", "flee > fl{ee}ing", "canoe > cano{e}ing",
             "dye > dy{e}ing | to colour something",
         ]),
         ("ie becomes y before -ing", ["d[ie] > d{y}ing", "l[ie] > l{y}ing", "t[ie] > t{y}ing"]),
     ]),
    ("y becomes i",
     "After a consonant, y becomes i before an ending: lazy &rarr; laziness. It stays before "
     "-ing and -ish: study &rarr; studying. After a vowel, y stays: enjoy &rarr; enjoyment.", [
         ("y becomes i", [
             "laz[y] > laz{i}ness, laz{i}ly", "happ[y] > happ{i}ness, happ{i}ly",
             "eas[y] > eas{i}ly", "bus[y] > bus{i}ness", "beaut[y] > beaut{i}ful",
             "myster[y] > myster{i}ous", "glor[y] > glor{i}ous", "fur[y] > fur{i}ous",
             "env[y] > env{i}ous", "var[y] > var{i}ous", "rel[y] > rel{i}able, rel{i}ance",
             "den[y] > den{i}al", "tr[y] > tr{i}al", "bur[y] > bur{i}al",
             "marr[y] > marr{i}age", "carr[y] > carr{i}age", "appl[y] > appl{i}ance",
             "compl[y] > compl{i}ance", "def[y] > def{i}ance", "all[y] > all{i}ance",
             "pit[y] > pit{i}ful", "plent[y] > plent{i}ful", "merc[y] > merc{i}ful",
             "penn[y] > penn{i}less", "heav[y] > heav{i}ness", "read[y] > read{i}ness, read{i}ly",
             "angr[y] > angr{i}ly", "empt[y] > empt{i}ness", "ugl[y] > ugl{i}ness",
             "lonel[y] > lonel{i}ness", "friendl[y] > friendl{i}ness", "sill[y] > sill{i}ness",
             "luxur[y] > luxur{i}ous", "industr[y] > industr{i}al, industr{i}ous",
             "colon[y] > colon{i}al", "harmon[y] > harmon{i}ous", "victor[y] > victor{i}ous",
             "cr[y] > cr{i}ed",
         ]),
         ("y stays before -ing and -ish", [
             "study > stud{y}ing", "carry > carr{y}ing", "copy > cop{y}ing", "worry > worr{y}ing",
             "hurry > hurr{y}ing", "baby > bab{y}ish",
         ]),
         ("y stays after a vowel", [
             "enjoy > enjo{y}ment, enjo{y}able", "play > pla{y}er, pla{y}ful",
             "employ > emplo{y}er, emplo{y}ment", "pay > pa{y}ment, pa{y}able",
             "obey > obe{y}ed", "destroy > destro{y}er", "joy > jo{y}ful",
             "annoy > anno{y}ing, anno{y}ance", "survey > surve{y}or", "convey > conve{y}or",
             "journey > journe{y}ed",
         ]),
         ("Words that break the rule", [
             "da[y] > da{i}ly", "pa[y] > pa{i}d", "sa[y] > sa{i}d", "la[y] > la{i}d",
             "shy > sh{y}ness, sh{y}ly | y stays",
         ]),
     ]),
    ("-ally, -ly and -fully",
     "Adjectives ending in -ic add -ally. Adjectives ending in -al or -ful just add -ly, so "
     "you get a double l.", [
         ("-ic adds -ally", [
             "basic > basic{ally}", "tragic > tragic{ally}", "dramatic > dramatic{ally}",
             "automatic > automatic{ally}", "scientific > scientific{ally}",
             "enthusiastic > enthusiastic{ally}", "realistic > realistic{ally}",
             "specific > specific{ally}", "fantastic > fantastic{ally}",
             "economic > economic{ally}", "energetic > energetic{ally}",
             "sarcastic > sarcastic{ally}", "heroic > heroic{ally}", "romantic > romantic{ally}",
             "artistic > artistic{ally}", "ironic > ironic{ally}",
             "systematic > systematic{ally}", "optimistic > optimistic{ally}",
             "public > public{ly} | the one exception",
         ]),
         ("-al adds -ly", [
             "accidental > accidenta{ll}y", "occasional > occasiona{ll}y",
             "natural > natura{ll}y", "usual > usua{ll}y", "final > fina{ll}y", "real > rea{ll}y",
             "general > genera{ll}y", "especial > especia{ll}y", "incidental > incidenta{ll}y",
             "additional > additiona{ll}y", "traditional > traditiona{ll}y",
             "personal > persona{ll}y", "total > tota{ll}y", "actual > actua{ll}y",
             "eventual > eventua{ll}y", "gradual > gradua{ll}y", "individual > individua{ll}y",
             "typical > typica{ll}y", "critical > critica{ll}y", "practical > practica{ll}y",
             "logical > logica{ll}y", "physical > physica{ll}y", "emotional > emotiona{ll}y",
             "intentional > intentiona{ll}y", "normal > norma{ll}y", "formal > forma{ll}y",
             "legal > lega{ll}y", "local > loca{ll}y", "mental > menta{ll}y",
         ]),
         ("-ful adds -ly", [
             "careful > carefu{ll}y", "hopeful > hopefu{ll}y", "beautiful > beautifu{ll}y",
             "successful > successfu{ll}y", "grateful > gratefu{ll}y", "peaceful > peacefu{ll}y",
             "thankful > thankfu{ll}y", "cheerful > cheerfu{ll}y", "powerful > powerfu{ll}y",
             "faithful > faithfu{ll}y", "respectful > respectfu{ll}y", "playful > playfu{ll}y",
             "skilful > skilfu{ll}y", "wonderful > wonderfu{ll}y", "painful > painfu{ll}y",
         ]),
         ("-le becomes -ly", [
             "gentl[e] > gentl{y}", "simpl[e] > simpl{y}", "possibl[e] > possibl{y}",
             "terribl[e] > terribl{y}", "comfortabl[e] > comfortabl{y}",
             "probabl[e] > probabl{y}", "horribl[e] > horribl{y}", "sensibl[e] > sensibl{y}",
             "responsibl[e] > responsibl{y}", "incredibl[e] > incredibl{y}",
             "suitabl[e] > suitabl{y}", "considerabl[e] > considerabl{y}", "idl[e] > idl{y}",
             "subtl[e] > subtl{y}",
         ]),
         ("-ll adds only -y", ["full > full{y}", "dull > dull{y}"]),
     ]),
    ("-our becomes -or",
     "In British spelling, a word ending in -our loses its u before -ous, -ious and -ary. "
     "Before other endings it keeps it.", [
         ("The u drops", [
             "glamo[u]r > glamorous", "vigo[u]r > vigorous", "rigo[u]r > rigorous",
             "labo[u]r > laborious", "hono[u]r > honorary",
         ]),
         ("The u stays", [
             "colour > colo{u}rful", "honour > hono{u}rable", "favour > favo{u}rable, favo{u}rite",
             "labour > labo{u}rer", "neighbour > neighbo{u}rhood",
         ]),
     ]),
    ("-ise or -ize",
     "In British spelling both are right: recognise or recognize, organise or organize. These "
     "words are always -ise.", [
         (None, [
             "advert{ise}", "adv{ise}", "exerc{ise}", "surpr{ise}", "comprom{ise}",
             "superv{ise}", "telev{ise}", "rev{ise}", "desp{ise}", "improv{ise}",
             "compr{ise}", "dev{ise}",
         ]),
     ]),
]

WATCH = [
    "-ful on its own has one l: beautiful, careful, helpful. The second l comes only with "
    "-ly: beautifully.",
    "British spelling has one l in <b>skilful</b>; American English writes skillful.",
    "<b>dying</b> comes from die; <b>dyeing</b> comes from dye, to colour something.",
    "A few words take either spelling, and both are right: ageing or aging, likeable or "
    "likable.",
]

CHECK_INTRO = ("Type the word made from the word in capitals, then press Check or Enter. The "
               "spelling has to be exact, as on the test.")
TYPED = [
    ("The scratch on my new bike is hardly ___ (NOTICE).", "noticeable",
     "the e stays after c, so the c still sounds like s.", None),
    ("My brother and I had a big ___ (ARGUE) about who would sit in the front.", "argument",
     "argue loses its e, although -ment starts with a consonant.", None),
    ("I am ___ (TRUE) sorry for breaking your phone.", "truly",
     "true loses its e: truly.", None),
    ("After his best friend moved away, he struggled with ___ (LONELY).", "loneliness",
     "y becomes i: lonely → loneliness.", None),
    ("Thank you for a very ___ (ENJOY) evening.", "enjoyable",
     "y after a vowel stays.", None),
    ("The story ends ___ (TRAGIC): both heroes die.", "tragically",
     "-ic adds -ally.", None),
    ("It was very ___ (COURAGE) of you to tell the teacher the truth.", "courageous",
     "the e stays after g, so the g still sounds like j.", None),
    ("The plants are ___ (DIE) because nobody has watered them.", "dying",
     "ie becomes y before -ing.", None),
]
CHECK_TIP = 'All eight right? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_2324_slowotworstwo_02", "SmartEn: word formation, OJAJ 2023/24"),
    ("/ojaj/cwiczenia/ojaj_e2gl_slowotworstwo", "SmartEn: word formation, stage 2"),
]

# Shown in each list's "Advanced" box: C1-C2, formal or rare words (judged by hand, 2026-10-25).
ADVANCED = """
    desirable debatable refusal purity scarcity stony settlement lateness duly wholly
    traceable serviceable enforceable outrageous advantageous fleeing dyeing burial
    compliance defiance alliance merciful penniless colonial harmonious surveyor conveyor
    heroically systematically incidentally idly subtly dully vigorous rigorous laborious
    honorary televise despise comprise devise
""".split()
