"""Study page: double-letters (Double letters). Data for tools/study/gen_study.py."""

KEY = "double-letters"
TITLE = "Double letters"
HEAD_TITLE = "Double Letters"
INDEX_TITLE = "Double letters"
BODY = "wordpage"
EYEBROW = "Word formation and wisielec"
LEDE = ("You cannot hear a double letter: forgetable and forgettable sound the same. Two rules "
        "decide most words: when the last letter of a word doubles before an ending, and what "
        "happens when a prefix or an ending meets the same letter. The rest have to be learnt "
        "by heart.")

MISTAKES_INTRO = ""
WIDE = False
MISTAKES = [
    {"wrong": "unforgetable", "right": "unforgettable",
     "why": "for-GET is stressed at the end, so the t doubles before -able."},
    {"wrong": "accidentaly", "right": "accidentally", "why": "accidental + ly: both l's stay."},
    {"wrong": "accomodation", "right": "accommodation", "why": "Two c's and two m's: a-cc-o-mm-o-dation."},
    {"wrong": "begining", "right": "beginning", "why": "be-GIN is stressed at the end, so the n doubles."},
    {"wrong": "neccessary", "right": "necessary", "why": "One c, two s's: like a shirt with one collar and two sleeves."},
]

RULE_TITLE = "The rule"
RULE_HTML = ""
LEGEND = "The letters to watch are in <b>green</b>."

GROUPS = [
    ("When the last letter doubles",
     "Double the last consonant before an ending that starts with a vowel (-ed, -ing, -er, "
     "-est, -able, -y) when the word ends in one vowel and one consonant, and the end of the "
     "word is stressed: stop &rarr; stopped, for-GET &rarr; forgettable.", [
         ("Short words", [
             "stop > stop{p}ed, stop{p}ing", "big > big{g}er, big{g}est", "run > run{n}ing, run{n}er",
             "swim > swim{m}ing, swim{m}er", "plan > plan{n}ing, plan{n}ed", "hot > hot{t}est",
             "thin > thin{n}er", "shop > shop{p}ing, shop{p}er", "sun > sun{n}y", "fat > fat{t}y",
             "drop > drop{p}ed", "sit > sit{t}ing", "get > get{t}ing", "hit > hit{t}ing",
             "wet > wet{t}er", "fog > fog{g}y", "mud > mud{d}y", "sad > sad{d}er",
             "win > win{n}er", "dig > dig{g}ing", "jog > jog{g}ing", "rob > rob{b}er",
         ]),
         ("Longer words stressed at the end", [
             "forget > forget{t}able, forget{t}ing, unforget{t}able",
             "begin > begin{n}ing, begin{n}er", "prefer > prefer{r}ed, prefer{r}ing",
             "occur > occur{r}ed, occur{r}ence", "refer > refer{r}ed, refer{r}al",
             "admit > admit{t}ed, admit{t}ance", "commit > commit{t}ed, commit{t}ee",
             "regret > regret{t}able, regret{t}ed", "permit > permit{t}ed",
             "control > control{l}ed, control{l}able", "compel > compel{l}ed",
             "expel > expel{l}ed", "rebel > rebel{l}ion", "upset > upset{t}ing",
             "forbid > forbid{d}en", "equip > equip{p}ed", "submit > submit{t}ed",
             "omit > omit{t}ed", "propel > propel{l}er", "excel > excel{l}ent",
             "patrol > patrol{l}ing", "transmit > transmit{t}er", "deter > deter{r}ent",
             "recur > recur{r}ing",
         ]),
         ("Not stressed at the end, so no double", [
             "visit > visi{t}ed", "open > ope{n}ed", "offer > offe{r}ed", "happen > happe{n}ed",
             "listen > liste{n}ing", "enter > ente{r}ed", "benefit > benefi{t}ed",
             "budget > budge{t}ed", "limit > limi{t}ed", "target > targe{t}ed",
             "develop > develo{p}ing", "gallop > gallo{p}ing", "focus > focu{s}ed",
             "edit > edi{t}ed", "orbit > orbi{t}ing", "profit > profi{t}able",
             "credit > credi{t}ed",
         ]),
         ("British spelling doubles l anyway", [
             "travel > travel{l}ed, travel{l}er", "cancel > cancel{l}ed, cancel{l}ation",
             "label > label{l}ed", "model > model{l}ing", "quarrel > quarrel{l}ed",
             "level > level{l}ed", "fuel > fuel{l}ed", "signal > signal{l}ed",
             "marvel > marvel{l}ous", "jewel > jewel{l}er, jewel{l}ery",
             "counsel > counsel{l}or",
         ]),
         ("No double: two vowels, two consonants, or an ending that starts with a consonant", [
             "rain > raining", "cook > cooking", "sleep > sleeping", "help > helping",
             "jump > jumped", "forget > forge{t}ful", "equip > equi{p}ment",
             "commit > commi{t}ment", "regret > regre{t}ful",
             "prefer > prefe{r}ence | the stress moves to PREF", "refer > refe{r}ence",
             "confer > confe{r}ence",
         ]),
     ]),
    ("When the same letters meet",
     "When a prefix ends with the letter the word starts with, keep both: un + necessary = "
     "unnecessary. The same goes for an ending: sudden + ness = suddenness, real + ly = really.", [
         ("A prefix meets the word", [
             "necessary > u{nn}ecessary", "natural > u{nn}atural", "noticed > u{nn}oticed",
             "mature > i{mm}ature", "mortal > i{mm}ortal", "moral > i{mm}oral",
             "measurable > i{mm}easurable", "mobile > i{mm}obile", "named > u{nn}amed",
             "regular > i{rr}egular", "relevant > i{rr}elevant",
             "responsible > i{rr}esponsible", "rational > i{rr}ational",
             "replaceable > i{rr}eplaceable", "legal > i{ll}egal", "logical > i{ll}ogical",
             "literate > i{ll}iterate", "legible > i{ll}egible",
             "satisfied > di{ss}atisfied", "similar > di{ss}imilar", "spell > mi{ss}pell",
             "appoint > di{s}appoint | only one s: dis + appoint",
             "agree > di{s}agree", "approve > di{s}approve",
         ]),
         ("The word meets an ending", [
             "sudden > sudde{nn}ess", "keen > kee{nn}ess", "open > ope{nn}ess",
             "thin > thi{nn}ess", "mean > mea{nn}ess", "stubborn > stubbor{nn}ess",
             "even > eve{nn}ess", "green > gree{nn}ess", "real > rea{ll}y", "cruel > crue{ll}y",
             "final > fina{ll}y", "usual > usua{ll}y", "cool > coo{ll}y",
         ]),
         ("Two words meet", [
             "room > roo{mm}ate", "book > boo{kk}eeper", "with > wit{hh}old",
         ]),
     ]),
    ("Learn by heart", None, [
        ("Double letters you might miss", [
            "a{cc}o{mm}odation", "a{dd}re{ss}", "a{gg}re{ss}ive", "a{pp}arently", "ba{ll}oon",
            "co{ll}apse", "co{ll}eague", "co{mm}i{ss}ion", "co{mm}unicate", "co{nn}ection",
            "co{rr}espond", "emba{rr}a{ss}ment", "exa{gg}erate",
            "Medite{rr}anean", "o{cc}ur", "po{ss}e{ss}", "su{cc}e{ss}", "a{ss}e{ss}",
            "mi{ll}ionaire", "ma{tt}re{ss}", "dile{mm}a", "i{mm}ediately", "o{pp}ortunity",
            "su{cc}eed", "su{mm}ary", "ta{tt}oo", "te{rr}ible", "te{rr}ific", "vi{ll}ain",
            "woo{ll}en", "ca{rr}ot", "ci{nn}amon", "a{cc}ident", "a{tt}ach", "a{tt}ack",
            "co{mm}ent", "co{rr}ect", "e{ff}ect", "e{ff}ort", "gra{mm}ar", "ha{pp}en",
            "i{rr}itate", "pa{ss}enger", "po{ss}ible", "sci{ss}ors", "su{dd}en", "su{gg}est",
            "su{pp}ort", "su{rr}ound", "a{pp}reciate", "a{pp}roximately", "a{rr}ange",
            "a{rr}est", "co{ll}ection", "i{mm}igrant", "i{nn}ocent", "o{cc}upy", "o{ff}icial",
            "o{pp}onent",
        ]),
        ("Single letters you might double", [
            "a{c}ross", "a{p}artment", "ha{r}ass | one r, two s's",
            "ne{c}essary | one c, two s's", "re{c}ommend | one c, two m's",
            "to{m}orrow | one m, two r's", "occa{s}ion | two c's, one s",
            "pa{r}allel | one r, then two l's", "pro{f}essor | one f, two s's",
            "o{m}ission | one m, two s's", "Ca{r}ibbean | one r, two b's",
            "sa{t}ellite | one t, two l's", "pa{s}time | one s, one t", "u{n}ti{l}",
            "we{l}come", "a{l}ready", "a{l}ways", "a{l}most", "a{l}so", "a{l}together",
            "fu{l}fi{l} | British spelling",
        ]),
    ]),
]

WATCH = [
    "Stress decides: pre-FER &rarr; preferred, but OF-fer &rarr; offered.",
    "Endings that start with a consonant never double anything: forgetful, equipment, "
    "commitment.",
    "British spelling doubles l: travelled, cancelled, jeweller. American English writes "
    "traveled.",
    "all- at the front of a word has one l: already, always, almost, altogether. But <b>all "
    "right</b> is two words.",
    "<b>until</b> has one l, but <b>till</b> has two.",
]

CHECK_INTRO = ("Type the word, then press Check or Enter. Where letters are given, the word must "
               "fit them, as in wisielec. The spelling has to be exact, as on the test.")
TYPED = [
    ("The school found cheap ___ for us near the beach.", "accommodation",
     "two c's and two m's.", "a _ _ o _ _ o d a t i o n"),
    ("We can't finish it today, so we will do it ___.", "tomorrow",
     "one m, two r's.", "t o _ o _ _ o w"),
    ("I didn't understand the ___ (BEGIN) of the film, so I watched it again.", "beginning",
     "be-GIN is stressed at the end, so the n doubles.", None),
    ("Last summer we ___ (TRAVEL) around Scotland by train.", "travelled",
     "British spelling doubles the l.", None),
    ("When I was younger, I ___ (PREFER) tea to coffee.", "preferred",
     "pre-FER is stressed at the end, so the r doubles.", None),
    ("My grandpa is getting a bit ___ (FORGET): he lost his glasses twice today.", "forgetful",
     "-ful starts with a consonant, so the t does not double.", None),
    ("You don't need to bring any food: it is completely ___ (NECESSARY).", "unnecessary",
     "un + necessary: both n's stay.", None),
    ("The accident ___ (OCCUR) on a dark, rainy night.", "occurred",
     "oc-CUR is stressed at the end, so the r doubles.", None),
]
CHECK_TIP = 'All eight right? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_2324_wisielec_01", "SmartEn: wisielec, OJAJ 2023/24"),
    ("/ojaj/cwiczenia/ojaj_e3_wisielec_01", "SmartEn: wisielec, stage 3"),
]

# Shown in each list's "Advanced" box: C1-C2, formal or rare words (judged by hand, 2026-10-25).
ADVANCED = """
    regrettable compelled expelled omitted propeller patrolling transmitter deterrent
    recurring budgeted galloping orbiting credited benefited levelled fuelled signalled
    regretful unnamed immeasurable immobile irrational irreplaceable illiterate illegible
    dissimilar keenness thinness meanness stubbornness evenness greenness coolly bookkeeper
    withhold commission dilemma harass parallel omission pastime fulfil
""".split()
