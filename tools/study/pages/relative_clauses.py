"""Study page: relative-clauses (Relative clauses). Data for tools/study/gen_study.py.

Relative "when" is left out: OJAJ online Test 03, which Tadzio has not seen, has an item on it.
"""

KEY = "relative-clauses"
TITLE = "Relative clauses"
HEAD_TITLE = "Relative Clauses"
INDEX_TITLE = "Relative clauses"
BODY = "grammar"
# Off the site for now: Lukasz put word formation and wisielec first (2026-10-25).
ON_INDEX = False
PUBLISH = False
EYEBROW = "Transformations and grammar"
LEDE = ("A relative clause joins two sentences about the same person or thing: I have a "
        "cousin. She lives in Spain. &rarr; I have a cousin who lives in Spain. The choice of "
        "word depends on whether you mean a person or a thing, and on what comes before it.")

MISTAKES_INTRO = ""
WIDE = True
MISTAKES = [
    {"task": ("I have two older brothers. They both play in the school band.", "BOTH",
              "I have two older brothers, ___ play in the school band."),
     "wrong": "both of which", "right": "both of whom",
     "why": "Brothers are people, so whom. which is for things."},
    {"wrong": "The girl who I talked to her is new.", "right": "The girl who I talked to is new.",
     "why": "who already stands for her, so do not say her again."},
    {"wrong": "This is the boy who's dog bit me.", "right": "This is the boy whose dog bit me.",
     "why": "whose shows that something belongs to someone; who's means who is."},
    {"wrong": "My sister, that lives in Krakow, is a doctor.",
     "right": "My sister, who lives in Krakow, is a doctor.", "why": "No that after a comma."},
    {"wrong": "the friend with who I went to the cinema",
     "right": "the friend with whom I went to the cinema",
     "why": "After a preposition, whom for people."},
]

RULE_TITLE = "The rule"
RULE_HTML = """    <h3>Which word to use</h3>
    <div class="scroll">
      <table class="grid">
        <thead><tr><th>Word</th><th>For</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td>who</td><td>people</td><td class="ex">The girl who sits next to me is from Spain.</td></tr>
          <tr><td>whom</td><td>people, after a preposition, or as the object in formal English</td><td class="ex">The man to whom I spoke was very helpful.</td></tr>
          <tr><td>which</td><td>things and animals</td><td class="ex">The book which I borrowed is really good.</td></tr>
          <tr><td>that</td><td>people or things, but only without commas</td><td class="ex">The film that we saw was scary.</td></tr>
          <tr><td>whose</td><td>something that belongs to a person or a thing</td><td class="ex">That is the boy whose dog follows him to school.</td></tr>
          <tr><td>where</td><td>places</td><td class="ex">This is the park where we played as children.</td></tr>
        </tbody>
      </table>
    </div>

    <h3>With commas or without</h3>
    <div class="fact">
      <ul>
        <li><b>Without commas</b>, the clause tells you which one you mean: <i>The teacher who helped me has left.</i> Which teacher? The one who helped me.</li>
        <li><b>With commas</b>, it only adds something about a person or thing that is already clear: <i>My uncle, who lives in Gdansk, is a pilot.</i> Here you cannot use that, and you cannot leave the word out.</li>
        <li>which after a comma can stand for the whole sentence before it: <i>Ola won the race, which surprised everyone.</i></li>
      </ul>
    </div>

    <h3>Leaving the word out</h3>
    <p>Without commas, you can leave out who, which or that when it is the object of the clause: <i>The book (that) I am reading is great.</i> You cannot leave it out when it is the subject: <i>the girl who won the prize</i>, not <i>the girl won the prize</i>.</p>

    <h3>With a preposition</h3>
    <div class="fact">
      <ul>
        <li>Formal: the preposition comes first, then whom or which: <i>the friend with whom I travelled</i>, <i>the house in which I grew up</i>.</li>
        <li>Everyday: the preposition goes to the end: <i>the friend I travelled with</i>, <i>the house I grew up in</i>.</li>
        <li>Never who or that straight after a preposition: <i>with whom</i>, not <i>with who</i>.</li>
      </ul>
    </div>

    <h3>both of whom, some of which</h3>
    <p>After a word of amount and of, use whom for people and which for things, with a comma before it.</p>
    <div class="scroll">
      <table class="grid">
        <thead><tr><th>Amount</th><th>People</th><th>Things</th></tr></thead>
        <tbody>
          <tr><td>both</td><td>both of whom</td><td>both of which</td></tr>
          <tr><td>all</td><td>all of whom</td><td>all of which</td></tr>
          <tr><td>none, neither</td><td>none of whom, neither of whom</td><td>none of which, neither of which</td></tr>
          <tr><td>some, many, most</td><td>some of whom, many of whom, most of whom</td><td>some of which, many of which, most of which</td></tr>
          <tr><td>one, two, each</td><td>one of whom, two of whom, each of whom</td><td>one of which, two of which, each of which</td></tr>
        </tbody>
      </table>
    </div>
    <p class="ex">I have two older brothers, both of whom play in the school band. We bought two cakes, neither of which was fresh.</p>"""

WATCH = [
    "People take who or whom; things take which. Brothers, friends and teachers: whom. Cars, "
    "books and castles: which.",
    "No that after a comma, and no that straight after a preposition.",
    "Do not say the person or thing twice: the film which I saw, not the film which I saw it.",
    "<b>who's</b> means who is; <b>whose</b> means belonging to whom.",
    "A pet can take who: our dog, who is ten, still loves long walks.",
    "Every transformation also needs the four checks on <a href=\"/ojaj_study/transformations\">"
    "the checklist</a>.",
]

CHECK_INTRO = "Write your answer on paper first, then open the answer."
DETAILS = [
    ("I have two cousins. Neither of them likes football.", "WHOM",
     "I have two cousins, ___ likes football.",
     '<span class="ans">neither of whom</span>. Cousins are people, so whom; and neither '
     "takes likes, not like."),
    ("We visited three castles. All of them were built in the Middle Ages.", "WHICH",
     "We visited three castles, ___ built in the Middle Ages.",
     '<span class="ans">all of which were</span>. Castles are things, so which.'),
    ("This is the girl. I told you about her.", "WHOM", "This is the girl ___ told you.",
     '<span class="ans">about whom I</span>. The preposition comes first, then whom.'),
    ("My aunt's dog is huge. She lives next door.", "WHOSE",
     "My aunt, ___ is huge, lives next door.",
     '<span class="ans">whose dog</span>. whose shows that the dog belongs to my aunt.'),
    ("Kasia won the competition. This surprised everyone.", "WHICH",
     "Kasia won the competition, ___ everyone.",
     '<span class="ans">which surprised</span>. which after a comma can stand for the whole '
     "sentence before it."),
    ("That is the hotel. We stayed there last summer.", "WHERE",
     "That is the hotel ___ last summer.",
     '<span class="ans">where we stayed</span>. where is for places. In which we stayed means '
     "the same, but the key word is WHERE."),
    ("I met lots of people at the camp. Most of them were from Spain.", "WHOM",
     "I met lots of people at the camp, ___ from Spain.",
     '<span class="ans">most of whom were</span>. People, so whom.'),
]
CHECK_TIP = 'Got them all? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_own_transformacje_01", "SmartEn: transformations (1)"),
    ("/ojaj/cwiczenia/ojaj_own_transformacje_02", "SmartEn: transformations (2)"),
]
