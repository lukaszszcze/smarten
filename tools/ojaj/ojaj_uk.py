#!/usr/bin/env python3
"""UK culture questions for the OJAJ 2026/27 school round, written for this app.

Imported by tools/ojaj/ojaj_new.py, which appends GROUPS to its own; tools/ojaj/gen_ojaj.py
then writes and checks these exercises with no further edit.

Unlike every other OJAJ exercise here, these are not taken from a published
paper. The 2026/27 programme says the school round tests "znajomosc zagadnien
kulturowych dotyczacych Wielkiej Brytanii, zgodnie z mapa mysli", and the only
material published for that is the mind map itself:

    https://ojaj.wsjo.pl/wp-content/uploads/2026/08/OJAJ-2026_2027-The-UK.pdf

Each question below covers one node of that map, in the paper's culture-task
format (a question, four options, one correct). Every exercise title says the
questions are the app's own, so nobody mistakes them for official material.

The map's nodes, and which exercise covers them:
    Symbols of the UK (flags, Royal Coat of Arms), the four nations' plants and
    patron saints                                          -> ojaj_uk_symbole
    The UK Parliament: components, officials, symbols and ceremonies,
    devolution, the two major parties                      -> ojaj_uk_parlament
    Magna Carta, Act of Supremacy, Great Fire of London, Suez, Falklands
                                                           -> ojaj_uk_historia
    Landmarks of London, Hyde Park, Kensington Gardens     -> ojaj_uk_londyn
    Notable Britons                                        -> ojaj_uk_postacie

A distractor must be false, not merely less good: "Honi soit qui mal y pense"
is also on the Royal Coat of Arms, so the motto question does not offer it.
"""

MAP_SRC = (
    "https://ojaj.wsjo.pl/wp-content/uploads/2026/08/OJAJ-2026_2027-The-UK.pdf"
)

INSTR = (
    "Pytania wlasne do mapy mysli OJAJ 2026/27 o Wielkiej Brytanii (nie z "
    "arkusza olimpiady). Z podanych odpowiedzi wybierz poprawna. Tylko jedna "
    "jest prawidlowa."
)


# Where the correct option lands, item by item. The rows list the correct
# option first because that is easiest to write and check; the player shuffles
# options anyway, but the stored key should not be all one letter.
SPREAD = "CADBBDACDB"


def uk_exercise(ex_id, title, rows):
    """rows: (question, [correct option, then three wrong ones], "A")."""
    items = []
    for i, (stem, opts, first) in enumerate(rows, start=1):
        assert len(opts) == 4, f"{ex_id} {i}: {len(opts)} options"
        assert first == "A", f"{ex_id} {i}: correct option must be listed first"
        answer = SPREAD[(i - 1) % len(SPREAD)]
        slot = "ABCD".index(answer)
        placed = opts[1:slot + 1] + [opts[0]] + opts[slot + 1:]
        items.append({
            "id": f"1.{i}",
            "stem": stem,
            "options": [f"{l}) {o}" for l, o in zip("ABCD", placed)],
            "answer": answer,
        })
    return ex_id, {
        "title": f"{title} (pytania wlasne)",
        "type": "practice",
        "source": MAP_SRC,
        "tasks": [{
            "id": "1",
            "type": "multiple_choice",
            "points": len(items),
            "instruction": INSTR,
            "items": items,
        }],
    }


SYMBOLS = uk_exercise("ojaj_uk_symbole", "Wielka Brytania: symbole", [
    ("Which three crosses are combined in the Union Flag (the Union Jack)?",
     ["St George, St Andrew and St Patrick",
      "St George, St David and St Andrew",
      "St David, St Patrick and St Andrew",
      "St George, St David and St Patrick"], "A"),
    ("Why does Wales not appear on the Union Flag?",
     ["Wales was already united with England when the first Union Flag was "
      "created in 1606.",
      "Wales joined the United Kingdom only in the twentieth century.",
      "The Welsh parliament voted to leave its symbol off the flag.",
      "The Welsh dragon was thought too difficult to sew."], "A"),
    ("When is the Royal Standard flown over a royal building?",
     ["When the monarch is inside the building.",
      "At half-mast, when a member of the royal family dies.",
      "Every day, on all government buildings.",
      "Only on the monarch's official birthday."], "A"),
    ("Which symbol represents Ireland on the Royal Standard?",
     ["a harp", "a shamrock", "a red hand", "a green lion"], "A"),
    ("Which two animals hold up the shield on the Royal Coat of Arms?",
     ["a lion and a unicorn", "a lion and a dragon", "a unicorn and an eagle",
      "a stag and a horse"], "A"),
    ("Which motto appears on the scroll at the bottom of the Royal Coat of "
     "Arms?",
     ["Dieu et mon droit", "Semper fidelis", "E pluribus unum",
      "Veni, vidi, vici"], "A"),
    ("Which plant is the national emblem of Scotland?",
     ["the thistle", "the daffodil", "the rose", "the shamrock"], "A"),
    ("Which plant is traditionally associated with Northern Ireland?",
     ["the shamrock", "the thistle", "the daffodil", "the rose"], "A"),
    ("Who is the patron saint of Scotland?",
     ["St Andrew", "St Patrick", "St David", "St George"], "A"),
    ("On which date is St David's Day, the national day of Wales?",
     ["1 March", "17 March", "23 April", "30 November"], "A"),
])

PARLIAMENT = uk_exercise("ojaj_uk_parlament", "Wielka Brytania: parlament", [
    ("What are the three components of the UK Parliament?",
     ["the House of Commons, the House of Lords and the monarch",
      "the House of Commons, the House of Lords and the Prime Minister",
      "the House of Commons, the Supreme Court and the monarch",
      "the Cabinet, the House of Lords and the Prime Minister"], "A"),
    ("How many Members of Parliament (MPs) sit in the House of Commons?",
     ["650", "435", "100", "800"], "A"),
    ("How do most members of the House of Lords get their seats?",
     ["They are appointed, not elected.",
      "They are elected every five years.",
      "They all inherit their seats from their fathers.",
      "They are chosen by lot from ordinary citizens."], "A"),
    ("What is one of the jobs of the Serjeant at Arms?",
     ["keeping order in the House of Commons and carrying the Mace",
      "writing the monarch's speech",
      "counting the votes in general elections",
      "choosing the Prime Minister"], "A"),
    ("What happens when Black Rod comes to call MPs to the State Opening of "
     "Parliament?",
     ["The door of the Commons is slammed shut, and Black Rod knocks on it "
      "three times.",
      "Black Rod reads the monarch's speech in the House of Commons.",
      "MPs throw their order papers at Black Rod.",
      "Black Rod locks the MPs inside until the ceremony is over."], "A"),
    ("Why is the official sometimes called \"Lady Usher of the Black Rod\"?",
     ["Since 2018 the post has been held by a woman.",
      "The post was created for a queen.",
      "The job has always been done by a woman.",
      "It is the title used only in the House of Commons."], "A"),
    ("What does the Mace in the House of Commons represent?",
     ["the authority of the monarch, without which the House cannot meet or "
      "pass laws",
      "the power of the Prime Minister over the Cabinet",
      "the victory of Parliament in the Falklands War",
      "the right of MPs to carry weapons"], "A"),
    ("What is the Woolsack?",
     ["the seat of the Lord Speaker in the House of Lords",
      "the bag in which MPs' votes are collected",
      "the Speaker's chair in the House of Commons",
      "the monarch's throne in Westminster Abbey"], "A"),
    ("What does the monarch do at the State Opening of Parliament?",
     ["reads a speech, written by the government, setting out its plans",
      "chooses the new Speaker of the House of Commons",
      "votes on the first new law of the year",
      "opens the doors of the House of Commons in person"], "A"),
    ("What is devolution in the UK?",
     ["passing some powers from the UK Parliament to Scotland, Wales and "
      "Northern Ireland",
      "the system in which the monarch chooses the Prime Minister",
      "the gradual change of the Labour Party into the Conservative Party",
      "the division of London into boroughs"], "A"),
])

HISTORY = uk_exercise("ojaj_uk_historia", "Wielka Brytania: historia", [
    ("Which king put his seal on the Magna Carta in 1215?",
     ["King John", "Richard the Lionheart", "Henry VIII", "Edward I"], "A"),
    ("Where was the Magna Carta sealed?",
     ["at Runnymede, beside the River Thames", "in the Tower of London",
      "at Stonehenge", "in Westminster Abbey"], "A"),
    ("Which king was made head of the Church of England by the Act of "
     "Supremacy in 1534?",
     ["Henry VIII", "Henry VII", "Charles I", "Edward VI"], "A"),
    ("Why did the king break with the Pope in Rome before the Act of "
     "Supremacy?",
     ["The Pope would not annul his marriage to Catherine of Aragon.",
      "The Pope refused to crown him king.",
      "The Pope had supported Spain in a war against England.",
      "The Pope demanded that England pay higher taxes to Rome."], "A"),
    ("Where did the Great Fire of London of 1666 start?",
     ["in a bakery in Pudding Lane", "in the Tower of London",
      "in the Globe Theatre", "in St Paul's Cathedral"], "A"),
    ("Which famous building was destroyed in the Great Fire and rebuilt by "
     "Sir Christopher Wren?",
     ["St Paul's Cathedral", "Westminster Abbey", "Buckingham Palace",
      "the Tower of London"], "A"),
    ("What started the Suez Crisis in 1956?",
     ["Egypt's President Nasser took control of the Suez Canal.",
      "Britain tried to build a second canal next to Suez.",
      "The Suez Canal was closed by a storm for a year.",
      "Israel bought the Suez Canal from France."], "A"),
    ("How did the Suez Crisis end for Britain?",
     ["Britain and France had to withdraw, mainly under pressure from the "
      "USA.",
      "Britain won control of the canal for another fifty years.",
      "Britain shared the canal with Egypt until 2000.",
      "Britain bought the canal back from Egypt."], "A"),
    ("Which country invaded the Falkland Islands in 1982?",
     ["Argentina", "Chile", "Spain", "Brazil"], "A"),
    ("Who was the British Prime Minister during the Falklands War?",
     ["Margaret Thatcher", "Winston Churchill", "Tony Blair",
      "Anthony Eden"], "A"),
])

LONDON = uk_exercise("ojaj_uk_londyn", "Wielka Brytania: Londyn", [
    ("Who began building the Tower of London?",
     ["William the Conqueror", "Henry VIII", "Queen Victoria",
      "King Arthur"], "A"),
    ("What is kept in the Tower of London and seen by millions of visitors?",
     ["the Crown Jewels", "the Magna Carta", "the Rosetta Stone",
      "the royal family's horses"], "A"),
    ("What is the popular name of the Yeoman Warders of the Tower of London?",
     ["Beefeaters", "Redcoats", "Bobbies", "Grenadiers"], "A"),
    ("What does the Monument near London Bridge commemorate?",
     ["the Great Fire of London", "the Battle of Britain",
      "the coronation of Queen Elizabeth I", "the Magna Carta"], "A"),
    ("The Monument is 61 metres tall. What is special about this height?",
     ["It is the distance from the Monument to where the Great Fire started.",
      "It is the height of the old St Paul's Cathedral.",
      "It is the depth of the River Thames under London Bridge.",
      "It is the number of houses that survived the fire."], "A"),
    ("Which king turned Hyde Park into a royal hunting ground in 1536?",
     ["Henry VIII", "Charles I", "William the Conqueror", "George III"], "A"),
    ("What can people do at Speakers' Corner in Hyde Park?",
     ["give a public speech on almost any topic",
      "watch the King's Speech on a big screen",
      "vote in general elections",
      "meet Members of Parliament every Sunday"], "A"),
    ("Which words are carved on the Animals in War memorial?",
     ["They had no choice", "Lest we forget", "Deeds, not words",
      "Keep calm and carry on"], "A"),
    ("Who did Queen Victoria build the Albert Memorial for?",
     ["her husband, Prince Albert", "her father, Prince Albert",
      "her son, King Albert", "her architect, Albert Scott"], "A"),
    ("How did the Peter Pan statue appear in Kensington Gardens in 1912?",
     ["J. M. Barrie had it put up secretly overnight, as if by magic.",
      "Children collected money for it for ten years.",
      "It was moved there from Buckingham Palace.",
      "It was a present from the people of Scotland."], "A"),
])

BRITONS = uk_exercise("ojaj_uk_postacie", "Wielka Brytania: slynni Brytyjczycy", [
    ("On which ship did Charles Darwin sail around the world?",
     ["HMS Beagle", "HMS Victory", "the Mayflower", "the Titanic"], "A"),
    ("Which book by Charles Darwin set out the theory of evolution by natural "
     "selection?",
     ["On the Origin of Species", "A Brief History of Time",
      "The Descent of the Planets", "The Wealth of Nations"], "A"),
    ("Why is Ada Lovelace often called the first computer programmer?",
     ["She wrote a program for Charles Babbage's Analytical Engine.",
      "She built the first electronic computer.",
      "She invented the World Wide Web.",
      "She broke the Enigma code in the Second World War."], "A"),
    ("Who was Ada Lovelace's father?",
     ["the poet Lord Byron", "Charles Darwin", "Charles Babbage",
      "Isaac Newton"], "A"),
    ("What did Emmeline Pankhurst fight for?",
     ["the right of women to vote", "the end of the slave trade",
      "free schools for all children", "independence for Scotland"], "A"),
    ("What was the motto of the suffragettes led by Emmeline Pankhurst?",
     ["Deeds, not words", "Keep calm and carry on", "Dieu et mon droit",
      "They had no choice"], "A"),
    ("Which famous detective did Arthur Conan Doyle create?",
     ["Sherlock Holmes", "Hercule Poirot", "Miss Marple",
      "Father Brown"], "A"),
    ("In which city was Arthur Conan Doyle born?",
     ["Edinburgh", "London", "Dublin", "Cardiff"], "A"),
    ("For which film did Christopher Nolan win the Oscar for Best Director?",
     ["Oppenheimer", "Inception", "Interstellar", "The Dark Knight"], "A"),
    ("Which Christopher Nolan film tells the story of the evacuation of "
     "Allied soldiers from France in 1940?",
     ["Dunkirk", "Tenet", "Memento", "Oppenheimer"], "A"),
])

# --------------------------------------------------------------------------
# What ojaj_new.py consumes
# --------------------------------------------------------------------------

GROUPS = [
    ("Wielka Brytania 2026/27 - pytania wlasne do mapy mysli",
     [SYMBOLS, PARLIAMENT, HISTORY, LONDON, BRITONS]),
]
