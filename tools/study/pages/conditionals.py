"""Study page: conditionals (Conditionals and wish). Data for tools/study/gen_study.py.

"supposing" is left out: it is a key word in OJAJ online Test 03, which Tadzio has not seen.
"""

KEY = "conditionals"
TITLE = "Conditionals and wish"
HEAD_TITLE = "Conditionals and Wish"
INDEX_TITLE = "Conditionals and wish"
BODY = "grammar"
# Off the site for now: Lukasz put word formation and wisielec first (2026-10-25).
ON_INDEX = False
PUBLISH = False
EYEBROW = "Transformations and grammar"
LEDE = ("A conditional says what happens, or would happen, if something is true. Its form "
        "depends on the time: a real future, something that is not real now, or something "
        "that did not happen in the past. Most mistakes come from putting will or would in the "
        "if part, or from choosing the wrong past form.")

MISTAKES_INTRO = ""
WIDE = True
MISTAKES = [
    {"task": ("I am hungry now because I did not have breakfast.", "HAD",
              "I would not be hungry now ___ breakfast."),
     "wrong": "if I have had", "right": "if I had had",
     "why": "The breakfast was in the past, so the if part needs the past perfect: had had. "
            "The other part is about now: would not be."},
    {"wrong": "If I will see him, I will tell him.", "right": "If I see him, I will tell him.",
     "why": "No will in the if part."},
    {"wrong": "If I would have known, I would have helped.",
     "right": "If I had known, I would have helped.", "why": "No would in the if part either."},
    {"wrong": "Unless you don't hurry, you will be late.",
     "right": "Unless you hurry, you will be late.", "why": "unless already means if not."},
    {"wrong": "I wish I would be taller.", "right": "I wish I were taller.",
     "why": "wish + would is only for what other people do."},
]

RULE_TITLE = "The rule"
RULE_HTML = """    <h3>The four types, and the two mixed ones</h3>
    <div class="scroll">
      <table class="grid">
        <thead><tr><th>Type</th><th>The if part</th><th>The other part</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td>Zero: always true</td><td>present</td><td>present</td><td class="ex">If you heat ice, it melts.</td></tr>
          <tr><td>First: a real future</td><td>present</td><td>will + verb</td><td class="ex">If it rains tomorrow, we will stay at home.</td></tr>
          <tr><td>Second: not real now</td><td>past</td><td>would + verb</td><td class="ex">If I had a dog, I would walk it every day.</td></tr>
          <tr><td>Third: did not happen</td><td>had + past participle</td><td>would have + past participle</td><td class="ex">If we had left earlier, we would have caught the bus.</td></tr>
          <tr><td>Mixed: the past changes now</td><td>had + past participle</td><td>would + verb</td><td class="ex">If I had had breakfast, I would not be hungry now.</td></tr>
          <tr><td>Mixed: now changes the past</td><td>past</td><td>would have + past participle</td><td class="ex">If I were braver, I would have spoken to her.</td></tr>
        </tbody>
      </table>
    </div>
    <p>could and might can take the place of would: <i>If I had a bike, I could ride to school.</i></p>

    <h3>had had</h3>
    <p>The past perfect of have is had + had, and both words are needed: <i>If I had had more time, I would have finished.</i> The first had makes the tense; the second is the verb have.</p>

    <h3>Words that work like if</h3>
    <div class="fact">
      <ul>
        <li><b>unless</b> = if not: <i>Unless you hurry, you will miss the bus.</i></li>
        <li><b>as long as, so long as, provided (that), providing (that)</b> = only if: <i>You can stay up late provided that you finish your homework first.</i></li>
        <li><b>in case</b> = because something might happen, which is not the same as if: <i>Take an umbrella in case it rains.</i></li>
        <li><b>otherwise</b> = if not, starting a new part of the sentence: <i>Hurry up, otherwise we will be late.</i></li>
        <li><b>if it were not for, if it had not been for, but for</b> = without: <i>If it had not been for your help, I would have failed.</i></li>
        <li><b>even if</b> = it does not matter whether: <i>I will go even if it rains.</i></li>
        <li><b>what if</b> = imagine that: <i>What if we miss the last train?</i></li>
      </ul>
    </div>

    <h3>Without if: the verb comes first</h3>
    <div class="fact">
      <ul>
        <li><b>Should</b> you need help, call me. = If you need help, call me.</li>
        <li><b>Were</b> I you, I would apologise. = If I were you, I would apologise.</li>
        <li><b>Were</b> it not for the rain, we would go out. = If it were not for the rain, we would go out.</li>
        <li><b>Had</b> I known, I would have come earlier. = If I had known, I would have come earlier.</li>
      </ul>
      <p>Only should, were and had can do this. Not goes after the subject: <i>Had I not seen it, I would never have believed it.</i></p>
    </div>

    <h3>wish and if only</h3>
    <div class="scroll">
      <table class="grid">
        <thead><tr><th>You want</th><th>Form</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td>Now to be different</td><td>wish + past</td><td class="ex">I wish I knew the answer. I wish I were taller.</td></tr>
          <tr><td>The past to be different</td><td>wish + had + past participle</td><td class="ex">I wish I had listened to you.</td></tr>
          <tr><td>To be able to do something</td><td>wish + could</td><td class="ex">I wish I could swim.</td></tr>
          <tr><td>Someone else to change</td><td>wish + someone + would</td><td class="ex">I wish you would stop talking.</td></tr>
        </tbody>
      </table>
    </div>
    <p>if only means the same as I wish, only stronger: <i>If only I had studied harder!</i></p>"""

WATCH = [
    "Never will or would in the if part: if it rains (not if it will rain), if I had known "
    "(not if I would have known).",
    "<b>unless</b> means if not, so it never takes another not.",
    "<b>in case</b> is not if: take a coat in case it gets cold means take it now, because "
    "it might get cold.",
    "<b>If I were you</b> is the safe form in a test; if I was you is common in speech.",
    "When the if part comes first, put a comma after it: If you need help, call me. No comma "
    "when it comes second: Call me if you need help.",
    "Every transformation also needs the four checks on <a href=\"/ojaj_study/transformations\">"
    "the checklist</a>.",
]

CHECK_INTRO = "Write your answer on paper first, then open the answer."
DETAILS = [
    ("I didn't know it was your birthday, so I didn't buy you a present.", "KNOWN",
     "___ it was your birthday, I would have bought you a present.",
     '<span class="ans">If I had known</span>. Third conditional: had + past participle in '
     "the if part."),
    ("I'm sorry I didn't listen to your advice.", "WISH", "I ___ to your advice.",
     '<span class="ans">wish I had listened</span>. A regret about the past: wish + had + past '
     "participle."),
    ("You can go to the party, but only if you are home by ten.", "PROVIDED",
     "You can go to the party ___ home by ten.",
     '<span class="ans">provided (that) you are</span>. provided means only if, and there is '
     "no will after it."),
    ("If you don't hurry, you will miss the bus.", "UNLESS", "You will miss the bus ___.",
     '<span class="ans">unless you hurry</span>. unless already means if not.'),
    ("If you need any help, just ask me.", "SHOULD", "___ any help, just ask me.",
     '<span class="ans">Should you need</span>. Without if, should comes first.'),
    ("Without your help, I would never have finished the project.", "BEEN",
     "If it ___ your help, I would never have finished the project.",
     '<span class="ans">had not been for</span>. It is about the past, so if it had not been '
     "for."),
    ("I'm cold now because I didn't bring a jacket.", "BROUGHT",
     "If I ___ a jacket, I would not be cold now.",
     '<span class="ans">had brought</span>. Mixed: the past (had brought) changes now (would '
     "not be cold)."),
    ("It annoys me that my brother always takes my things.", "WISH",
     "I ___ taking my things.",
     '<span class="ans">wish my brother would stop</span>. wish + would, for something '
     "someone else does that annoys you."),
]
CHECK_TIP = 'Got them all? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_own_transformacje_01", "SmartEn: transformations (1)"),
    ("/ojaj/cwiczenia/ojaj_own_transformacje_02", "SmartEn: transformations (2)"),
]
