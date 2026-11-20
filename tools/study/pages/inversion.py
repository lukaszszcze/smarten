"""Study page: inversion (Hardly had I sat down, Not only did she).
Data for tools/study/gen_study.py.

The mistakes are Tadzio's misses on inversion items in the online tests up to 2026-11-10
(9 items, 12 misses), worked out with tools/ojaj/record_now.mjs.
The check sentences are new: none is in the vault or in a SmartEn exercise.
"""

KEY = "inversion"
TITLE = "Inversion"
HEAD_TITLE = "Inversion"
INDEX_TITLE = "Inversion"
BODY = "grammar"
EYEBROW = "Transformations and grammar"
LEDE = ("When a sentence starts with a negative or limiting word such as never, hardly, "
        "not only or only when, the words after it go in question order: "
        "<i>Never <b>have I</b> seen such a mess.</i> In the online tests this is one of the "
        "hardest kinds of question for you. Of your 12 misses, four kept the usual word "
        "order, two left out one small word and four were left empty.")

MISTAKES_INTRO = ("These are the inversion questions you got wrong in the online tests. Where "
                  "you left the gap empty, it says so.")
WIDE = True
MISTAKES = [
    {"task": ("I had only just sat down when the phone rang.", "HARDLY",
              "___ down when the phone rang."),
     "wrong": "hardly sat / had hadly sat", "right": "Hardly had I sat",
     "why": "Hardly comes first, then had, then I: <i>Hardly had I sat down</i>, like the "
            "question <i>Had I sat down?</i> Spell it h-a-r-d-l-y. The time is past perfect "
            "(had sat), because sitting down came before the phone rang."},
    {"task": ("I am not responsible for this mess at all.", "WAY",
              "___ responsible for this mess."),
     "wrong": "There's no way I'm (and once left empty)", "right": "In no way am I",
     "why": "There's no way I'm is fine when you speak, but short forms like there's and "
            "I'm lose the point in this task. A gap at the start with WAY is a sign that the "
            "task wants <i>In no way</i> and the question order after it: <i>am I</i>."},
    {"task": ("I didn't suspect at all that he was lying.", "MOMENT",
              "Not for ___ he was lying."),
     "wrong": "moment did I suspect that", "right": "a moment did I suspect that",
     "why": "The inversion was right. The phrase is <i>not for a moment</i>, and the a "
            "was missing."},
    {"task": ("I didn't realise I had lost my keys until I got home.", "UNTIL",
              "Not ___ realise that I had lost my keys."),
     "wrong": "until I got home did", "right": "until I got home did I",
     "why": "The inversion is did + I, so the I belongs in the gap too. Read the whole "
            "sentence when you finish: <i>did realise</i> has no subject."},
    {"task": ("You must never open this door, whatever happens.", "CIRCUMSTANCES",
              "___ open this door."),
     "wrong": "(left empty)", "right": "Under no circumstances must you",
     "why": "never ... whatever happens means <i>under no circumstances</i>. You got this "
            "right three times when Under was printed before the gap; here the whole phrase "
            "goes in the gap, so it starts with a capital U."},
    {"wrong": "Only when I got home had I realised that I had lost my wallet.",
     "right": "Only when I got home did I realise that I had lost my wallet.",
     "why": "Keep the tense of the plain sentence. I realised (past simple) becomes "
            "<i>did I realise</i>. had is only for the past perfect: I had realised becomes "
            "had I realised."},
    {"wrong": "Not only she had baked the cake, but she also made all the decorations.",
     "right": "Not only did she bake the cake, but she also made all the decorations.",
     "why": "Not only at the start needs the question order. She baked becomes "
            "<i>did she bake</i>, with bake in its base form."},
    {"wrong": "So hot the soup was that I couldn't eat it.",
     "right": "So hot was the soup that I couldn't eat it.",
     "why": "So + adjective at the start: was comes before the soup."},
    {"wrong": "(left empty)",
     "right": "Such was his surprise that he couldn't say a word.",
     "why": "<i>Such was his surprise that</i> means his surprise was so great that. "
            "was, not were, because surprise is one thing; with a plural it is were: "
            "<i>Such were the crowds that ...</i>"},
]

RULE_TITLE = "The rule"
RULE_HTML = """    <h3>Question order after a negative word</h3>
    <div class="fact">
      <p>Put the negative or limiting word first. Then the words go as in a question: the helping verb, then the subject, then the main verb.</p>
      <ul>
        <li>I have never seen such a mess. &rarr; <b>Never have I seen</b> such a mess. (Have I seen ...?)</li>
        <li>She rarely complains. &rarr; <b>Rarely does she complain.</b> (Does she complain?)</li>
        <li>I didn't know the truth. &rarr; <b>Little did I know</b> the truth. (Did I know ...?)</li>
      </ul>
    </div>

    <h3>Which helping verb</h3>
    <p>Use the one the question would use. Keep the tense of the plain sentence.</p>
    <div class="scroll">
      <table class="grid">
        <thead><tr><th>The plain sentence</th><th>After the negative word</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td>present simple</td><td>do / does + subject + base form</td><td class="ex">Rarely do we eat out. Seldom does he smile.</td></tr>
          <tr><td>past simple</td><td>did + subject + base form</td><td class="ex">Not only did she bake the cake ... (not did she baked)</td></tr>
          <tr><td>present perfect</td><td>have / has + subject + past participle</td><td class="ex">Never have I seen such a mess.</td></tr>
          <tr><td>past perfect</td><td>had + subject + past participle</td><td class="ex">Hardly had I sat down when the phone rang.</td></tr>
          <tr><td>be</td><td>am / is / are / was / were + subject</td><td class="ex">In no way am I responsible. So hot was the soup that ...</td></tr>
          <tr><td>will, can, must, should</td><td>the same verb + subject + base form</td><td class="ex">Nowhere will you find a better pizza. Under no circumstances must you open this door.</td></tr>
        </tbody>
      </table>
    </div>

    <h3>The words that start it</h3>
    <div class="scroll">
      <table class="grid">
        <thead><tr><th>Words</th><th>Meaning</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td>Never, Never before</td><td>not ever</td><td class="ex">Never before had I seen so many people.</td></tr>
          <tr><td>Rarely, Seldom</td><td>not often</td><td class="ex">Seldom do we go to the cinema.</td></tr>
          <tr><td>Little</td><td>not at all (with know, realise, suspect, think)</td><td class="ex">Little did I know that my friends were planning a party.</td></tr>
          <tr><td>At no time</td><td>never</td><td class="ex">At no time did he say anything about it.</td></tr>
          <tr><td>In no way, By no means</td><td>not at all</td><td class="ex">In no way am I responsible. By no means is it easy.</td></tr>
          <tr><td>Under no circumstances, In no circumstances, On no account</td><td>never, whatever happens (often with must, should, can)</td><td class="ex">On no account should you touch it.</td></tr>
          <tr><td>Nowhere</td><td>not anywhere</td><td class="ex">Nowhere will you find a better pizza.</td></tr>
          <tr><td>Not once, Not a single + noun, Not for a moment</td><td>not even once, not even one, not at all</td><td class="ex">Not once did he say thank you. Not a single word did he say. Not for a moment did I suspect him.</td></tr>
          <tr><td>Neither, Nor</td><td>and also not</td><td class="ex">I can't swim, and neither can my brother.</td></tr>
        </tbody>
      </table>
    </div>

    <h3>Phrases with two parts</h3>
    <div class="fact">
      <ul>
        <li><b>Not only ... but (also)</b>: the question order only in the first part. <i>Not only did she bake the cake, but she also made the decorations.</i></li>
        <li><b>Hardly / Scarcely / Barely ... when</b> and <b>No sooner ... than</b>: one thing happened just after another. The first part is past perfect, the second past simple. <i>Hardly had I sat down when the phone rang. No sooner had I sat down than the phone rang.</i></li>
        <li><b>So + adjective + be ... that</b>: <i>So hot was the soup that I couldn't eat it.</i></li>
        <li><b>Such + be + noun ... that</b>: <i>Such was his surprise that he couldn't say a word.</i> Use were with a plural noun.</li>
      </ul>
    </div>

    <h3>Only and Not until: the question order comes later</h3>
    <div class="fact">
      <p>After Only when, Only after, Only if, Only by and Not until, the whole first part comes first, in the usual order. The question order goes in the second part.</p>
      <ul>
        <li><b>Only when</b> I got home <b>did I realise</b> that I had lost my wallet.</li>
        <li><b>Only by</b> working hard <b>can you</b> pass the exam.</li>
        <li><b>Not until</b> I got home <b>did I realise</b> that I had lost my keys.</li>
        <li><b>Only then</b> and <b>Only later</b> have no first part, so the question order comes straight after them: <i>Only then did I understand.</i></li>
      </ul>
    </div>

    <h3>The same order in conditionals</h3>
    <p>A conditional can drop if and start with had, were or should in the same question order: <i>Had I known, I would have come.</i> <i>Were I you, I would apologise.</i> <i>Should you need help, call me.</i></p>"""
LEGEND = ""

WATCH = [
    "Question order only when the negative word starts the sentence. In the middle of a "
    "sentence the order stays as usual: I have never seen such a mess. I had hardly sat "
    "down when the phone rang.",
    "No question order when only or hardly belongs to the subject: <i>Only Tom knew the "
    "answer. Hardly anyone came.</i>",
    "Hardly goes with when, No sooner with than. Never <i>no sooner ... when</i>.",
    "After do, does and did the verb is in its base form: <i>did I realise</i>, not did I "
    "realised.",
    "<i>It was not until I got home that I realised</i> means the same as Not until I got "
    "home did I realise, but it keeps the usual order. If the gap starts with It was, use "
    "this form.",
    "No short forms in transformations: there's, I'm and didn't lose the point. Count the "
    "words too: up to six, the key word included. <i>Under no circumstances must you</i> "
    "is five.",
    "Before you move on, read the whole sentence with your answer in it. A missing a, I or "
    "did is easy to hear that way.",
]

CHECK_INTRO = ("Type the missing words in the first four; capitals do not matter, but every "
               "letter does. For the last four, write your answer on paper first, then open "
               "the answer.")
TYPED = [
    ("Hardly ___ (I / close) my eyes when the alarm went off.", "had I closed",
     "Hardly first, then had + I + past participle.", None),
    ("Not only ___ (he / break) the window, but he also lied about it.", "did he break",
     "Past simple becomes did + he + base form.", None),
    ("So cold ___ (the water / be) that nobody wanted to swim.", "was the water",
     "So + adjective first, then was before the subject.", None),
    ("Only after the film had finished ___ (we / notice) how late it was.", "did we notice",
     "The question order goes in the second part, after the whole only phrase.", None),
]
DETAILS = [
    ("I had only just got into bed when my phone buzzed.", "SOONER",
     "No ___ than my phone buzzed.",
     '<span class="ans">sooner had I got into bed</span>. No sooner + had + I + past '
     "participle, then than. Six words with the key word, which is the limit."),
    ("You must not tell anyone about this, whatever happens.", "ACCOUNT",
     "On ___ anyone about this.",
     '<span class="ans">no account must you tell</span> (or should you tell). On no account '
     "= never, whatever happens."),
    ("I don't agree with you at all.", "WAY", "___ with you.",
     '<span class="ans">In no way do I agree</span>. In no way + do + I + agree: the present '
     "simple takes do."),
    ("The noise was so loud that we couldn't hear each other.", "SUCH",
     "___ that we couldn't hear each other.",
     '<span class="ans">Such was the noise</span>. Such + was + the noise, and was because '
     "noise is one thing."),
]
CHECK_TIP = 'Got them all? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/cwiczenia/sentence_transformation/transform_021",
     "SmartEn: transformations with inversion"),
    ("/cwiczenia/grammar_gaps/grammar_016", "SmartEn: inversion gaps"),
]
