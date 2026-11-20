"""Write the USA & Canada notebook, the reading page for the kuratoryjny 2026/27 etap rejonowy
(theme: geography, nature and national parks of the USA and Canada).

The facts come from the reading list in the official programme
(tools/usa_canada/src/kurat_program_2627.pdf, section IV, "Etap rejonowy"); copies of the pages
are in tools/usa_canada/src/. Two of the listed pages (ThoughtCo's state capitals and largest
national parks) refuse downloads, so those two lists were written from standard facts and then
checked by hand against the ThoughtCo pages on 18.11.2026
(tools/usa_canada/notes/thoughtco_lists_verified.md: all 50 capitals and the order of the ten
parks match). Facts not on the reading list are marked with *. The look
is the OJAJ UK notebook's: its first <style> block is copied from site/public/ojaj_uk.html.

The pictures (maps, charts, timelines, photos) come from tools/usa_canada/usa_canada_art.py:
maps drawn from
Natural Earth data (tools/usa_canada/src/na_geo.json), photos from Wikimedia Commons in
site/public/img/usa_kanada/ (put there by tools/usa_canada/photo_prep.py, with their credits in
tools/usa_canada/src/photos/credits.json, which the footer prints).

Before writing, it checks that every answer in the 15 "USA i Kanada" practice exercises appears
on the page, that all 50 states and 13 provinces and territories are there once, that every
quiz link points at an exercise in the practice index, that the tags are balanced, that every
photo is on disk with a credit and every photo on disk is used, that every picture has a text
description, and that the maps and charts list the same parks as the text.

Usage: python3 tools/usa_canada/gen_usa_canada_notes.py           # checks only
       python3 tools/usa_canada/gen_usa_canada_notes.py --write   # checks, then writes the page
Output: site/public/usa_kanada.html, served at /usa_kanada
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import usa_canada_art as art  # noqa: E402

OUT = Path("site/public/usa_kanada.html")
IMG = Path("site/public/img/usa_kanada")
UK = Path("site/public/ojaj_uk.html")
PRACTICE = Path("pub/konkursy/angielski/data/practice")
INDEX = {e["id"]: e for e in json.loads((PRACTICE / "index.json").read_text())["exercises"]}
X = '<sup class="x" title="not on the reading list">*</sup>'


def ft(n):
    """A height in feet with metres, e.g. 14,505 ft (4,421 m)."""
    return f"{n:,} ft ({round(n * 0.3048):,} m)"


def mi(n):
    """A length in miles with kilometres."""
    return f"{n:,} miles ({round(n * 1.609344):,} km)"


def chips(pairs):
    items = "".join(f"<li><b>{en}</b> <i>{pl}</i></li>" for en, pl in pairs)
    return f'<ul class="words">{items}</ul>'


def remember(pairs):
    rows = "".join(f"<dt>{dt}</dt><dd>{dd}</dd>" for dt, dd in pairs)
    return f'<div class="remember"><div class="eyebrow">Remember</div><dl>{rows}</dl></div>'


def table(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div class="tbl {cls}"><table><thead><tr>{th}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def checks(qas, quiz_ids):
    det = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in qas)
    links = ""
    for eid in quiz_ids:
        e = INDEX[eid]
        name = e["title"].replace("USA i Kanada: ", "")
        links += (f'<a class="quiz" href="/cwiczenia/{e["taskType"]}/{eid}" target="_blank" '
                  f'rel="noopener">SmartEn: {name} &rarr;</a> ')
    return (f'<div class="check"><div class="eyebrow">Check yourself</div>{det}'
            f'<div class="quizzes">{links.strip()}</div></div>')


def watch(title, body):
    return f'<div class="watch"><strong>{title}</strong>{body}</div>'


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def fact(*parts):
    return '<div class="fact">' + "".join(parts) + "</div>"


def p(text):
    return f"<p>{text}</p>"


# ---------------------------------------------------------------- 1. where they are
STATES = {
    "Northeast": [("Maine", "Augusta"), ("Massachusetts", "Boston"),
                  ("Rhode Island", "Providence"), ("Connecticut", "Hartford"),
                  ("New Hampshire", "Concord"), ("Vermont", "Montpelier"),
                  ("New York", "Albany"), ("Pennsylvania", "Harrisburg"),
                  ("New Jersey", "Trenton"), ("Delaware", "Dover"), ("Maryland", "Annapolis")],
    "Southeast": [("West Virginia", "Charleston"), ("Virginia", "Richmond"),
                  ("Kentucky", "Frankfort"), ("Tennessee", "Nashville"),
                  ("North Carolina", "Raleigh"), ("South Carolina", "Columbia"),
                  ("Georgia", "Atlanta"), ("Alabama", "Montgomery"),
                  ("Mississippi", "Jackson"), ("Arkansas", "Little Rock"),
                  ("Louisiana", "Baton Rouge"), ("Florida", "Tallahassee")],
    "Midwest": [("Ohio", "Columbus"), ("Indiana", "Indianapolis"), ("Michigan", "Lansing"),
                ("Illinois", "Springfield"), ("Missouri", "Jefferson City"),
                ("Wisconsin", "Madison"), ("Minnesota", "St. Paul (Saint Paul)"), ("Iowa", "Des Moines"),
                ("Kansas", "Topeka"), ("Nebraska", "Lincoln"), ("South Dakota", "Pierre"),
                ("North Dakota", "Bismarck")],
    "Southwest": [("Texas", "Austin"), ("Oklahoma", "Oklahoma City"),
                  ("New Mexico", "Santa Fe"), ("Arizona", "Phoenix")],
    "West": [("Colorado", "Denver"), ("Wyoming", "Cheyenne"), ("Montana", "Helena"),
             ("Idaho", "Boise"), ("Washington", "Olympia"), ("Oregon", "Salem"),
             ("Utah", "Salt Lake City"), ("Nevada", "Carson City"),
             ("California", "Sacramento"), ("Alaska", "Juneau"), ("Hawaii", "Honolulu")],
}

PROVINCES = [
    # name, capital, region, what it is known for
    ("Newfoundland and Labrador", "St. John's", "East",
     "the most easterly point in North America; dramatic cliffs, puffins and icebergs; "
     "Gros Morne National Park"),
    ("Nova Scotia", "Halifax", "East",
     "seafood (lobster); the Cabot Trail on Cape Breton Island; the Bay of Fundy"),
    ("Prince Edward Island", "Charlottetown", "East",
     "red sand beaches; the setting of <i>Anne of Green Gables</i>; the smallest province" + X),
    ("New Brunswick", "Fredericton", "East",
     "bilingual (English and French); views along the Bay of Fundy"),
    ("Quebec", "Quebec City", "Central",
     "French heritage; Montreal and Quebec City (Old Town founded in 1608); wilderness in the "
     "north; the largest province" + X),
    ("Ontario", "Toronto", "Central",
     "Toronto (Canada's largest city) and Ottawa (the capital); Niagara Falls; "
     "Thousand Islands National Park"),
    ("Manitoba", "Winnipeg", "West: the Prairies",
     "endless golden fields, flat landscapes and great sunsets"),
    ("Saskatchewan", "Regina", "West: the Prairies",
     "grows 45% of Canada's grain (wheat, canola, flax, rye); Cigar Lake uranium mine"),
    ("Alberta", "Edmonton", "West",
     "the Rocky Mountains; Banff, Jasper and Waterton Lakes National Parks; oil and gas; "
     "Dinosaur Provincial Park"),
    ("British Columbia", "Victoria", "West",
     "where the mountains meet the sea; Vancouver; Yoho and Pacific Rim National Parks"),
    ("Yukon", "Whitehorse", "North (territory)",
     "Mount Logan in Kluane National Park; the record cold at Snag"),
    ("Northwest Territories", "Yellowknife", "North (territory)",
     "the Mackenzie River and Great Bear Lake; more lakes than most countries"),
    ("Nunavut", "Iqaluit", "North (territory)",
     "Baffin Island and most of the Arctic Archipelago; polar bears, walruses, narwhals"),
]

S_WHERE = "".join([
    "<h3>The USA and Canada side by side</h3>",
    table(["", "USA", "Canada"], [
        ["Where", "North America, south of Canada",
         "the northern part of North America, right above the USA; from about 41&deg; to "
         "83&deg; N, well into the Arctic"],
        ["Size", "the third largest country in the world: smaller than Russia and Canada, "
         "larger than China (if all territories and waters are counted)",
         "the second largest country in the world, after Russia, and the largest in the "
         "western hemisphere: 9.98 million km&sup2; / 3.85 million sq mi"],
        ["Made up of", "50 states, a federal district (the District of Columbia) and 14 "
         "territories; 5 territories have people: Puerto Rico (the biggest), Guam, the "
         "Northern Mariana Islands, the U.S. Virgin Islands and American Samoa",
         "10 provinces and 3 territories (Yukon, Northwest Territories, Nunavut)"],
        ["Capital", "Washington, D.C. (D.C. = District of Columbia)", "Ottawa, in Ontario"],
        ["Largest city", "New York (almost 8.4 million people)",
         "Toronto (about 7 million in the metropolitan area)"],
        ["People", "346 million, the third most populous country after China and India; "
         "almost 40% live in the East Coast states, about 16% on the West Coast; 83% in "
         "towns and cities",
         "40 million, one of the ten most sparsely populated countries; more than half live "
         "in Ontario and Quebec, most near the southern border"],
        ["Land borders", "Canada (north) and Mexico (south)",
         "only the USA: in the south, and in the northwest, where it borders Alaska"],
        ["Coasts", "the Atlantic Ocean (East Coast), the Pacific Ocean (West Coast) and the "
         "Gulf of Mexico in the south",
         "three oceans: the Atlantic (east), the Pacific (west) and the Arctic (north); a sea "
         "border with Greenland"],
    ], cls="wide"),
    art.where_map(),
    fact(ul([
        "<b>The USA&ndash;Canada border is the longest international border in the world:</b> "
        "8,891 km / 5,525 miles. Its longest part, more than 2,475 km / 1,538 miles, is the "
        "border with Alaska.",
        "The USA&ndash;Mexico border is 3,145 km / 1,954 miles long.",
        "Of the 50 states, 49 are on the North American mainland. Hawaii is in the Pacific "
        "Ocean.",
        "Canada has the <b>longest coastline in the world</b>, 202,080 km, thanks to its three "
        "oceans and thousands of islands.",
    ])),
    art.size_people_chart(),
    watch("Two Washingtons.", p(
        "Washington, D.C. is the capital of the USA, on the East Coast. Washington is also a "
        "state in the northwest, whose capital is Olympia.")),
    "<h3>Regions of the USA</h3>",
    p("The USA is usually divided into five regions: the Northeast, the Southeast, the "
      "Midwest, the Southwest and the West. They are not official, so a border state can "
      "appear in different regions on different maps (Maryland is sometimes in the "
      "Southeast). The states of each region are in the next section."),
    art.regions_map(),
    table(["Region", "Main geographical features"], [
        ["Northeast", "the Appalachian Mountains, the Atlantic Ocean, the Great Lakes; borders "
         "Canada to the north"],
        ["Southeast", "the Appalachian Mountains, the Atlantic Ocean, the Gulf of Mexico, the "
         "Mississippi River"],
        ["Midwest", "the Great Lakes, the Great Plains, the Mississippi River; borders Canada to "
         "the north"],
        ["Southwest", "the Rocky Mountains, the Colorado River, the Grand Canyon, the Gulf of "
         "Mexico; borders Mexico to the south"],
        ["West", "the Rocky Mountains, the Sierra Nevada, the Mojave Desert, the Pacific Ocean; "
         "borders Canada to the north and Mexico to the south"],
    ]),
    p("Smaller regions people often name: <b>New England</b> (Maine, Vermont, New Hampshire, "
      "Massachusetts, Rhode Island, Connecticut), the <b>Mid-Atlantic</b> (Virginia, West "
      "Virginia, Pennsylvania, Maryland, Delaware, New Jersey), the <b>Great Lakes</b> "
      "(Minnesota, Wisconsin, Illinois, Indiana, Ohio, Michigan), the <b>Central Plains</b> "
      "(Iowa, Missouri, Kansas, Nebraska), the <b>Pacific Northwest</b> (Washington, Oregon, "
      "Idaho) and the <b>Rocky Mountains</b> (Utah, Colorado, New Mexico, Wyoming, Montana)."),
    p("<b>The lower 48</b> means the 48 states that touch each other, without Alaska and "
      "Hawaii. Sources use it for records such as \"the tallest mountain in the lower 48\"."),
    "<h3>Regions of Canada</h3>",
    table(["Region", "Provinces and territories"], [
        ["East (the Atlantic provinces)", "Newfoundland and Labrador, Nova Scotia, Prince Edward "
         "Island, New Brunswick: fishing villages, coastal cliffs, life by the sea"],
        ["Central Canada", "Ontario and Quebec, the two most populous provinces"],
        ["West", "Manitoba and Saskatchewan (the Prairies), Alberta, British Columbia: from "
         "prairies to the Rocky Mountains"],
        ["North", "the territories Yukon, Northwest Territories and Nunavut: remote and wild, "
         "deep into the Arctic, with the Northern Lights, glaciers and tundra"],
    ]),
    chips([("hemisphere", "półkula"), ("border", "granica"),
           ("coastline", "linia brzegowa"), ("mainland", "ląd stały, kontynent"),
           ("territory", "terytorium"), ("federal district", "okręg federalny"),
           ("sparsely populated", "słabo zaludniony"), ("populous", "ludny"),
           ("metropolitan area", "obszar metropolitalny"),
           ("the lower 48", "48 stanów bez Alaski i Hawajów")]),
    remember([("3rd / 2nd", "largest country in the world: the USA / Canada"),
              ("50 + D.C.", "the US states plus the District of Columbia"),
              ("10 + 3", "Canada's provinces plus territories"),
              ("8,891 km", "the USA&ndash;Canada border, the longest in the world"),
              ("3 oceans", "on Canada's coasts: Atlantic, Pacific, Arctic"),
              ("5 regions", "Northeast, Southeast, Midwest, Southwest, West")]),
    checks([
        ("Which countries does the USA share land borders with?", "Canada and Mexico."),
        ("Which three oceans does Canada border?",
         "The Atlantic (east), the Pacific (west) and the Arctic (north)."),
        ("Which US state is not on the North American mainland?", "Hawaii, in the Pacific."),
        ("Texas, Oklahoma, New Mexico and Arizona make up which region?", "The Southwest."),
    ], ["knowledge_035", "knowledge_036"]),
])

# ---------------------------------------------------------------- 2. states and provinces
REGION_BLOCKS = "".join(
    f'<div class="region">{art.region_map(region)}<div><h4>{region}</h4>'
    + table(["State", "Capital"], [[s, c] for s, c in rows]) + "</div></div>"
    for region, rows in STATES.items())

S_STATES = "".join([
    p("Every US state has its own capital, and it is often <b>not</b> the state's biggest or "
      "most famous city. The states are grouped here by the five regions."),
    art.map_legend_html(),
    REGION_BLOCKS,
    watch("Capitals that catch people out.", ul([
        "New York &rarr; <b>Albany</b> (not New York City); California &rarr; <b>Sacramento</b> "
        "(not Los Angeles); Texas &rarr; <b>Austin</b> (not Houston); Florida &rarr; "
        "<b>Tallahassee</b> (not Miami)",
        "Illinois &rarr; <b>Springfield</b> (not Chicago); Pennsylvania &rarr; "
        "<b>Harrisburg</b> (not Philadelphia); Michigan &rarr; <b>Lansing</b> (not Detroit); "
        "Missouri &rarr; <b>Jefferson City</b> (not St. Louis)",
        "Washington &rarr; <b>Olympia</b> (not Seattle); Nevada &rarr; <b>Carson City</b> (not "
        "Las Vegas); Oregon &rarr; <b>Salem</b> (not Portland); Alaska &rarr; <b>Juneau</b> "
        "(not Anchorage)",
        "Louisiana &rarr; <b>Baton Rouge</b> (not New Orleans); Kentucky &rarr; "
        "<b>Frankfort</b> (not Louisville); Maryland &rarr; <b>Annapolis</b> (not Baltimore)",
        "<b>Columbus</b> is the capital of Ohio, <b>Columbia</b> of South Carolina. "
        "<b>Charleston</b> is the capital of West Virginia; South Carolina has a better-known "
        "Charleston, but its capital is Columbia.",
    ])),
    fact(ul([
        "<b>Largest state: Alaska.</b> It is a bit more than twice the size of Texas and four "
        "times the size of California, about as big as Germany, Austria, Switzerland, Italy "
        "and France together.",
        "<b>Smallest state: Rhode Island</b>, about 1.5 times the size of Luxembourg.",
        "<b>Most people: California</b> (almost 40 million). <b>Fewest: Wyoming</b> (about "
        "580,000).",
    ])),
    art.sizes_figure(),
    "<h3>Canada's provinces and territories</h3>",
    art.canada_map(),
    table(["Province or territory", "Capital" + X, "Region", "Known for"],
          [[n, c, r, k] for n, c, r, k in PROVINCES], cls="wide"),
    watch("Capitals that catch people out.", ul([
        "British Columbia &rarr; <b>Victoria</b>, on Vancouver Island (not Vancouver)",
        "Alberta &rarr; <b>Edmonton</b> (not Calgary); Saskatchewan &rarr; <b>Regina</b> "
        "(not Saskatoon); Quebec &rarr; <b>Quebec City</b> (not Montreal)",
        "Ontario's capital is <b>Toronto</b>; Ottawa, also in Ontario, is the capital of the "
        "whole country.",
    ])),
    chips([("state capital", "stolica stanu"), ("province", "prowincja"),
           ("bilingual", "dwujęzyczny"), ("the Prairies", "prerie (Manitoba, Saskatchewan, "
                                                          "Alberta)"),
           ("the Atlantic provinces", "prowincje atlantyckie"),
           ("heritage", "dziedzictwo")]),
    remember([("Albany", "New York State; Sacramento: California; Austin: Texas"),
              ("Juneau", "Alaska, the largest state"),
              ("Rhode Island", "the smallest state"),
              ("Victoria", "British Columbia; Edmonton: Alberta; Regina: Saskatchewan"),
              ("Iqaluit", "Nunavut; Whitehorse: Yukon; Yellowknife: Northwest Territories")]),
    checks([
        ("What is the capital of New York State?",
         "Albany. New York City is the biggest city, not the capital."),
        ("Which province is bilingual and lies on the Bay of Fundy?", "New Brunswick."),
        ("Which province grows 45% of Canada's grain?", "Saskatchewan."),
        ("Which province is the setting of <i>Anne of Green Gables</i>?",
         "Prince Edward Island, known for its red sand beaches."),
    ], ["matching_025", "knowledge_035", "matching_028", "knowledge_037"]),
])

# ---------------------------------------------------------------- 3. land and water
S_LAND = "".join([
    "<h3>Mountains of the USA</h3>",
    fact(p("The three major ranges are the Appalachians, the Rocky Mountains and the Sierra "
           "Nevada."), ul([
        "<b>The Appalachian Mountains</b> run for 1,500 miles along the east of the country, "
        "from northern Alabama to Maine. They are old, forested mountains (pine, spruce, birch, "
        "maple). Smaller ranges inside them: the Great Smoky Mountains, the Blue Ridge "
        "Mountains, the Green Mountains, the White Mountains and the Berkshires. Early "
        "colonists found them a barrier to moving west.",
        "<b>The Rocky Mountains</b> (the Rockies) are the longest range in North America and "
        "the second longest in the world: 3,000 miles from New Mexico through Montana and far "
        "into Canada. The <b>Continental Divide</b> runs along them: water on one side flows "
        "to the Atlantic, on the other to the Pacific. They are <i>fold mountains</i>, formed "
        "where two tectonic plates meet. National parks there: Yellowstone, Rocky Mountain, "
        "Grand Teton, Glacier.",
        "<b>The Sierra Nevada</b> runs about 400 miles through California (and a little of "
        "Nevada). It is home to the giant sequoias, Yosemite National Park and Lake Tahoe. "
        "These are <i>fault-block mountains</i>, formed along a fault in the Earth's crust.",
        "<b>The Cascade Range</b> runs 700 miles along the northwest coast into Canada and is "
        "part of the volcanic <b>Ring of Fire</b> around the Pacific; the active volcano Mount "
        "Saint Helens is in it.",
        "Also: <b>the Alaska Range</b> (the tallest range in the USA), <b>the Brooks Range</b> "
        "(over 700 miles across northern Alaska), <b>the Adirondacks</b> (New York; Adirondack "
        "Park is the largest state park in the USA) and <b>the Ozarks</b> (Missouri and "
        "Arkansas, the largest range between the Appalachians and the Rockies).",
    ])),
    art.mountains_map(),
    table(["Peak", "Range, state", "Height", "Record"], [
        ["Denali (Mount Denali)", "Alaska Range, Alaska", "6,190 m / 20,310 ft",
         "the highest mountain in the USA and in North America"],
        ["Mount Whitney", "Sierra Nevada, California", ft(14505),
         "the highest in the lower 48"],
        ["Mount Elbert", "Rocky Mountains, Colorado", ft(14440), "the highest in the Rockies"],
        ["Mount Rainier", "Cascade Range, Washington", ft(14411), "the highest in the Cascades"],
        ["Mount Mitchell", "Appalachians, North Carolina", ft(6684),
         "the highest in the Appalachians"],
        ["Mount Chamberlin", "Brooks Range, Alaska", ft(9020), "the highest in the Brooks Range"],
        ["Mount Marcy", "Adirondacks, New York", ft(5344), "the highest in the Adirondacks"],
    ], cls="wide"),
    art.peaks_chart(),
    art.photos([("denali", "Denali (6,190 m), the highest peak in North America"),
                ("logan", "Mount Logan (5,959 m), Canada's highest"),
                ("saint_helens", "Mount Saint Helens, an active volcano in the Cascade Range")]),
    "<h3>Rivers of the USA</h3>",
    table(["", "River", "Length", "Remember"], [
        ["1", "Missouri", mi(2540), "<b>the longest river in the USA</b>; from western Montana "
         "to the Mississippi just north of St. Louis; Lewis and Clark travelled its whole "
         "length"],
        ["2", "Mississippi", mi(2340), "begins at <b>Lake Itasca</b> in Minnesota and flows "
         "north to south into the <b>Gulf of Mexico</b> in Louisiana; with the Missouri, the "
         "fourth largest river system in the world; Minneapolis, St. Louis, Memphis, New "
         "Orleans"],
        ["3", "Yukon", mi(1980), "begins at Llewellyn Glacier in Canada and crosses Alaska to "
         "the Bering Sea"],
        ["4", "Rio Grande", mi(1900), "from Colorado through New Mexico to the Gulf of Mexico; "
         "the border between Texas and Mexico"],
        ["5", "St. Lawrence", mi(1900), "links the Great Lakes with the Atlantic"],
        ["6", "Arkansas", mi(1460), ""],
        ["7", "Colorado", mi(1450), "from the Rocky Mountains of Colorado to the Gulf of "
         "California; <b>carved the Grand Canyon</b>; the Hoover Dam (1936) made Lake Mead and "
         "powers Las Vegas"],
        ["8", "Atchafalaya", mi(1420), ""],
        ["9", "Ohio", mi(1310), ""],
        ["10", "Red", mi(1290), ""],
    ], cls="wide num"),
    art.waters_map(),
    art.rivers_chart(),
    fact(ul([
        "<b>The Columbia</b> (1,240 miles) is the largest river of the northwest: from the "
        "Canadian Rockies through Washington State to the Pacific. Its Grand Coulee Dam produces "
        "the most power of any dam in the USA.",
        "<b>The Hudson</b> (315 miles, eastern New York) is short but important: the Erie "
        "Canal (1825) joined it to the Great Lakes, which helped New York City grow.",
    ])),
    "<h3>Lakes of the USA</h3>",
    fact(ul([
        "<b>The Great Lakes</b>: Superior, Huron, Michigan, Erie and Ontario, on the border "
        "with Canada. Remember them as <b>SMHEO</b>: \"Super Man Helps Every One\". Only "
        "<b>Lake Michigan</b> is entirely in the USA. Together they are the largest group of "
        "freshwater lakes in the world (about 21% of the world's surface fresh water). Eight "
        "states have a Great Lakes shore; cities on them include Chicago, Cleveland, Buffalo, "
        "Milwaukee and Toronto.",
        "<b>Lake Superior</b> is the largest and deepest of them (31,700 sq mi / 82,100 "
        "km&sup2;, up to " + ft(1335) + " deep) and the largest freshwater lake in the world by "
        "area.",
        "<b>The Great Salt Lake</b> (Utah) is the largest lake outside the Great Lakes. It is "
        "saltier than the ocean, so no fish live in it, only brine shrimp and algae.",
        "<b>Crater Lake</b> (Oregon) is the <b>deepest lake in the USA</b>: " + ft(1943) + ". "
        "It is a <i>caldera</i> lake, in the collapsed top of the volcano Mount Mazama.",
        "<b>Lake Tahoe</b>, high in the Sierra Nevada on the California&ndash;Nevada border, is "
        "the second deepest.",
        "<b>Lake Okeechobee</b> (south Florida) is large but only 9 feet deep on average; "
        "alligators, manatees, herons and bobcats live there.",
    ])),
    art.great_lakes_map(),
    table(["", "Largest US lakes by area", "sq miles"], [
        ["1", "Lake Superior", "31,700"], ["2", "Lake Huron", "23,000"],
        ["3", "Lake Michigan", "22,300"], ["4", "Lake Erie", "9,910"],
        ["5", "Lake Ontario", "7,340"], ["6", "Great Salt Lake", "2,117"],
        ["7", "Lake of the Woods", "1,485"], ["8", "Iliamna Lake", "1,014"],
        ["9", "Lake Oahe", "685"], ["10", "Lake Okeechobee", "662"],
    ], cls="num"),
    art.photos([("great_salt", "The Great Salt Lake from space: saltier than the ocean"),
                ("hoover", "The Hoover Dam on the Colorado River; behind it, Lake Mead")]),
    "<h3>Deserts of the USA</h3>",
    p("A desert gets less than ten inches (25 cm) of precipitation a year. The four big US "
      "deserts are all in the west."),
    table(["Desert", "Where", "Remember"], [
        ["Great Basin", "between the Sierra Nevada and the Rockies; mostly Nevada",
         "<b>the largest</b>; a cold desert, high up, where most precipitation is snow; the "
         "Sierra Nevada blocks the wet winds from the Pacific; the <b>bristlecone pine</b>, "
         "the oldest known living organism (over 5,000 years)"],
        ["Mojave", "California, Nevada, Arizona",
         "the <b>Joshua tree</b>; Death Valley, the hottest place in the USA (134&deg;F) and "
         "282 ft below sea level; Telescope Peak " + ft(11049)],
        ["Sonoran", "southern California, Arizona, Mexico",
         "the <b>saguaro</b> cactus, over 60 ft tall, with \"arms\"; the Colorado and Gila "
         "rivers"],
        ["Chihuahuan", "Texas, New Mexico, Arizona; mostly in Mexico",
         "the creosote bush, yuccas, agaves, prickly pears; the Rio Grande; Big Bend National "
         "Park"],
    ], cls="wide"),
    art.west_map(),
    art.cross_section(),
    "<h3>Canada's land and water</h3>",
    table(["Landscape", "Where and what"], [
        ["The Rockies", "British Columbia and Alberta: towering mountains, Lake Louise and "
         "Moraine Lake"],
        ["The Prairies", "Manitoba, Saskatchewan and parts of Alberta: flat, wide-open fields"],
        ["The Canadian Shield", "much of Ontario and Quebec: rocky ground, forests and lakes, "
         "good for canoeing and camping"],
        ["The Arctic tundra", "the north: cold, vast and mostly treeless; polar bears and "
         "caribou"],
    ]),
    art.photos([("moraine", "The Rockies: Moraine Lake, Alberta"),
                ("prairies", "The Prairies: flat, wide-open fields (canola in Alberta)")]),
    fact(ul([
        "<b>Mount Logan</b> (5,959 m / 19,551 ft), in <b>Kluane National Park</b> in the Yukon, "
        "on the border with Alaska, is Canada's highest mountain and the second highest in "
        "North America, after Denali.",
        "Canada has <b>more lakes than any other country</b>: about three million, around 60% "
        "of the world's natural lakes. The Northwest Territories alone have more lakes than "
        "most countries. The largest lake entirely in Canada is <b>Great Bear Lake</b>.",
        "The longest river system is the <b>Mackenzie</b> (4,241 km / 2,635 miles) in the "
        "Northwest Territories, the largest river flowing from North America into the Arctic.",
        "At Lytton (British Columbia) the <b>Thompson and Fraser rivers</b> meet, and at first "
        "they look as if they do not mix (a <i>confluence</i>).",
        "<b>Niagara Falls</b>, on the Canada&ndash;USA border, formed in the last Ice Age. The "
        "<b>Horseshoe Falls</b> on the Canadian side are the most powerful waterfall in North "
        "America, and the best views are from Canada.",
        "<b>The Bay of Fundy</b>, between New Brunswick and Nova Scotia, has the <b>highest "
        "tides in the world</b>: the water rises and falls by up to 16 m, twice a day. At the "
        "Hopewell Rocks you can walk on the seabed at low tide and kayak there a few hours "
        "later.",
        "<b>Baffin Island</b> (Nunavut) is Canada's largest island and the world's fifth "
        "largest, as big as Spain. Its <b>Mount Thor</b> has the world's highest vertical "
        "cliff (a drop of 1,250 m). Most of Canada's islands are in the <b>Arctic "
        "Archipelago</b>: 36,563 islands.",
    ])),
    art.tide_chart(),
    art.photos([("fundy", "The Hopewell Rocks, Bay of Fundy, at low tide: you walk on the seabed"),
                ("niagara", "The Horseshoe Falls at Niagara: the most powerful waterfall in North "
                 "America"),
                ("thor", "Mount Thor, Baffin Island: the world's highest vertical cliff")]),
    chips([("mountain range", "pasmo górskie"), ("peak, summit", "szczyt"),
           ("source (of a river)", "źródło"), ("mouth", "ujście"), ("tributary", "dopływ"),
           ("river system", "system rzeczny"), ("confluence", "zbieg rzek"),
           ("dam", "zapora"), ("canyon", "kanion"), ("gorge", "wąwóz"),
           ("caldera", "kaldera"), ("glacier", "lodowiec"), ("icefield", "pole lodowe"),
           ("fjord", "fiord"), ("tide", "pływ"), ("low tide / high tide", "odpływ / przypływ"),
           ("seabed", "dno morskie"), ("archipelago", "archipelag"),
           ("vertical cliff", "pionowe urwisko"), ("Continental Divide",
                                                   "kontynentalny dział wód"),
           ("fold mountains", "góry fałdowe"), ("fault-block mountains", "góry zrębowe"),
           ("tectonic plate", "płyta tektoniczna"), ("tundra", "tundra"),
           ("precipitation", "opady")]),
    remember([("Missouri", "the longest US river; the Mississippi starts at Lake Itasca"),
              ("Superior / Crater", "the largest / the deepest lake"),
              ("Denali", "the highest peak in the USA and North America"),
              ("Great Basin", "the largest US desert; Mojave: Joshua trees, Death Valley"),
              ("Logan", "Canada's highest peak, in Kluane National Park"),
              ("Mackenzie", "Canada's longest river; Great Bear Lake: largest lake in Canada")]),
    checks([
        ("Which of the Great Lakes lies entirely in the USA?", "Lake Michigan."),
        ("What is the Continental Divide?", "A line along the Rockies: on one side water flows "
         "to the Atlantic, on the other to the Pacific."),
        ("Why does the Great Basin Desert get so little rain?",
         "The Sierra Nevada shields it from the wet winds from the Pacific."),
        ("Where are the highest tides in the world?",
         "In the Bay of Fundy, between New Brunswick and Nova Scotia: up to 16 m."),
    ], ["knowledge_033", "knowledge_034", "knowledge_036"]),
])

# ---------------------------------------------------------------- 4. climate
S_CLIMATE = "".join([
    "<h3>The USA, region by region</h3>",
    table(["Region", "Climate"], [
        ["Northeast", "humid continental, with cool summers in the far north; snow in winter, "
         "when temperatures are regularly below freezing"],
        ["Southeast", "humid subtropical, with hot summers; hurricanes can make landfall in "
         "summer and autumn on the Atlantic and Gulf coasts"],
        ["Midwest", "humid continental; snow is common in winter, especially in the north"],
        ["Southwest", "semiarid steppe in the west, more humid in the east; alpine or desert in "
         "some far western areas"],
        ["West", "many climates: semiarid and alpine in the Rockies and the Sierra Nevada, "
         "Mediterranean on the California coast, desert in Nevada and southern California"],
    ]),
    art.climate_map(),
    fact(ul([
        "The Rockies have distinct seasons: warm, rainy summers and cold, snowy winters.",
        "<b>Not every desert is hot.</b> The Great Basin Desert is often very cold, and most of "
        "its precipitation falls as snow.",
        "<b>Death Valley</b> is the hottest and driest place in North America: a world record "
        "of 134&deg;F (56.7&deg;C) and less than two inches (5 cm) of rain a year.",
    ])),
    "<h3>Canada</h3>",
    fact(ul([
        "Canada has a wide range of climates. The north is very cold, with long, snowy winters; "
        "most of northern Canada falls below &minus;30&deg;C (&minus;22&deg;F) in winter, and "
        "parts of the Arctic are frozen all year.",
        "<b>Snag</b>, in the Yukon, recorded one of the coldest temperatures in North America: "
        "&minus;63&deg;C (&minus;81&deg;F) in February 1947.",
        "In the south, summers can be warm or even hot. The coasts are milder than inland.",
        "In the northern territories, and sometimes on the Prairies, you can see the "
        "<b>Northern Lights</b> (the <i>aurora borealis</i>).",
    ])),
    art.temperature_chart(),
    chips([("climate", "klimat"), ("humid", "wilgotny"), ("arid / semiarid", "suchy / półsuchy"),
           ("continental", "kontynentalny"), ("subtropical", "podzwrotnikowy"),
           ("Mediterranean", "śródziemnomorski"), ("alpine", "wysokogórski"),
           ("below freezing", "poniżej zera"), ("hurricane", "huragan"),
           ("make landfall", "uderzyć w ląd"), ("tornado", "tornado"),
           ("blizzard", "zamieć śnieżna"), ("avalanche", "lawina"), ("drought", "susza"),
           ("heatwave", "fala upałów"), ("thunderstorm", "burza z piorunami"),
           ("hail", "grad"), ("sleet", "deszcz ze śniegiem"), ("frost", "mróz, szron"),
           ("fog / mist / haze", "mgła / mgiełka / zamglenie"),
           ("permafrost", "wieczna zmarzlina"), ("Northern Lights", "zorza polarna")]),
    remember([("humid continental", "the Northeast and the Midwest: snowy winters"),
              ("humid subtropical", "the Southeast: hot summers, hurricanes"),
              ("Mediterranean", "the California coast"),
              ("134&deg;F", "Death Valley, the world record"),
              ("&minus;63&deg;C", "Snag, Yukon, February 1947")]),
    checks([
        ("Which US region gets hurricanes?",
         "The Southeast, on the Atlantic and Gulf coasts, in summer and autumn."),
        ("What kind of climate does the California coast have?", "Mediterranean."),
        ("Is every desert hot?", "No. In the Great Basin Desert most precipitation is snow."),
    ], ["spelling_033"]),
])

# ---------------------------------------------------------------- 5. plants and animals
WWF = [
    ("Beaver", "the largest rodent in North America; flat tail, sharp incisors that bite "
     "through trees; \"busy as a beaver\", called <b>\"nature's engineer\"</b> because it "
     "keeps freshwater ecosystems healthy"),
    ("Moose", "the <b>largest member of the deer family</b>, up to 1.8 m tall at the shoulder "
     "and 360&ndash;725 kg; males (<i>bulls</i>) have antlers up to 1.5 m wide; strong "
     "swimmers that dive for plants; boreal forests and wetlands"),
    ("Polar bear", "<b>at least two-thirds</b> of the world's polar bears live in Canada; "
     "<i>Ursus maritimus</i>, \"sea bear\"; hunts from sea ice, which is melting"),
    ("Monarch butterfly", "orange, black and white; every autumn flies 4,000&ndash;5,000 km "
     "from southern Ontario and Quebec to the mountain forests of Mexico, one of the world's "
     "longest insect migrations; a pollinator"),
    ("Southern resident killer whale", "the orca of British Columbia's Salish Sea; "
     "endangered: only 72 are left"),
    ("Walrus", "the Atlantic walrus: whiskers and ivory tusks (on males and females, up to "
     "3 ft) used to break sea ice and climb out of the water; the High Arctic"),
    ("Caribou", "the Arctic, boreal and mountain regions; the woodland caribou is on the "
     "25-cent coin; many herds have dropped by over 90%"),
    ("Atlantic puffin", "the provincial bird of Newfoundland; breeds in huge colonies; dives "
     "up to 60 m for small fish"),
    ("Canada lynx", "paws like snowshoes; hunts hares, ducks and young deer in the snow; "
     "climbs trees and swims; tufted ears and a short tail"),
    ("Beluga whale", "white, with a \"smiling\" mouth; about two-thirds of the world's belugas "
     "spend the summer in Canadian waters; called <b>\"the canary of the sea\"</b> for its "
     "chirps, clicks, whistles and squeals"),
]

WWF_PHOTO = {"Beaver": "beaver", "Moose": "moose", "Polar bear": "polar_bear",
             "Monarch butterfly": "monarch", "Southern resident killer whale": "orca",
             "Walrus": "walrus", "Caribou": "caribou", "Atlantic puffin": "puffin",
             "Canada lynx": "lynx", "Beluga whale": "beluga"}

S_WILDLIFE = "".join([
    "<h3>National symbols</h3>",
    table(["", "USA", "Canada"], [
        ["National animal", "the American bison", "the beaver"],
        ["National bird", "the bald eagle", "the Canada goose"],
        ["National tree", "the oak", "the maple"],
        ["National flower", "the rose", ""],
        ["Also", "the flag: 13 stripes (the 13 colonies) and 50 stars (the states)",
         "the maple leaf; the colours red and white"],
    ]),
    art.flags_figure(),
    art.photos([("bison", "USA: the American bison"), ("bald_eagle", "USA: the bald eagle"),
                ("beaver", "Canada: the beaver"), ("canada_goose", "Canada: the Canada goose")]),
    "<h3>Plants of the USA</h3>",
    fact(ul([
        "<b>Giant sequoias</b> (Sierra Nevada) are the largest trees in the world: up to 270 ft "
        "tall, over 25 ft across and over 3,000 years old. The <b>General Sherman Tree</b> in "
        "Sequoia National Park is the world's largest tree by volume.",
        "<b>Coast redwoods</b> (Redwood National Park, California) are the tallest living "
        "things on the planet.",
        "<b>The bristlecone pine</b> (Great Basin Desert) is the oldest known living organism: "
        "some are over 5,000 years old.",
        "Deserts: the <b>Joshua tree</b> (Mojave; its scientific name is <i>Yucca "
        "brevifolia</i>), the <b>saguaro</b> cactus (Sonoran), the creosote bush, sagebrush, "
        "yuccas, agaves and prickly pears.",
        "Mountain forests: pine, spruce, birch and maple in the Appalachians; spruce, pine, "
        "oak, juniper and fir in the Rockies.",
    ])),
    art.photos([("sherman", "Giant sequoia: the General Sherman Tree"),
                ("redwood", "Coast redwoods, the tallest living things"),
                ("bristlecone", "Bristlecone pine: over 5,000 years old"),
                ("joshua", "Joshua tree (Mojave Desert)"),
                ("saguaro", "Saguaro cactus (Sonoran Desert)")]),
    art.trees_chart(),
    art.ages_axis(),
    "<h3>Animals of the USA</h3>",
    fact(ul([
        "<b>Yellowstone</b>: bears and bison.",
        "<b>The Rockies</b>: bighorn sheep, badgers, grizzly bears, black bears, coyotes, elk "
        "and white-tailed deer.",
        "<b>The Appalachians</b>: squirrels, cottontail rabbits, white-tailed deer, wolves, "
        "beavers, black bears and the red-tailed hawk.",
        "<b>The deserts</b>: lizards, snakes, bats, owls, jackrabbits, scorpions, pronghorns, "
        "the Mojave ground squirrel and the kangaroo rat.",
        "<b>Lake Okeechobee and the Everglades</b> (Florida): alligators, manatees, herons, "
        "cranes, river otters and bobcats.",
    ])),
    "<h3>Canada's 10 most iconic animals (WWF)</h3>",
    p("Canada is home to about 80,000 plant and animal species. WWF-Canada picks these ten:"),
    art.cards([art.card(WWF_PHOTO[a], i, a, "", r) for i, (a, r) in enumerate(WWF, 1)]),
    art.monarch_map(),
    fact(ul([
        "Canada has the <b>world's largest moose population</b>: about one million.",
        "The <b>Canada goose</b> migrates thousands of kilometres in a 'V' formation, which "
        "saves energy, at up to 96 km/h.",
        "The beaver once made Canada famous for the fur trade.",
        "In the Arctic: polar bears, walruses and narwhals. Kluane National Park has many "
        "grizzly bears. Travellers often see moose, bighorn sheep, mountain goats, bison and "
        "muskox.",
    ])),
    watch("Elk is not always the same animal.", p(
        "In North America an <b>elk</b> is a large deer, the wapiti. In British English "
        "\"elk\" means the animal Americans call a <b>moose</b> (a łoś). The <b>caribou</b> is "
        "the North American name for the reindeer.")),
    chips([("bison", "bizon"), ("bald eagle", "bielik amerykański"),
           ("Canada goose", "bernikla kanadyjska"), ("beaver", "bóbr"), ("moose", "łoś"),
           ("elk (AmE)", "wapiti"), ("caribou", "karibu, renifer"),
           ("bighorn sheep", "owca kanadyjska"), ("grizzly bear", "niedźwiedź grizli"),
           ("coyote", "kojot"), ("badger", "borsuk"), ("white-tailed deer", "jeleń wirginijski"),
           ("pronghorn", "widłoróg"), ("bobcat", "ryś rudy"), ("lynx", "ryś"),
           ("manatee", "manat"), ("heron", "czapla"), ("crane", "żuraw"),
           ("walrus", "mors"), ("beluga", "białucha"), ("narwhal", "narwal"),
           ("killer whale, orca", "orka"), ("puffin", "maskonur"),
           ("monarch butterfly", "motyl monarcha"), ("muskox", "piżmowół"),
           ("rodent", "gryzoń"), ("incisors", "siekacze"), ("antlers", "poroże"),
           ("tusks", "kły"), ("herd", "stado"), ("migration", "wędrówka, migracja"),
           ("pollinator", "zapylacz"), ("endangered", "zagrożony wyginięciem"),
           ("habitat", "siedlisko"), ("boreal forest", "las borealny, tajga"),
           ("giant sequoia", "mamutowiec olbrzymi (sekwoja)"),
           ("coast redwood", "sekwoja wieczniezielona"),
           ("bristlecone pine", "sosna długowieczna"),
           ("cactus / cacti", "kaktus / kaktusy"), ("prickly pear", "opuncja"),
           ("sagebrush", "bylica"), ("maple", "klon"), ("oak", "dąb"),
           ("spruce", "świerk"), ("fir", "jodła"), ("birch", "brzoza")]),
    remember([("bison + bald eagle", "the USA's national animal and bird"),
              ("beaver + Canada goose", "Canada's national animal and bird"),
              ("General Sherman", "the largest tree by volume, Sequoia National Park"),
              ("bristlecone pine", "the oldest living organism, over 5,000 years"),
              ("two-thirds", "of the world's polar bears live in Canada")]),
    checks([
        ("Why is the beaver called \"nature's engineer\"?",
         "Because it works so hard and keeps freshwater ecosystems healthy."),
        ("Which cactus is the Sonoran Desert famous for?", "The saguaro, over 60 ft tall."),
        ("What is a \"bull\" moose?", "A male moose."),
        ("Why is the beluga called \"the canary of the sea\"?",
         "Because of its chirps, clicks, whistles and squeals."),
    ], ["matching_030", "knowledge_038"]),
])

# ---------------------------------------------------------------- 6. national parks
NATGEO = [
    ("Zion", "Utah", "Watchman Mountain seen from the Canyon Junction Bridge, one of the most "
     "photographed views"),
    ("Yellowstone", "Wyoming, Montana, Idaho", "<b>America's first national park</b> (1872"
     + X + "); bears, bison, hot springs and geysers; the Great Fountain Geyser erupts every "
     "9&ndash;15 hours, up to 220 ft (67 m)"),
    ("Acadia", "Maine", "the first sunrise in the country at Bass Harbor Head Lighthouse; "
     "crowds on Cadillac Mountain; old carriage roads for bikes"),
    ("Yosemite", "California", "<b>\"moonbows\"</b>: rainbows at night under a full moon at "
     "Yosemite Falls"),
    ("Sequoia", "California", "in the Sierra Nevada, nearly 97% wilderness; over 2,000 giant "
     "sequoias, including the <b>General Sherman Tree</b>, the world's largest tree by volume"),
    ("Crater Lake", "Oregon", "the <b>deepest lake in the USA</b> (1,943 ft); Wizard Island, "
     "shaped like a sorcerer's hat"),
    ("Grand Canyon", "Arizona", "a huge gorge of pink, red and orange layers showing millions "
     "of years of geology"),
    ("Great Smoky Mountains", "Tennessee (and North Carolina)", "the southern Appalachians; "
     "fog among forested hills: water and hydrocarbons given off by the trees make the "
     "\"smoke\" that names them"),
    ("Death Valley", "California and Nevada", "the largest national park south of Alaska; "
     "North America's <b>driest and hottest spot</b> (under 2 inches of rain, 134&deg;F) and "
     "its <b>lowest point</b>, 282 ft below sea level; the Mesquite Sand Dunes"),
    ("Redwood", "California", "the oldest, largest and tallest coast redwoods, the tallest "
     "living things; John Steinbeck's \"cathedral hush\""),
    ("Olympic", "Washington", "73 miles of coast: cliffs, sea stacks, sandy beaches, rocky "
     "shores and tide pools"),
    ("Grand Teton", "Wyoming", "the Teton Range from Schwabacher Landing on the Snake River, "
     "made famous by Ansel Adams; lakes, glaciers, granite peaks; 3.5 million visitors in "
     "2024"),
    ("Everglades", "Florida", "between Lake Okeechobee and the Gulf of Mexico; one of the "
     "world's largest <b>tropical wetlands</b>; the third largest park in the lower 48"),
    ("Big Bend", "Texas", "the world's largest <b>International Dark Sky Reserve</b>; the "
     "Chihuahuan Desert; Boquillas Canyon"),
    ("Joshua Tree", "California", "the Mojave Desert; its tough, twisted Joshua trees are "
     "threatened by climate change"),
    ("Bryce Canyon", "Utah", "over 2.7 million visitors a year; red rock spires called "
     "<b>hoodoos</b>; the Amphitheater"),
    ("Arches", "Utah", "over 2,000 natural stone arches, shaped by weathering and erosion; "
     "Delicate Arch"),
    ("Great Sand Dunes", "Colorado", "the <b>highest sand dunes in North America</b>, below the "
     "Sangre de Cristo Mountains"),
    ("Dry Tortugas", "Florida", "70 miles west of Key West; Fort Jefferson (19th century); the "
     "third largest coral barrier reef in the world and the <b>only tropical reef in the "
     "continental USA</b>"),
    ("Mammoth Cave", "Kentucky", "more than 400 miles of caves under the hills"),
]

LARGEST = [("Wrangell-St. Elias", "Alaska"), ("Gates of the Arctic", "Alaska"),
           ("Denali", "Alaska"), ("Katmai", "Alaska"),
           ("Death Valley", "California and Nevada"), ("Glacier Bay", "Alaska"),
           ("Lake Clark", "Alaska"), ("Yellowstone", "Wyoming, Montana, Idaho"),
           ("Kobuk Valley", "Alaska"), ("Everglades", "Florida")]

CANADA_TOP = [
    ("Pacific Rim (National Park Reserve)", "British Columbia",
     "the west coast of Vancouver Island: Long Beach (big surf), the Broken Group Islands and "
     "the 47-mile <b>West Coast Trail</b>; temperate rainforest, cliffs and sandy beaches; "
     "humpback whales"),
    ("Banff", "Alberta", "in the heart of the Rockies, about 80 miles (128 km) west of Calgary; "
     "open since <b>1885</b>, Canada's oldest and most popular park; over 1,000 km of trails; "
     "turquoise <b>Lake Louise</b> with a glacier behind it; the Icefields Parkway"),
    ("Yoho", "British Columbia", "the western slopes of the Rockies; fossils of some of the "
     "earliest life on Earth; <b>Takakkaw Falls</b>, one of Canada's highest; Emerald Lake"),
    ("Jasper", "Alberta", "the eastern slopes of the Rockies; icefields, teal lakes, alpine "
     "meadows; bears, elk, caribou, bighorn sheep; the Columbia Icefield; a <b>Dark Sky "
     "Preserve</b> with a Dark Sky Festival in October"),
    ("Mont-Tremblant", "Quebec", "north of Montreal; six rivers, 400 streams and lakes, the "
     "Laurentian peaks, 40 kinds of mammals; the Via Ferrata du Diable climbing route"),
    ("Cape Breton Highlands", "Nova Scotia", "the north of Cape Breton Island; a high "
     "tundra-like plateau with forested river canyons; lynx, moose, minke whales, seals, bald "
     "eagles; a third of the <b>Cabot Trail</b>"),
    ("Gaspesie (Gaspésie)", "Quebec", "created in 1937; the <b>only caribou herd south of the "
     "St. Lawrence River</b>, salmon, the Chic-Choc and McGerrigle mountains (25 peaks over "
     "3,300 ft); the International Appalachian Trail"),
    ("Waterton Lakes", "Alberta", "where the prairies meet the Rockies; borders Glacier "
     "National Park in Montana; lakes, waterfalls, wildflowers"),
    ("Thousand Islands", "Ontario", "one of Canada's <b>smallest</b> national parks: 20-plus "
     "granite islands in the St. Lawrence River at the east end of Lake Ontario; rare turtles "
     "and birds"),
    ("Gros Morne", "Newfoundland and Labrador", "a UNESCO World Heritage Site on Newfoundland's "
     "west coast; granite mountains and <b>deep fjords</b>; the Tablelands, rocks from deep "
     "inside the Earth that show plate tectonics"),
]

NATGEO_PHOTO = ["zion", "yellowstone", "acadia", "yosemite", "sequoia", "crater", "grand_canyon",
                "smokies", "death_valley", "redwood_np", "olympic", "teton", "everglades",
                "big_bend", "joshua_np", "bryce", "arches", "sand_dunes", "tortugas", "mammoth"]
CANADA_PHOTO = ["pacific_rim", "banff", "yoho", "jasper", "tremblant", "cape_breton", "gaspesie",
                "waterton", "thousand", "gros_morne"]

S_PARKS = "".join([
    "<h3>USA: the 20 parks on the reading list</h3>",
    p("The USA has 63 national parks. The reading list covers the first 20 in National "
      "Geographic's photo article, in this order:"),
    art.us_parks_map(),
    art.cards([art.card(k, i, n, s, r, alt=f"{n} National Park, {s}")
               for i, ((n, s, r), k) in enumerate(zip(NATGEO, NATGEO_PHOTO), 1)]),
    "<h3>The ten largest US national parks</h3>",
    art.largest_parks_chart(),
    p('<span class="tip">This order, by area, is the same as on the ThoughtCo page in the '
      "reading list. Seven of the ten are in Alaska; "
      "Death Valley is the largest outside Alaska.</span>"),
    "<h3>Canada</h3>",
    fact(ul([
        "Canada has 48 national parks and national park reserves.",
        "<b>Wood Buffalo</b> (Alberta and the Northwest Territories) is the largest.",
        "<b>Banff</b> (1885) is the oldest and the most popular.",
        "<b>Kluane</b> (Yukon) has Mount Logan, Canada's largest icefields and many grizzly "
        "bears.",
        "<b>The Icefields Parkway</b>, one of the world's great drives (227 km / 141 miles), "
        "links Jasper with Lake Louise past the Columbia Icefield and the Athabasca Glacier.",
        "Canada has 22 UNESCO World Heritage Sites, among them the Rocky Mountain parks, Old "
        "Quebec, <b>Dinosaur Provincial Park</b> in Alberta (35 kinds of dinosaurs lived there) "
        "and <b>Writing-on-Stone / Áísínai'pi</b>, where the Blackfoot people left rock art.",
    ])),
    p("Canadian Sky's top 10, counted down from 10 to 1; here number 1 comes first:"),
    art.canada_parks_map(),
    art.cards([art.card(k, i, n, s, r, alt=f"{n}, {s}")
               for i, ((n, s, r), k) in enumerate(zip(CANADA_TOP, CANADA_PHOTO), 1)]),
    watch("Quebec's \"national parks\".", p(
        "In Quebec, a <i>parc national</i> is run by the province, not by Parks Canada. "
        "Gaspésie and Mont-Tremblant are this kind of park.")),
    chips([("national park", "park narodowy"), ("nature reserve", "rezerwat przyrody"),
           ("wilderness", "dzicz, dzika przyroda"), ("wildlife", "dzika przyroda (zwierzęta)"),
           ("geyser", "gejzer"), ("hot spring", "gorące źródło"), ("erupt", "wybuchać"),
           ("wetland(s)", "mokradła"), ("coral reef", "rafa koralowa"),
           ("sea stack", "ostaniec morski"), ("tide pool", "kałuża pływowa"),
           ("hoodoo", "skalny słup (hoodoo)"), ("arch", "łuk skalny"),
           ("cave", "jaskinia"), ("sand dune", "wydma"), ("weathering", "wietrzenie"),
           ("erosion", "erozja"), ("Dark Sky Reserve", "rezerwat ciemnego nieba"),
           ("temperate rainforest", "las deszczowy strefy umiarkowanej"),
           ("trail", "szlak"), ("World Heritage Site", "obiekt światowego dziedzictwa")]),
    remember([("Yellowstone", "the first US national park; the Great Fountain Geyser"),
              ("Wrangell-St. Elias", "the largest US national park, in Alaska"),
              ("Death Valley", "the largest park south of Alaska; hottest, driest, lowest"),
              ("Banff (1885)", "Canada's oldest park; Wood Buffalo: Canada's largest")]),
    checks([
        ("Where can you see \"moonbows\"?", "At Yosemite Falls, under a full moon."),
        ("Which park has the only tropical reef in the continental USA?", "Dry Tortugas, in "
         "Florida."),
        ("Which park protects the only caribou herd south of the St. Lawrence River?",
         "Gaspésie National Park, in Quebec."),
        ("Which Alberta park borders Glacier National Park in Montana?", "Waterton Lakes."),
    ], ["matching_026", "matching_027", "tfni_037", "matching_029"]),
])

# ---------------------------------------------------------------- 7. words and idioms
IDIOMS = {
    "Weather": [
        ("be under the weather", "feel slightly ill", "czuć się nie najlepiej"),
        ("a storm in a teacup", "a lot of fuss about something small (AmE: a tempest in a "
         "teapot)", "burza w szklance wody"),
        ("come rain or shine", "whatever happens", "bez względu na wszystko"),
        ("a fair-weather friend", "a friend only in good times", "przyjaciel na dobre czasy"),
        ("steal someone's thunder", "take the attention or praise someone else expected",
         "skraść komuś show"),
        ("every cloud has a silver lining", "something good comes from every bad situation",
         "nie ma tego złego, co by na dobre nie wyszło"),
        ("the calm before the storm", "a quiet time before trouble", "cisza przed burzą"),
        ("break the ice", "make people feel relaxed when they first meet", "przełamać lody"),
        ("be on cloud nine", "be extremely happy", "być w siódmym niebie"),
        ("a bolt from the blue", "a complete surprise", "grom z jasnego nieba"),
        ("weather the storm", "get through a difficult time", "przetrwać trudny okres"),
        ("be snowed under", "have too much work", "być zawalonym pracą"),
        ("it's raining cats and dogs", "it's raining very hard", "leje jak z cebra"),
        ("take a rain check (AmE)", "say no now, but maybe another time",
         "przełożyć na inny raz"),
    ],
    "Landscape": [
        ("make a mountain out of a molehill", "treat a small problem as a big one",
         "robić z igły widły"),
        ("not be out of the woods (yet)", "still be in difficulty or danger",
         "jeszcze nie wyjść na prostą"),
        ("a drop in the ocean", "a tiny amount compared with what is needed",
         "kropla w morzu"),
        ("the tip of the iceberg", "the small visible part of a much bigger problem",
         "wierzchołek góry lodowej"),
        ("can't see the wood for the trees (AmE: the forest for the trees)",
         "be so busy with details that you miss the main point",
         "nie widzieć lasu spoza drzew"),
        ("move mountains", "do something very difficult", "przenosić góry"),
        ("be over the hill", "be too old", "mieć najlepsze lata za sobą"),
        ("go downhill", "get worse and worse", "staczać się, pogarszać się"),
        ("a slippery slope", "something that will lead to worse things", "równia pochyła"),
        ("be in deep water", "be in serious trouble", "mieć poważne kłopoty"),
    ],
    "Plants": [
        ("beat about the bush (AmE: beat around the bush)",
         "avoid saying something directly", "owijać w bawełnę"),
        ("nip something in the bud", "stop a problem early, before it grows",
         "zdusić coś w zarodku"),
        ("bark up the wrong tree", "look for something in the wrong place, or blame the "
         "wrong person", "szukać nie tam, gdzie trzeba"),
        ("the grass is always greener on the other side",
         "other people's lives always seem better", "wszędzie dobrze, gdzie nas nie ma"),
        ("turn over a new leaf", "start to behave better", "zacząć od nowa"),
        ("a late bloomer", "someone who develops later than others",
         "ktoś, kto rozwinął się później"),
        ("money doesn't grow on trees", "money is not easy to get",
         "pieniądze nie rosną na drzewach"),
        ("as fresh as a daisy", "full of energy, not tired", "rześki jak skowronek"),
        ("hear something through the grapevine", "hear news unofficially",
         "dowiedzieć się pocztą pantoflową"),
    ],
    "Animals": [
        ("busy as a beaver / an eager beaver", "very busy / a very keen, hard-working person",
         "pracowity jak mrówka / gorliwiec"),
        ("take to something like a duck to water", "learn it quickly and easily",
         "czuć się w czymś jak ryba w wodzie"),
        ("a fish out of water", "someone who feels uncomfortable in a new place",
         "nie w swoim żywiole"),
        ("let the cat out of the bag", "tell a secret by mistake", "wygadać się"),
        ("kill two birds with one stone", "do two things with one action",
         "upiec dwie pieczenie na jednym ogniu"),
        ("a wild goose chase", "a hopeless search", "szukanie wiatru w polu"),
        ("the lion's share", "the biggest part", "lwia część"),
        ("cry wolf", "give a false alarm", "podnosić fałszywy alarm"),
        ("have butterflies in your stomach", "be nervous", "mieć tremę"),
        ("like a bear with a sore head", "in a very bad mood", "zły jak osa"),
        ("the elephant in the room", "an obvious problem nobody talks about",
         "temat, którego wszyscy unikają"),
        ("hold your horses", "wait, don't rush", "nie tak szybko"),
        ("when pigs fly", "never", "prędzej mi kaktus na dłoni wyrośnie"),
    ],
}

S_WORDS = "".join([
    p("The programme also asks for nature vocabulary: landforms and landscape, plants and "
      "animals, weather and climate, national parks and nature reserves, ecotourism, and "
      "idioms about landscape, weather, plants and animals. The reading list gives no source "
      "for this part, so these lists are our own. More words are in the sections above."),
    "<h3>Landforms and landscape</h3>",
    chips([("landscape", "krajobraz"), ("plain", "równina"), ("plateau", "płaskowyż"),
           ("valley", "dolina"), ("hill", "wzgórze"), ("slope", "zbocze"),
           ("ridge", "grzbiet"), ("cliff", "klif, urwisko"), ("mesa", "góra stołowa"),
           ("volcano", "wulkan"), ("crater", "krater"), ("peninsula", "półwysep"),
           ("bay", "zatoka"), ("swamp / marsh", "bagno / mokradło"),
           ("forest", "las"), ("rainforest", "las deszczowy"),
           ("desert", "pustynia"), ("prairie", "preria")]),
    "<h3>National parks, reserves and ecotourism</h3>",
    chips([("ecotourism", "ekoturystyka"), ("eco-friendly", "przyjazny środowisku"),
           ("sustainable", "zrównoważony"), ("conservation", "ochrona przyrody"),
           ("protected area", "obszar chroniony"), ("park ranger", "strażnik parku"),
           ("wildlife watching", "obserwowanie dzikich zwierząt"),
           ("guided tour", "wycieczka z przewodnikiem"), ("campsite", "pole namiotowe"),
           ("leave no trace", "nie zostawiaj śladów"), ("litter", "śmieci; śmiecić"),
           ("carbon footprint", "ślad węglowy"), ("biodiversity", "bioróżnorodność"),
           ("poaching", "kłusownictwo"), ("endangered species", "gatunek zagrożony"),
           ("reintroduce", "przywrócić (gatunek)")]),
    "".join(f"<h3>Idioms: {group.lower()}</h3>"
            + table(["Idiom", "Meaning", "Po polsku"], [[f"<b>{i}</b>", m, pl]
                                                         for i, m, pl in rows], cls="wide")
            for group, rows in IDIOMS.items()),
    watch("British and American versions.", p(
        "Some idioms change across the Atlantic: <i>beat about the bush</i> (BrE) / <i>beat "
        "around the bush</i> (AmE); <i>can't see the wood for the trees</i> / <i>the forest for "
        "the trees</i>; <i>a storm in a teacup</i> / <i>a tempest in a teapot</i>. Both are "
        "correct.")),
    checks([
        ("\"I've been under the weather.\" What does it mean?", "I've been slightly ill."),
        ("Finish it: \"You're making a mountain out of a ...\"", "molehill."),
        ("What does \"nip it in the bud\" mean?", "Stop a problem early, before it grows."),
        ("Your brother tells your news before you can. What did he do?",
         "He stole your thunder."),
    ], ["mc_017", "spelling_033"]),
])

# ---------------------------------------------------------------- 8. records
S_RECORDS = "".join([
    table(["Record", "USA", "Canada"], [
        ["Highest mountain", "Denali, Alaska: 6,190 m / 20,310 ft, also the highest in North "
         "America", "Mount Logan, Yukon: 5,959 m / 19,551 ft, second in North America"],
        ["Longest river", "Missouri: 2,540 miles", "Mackenzie: 4,241 km / 2,635 miles"],
        ["Largest lake", "Lake Superior (shared with Canada)",
         "Lake Superior (shared); entirely in Canada: Great Bear Lake"],
        ["Deepest lake", "Crater Lake, Oregon: " + ft(1943), ""],
        ["Largest state / province", "Alaska", "Quebec" + X],
        ["Smallest state / province", "Rhode Island", "Prince Edward Island" + X],
        ["Most people", "California", "Ontario" + X],
        ["Lowest point", "Badwater Basin, Death Valley: 86 m / 282 ft below sea level, the "
         "lowest in North America", ""],
        ["Hottest / coldest", "Death Valley: 134&deg;F (56.7&deg;C), a world record",
         "Snag, Yukon: &minus;63&deg;C (&minus;81&deg;F), February 1947"],
        ["Highest waterfall", "continental USA: Colonial Creek Falls, Washington (783 m); "
         "Hawaii: Olo'upena Falls (about 900 m)",
         "Takakkaw Falls (Yoho) is one of the highest; the Horseshoe Falls (Niagara) are the "
         "most powerful in North America"],
        ["Largest national park", "Wrangell-St. Elias, Alaska",
         "Wood Buffalo (Alberta and the Northwest Territories)"],
        ["Oldest national park", "Yellowstone (1872" + X + ")", "Banff (1885)"],
        ["Largest city / capital", "New York / Washington, D.C.", "Toronto / Ottawa"],
        ["Largest island", "", "Baffin Island, Nunavut: the world's fifth largest"],
    ], cls="wide"),
    "<h3>Dates on a timeline</h3>",
    art.timeline(),
    "<h3>World and North American records</h3>",
    fact(ul([
        "the longest international border: USA&ndash;Canada, 8,891 km",
        "the longest coastline: Canada, 202,080 km",
        "the most lakes: Canada, about three million",
        "the highest tides: the Bay of Fundy, up to 16 m",
        "the highest vertical cliff: Mount Thor, Baffin Island (a 1,250 m drop)",
        "the largest freshwater lake by area: Lake Superior, 82,100 km&sup2;",
        "the second longest mountain range in the world: the Rockies (the longest in North "
        "America)",
        "the fourth largest river system in the world: the Mississippi with the Missouri",
        "the largest tree by volume: the General Sherman Tree (a giant sequoia)",
        "the tallest living things: coast redwoods",
        "the oldest known living organism: the bristlecone pine",
        "the largest International Dark Sky Reserve: Big Bend",
        "the highest sand dunes in North America: Great Sand Dunes",
        "the largest moose population: Canada, about one million",
        "one of the longest insect migrations: the monarch butterfly",
        "the largest rodent in North America: the beaver",
    ])),
    "<h3>Where the sources disagree, or slip</h3>",
    p("A test question may copy its source, so know both versions."),
    fact(ul([
        "<b>The Missouri's length</b>: the USA Facts page gives 3,767 km / 2,341 miles; "
        "Ducksters gives 2,540 miles. Both say it is the longest river.",
        "<b>Denali's height</b>: 6,190 m / 20,310 ft on the USA Facts page; Ducksters still "
        "has the older 20,237 ft and the name Mount McKinley. In 2025 the US government "
        "brought back the name <b>Mount McKinley</b>; Alaska and the national park still say "
        "Denali. In 2025 it also renamed the Gulf of Mexico the <b>Gulf of America</b>. The "
        "sources use Denali and the Gulf of Mexico.",
        "<b>Death Valley</b>: National Geographic's heading puts it in Nevada. Most of the park "
        "is in California, with a part in Nevada.",
        "National Geographic's heading says <b>\"Grand Sand Dunes\"</b>; the park is called "
        "Great Sand Dunes.",
        "The USA Facts page gives <b>Badwater Basin</b> as \"86 m / 282 ft\": that is below sea "
        "level.",
        "Canada Facts' FAQ puts <b>Mount Logan</b> in the Rocky Mountains. It is in the Saint "
        "Elias Mountains, in Kluane National Park, as the same page says elsewhere.",
        "Canada Facts puts <b>Wood Buffalo</b> in Alberta; it lies in Alberta and the "
        "Northwest Territories.",
        "Canada's area is 3.85 million sq mi; the FAQ's \"3.58 million\" swaps two digits.",
        "Butter Insurance calls all four eastern provinces \"the Maritimes\". Strictly, the "
        "Maritimes are New Brunswick, Nova Scotia and Prince Edward Island; with Newfoundland "
        "and Labrador they are the Atlantic provinces. It also calls Manitoba and Saskatchewan "
        "\"the Prairies\"; usually Alberta is the third Prairie province.",
        "Canadian Sky spells the waterfall \"Takkakaw\"; the name is <b>Takakkaw Falls</b>.",
        "The moose: up to 1.8 m and 725 kg (WWF), or a bull up to 2.1 m and 700 kg (Canada "
        "Facts).",
        "The USA Facts page gives Washington, D.C. \"about 7.5 million inhabitants\". The "
        "city itself has far fewer (about 700,000)" + X + ".",
        "WWF calls the Canada lynx one of three lynx species; most lists count four, with the "
        "bobcat" + X + ".",
    ])),
])

SECTIONS = [
    ("where", "y", "Where they are", "Size, borders, oceans, regions", S_WHERE),
    ("states", "p", "States, provinces and capitals", "50 states, 10 provinces, 3 territories",
     S_STATES),
    ("land", "o", "Mountains, rivers, lakes and deserts",
     "Rockies, Missouri, Great Lakes, Mount Logan", S_LAND),
    ("climate", "g", "Climate and weather", "Region by region; the hottest and the coldest",
     S_CLIMATE),
    ("wildlife", "y", "Plants and animals", "Symbols, sequoias, WWF's 10 Canadian animals",
     S_WILDLIFE),
    ("parks", "p", "National parks", "20 US parks, the 10 largest, Canada's top 10", S_PARKS),
    ("words", "o", "Nature words and idioms", "Landforms, ecotourism, 46 idioms", S_WORDS),
    ("records", "g", "Records at a glance", "Highest, longest, largest; where sources disagree",
     S_RECORDS),
]

SOURCES = [
    ("USA Facts (Kids World Travel Guide)", "https://www.kids-world-travel-guide.com/usa-facts.html"),
    ("United States Geography (Ducksters)", "https://www.ducksters.com/geography/usgeography.php"),
    ("State Capitals of the 50 US States (ThoughtCo)",
     "https://www.thoughtco.com/capitals-of-the-fifty-states-1435160"),
    ("Largest National Parks in the United States (ThoughtCo)",
     "https://www.thoughtco.com/largest-national-parks-in-the-united-states-1435732"),
    ("See the beauty of all 63 U.S. national parks (National Geographic), parks 1-20",
     "https://www.nationalgeographic.com/travel/article/beautiful-photos-of-all-us-national-parks"),
    ("Canada Facts for Kids (Kids World Travel Guide)",
     "https://www.kids-world-travel-guide.com/canada-facts-for-kids.html"),
    ("Where Is Canada? (Butter Insurance)",
     "https://www.butterinsurance.com.au/posts/where-is-canada-understanding-its-geography-and-provinces"),
    ("Top 10 national parks in Canada (Canadian Sky)",
     "https://www.canadiansky.co.uk/wildlife-holidays/top-10-national-parks-in-canada"),
    ("Canada's 10 most iconic animals (WWF-Canada)",
     "https://wwf.ca/stories/canadas-10-most-iconic-animals"),
]

EXTRA_CSS = """
.tbl { overflow-x: auto; margin: 12px 0; }
.tbl table { border-collapse: collapse; width: 100%; background: var(--paper); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
.tbl.wide table { min-width: 560px; }
.tbl td, .tbl th { text-align: left; padding: 7px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
.tbl tr:last-child td { border-bottom: 0; }
.tbl th { font-size: .78rem; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.tbl td:first-child { font-weight: 700; }
.tbl.num td:first-child { font-variant-numeric: tabular-nums; color: var(--c); width: 2.4em; }
.tbl.num td:nth-child(2) { font-weight: 700; }
.cols { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); margin: 12px 0; }
.cols .tbl { margin: 4px 0 0; }
.cols h4 { margin: 0; font-family: "Bricolage Grotesque", sans-serif; color: var(--c); font-size: 1.05rem; }
.watch { border-left: 4px solid var(--c); background: var(--paper); border-radius: 0 12px 12px 0; padding: 10px 16px; margin: 16px 0; }
.watch ul { margin: .4rem 0 0; padding-left: 1.2rem; }
.watch li { margin: .25rem 0; }
.quizzes { display: flex; flex-wrap: wrap; gap: 8px; }
.x { color: var(--muted); font-weight: 700; }
@media print {
  .map, .howto, .learnt, .quizzes, .back { display: none; }
  body { background: #fff; color: #000; font-size: 12pt; }
  section.branch { break-before: page; }
  .tbl.wide table { min-width: 0; }
}
""" + art.ART_CSS


def used_photos(doc):
    return sorted(set(re.findall(r'src="/img/usa_kanada/(\w+)\.jpg"', doc)))


def page():
    uk = UK.read_text(encoding="utf-8")
    css = uk[uk.index("<style>") + len("<style>"):uk.index("</style>")]
    nav = "".join(
        f'<a class="node {cls}" href="#{key}"><strong>{title}</strong><span>{sub}</span>'
        f'<span class="done" data-for="{key}"></span></a>'
        for key, cls, title, sub, _ in SECTIONS)
    body = "".join(
        f'<section class="branch {cls}" id="{key}"><div class="branch-head"><h2>{title}</h2>'
        f'<label class="learnt"><input type="checkbox" data-key="{key}"> I\'ve learnt this'
        f"</label></div>{content}</section>\n"
        for key, cls, title, _, content in SECTIONS)
    sources = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(n)}</a></li>'
                      for n, u in SOURCES)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Tadzio's USA &amp; Canada Notebook</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap">
<style>{css}</style>
<style>body{{margin:0}}{EXTRA_CSS}</style>
</head>
<body>
<div class="wrap">
  <p class="back"><a href="/">&larr; Powrot do konkursu</a></p>
  <p class="eyebrow">Konkurs kuratoryjny 2026/27 · etap rejonowy · 3 December 2026</p>
  <h1>Tadzio's USA &amp; Canada Notebook</h1>
  <p class="lede">Everything on the regional round's reading list: the geography, nature and national parks of the USA and Canada, plus nature words and idioms. Hard words have their Polish meaning next to them.</p>

  <nav class="map" aria-label="Sections">
    <div class="hub">The USA and Canada: geography, nature and national parks</div>
    {nav}
  </nav>

  <div class="howto">
    <strong>How to use this notebook</strong>
    <ol>
      <li>Read one section a day; there are eight, so you finish with time to revise. Say the facts in the "Remember" box out loud.</li>
      <li>Answer the "Check yourself" questions before you open them.</li>
      <li>Do the SmartEn exercises for that section. Tick "I've learnt this" when you score well.</li>
      <li>Use the maps: cover the names with your hand and say what is where, then check.</li>
    </ol>
    <p class="tip">A star (<span class="x">*</span>) marks a fact that is not on the reading list but is worth knowing. To print, use the browser's print button: every answer opens and each section starts on a new page.</p>
  </div>

{body}
  <footer>
    <p>Based on the reading list for the etap rejonowy in the official programme of the Konkurs Jezyka Angielskiego 2026/27 (woj. mazowieckie):</p>
    <ul>{sources}</ul>
    <p>The two ThoughtCo pages could not be downloaded, so the state capitals and the ten largest parks were written from standard facts and then checked against those pages by hand on 18 November 2026. The ticks are saved only on this device.</p>
    <p>Maps drawn from <a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener">Natural Earth</a> data (public domain). Photos from Wikimedia Commons:</p>
    <details><summary>Photo credits ({len(used_photos(body))})</summary>{art.credits_html(used_photos(body))}</details>
  </footer>
</div>

<script>
(function () {{
  var KEY = "usa-canada-notebook-learnt";
  var state = {{}};
  try {{ state = JSON.parse(localStorage.getItem(KEY) || "{{}}") || {{}}; }} catch (e) {{ state = {{}}; }}
  function paint() {{
    document.querySelectorAll(".done").forEach(function (el) {{
      el.textContent = state[el.getAttribute("data-for")] ? "\\u2713 learnt" : "";
    }});
  }}
  document.querySelectorAll(".learnt input").forEach(function (box) {{
    var k = box.getAttribute("data-key");
    box.checked = !!state[k];
    box.addEventListener("change", function () {{
      state[k] = box.checked;
      try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch (e) {{}}
      paint();
    }});
  }});
  window.addEventListener("beforeprint", function () {{
    document.querySelectorAll("details").forEach(function (d) {{ d.open = true; }});
  }});
  paint();
}})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- checks
EXERCISES = ["knowledge_033", "knowledge_034", "knowledge_035", "knowledge_036",
             "knowledge_037", "knowledge_038", "matching_025", "matching_026", "matching_027",
             "matching_028", "matching_029", "matching_030", "mc_017", "spelling_033"]
IDIOM_PHRASES = ["under the weather", "storm in a teacup", "come rain or shine",
                 "fair-weather friend", "mountain out of a molehill", "beat about the bush",
                 "out of the woods", "drop in the ocean", "like a duck to water",
                 "nip something in the bud", "tip of the iceberg", "steal someone's thunder"]
VOID = {"meta", "link", "br", "input", "img", "hr"}


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.text = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"</{tag}> closes <{self.stack[-1] if self.stack else '-'}>")
        else:
            self.stack.pop()

    def handle_data(self, data):
        self.text.append(data)


def norm(s):
    return " ".join(s.lower().replace("’", "'").split())


def check(doc):
    problems = []
    parser = Tags()
    parser.feed(doc)
    problems += parser.errors + [f"<{t}> never closed" for t in parser.stack]
    text = norm(" ".join(parser.text))

    def has(variants):
        return any(norm(v) in text for v in (variants if isinstance(variants, list) else [variants]))

    for eid in EXERCISES:
        task = json.loads((PRACTICE / f"{eid}.json").read_text())["tasks"][0]
        letters = {o["letter"]: o["text"] for o in task.get("options", [])}
        for it in task["items"]:
            if task["type"] == "knowledge_questions":
                for key in ("answer", "secondAnswer"):
                    if it.get(key) and not has(it[key]):
                        problems.append(f"{eid} {it['id']}: no {it[key]!r} on the page")
            elif task["type"] == "matching":
                for v in (it["label"], letters[it["answer"]] if eid in ("matching_025",
                                                                       "matching_028") else None):
                    if v and not has(v):
                        problems.append(f"{eid} {it['id']}: no {v!r} on the page")
            elif task["type"] == "word_spelling" and not has(it["answer"]):
                problems.append(f"{eid} {it['id']}: no {it['answer']!r} on the page")
    problems += [f"mc_017: idiom {ph!r} missing" for ph in IDIOM_PHRASES if not has(ph)]
    states = [s for rows in STATES.values() for s, _ in rows]
    if len(states) != 50 or len(set(states)) != 50:
        problems.append(f"{len(states)} state rows, {len(set(states))} different")
    if len(PROVINCES) != 13 or len({n for n, *_ in PROVINCES}) != 13:
        problems.append("Canada needs its 10 provinces and 3 territories once each")
    for eid in re.findall(r'href="/cwiczenia/(\w+)/(\w+)"', doc):
        if eid[1] not in INDEX or INDEX[eid[1]]["taskType"] != eid[0]:
            problems.append(f"quiz link to unknown exercise {eid}")
    if len(NATGEO) != 20 or len(LARGEST) != 10 or len(CANADA_TOP) != 10 or len(WWF) != 10:
        problems.append("a list has the wrong length")
    n_idioms = sum(len(v) for v in IDIOMS.values())
    if "46 idioms" in doc and n_idioms != 46:
        problems.append(f"the nav card says 46 idioms but there are {n_idioms}")
    problems += check_pictures(doc)
    return problems


def check_pictures(doc):
    problems = []
    used = used_photos(doc)
    for key in used:
        if not (IMG / f"{key}.jpg").exists():
            problems.append(f"photo {key} is not in {IMG}")
        if key not in art.CREDITS:
            problems.append(f"photo {key} has no credit")
        elif art.esc(art.CREDITS[key]["page"]) not in doc:
            problems.append(f"photo {key}: credit not printed")
    on_disk = {f.stem for f in IMG.glob("*.jpg")}
    problems += [f"photo {k} is on disk but not used" for k in sorted(on_disk - set(used))]
    problems += [f"an <img> without alt text: {m[:60]}"
                 for m in re.findall(r"<img [^>]*>", doc) if 'alt=""' in m or "alt=" not in m]
    problems += ["an <svg> without aria-label" for m in re.findall(r"<svg [^>]*>", doc)
                 if "aria-label=" not in m and "aria-hidden" not in m]
    if [n for n, *_ in NATGEO] != [n for n, *_ in art.US_PARKS]:
        problems.append("the US parks map does not list the NatGeo parks in order")
    if [n for n, *_ in LARGEST] != [n for n, *_ in art.LARGEST_KM2]:
        problems.append("the largest-parks chart does not list LARGEST in order")
    if ([n.split(" (")[0] for n, *_ in CANADA_TOP]
            != [n.replace("é", "e") for n, *_ in art.CA_PARKS]):
        problems.append("the Canada parks map does not list CANADA_TOP in order")
    if len(NATGEO_PHOTO) != len(NATGEO) or len(CANADA_PHOTO) != len(CANADA_TOP):
        problems.append("a park has no photo")
    return problems


doc = page()
problems = check(doc)
for line in problems:
    print("PROBLEM", line)
if problems:
    sys.exit(1)
print(f"all checks pass ({len(doc):,} characters, "
      f"{sum(len(v) for v in IDIOMS.values())} idioms)")
if "--write" in sys.argv:
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT}")
