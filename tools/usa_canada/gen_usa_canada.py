"""Practice exercises on the 2026/27 kuratoryjny etap rejonowy theme (3.12.2026).

The theme: geography, nature and national parks of the USA and Canada, plus nature
vocabulary and idioms (landscape, weather, plants, animals). Every fact is taken
from the syllabus's own reading list (programme, section IV.3, etap rejonowy):
kids-world-travel-guide USA and Canada facts, Ducksters US geography (regions,
rivers, lakes, mountain ranges, deserts), the 50 state capitals, the largest US
national parks, National Geographic's photos of the US parks (parks 1-20),
butterinsurance on Canada's provinces, canadiansky's top 10 Canadian parks and
WWF's 10 iconic Canadian animals. Where a source is wrong (kids-world gives
Badwater Basin as +86 m) the correct fact is used.

Shapes copy the regional paper's culture tasks: open knowledge questions worth 6
points (a 2-point question asks two things, each in its own field via
`secondAnswer`), and matching of 6 names to 10 descriptions with 4 left over.
Language exercises on the theme: idioms (multiple choice), a reading text with
T/F/NI statements, and spelling of nature words with given letters.

Open answers are marked by exact match after lower-casing, so every key lists
its variants (with and without "the", "Mount"/"Mt", "National Park").

Usage (from the repo root):
    python3 tools/usa_canada/gen_usa_canada.py           # checks, writes tmp/usa_canada_review.md
    python3 tools/usa_canada/gen_usa_canada.py --write   # also writes the JSON and index entries
"""
import json
import os
import random
import sys

BASE = "pub/konkursy/angielski/data/practice"
PREFIX = "USA i Kanada: "


def the(*names):
    """Each name with and without a leading "the"."""
    out = []
    for n in names:
        out += [n, "the " + n]
    return out


def mount(name):
    """Mount X, Mt X, Mt. X and X."""
    return [f"Mount {name}", f"Mt {name}", f"Mt. {name}", name]


def park(*names):
    """A park's name alone and with "National Park"."""
    out = []
    for n in names:
        out += [n, n + " National Park"]
    return out


# --- open knowledge questions -------------------------------------------------

KQ_INSTRUCTION = (
    "Rozwiaz zadania (1.1.-1.{n}.), udzielajac odpowiedzi w jezyku angielskim. "
    "Wymagana jest pelna poprawnosc merytoryczna i jezykowa odpowiedzi."
)
KQ_TWO = " W zadaniach za 2 punkty nalezy wpisac dwie odpowiedzi - kazda w osobnym polu."

# (id, title, [(question, answer list, secondAnswer list or None)])
KNOWLEDGE = [
    ("knowledge_033", "rzeki i jeziora USA", [
        ("Which is the longest river in the USA?",
         the("Missouri", "Missouri River"), None),
        ("In which lake does the Mississippi River begin, and into which body of water "
         "does it flow?",
         ["Lake Itasca", "Itasca"], the("Gulf of Mexico")),
        ("Which is the only one of the five Great Lakes that lies entirely in the USA?",
         ["Lake Michigan", "Michigan"], None),
        ("Which river carved the Grand Canyon?",
         the("Colorado", "Colorado River"), None),
        ("Which is the deepest lake in the USA?",
         ["Crater Lake"], None),
    ]),
    ("knowledge_034", "gory i pustynie USA", [
        ("What is the highest mountain in the USA, and in which state is it?",
         mount("Denali") + mount("McKinley"), ["Alaska"]),
        ("Which mountain range stretches about 1,500 miles from northern Alabama to Maine?",
         the("Appalachian Mountains", "Appalachians", "Appalachian Range"), None),
        ("What is the highest peak of the Rocky Mountains?",
         mount("Elbert"), None),
        ("In which desert does the Joshua tree grow?",
         the("Mojave", "Mojave Desert", "Mohave", "Mohave Desert"), None),
        ("Which tree of the Great Basin Desert is the oldest known living organism in "
         "the world?",
         the("bristlecone pine", "bristlecone pines", "Great Basin bristlecone pine",
             "bristlecone"), None),
    ]),
    ("knowledge_035", "stany i regiony USA", [
        ("What is the capital of California, and what is the capital of Texas?",
         ["Sacramento"], ["Austin"]),
        ("What is the capital of Alaska?",
         ["Juneau"], None),
        ("Which is the largest US state by area, and which is the smallest?",
         ["Alaska"], ["Rhode Island"]),
        ("Texas, Oklahoma, New Mexico and Arizona make up one region of the USA. "
         "What is it called?",
         the("Southwest", "South West", "Southwest region", "American Southwest"), None),
    ]),
    ("knowledge_036", "geografia Kanady", [
        ("What is the highest mountain in Canada, and in which national park is it?",
         mount("Logan"), park("Kluane") + ["Kluane National Park and Reserve"]),
        ("Which is the largest lake that lies entirely within Canada?",
         ["Great Bear Lake", "the Great Bear Lake"], None),
        ("Which is the longest river (river system) in Canada?",
         the("Mackenzie", "Mackenzie River", "Mackenzie River system"), None),
        ("What is the capital of Canada, and which is Canada's largest city?",
         ["Ottawa"], ["Toronto"]),
    ]),
    ("knowledge_037", "prowincje Kanady", [
        ("In which province are Banff and Jasper National Parks?",
         ["Alberta"], None),
        ("Which province is famous for its red sand beaches and is the setting of "
         "\"Anne of Green Gables\"?",
         ["Prince Edward Island", "PEI", "P.E.I."], None),
        ("Which is the only officially bilingual (English and French) province of Canada?",
         ["New Brunswick"], None),
        ("In which province is the Cabot Trail on Cape Breton Island?",
         ["Nova Scotia"], None),
        ("Which Prairie province grows 45% of Canada's grain?",
         ["Saskatchewan"], None),
        ("Which province has the most easterly point in North America?",
         ["Newfoundland and Labrador", "Newfoundland & Labrador", "Newfoundland"], None),
    ]),
    ("knowledge_038", "rekordy i symbole", [
        ("What is the national animal of the USA, and what is the national animal of "
         "Canada?",
         the("American bison", "bison", "buffalo", "American buffalo"),
         the("beaver", "North American beaver", "Canadian beaver")),
        ("What is the national bird of the USA?",
         the("bald eagle"), None),
        ("Which is the largest national park in the USA?",
         park("Wrangell-St. Elias", "Wrangell-St Elias", "Wrangell-Saint Elias",
              "Wrangell St. Elias", "Wrangell St Elias", "Wrangell – St. Elias",
              "Wrangell–St. Elias"), None),
        ("What is the name of the lowest point in North America, in Death Valley?",
         ["Badwater Basin", "Badwater", "the Badwater Basin"], None),
        ("What is the name of the Canadian part of Niagara Falls, the most powerful "
         "waterfall in North America?",
         the("Horseshoe Falls", "Horseshoe Fall", "Canadian Horseshoe Falls"), None),
    ]),
]

# --- matching -------------------------------------------------------------------

MATCH_INSTRUCTION = (
    "Do podanych nazw (1.1.-1.6.) dopasuj zwiazane z nimi {what} (A-J). Cztery "
    "{what2} zostaly podane dodatkowo i nie odnosza sie do zadnej nazwy."
)

# (id, title, what, what2, [(label, right option)], [4 extra options])
MATCHING = [
    ("matching_025", "stolice stanow USA", "stolice", "stolice", [
        ("New York", "Albany"),
        ("Florida", "Tallahassee"),
        ("Illinois", "Springfield"),
        ("Pennsylvania", "Harrisburg"),
        ("Washington", "Olympia"),
        ("Nevada", "Carson City"),
    ], ["Miami", "Chicago", "Seattle", "Las Vegas"]),
    ("matching_026", "parki narodowe USA (1)", "opisy", "opisy", [
        ("Yellowstone", "America's first national park, with geysers such as the Great "
                        "Fountain Geyser"),
        ("Sequoia", "the home of General Sherman, the largest tree in the world by volume"),
        ("Crater Lake", "a park in Oregon with the deepest lake in the USA"),
        ("Everglades", "one of the world's largest tropical wetlands, in Florida"),
        ("Arches", "more than 2,000 natural stone arches shaped by weathering and erosion"),
        ("Mammoth Cave", "more than 400 miles of caves under the hills of Kentucky"),
    ], ["the highest sand dunes in North America, in Colorado",
        "the driest and hottest place in North America",
        "the only tropical reef in the continental USA, next to a 19th-century fort",
        "mountains named after the hazy 'smoke' made by fog and the trees"]),
    ("matching_027", "parki narodowe USA (2)", "opisy", "opisy", [
        ("Death Valley", "the lowest point in North America and a world record "
                         "temperature of 134°F"),
        ("Great Smoky Mountains", "a park in Tennessee whose mountains are named after "
                                  "the haze made by fog and the trees"),
        ("Bryce Canyon", "red rock spires called hoodoos, seen by over 2.7 million "
                         "visitors a year"),
        ("Joshua Tree", "twisted, spiky trees in the Mojave Desert, threatened by "
                        "climate change"),
        ("Grand Teton", "a mountain range photographed from Schwabacher Landing on the "
                        "Snake River"),
        ("Olympic", "73 miles of coastline with sea stacks and tide pools in "
                    "Washington State"),
    ], ["'moonbows' under the full moon over a famous waterfall in California",
        "the world's largest International Dark Sky Reserve, in the Chihuahuan Desert",
        "the oldest, largest and tallest coast redwoods",
        "Bass Harbor Head Lighthouse on the coast of Maine"]),
    ("matching_028", "stolice prowincji Kanady", "stolice", "stolice", [
        ("Alberta", "Edmonton"),
        ("British Columbia", "Victoria"),
        ("Saskatchewan", "Regina"),
        ("Quebec", "Quebec City"),
        ("Manitoba", "Winnipeg"),
        ("Nunavut", "Iqaluit"),
    ], ["Calgary", "Vancouver", "Saskatoon", "Montreal"]),
    ("matching_029", "parki narodowe Kanady", "opisy", "opisy", [
        ("Banff", "Canada's oldest national park, visited since 1885"),
        ("Jasper", "a Dark Sky Preserve in Alberta with icefields, teal lakes, elk and "
                   "caribou"),
        ("Gros Morne", "granite mountains and deep fjords in Newfoundland and Labrador"),
        ("Thousand Islands", "one of Canada's smallest national parks, with more than "
                             "20 granite islands in Ontario"),
        ("Pacific Rim", "temperate rainforest and sandy beaches on Vancouver Island, "
                        "with the West Coast Trail"),
        ("Wood Buffalo", "the largest national park in Canada"),
    ], ["the only caribou herd south of the St. Lawrence River",
        "Takkakaw Falls, one of the highest waterfalls in Canada",
        "a place in Alberta where the prairies meet the Rocky Mountains",
        "Mount Logan, the highest mountain in Canada"]),
    ("matching_030", "zwierzeta Kanady", "opisy", "opisy", [
        ("beaver", "North America's largest rodent, called 'nature's engineer'"),
        ("moose", "the largest member of the deer family, a strong swimmer"),
        ("polar bear", "at least two-thirds of the world's population live in Canada, "
                       "and it hunts from sea ice"),
        ("monarch butterfly", "every autumn it flies 4,000 to 5,000 km to Mexico"),
        ("beluga whale", "known as the 'canary of the sea' because of the many sounds "
                         "it makes"),
        ("Atlantic puffin", "the provincial bird of Newfoundland, which dives up to "
                            "60 m to catch fish"),
    ], ["it appears on Canada's 25-cent coin",
        "its paws work like snowshoes when it hunts hares in deep snow",
        "both males and females have tusks up to about 0.9 m long",
        "a large bird that migrates in a V formation at up to 96 km/h"]),
]

# --- idioms (multiple choice) -----------------------------------------------------

# (stem, [A, B, C], right letter)
IDIOMS = [
    ("I've been feeling a bit under the _________ since Monday, so I stayed at home.",
     ["weather", "storm", "cloud"], "A"),
    ("Don't worry about their argument - it was just a storm in a _________.",
     ["teacup", "bucket", "river"], "A"),
    ("I'll be at the match on Saturday, come rain or _________.",
     ["snow", "shine", "wind"], "B"),
    ("He's only a fair-_________ friend: he disappears as soon as you need help.",
     ["sky", "weather", "season"], "B"),
    ("It's only a small scratch. You're making a mountain out of a _________.",
     ["hill", "molehill", "rock"], "B"),
    ("Stop beating about the _________ and tell me what really happened.",
     ["tree", "bush", "forest"], "B"),
    ("The patient is doing better, but he isn't out of the _________ yet.",
     ["woods", "fields", "hills"], "A"),
    ("Our donation is only a drop in the _________ compared with what the park needs.",
     ["lake", "ocean", "river"], "B"),
    ("She had never skied before, but she took to it like a duck to _________.",
     ["water", "snow", "ice"], "A"),
    ("Let's nip this problem in the _________ before it gets any worse.",
     ["leaf", "bud", "root"], "B"),
    ("The pollution we can see is only the tip of the _________.",
     ["iceberg", "mountain", "glacier"], "A"),
    ("I was going to tell them my news, but my brother stole my _________ by telling "
     "them first.",
     ["lightning", "thunder", "rain"], "B"),
]

# --- reading: T/F/NI ----------------------------------------------------------------

READING_TEXT = """YELLOWSTONE: THE PARK ON TOP OF A VOLCANO

In 1872 President Ulysses S. Grant signed a law that created Yellowstone, the first national park in the United States. Most of the park lies in Wyoming, but small parts of it are in Montana and Idaho. Under the forests and meadows there is a huge volcano, and its heat is what makes Yellowstone so unusual.

The park has about half of all the active geysers in the world. The most famous of them, Old Faithful, shoots hot water and steam into the air roughly every ninety minutes, and crowds gather on the benches around it to wait. Not far away lies Grand Prismatic Spring, the largest hot spring in the country. Its blue centre is surrounded by rings of yellow, orange and red. These colours are not painted by minerals, as many visitors think, but by billions of tiny living things that love hot water.

Yellowstone is also one of the best places in North America to watch wildlife. Bison have lived here without a break since prehistoric times. Wolves were not so lucky: by the 1920s people had killed the last of them, and they only returned in 1995, when scientists brought a group from Canada. Today visitors can also see elk, grizzly bears and, with some luck, a moose.

Watching animals comes with rules. Visitors must stay at least 100 yards from bears and wolves, and at least 25 yards from every other animal, including bison, which can run three times faster than a person. In the geyser areas everyone has to stay on the wooden boardwalks, because the ground can be a thin crust over boiling water. Every year a few people ignore the signs, and some of them pay for it with serious burns."""

# (statement, answer, explanation)
READING_ITEMS = [
    ("Yellowstone was the first national park in the United States.", "T",
     "TRUE - '... created Yellowstone, the first national park in the United States.'"),
    ("Most of the park lies in Montana.", "F",
     "FALSE - 'Most of the park lies in Wyoming, but small parts of it are in Montana "
     "and Idaho.'"),
    ("Old Faithful is the tallest geyser in the park.", "NI",
     "NO INFORMATION - the text says it is the most famous, not how tall it is."),
    ("The colours of Grand Prismatic Spring come from minerals in the water.", "F",
     "FALSE - 'These colours are not painted by minerals ... but by billions of tiny "
     "living things.'"),
    ("Wolves have lived in Yellowstone without a break since 1872.", "F",
     "FALSE - 'by the 1920s people had killed the last of them, and they only "
     "returned in 1995.'"),
    ("The wolves brought to the park in 1995 came from Canada.", "T",
     "TRUE - '... when scientists brought a group from Canada.'"),
    ("Visitors have to keep further away from bears than from bison.", "T",
     "TRUE - 100 yards from bears and wolves, 25 yards from every other animal, "
     "including bison."),
    ("Visitors may leave the boardwalks if a park ranger is with them.", "NI",
     "NO INFORMATION - the text says everyone has to stay on the boardwalks and says "
     "nothing about rangers."),
]

READING_INSTRUCTION = (
    "Przeczytaj ponizszy tekst. Zdecyduj, ktore zdania (1.1.-1.8.) sa zgodne z trescia "
    "tekstu (T - True), ktore sa niezgodne (F - False), a ktore zawieraja informacje "
    "niepodane w tekscie (NI - No Information)."
)

# --- spelling of nature words ------------------------------------------------------

# (sentence with {} for the gap, answer, indices of the letters given)
SPELLING = [
    ("Thousands of years ago a huge {} covered this valley, but the ice has slowly "
     "melted since.", "glacier", [3]),
    ("Over millions of years the river has cut a deep {} with steep red walls.",
     "canyon", [3]),
    ("About every ninety minutes the {} shoots hot water and steam high into the air.",
     "geyser", [3]),
    ("After six months without rain, the {} destroyed most of the farmers' crops.",
     "drought", [3]),
    ("The {} hit the coast of Florida with winds of over 200 km/h.",
     "hurricane", [5]),
    ("We couldn't see the road in the {}, so we waited in the car until the snow "
     "stopped.", "blizzard", [4]),
    ("In Saskatchewan the flat {} stretches as far as the eye can see.",
     "prairie", [4]),
    ("Skiers must stay on the marked runs because of the risk of an {}.",
     "avalanche", [5]),
    ("Wetlands are the natural {} of many birds, frogs and insects.",
     "habitat", [4]),
    ("Only 72 southern resident killer whales are left, so they are an {} species.",
     "endangered", [5]),
]

SPELLING_INSTRUCTION = (
    "Uzupelnij luki w zdaniach (1.1.-1.{n}.). Wpisz w kazda luke jeden wyraz, tak aby "
    "otrzymac logiczne i gramatycznie poprawne zdania. Podane sa wybrane litery "
    "wyrazu. Wymagana jest pelna poprawnosc ortograficzna."
)


# --- building ---------------------------------------------------------------------

def build_knowledge(eid, title, questions):
    items = []
    for i, (q, ans, second) in enumerate(questions, 1):
        item = {"id": f"1.{i}", "question": q, "answer": ans,
                "points": 2 if second else 1}
        if second:
            item["secondAnswer"] = second
        items.append(item)
    n = len(items)
    instruction = KQ_INSTRUCTION.format(n=n)
    if any("secondAnswer" in it for it in items):
        instruction += KQ_TWO
    points = sum(it["points"] for it in items)
    task = {"id": "1", "type": "knowledge_questions", "points": points,
            "instruction": instruction, "items": items}
    return eid, PREFIX + title, task


def build_matching(eid, title, what, what2, pairs, extra):
    rng = random.Random(eid)
    texts = [right for _, right in pairs] + extra
    order = texts[:]
    rng.shuffle(order)
    letters = "ABCDEFGHIJ"
    letter_of = {t: letters[k] for k, t in enumerate(order)}
    options = [{"letter": letters[k], "text": t} for k, t in enumerate(order)]
    items = [{"id": f"1.{i}", "label": label, "answer": letter_of[right]}
             for i, (label, right) in enumerate(pairs, 1)]
    task = {"id": "1", "type": "matching", "points": len(items),
            "instruction": MATCH_INSTRUCTION.format(what=what, what2=what2),
            "options": options, "items": items}
    return eid, PREFIX + title, task


def build_idioms():
    items = []
    for i, (stem, opts, ans) in enumerate(IDIOMS, 1):
        items.append({"id": f"1.{i}", "stem": stem,
                      "options": [f"{l}) {o}" for l, o in zip("ABC", opts)],
                      "answer": ans})
    task = {"id": "1", "type": "multiple_choice", "points": len(items),
            "instruction": "Wybierz poprawna odpowiedz A, B lub C, tak aby otrzymac "
                           "poprawny idiom.",
            "items": items}
    return "mc_017", PREFIX + "idiomy o pogodzie i przyrodzie", task


def build_reading():
    items = [{"id": f"1.{i}", "statement": s, "answer": a, "explanation": e}
             for i, (s, a, e) in enumerate(READING_ITEMS, 1)]
    task = {"id": "1", "type": "true_false_ni", "points": len(items),
            "instruction": READING_INSTRUCTION, "text": READING_TEXT, "items": items}
    return "tfni_037", PREFIX + "Yellowstone (czytanie)", task


def hint_for(word, given):
    return " ".join(ch if k in given else "_" for k, ch in enumerate(word))


def build_spelling():
    items = []
    for i, (sentence, word, given) in enumerate(SPELLING, 1):
        hint = hint_for(word, given)
        items.append({"id": f"1.{i}", "stem": sentence.format(hint), "hint": hint,
                      "answer": word})
    task = {"id": "1", "type": "word_spelling", "points": len(items),
            "instruction": SPELLING_INSTRUCTION.format(n=len(items)), "items": items}
    return "spelling_033", PREFIX + "slownictwo - swiat przyrody", task


def build_all():
    out = [build_knowledge(*k) for k in KNOWLEDGE]
    out += [build_matching(*m) for m in MATCHING]
    out += [build_idioms(), build_reading(), build_spelling()]
    return out


# --- checks -----------------------------------------------------------------------

def check(exercises):
    errors = []
    ids = [e[0] for e in exercises]
    if len(set(ids)) != len(ids):
        errors.append("duplicate exercise id")
    for eid, title, task in exercises:
        if not title.isascii() or not task["instruction"].isascii():
            errors.append(f"{eid}: title or instruction is not ASCII")
        t = task["type"]
        if t == "knowledge_questions":
            for it in task["items"]:
                for key in ("answer", "secondAnswer"):
                    if key in it and (not isinstance(it[key], list) or not it[key]):
                        errors.append(f"{eid} {it['id']}: {key} must be a non-empty list")
                if it["points"] == 2 and "secondAnswer" not in it:
                    errors.append(f"{eid} {it['id']}: 2 points without secondAnswer")
            if task["points"] != 6:
                errors.append(f"{eid}: {task['points']} points, the paper's task has 6")
        if t == "matching":
            letters = [o["letter"] for o in task["options"]]
            answers = [it["answer"] for it in task["items"]]
            if len(letters) != 10 or len(answers) != 6 or len(set(answers)) != 6:
                errors.append(f"{eid}: needs 6 distinct answers among 10 options")
            if not set(answers) <= set(letters):
                errors.append(f"{eid}: an answer letter has no option")
        if t == "multiple_choice":
            for it in task["items"]:
                if it["answer"] not in "ABC" or len(it["options"]) != 3:
                    errors.append(f"{eid} {it['id']}: bad options or answer")
                if it["stem"].count("_________") != 1:
                    errors.append(f"{eid} {it['id']}: stem needs exactly one gap")
        if t == "true_false_ni":
            for it in task["items"]:
                if it["answer"] not in ("T", "F", "NI"):
                    errors.append(f"{eid} {it['id']}: answer must be T, F or NI")
        if t == "word_spelling":
            for it in task["items"]:
                slots = it["hint"].split(" ")
                if len(slots) != len(it["answer"]) or it["hint"] not in it["stem"]:
                    errors.append(f"{eid} {it['id']}: hint does not fit the answer")
                if all(s == "_" for s in slots):
                    errors.append(f"{eid} {it['id']}: hint gives no letter")
    return errors


# --- review copy ------------------------------------------------------------------

def review(exercises):
    lines = ["# USA and Canada exercises - review copy", "",
             "Theme of the kuratoryjny etap rejonowy, 3.12.2026. Keys in bold.", ""]
    for eid, title, task in exercises:
        lines += [f"## {eid} - {title} ({task['points']} pkt)", ""]
        t = task["type"]
        if t == "true_false_ni":
            lines += [task["text"], ""]
        if t == "matching":
            opts = {o["letter"]: o["text"] for o in task["options"]}
            for o in task["options"]:
                lines.append(f"- {o['letter']}. {o['text']}")
            lines.append("")
        for it in task["items"]:
            if t == "knowledge_questions":
                key = " / ".join(it["answer"][:4])
                if "secondAnswer" in it:
                    key += "  +  " + " / ".join(it["secondAnswer"][:4])
                lines.append(f"{it['id']} ({it['points']} pkt) {it['question']}  "
                             f"**{key}**")
            elif t == "matching":
                lines.append(f"{it['id']} {it['label']}  **{it['answer']}** "
                             f"({opts[it['answer']]})")
            elif t == "multiple_choice":
                right = it["options"]["ABC".index(it["answer"])]
                lines.append(f"{it['id']} {it['stem']}  {' '.join(it['options'])}  "
                             f"**{right}**")
            elif t == "true_false_ni":
                lines.append(f"{it['id']} {it['statement']}  **{it['answer']}**")
            elif t == "word_spelling":
                lines.append(f"{it['id']} {it['stem']}  **{it['answer']}**")
            lines.append("")
    return "\n".join(lines)


# --- writing ----------------------------------------------------------------------

def write(exercises):
    index_path = f"{BASE}/index.json"
    index = json.load(open(index_path))
    entries = index["exercises"]
    known = {e["id"] for e in entries}
    for eid, title, task in exercises:
        with open(f"{BASE}/{eid}.json", "w") as f:
            json.dump({"title": title, "type": "practice", "tasks": [task]}, f,
                      ensure_ascii=False, indent=2)
            f.write("\n")
        entry = {"id": eid, "title": title, "taskType": task["type"], "taskCount": 1,
                 "points": task["points"]}
        if eid in known:
            entries[[e["id"] for e in entries].index(eid)] = entry
            continue
        prefix = eid.rsplit("_", 1)[0] + "_"
        same = [k for k, e in enumerate(entries) if e["id"].startswith(prefix)]
        entries.insert(same[-1] + 1 if same else len(entries), entry)
        known.add(eid)
    with open(index_path, "w") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    exercises = build_all()
    errors = check(exercises)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    os.makedirs("tmp", exist_ok=True)
    with open("tmp/usa_canada_review.md", "w") as f:
        f.write(review(exercises) + "\n")
    total = sum(task["points"] for _, _, task in exercises)
    print(f"{len(exercises)} exercises, {total} points, all checks pass; "
          f"review copy tmp/usa_canada_review.md")
    if "--write" in sys.argv:
        write(exercises)
        print("JSON and index entries written")


if __name__ == "__main__":
    main()
