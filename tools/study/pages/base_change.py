"""Study page: base-change (When the base word changes). Data for tools/study/gen_study.py."""

KEY = "base-change"
TITLE = "When the base word changes"
HEAD_TITLE = "When the Base Word Changes"
INDEX_TITLE = "When the base word changes"
BODY = "wordpage"
EYEBROW = "Word formation and wisielec"
LEDE = ("Most words are built by adding an ending to the word in capitals: care &rarr; careless, "
        "enjoy &rarr; enjoyment. Some words do not work like that. When the ending goes on, the "
        "base word changes inside: a letter drops out, the last letters change, an old ending "
        "comes off first, or the vowel changes. These words cannot be worked out by adding an "
        "ending, so learn them in pairs.")

MISTAKES_INTRO = ""
WIDE = False
MISTAKES = [
    {"wrong": "pronounciation", "right": "pronunciation",
     "why": "pronounce loses its o: pro-nun-ci-a-tion."},
    {"wrong": "irrepairable", "right": "irreparable", "why": "repair loses its i."},
    {"wrong": "indecidous", "right": "indecisive",
     "why": "decide becomes decis-: decision, decisive, indecisive."},
    {"wrong": "speachless", "right": "speechless", "why": "speak becomes speech, with ee."},
    {"wrong": "hinderance", "right": "hindrance", "why": "hinder loses its e."},
]

RULE_TITLE = "The rule"
RULE_HTML = ""
LEGEND = ("The lists group the words by what changes. The letters that go are <s>crossed out</s> "
          "and the letters that come in are <b>green</b>.")

GROUPS = [
    ("A letter drops out",
     'Say the new word aloud. A letter you no longer hear is usually not written either: '
     'in pro-nun-ci-a-tion you hear "nun", not "noun".', [
         ("The e before r", [
             "ent[e]r > entrance", "hind[e]r > hindrance", "rememb[e]r > remembrance",
             "regist[e]r > registration", "administ[e]r > administration",
             "minist[e]r > ministry", "ang[e]r > angry", "hung[e]r > hungry",
             "wint[e]r > wintry", "monst[e]r > monstrous", "disast[e]r > disastrous",
             "wond[e]r > wondrous", "sob[e]r > sobriety",
         ]),
         ("The i after a", [
             "expla[i]n > explanation", "excla[i]m > exclamation",
             "procla[i]m > proclamation", "repa[i]r > irreparable", "va[i]n > vanity",
         ]),
         ("The u of -ous", ["genero[u]s > generosity", "curio[u]s > curiosity"]),
         ("Other letters", ["pron[o]unce > pronunciation", "cl[e]ar > clarity, clarify"]),
     ]),
    ("The last letters change",
     "Learn the whole family at once: decide, decision, decisive, indecisive.", [
         ("d or de becomes s (or c)", [
             "deci[de] > deci{s}ion, deci{s}ive, indeci{s}ive", "divi[de] > divi{s}ion",
             "provi[de] > provi{s}ion", "conclu[de] > conclu{s}ion, conclu{s}ive",
             "inclu[de] > inclu{s}ion, inclu{s}ive", "exclu[de] > exclu{s}ion, exclu{s}ive",
             "explo[de] > explo{s}ion, explo{s}ive", "colli[de] > colli{s}ion",
             "persua[de] > persua{s}ion, persua{s}ive", "inva[de] > inva{s}ion, inva{s}ive",
             "eva[de] > eva{s}ion, eva{s}ive", "ero[de] > ero{s}ion",
             "intru[de] > intru{s}ion, intru{s}ive", "defen[d] > defen{c}e, defen{s}ive",
             "offen[d] > offen{c}e, offen{s}ive", "preten[d] > preten{c}e",
             "expan[d] > expan{s}ion, expan{s}ive", "exten[d] > exten{s}ion, exten{s}ive",
             "comprehen[d] > comprehen{s}ion, comprehen{s}ive, incomprehen{s}ible",
             "apprehen[d] > apprehen{s}ion, apprehen{s}ive",
             "suspen[d] > suspen{s}e, suspen{s}ion", "respon[d] > respon{s}e, respon{s}ive",
         ]),
         ("d becomes t", [
             "inten[d] > inten{t}ion", "atten[d] > atten{t}ion, atten{t}ive",
             "ascen[d] > ascen{t}", "descen[d] > descen{t}",
         ]),
         ("t becomes ss", [
             "permi[t] > permi{ss}ion, permi{ss}ive", "admi[t] > admi{ss}ion",
             "submi[t] > submi{ss}ion, submi{ss}ive", "omi[t] > omi{ss}ion",
             "transmi[t] > transmi{ss}ion", "emi[t] > emi{ss}ion", "commi[t] > commi{ss}ion",
         ]),
         ("t becomes s", ["conver[t] > conver{s}ion", "diver[t] > diver{s}ion"]),
         ("-ceed and -cede", [
             "succ[eed] > succ{ess}, succ{ess}ion", "exc[eed] > exc{ess}, exc{ess}ive",
             "proc[eed] > proc{ed}ure, proc{ess}", "rec[ede] > rec{ess}ion",
             "conc[ede] > conc{ess}ion",
         ]),
         ("b becomes p", [
             "descri[be] > descri{p}tion, descri{p}tive", "prescri[be] > prescri{p}tion",
             "subscri[be] > subscri{p}tion", "absor[b] > absor{p}tion",
         ]),
         ("-ceive becomes -cept- or -ceit", [
             "rece[ive] > rece{p}tion, rece{ip}t", "dece[ive] > dece{p}tion, dece{it}",
             "perce[ive] > perce{p}tion", "conce[ive] > conce{p}tion",
         ]),
         ("p comes in after m", [
             "assum[e] > assum{p}tion", "consum[e] > consum{p}tion",
             "presum[e] > presum{p}tion", "resum[e] > resum{p}tion",
         ]),
         ("ve becomes u", [
             "sol[ve] > sol{u}tion", "resol[ve] > resol{u}tion",
             "dissol[ve] > dissol{u}tion", "revol[ve] > revol{u}tion",
             "evol[ve] > evol{u}tion",
         ]),
         ("el becomes ul", [
             "comp[e]l > comp{u}lsion, comp{u}lsory", "exp[e]l > exp{u}lsion",
             "rep[e]l > rep{u}lsive",
         ]),
         ("re becomes s", [
             "acqui[re] > acqui{s}ition", "inqui[re] > inqui{s}itive",
             "adhe[re] > adhe{s}ive", "cohe[re] > cohe{s}ion",
         ]),
         ("ce becomes t", [
             "scien[c]e > scien{t}ist, scien{t}ific", "essen[c]e > essen{t}ial",
             "influen[c]e > influen{t}ial", "confiden[c]e > confiden{t}ial",
             "residen[c]e > residen{t}ial", "substan[c]e > substan{t}ial",
             "circumstan[c]e > circumstan{t}ial", "sequen[c]e > sequen{t}ial",
         ]),
         ("c becomes s: noun to verb", ["advi[c]e > advi{s}e", "devi[c]e > devi{s}e"]),
         ("y becomes ic", [
             "appl[y] > appl{ic}ation, appl{ic}able, appl{ic}ant",
             "multipl[y] > multipl{ic}ation", "impl[y] > impl{ic}ation",
             "qualif[y] > qualif{ic}ation", "classif[y] > classif{ic}ation",
             "identif[y] > identif{ic}ation", "justif[y] > justif{ic}ation",
             "modif[y] > modif{ic}ation", "notif[y] > notif{ic}ation",
             "simplif[y] > simplif{ic}ation",
             "satisf[y] > satisf{ac}tion, satisf{ac}tory | here y becomes ac",
         ]),
         ("f and v swap", [
             "belie[ve] > belie{f}", "relie[ve] > relie{f}", "grie[ve] > grie{f}",
             "pro[ve] > pro{of}", "li[ve] > li{fe}", "wi[f]e > wi{v}es",
             "kni[f]e > kni{v}es", "li[f]e > li{v}es", "lea[f] > lea{v}es",
             "hal[f] > hal{v}es, hal{v}e", "shel[f] > shel{v}es", "thie[f] > thie{v}es",
             "wol[f] > wol{v}es", "loa[f] > loa{v}es",
         ]),
         ("Other changes", [
             "susp[ect] > susp{ic}ion, susp{ic}ious", "destr[oy] > destr{uc}tion, destr{uc}tive",
             "pursu[e] > pursu{it}", "gramma[r] > gramma{t}ical", "crim[e] > crim{in}al",
             "simpl[e] > simpl{ic}ity",
         ]),
     ]),
    ("An old ending comes off first",
     "Take the old ending off the base word, then put the new one on: anxi-ous, anxi-ety.", [
         ("-ous comes off", [
             "anxi[ous] > anxiety", "vari[ous] > variety", "notori[ous] > notoriety",
             "fam[ous] > fame",
         ]),
         ("-ion becomes -ious", [
             "ambitio[n] > ambitious", "cautio[n] > cautious", "nutritio[n] > nutritious",
             "religio[n] > religious", "superstitio[n] > superstitious",
             "infectio[n] > infectious",
         ]),
         ("-ble becomes -bility", [
             "ab[le] > ab{il}ity", "possib[le] > possib{il}ity",
             "responsib[le] > responsib{il}ity", "visib[le] > visib{il}ity",
             "flexib[le] > flexib{il}ity", "reliab[le] > reliab{il}ity",
             "availab[le] > availab{il}ity", "probab[le] > probab{il}ity",
             "capab[le] > capab{il}ity", "credib[le] > credib{il}ity",
             "sensib[le] > sensib{il}ity", "stab[le] > stab{il}ity", "nob[le] > nob{il}ity",
             "hum[ble] > hum{il}ity | humble loses its b too",
         ]),
         ("-ate comes off before -able", [
             "separ[ate] > separable, inseparable", "toler[ate] > tolerable, intolerable",
             "negoti[ate] > negotiable", "irrit[ate] > irritable", "calcul[ate] > incalculable",
         ]),
         ("-or comes off before -ible", ["horr[or] > horrible", "terr[or] > terrible"]),
         ("Other endings", [
             "politic[s] > political, politician", "comment[ate] > commentary",
         ]),
     ]),
    ("The vowel changes", None, [
        (None, [
            "sp[eak] > sp{eech}, sp{eech}less", "l[o]ng > l{e}ngth, l{e}ngthy, l{e}ngthen",
            "str[o]ng > str{e}ngth, str{e}ngthen", "d[ee]p > d{e}pth", "wid[e] > width",
            "br[oa]d > br{ea}dth", "h[i]gh > h{ei}ght", "h[o]t > h{ea}t",
            "you[ng] > you{th}", "pr[ou]d > pr{i}de", "po[or] > poverty",
            "ch[oos]e > ch{oic}e", "lo[se] > lo{ss}", "d[ie] > d{ea}th", "s[i]ng > s{o}ng",
            "f[ee]d > f{oo}d", "bl[ee]d > bl{oo}d", "s[ell] > s{ale}", "fl[y] > fl{igh}t",
            "s[ee] > s{igh}t", "th[ink] > th{ough}t", "gi[ve] > gi{f}t",
            "maint[ai]n > maint{e}nance", "sust[ai]n > sust{e}nance",
            "ret[ai]n > ret{e}ntion", "det[ai]n > det{e}ntion", "abst[ai]n > abst{e}ntion",
            "desp[ai]r > desp{e}rate, desp{e}ration", "rep[ea]t > rep{e}tition, rep{e}titive",
        ]),
    ]),
    ("Countries and numbers", None, [
        ("Countries", [
            "Sp[ai]n > Sp{a}nish", "Brit[ain] > British", "Eng[land] > English",
            "Ir[eland] > Irish", "Pol[and] > Polish", "Fin[land] > Fin{n}ish",
            "Scot[land] > Scot{t}ish", "Portug[al] > Portug{u}ese", "Norw[ay] > Norw{eg}ian",
            "France > French", "Wales > Welsh", "Denmark > Danish", "Switzerland > Swiss",
            "the Netherlands > Dutch", "Greece > Greek",
        ]),
        ("Numbers", [
            "fo[u]r > forty | but fourteen and fourth keep the u", "fi[ve] > fi{f}th",
            "twel[ve] > twel{f}th", "th[ree] > th{ir}d",
        ]),
    ]),
]


APP_PAIRS = [
    ("able", "ability"), ("advice", "advise"), ("anxious", "anxiety"), ("clear", "clarify"),
    ("commentate", "commentary"), ("comprehend", "incomprehensible"),
    ("curious", "curiosity"), ("decide", "decisive"), ("decide", "indecisive"),
    ("disaster", "disastrous"), ("enter", "entrance"), ("famous", "fame"),
    ("flexible", "flexibility"), ("grammar", "grammatical"), ("hinder", "hindrance"),
    ("horror", "horrible"), ("hot", "heat"), ("infection", "infectious"), ("long", "length"),
    ("long", "lengthy"), ("maintain", "maintenance"), ("politics", "politician"),
    ("pronounce", "pronunciation"), ("repair", "irreparable"), ("repeat", "repetitive"),
    ("respond", "responsive"), ("science", "scientific"), ("science", "scientist"),
    ("separate", "inseparable"), ("solve", "solution"), ("speak", "speechless"),
    ("strong", "strength"), ("strong", "strengthen"), ("suspect", "suspicious"),
    ("tolerate", "tolerable"), ("wife", "wives"),
]

WATCH = [
    "The vowel in <b>speech</b> sounds just like the one in speak, but it is spelt ee. Here "
    "saying the word aloud does not help: learn the spelling.",
    "The ending -ment usually keeps the base word whole: announce &rarr; announcement, amaze "
    "&rarr; amazement. So it is <b>pronunciation</b> but <b>announcement</b>.",
    "Not every f becomes v: roof &rarr; roofs, chief &rarr; chiefs, belief &rarr; beliefs.",
    "deep &rarr; depth, but <b>deepen</b> keeps its ee.",
    "<b>advice</b> and <b>device</b> are nouns; <b>advise</b> and <b>devise</b> are verbs.",
    "<b>deciduous</b> is a real word, but it is about trees that lose their leaves in autumn. It "
    "has nothing to do with deciding. Someone who cannot decide is <b>indecisive</b>.",
]

CHECK_INTRO = ("Type the word made from the word in capitals, then press Check or Enter. The "
               "spelling has to be exact, as on the test.")
TYPED = [
    ("Her ___ (EXPLAIN) was so clear that everyone understood the problem at once.",
     "explanation", "explain loses its i, like exclaim → exclamation.", None),
    ("The first day of our holiday was ___ (DISASTER): our flight was cancelled and our bags "
     "were lost.", "disastrous", "disaster loses its e, like monster → monstrous.", None),
    ("Everyone was amazed by her ___ (GENEROUS): she gave half of her prize money to charity.",
     "generosity", "generous loses its u, like curious → curiosity.", None),
    ("My brother is very ___ (PERSUADE): in the end he always gets what he wants.",
     "persuasive", "the d becomes s, like decide → decisive.", None),
    ("___ (ADMIT) to the museum is free for children under twelve.",
     "admission", "the t becomes ss, like permit → permission.", None),
    ("When the balloon burst, it sounded like a small ___ (EXPLODE).",
     "explosion", "the d becomes s, like divide → division.", None),
    ("Lifting that heavy box took all my ___ (STRONG).",
     "strength", "the o becomes e, like long → length.", None),
    ("The ___ (WIDE) of the river here is about fifty metres.",
     "width", "the vowel changes, like deep → depth.", None),
]
CHECK_TIP = 'All eight right? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_formation_001", "SmartEn: word formation, sample test"),
    ("/ojaj/cwiczenia/ojaj_e3_slowotworstwo", "SmartEn: word formation, stage 3"),
]

# Shown in each list's "Advanced" box: C1-C2, formal or rare words (judged by hand, 2026-10-25).
ADVANCED = """
    administration wintry monstrous wondrous sobriety proclamation vanity provision evasion
    erosion intrusion pretence apprehension ascent descent submission omission transmission
    emission commission conversion diversion recession concession absorption deception
    perception conception presumption resumption dissolution compulsion expulsion repulsive
    acquisition inquisitive adhesive cohesion confidential substantial circumstantial
    sequential devise implication justification modification simplification pursuit
    notoriety capability credibility sensibility nobility humility negotiable incalculable
    breadth sustenance retention abstention
""".split()
