"""Study page: comparison (Comparison, too and enough). Data for tools/study/gen_study.py.

"than anyone else" is left out: it is the answer to an item in OJAJ online Test 03, which
Tadzio has not seen.
"""

KEY = "comparison"
TITLE = "Comparison, too and enough"
HEAD_TITLE = "Comparison, Too and Enough"
INDEX_TITLE = "Comparison, too and enough"
BODY = "grammar"
# Off the site for now: Lukasz put word formation and wisielec first (2026-10-25).
ON_INDEX = False
PUBLISH = False
EYEBROW = "Transformations and grammar"
LEDE = ("Comparing two things takes -er or more; picking the top one takes the -est or the "
        "most. Too and enough say whether something is possible. In transformations these "
        "patterns turn one sentence into another, and the mistakes are usually small: a "
        "missing for me, a more too many, an enough in the wrong place.")

MISTAKES_INTRO = ""
WIDE = True
MISTAKES = [
    {"task": ("The box was so heavy that I could not lift it.", "TOO", "The box was ___ lift."),
     "wrong": "too heavy to", "right": "too heavy for me to",
     "why": "The first sentence says that I could not lift it, so for me has to be there."},
    {"wrong": "Kuba is more taller than me.", "right": "Kuba is taller than me.",
     "why": "-er or more, never both."},
    {"wrong": "She is enough old to drive.", "right": "She is old enough to drive.",
     "why": "enough goes after an adjective."},
    {"wrong": "This is the most good pizza I have ever eaten.",
     "right": "This is the best pizza I have ever eaten.", "why": "good, better, best."},
    {"wrong": "My bag is heavier then yours.", "right": "My bag is heavier than yours.",
     "why": "than, not then."},
]

RULE_TITLE = "The rule"
RULE_HTML = """    <h3>-er and -est, or more and most</h3>
    <div class="scroll">
      <table class="grid">
        <thead><tr><th>Adjective</th><th>Comparing two</th><th>The top one</th></tr></thead>
        <tbody>
          <tr><td>one syllable</td><td>tall &rarr; taller, big &rarr; bigger, nice &rarr; nicer</td><td>the tallest, the biggest, the nicest</td></tr>
          <tr><td>two syllables, ending in -y</td><td>happy &rarr; happier, easy &rarr; easier</td><td>the happiest, the easiest</td></tr>
          <tr><td>two syllables or more</td><td>more careful, more interesting</td><td>the most careful, the most interesting</td></tr>
          <tr><td>irregular</td><td>good &rarr; better, bad &rarr; worse, far &rarr; further, little &rarr; less, much and many &rarr; more</td><td>the best, the worst, the furthest, the least, the most</td></tr>
        </tbody>
      </table>
    </div>
    <p>A few two-syllable adjectives take either form: cleverer or more clever, quieter or more quiet.</p>

    <h3>Ways of comparing</h3>
    <div class="fact">
      <ul>
        <li><b>not as ... as</b>: <i>Kuba is not as tall as Ola.</i> = Ola is taller than Kuba.</li>
        <li><b>the same as, similar to, different from</b>: <i>My phone is the same as yours.</i></li>
        <li><b>twice as ... as, half as ... as</b>: <i>This bag is twice as heavy as that one.</i></li>
        <li><b>the + -est + in</b> a place or a group, or <b>of</b> a time: <i>the tallest boy in the class</i>, <i>the best day of my life</i>.</li>
        <li><b>No other ... is as ... as</b>: <i>No other girl in the team is as fast as Ola.</i> = Ola is the fastest girl in the team.</li>
        <li><b>never ... before</b> becomes <b>the -est ... ever</b>: <i>I have never seen such a good film.</i> = It is the best film I have ever seen.</li>
        <li><b>the + -er, the + -er</b>: <i>The more you practise, the better you get.</i></li>
        <li><b>-er and -er</b>: <i>It is getting colder and colder.</i> <i>The film got more and more exciting.</i></li>
        <li><b>much, far, a lot, a bit, slightly</b> + -er: <i>much bigger</i>, <i>far more expensive</i>; never <i>very bigger</i>.</li>
      </ul>
    </div>

    <h3>too and enough</h3>
    <div class="scroll">
      <table class="grid">
        <thead><tr><th>Pattern</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td>too + adjective + to</td><td class="ex">It is too cold to swim.</td></tr>
          <tr><td>too + adjective + for someone + to</td><td class="ex">The box was too heavy for me to lift.</td></tr>
          <tr><td>adjective + enough + to</td><td class="ex">She is old enough to drive.</td></tr>
          <tr><td>enough + noun</td><td class="ex">We do not have enough money.</td></tr>
          <tr><td>too much + a noun you cannot count, too many + a plural</td><td class="ex">too much sugar, too many people</td></tr>
        </tbody>
      </table>
    </div>
    <p>When the sentence starts with the thing, it does not come back at the end: <i>The box was too heavy for me to lift</i>, not <i>to lift it</i>.</p>

    <h3>so and such</h3>
    <div class="fact">
      <ul>
        <li><b>so</b> + adjective (+ that): <i>It was so cold that we stayed in.</i></li>
        <li><b>such</b> + (a) + adjective + noun (+ that): <i>It was such a cold day that we stayed in.</i> <i>They are such nice people.</i></li>
        <li><b>so much, so many</b> + noun: <i>There were so many people that we could not get in.</i></li>
      </ul>
    </div>"""

WATCH = [
    "If the first sentence says who (I, we, my sister), keep it: too heavy for me to. This "
    "is check 3 on <a href=\"/ojaj_study/transformations\">the checklist</a>.",
    "-er or more, never both: taller, not more taller.",
    "<b>enough</b> goes after an adjective (old enough) but before a noun (enough time).",
    "<b>than</b> compares; <b>then</b> means after that.",
    "the comes before -est and most: the best, the most interesting.",
    "For distance you can say further or farther; for more of something, only further: "
    "further information.",
]

CHECK_INTRO = "Write your answer on paper first, then open the answer."
DETAILS = [
    ("The film was so scary that my sister could not watch it.", "TOO",
     "The film was ___ watch.",
     '<span class="ans">too scary for my sister to</span>. Six words, and for my sister keeps '
     "who could not watch it."),
    ("Ola is not old enough to see this film.", "YOUNG", "Ola is ___ see this film.",
     '<span class="ans">too young to</span>. Not old enough means too young.'),
    ("I have never read such an exciting book.", "MOST", "It is ___ book I have ever read.",
     '<span class="ans">the most exciting</span>. never ... before becomes the most ... ever.'),
    ("Kuba runs faster than Tomek.", "AS", "Tomek does not ___ Kuba.",
     '<span class="ans">run as fast as</span>. not as ... as turns the comparison round.'),
    ("If you practise more, you will play better.", "THE",
     "___ you practise, the better you will play.",
     '<span class="ans">The more</span>. the + -er, the + -er.'),
    ("We could not buy the tickets because they cost too much.", "EXPENSIVE",
     "The tickets were ___ buy.",
     '<span class="ans">too expensive for us to</span>. for us keeps who could not buy them.'),
    ("It was such a hot day that we stayed indoors.", "SO", "The day was ___ we stayed indoors.",
     '<span class="ans">so hot that</span>. so + adjective; such + noun.'),
    ("This test is much easier than the last one.", "DIFFICULT",
     "The last test was ___ this one.",
     '<span class="ans">much more difficult than</span>. much stays, because the difference '
     "is still big."),
]
CHECK_TIP = 'Got them all? Tick "I\'ve learnt this" at the top, then practise in SmartEn.'
PRACTICE = [
    ("/ojaj/cwiczenia/ojaj_own_transformacje_01", "SmartEn: transformations (1)"),
    ("/ojaj/cwiczenia/ojaj_own_transformacje_02", "SmartEn: transformations (2)"),
]
