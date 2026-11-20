"""Tag every exercise available to the quest section with a track and a level.

Builds pub/konkursy/angielski/data/quest/index.json from three sources:

  quest/          45 exercises written for young learners
  practice/      325 competition exercises, kuratoryjny
  ojaj/practice/  44 olympiad exercises, B2-C1+

A track groups exercises by what they ask a student to DO, not by subject, so a
student's level in one track cannot drag another down. Reading and Vocabulary
ask her to understand and choose; Spelling asks her to produce the word.

Level is WITHIN-TRACK (1-6) and comes from difficulty a human already assigned,
never from a text measure of my own:

  L1-3  quest/, from the hand-authored ladder it shipped with (old 1-5 -> 1-3)
  L4    practice/ with no stage label   (etap szkolny, entry competition)
  L5    practice/ labelled "poziom rejonowy/wojewodzki"
  L6    practice/ labelled "poziom wojewodzki", plus every OJAJ exercise

Run:  python3 tools/practice/tag_quest.py            # print the ladder for review
      python3 tools/practice/tag_quest.py --write    # write index.json
"""
import json, glob, os, re, sys, collections

ROOT = "pub/konkursy/angielski/data"

TRACKS = [
    {"id": "reading", "name": "Reading", "colour": "#38bdf8",
     "blurb": "Read something and work out what it says"},
    {"id": "vocabulary", "name": "Vocabulary", "colour": "#f59e0b",
     "blurb": "Pick the word that fits"},
    {"id": "grammar", "name": "Grammar", "colour": "#8b5cf6",
     "blurb": "Put the sentence together correctly"},
    {"id": "spelling", "name": "Spelling and word building", "colour": "#34d399",
     "blurb": "Write the word yourself"},
]

# A task type absent from this map is left out of the quest pool:
#
#   knowledge_questions      British-culture trivia rather than English
#   writing                  a long sitting, and marked by the model
#   sentence_transformation  the hardest format in the app: write the whole
#   grammar_gaps             sentence out. Both are marked by an API call, so a
#                            failed call leaves a zero on the board and moves a
#                            level for the wrong reason. The cloze pool is large
#                            enough without them; revisit if she outgrows it.
TRACK_OF_TYPE = {
    "true_false_ni": "reading",
    "gap_fill_sentences": "reading",
    "matching": "reading",
    "matching_columns": "reading",
    "multiple_choice": "vocabulary",
    "dialogue_choice": "vocabulary",
    "open_cloze": "grammar",
    "word_spelling": "spelling",
    "word_formation": "spelling",
}

# Which of the five hand-authored levels each quest exercise sat on, copied out
# of the index this script replaced. Held here rather than read back from
# index.json, which this script overwrites -- otherwise a second run has nothing
# to read and the ordering is gone.
QUEST_LADDER = {
    "quest_grammar_01": 1,
    "quest_grammar_02": 1,
    "quest_grammar_03": 1,
    "quest_grammar_04": 2,
    "quest_grammar_05": 2,
    "quest_grammar_06": 2,
    "quest_grammar_07": 3,
    "quest_grammar_08": 3,
    "quest_grammar_09": 3,
    "quest_grammar_10": 4,
    "quest_grammar_11": 4,
    "quest_grammar_12": 4,
    "quest_grammar_13": 5,
    "quest_grammar_14": 5,
    "quest_grammar_15": 5,
    "quest_reading_01": 1,
    "quest_reading_02": 1,
    "quest_reading_03": 1,
    "quest_reading_04": 2,
    "quest_reading_05": 2,
    "quest_reading_06": 2,
    "quest_reading_07": 3,
    "quest_reading_08": 3,
    "quest_reading_09": 3,
    "quest_reading_10": 4,
    "quest_reading_11": 4,
    "quest_reading_12": 4,
    "quest_reading_13": 5,
    "quest_reading_14": 5,
    "quest_reading_15": 5,
    "quest_vocab_01": 1,
    "quest_vocab_02": 1,
    "quest_vocab_03": 1,
    "quest_vocab_04": 2,
    "quest_vocab_05": 2,
    "quest_vocab_06": 2,
    "quest_vocab_07": 3,
    "quest_vocab_08": 3,
    "quest_vocab_09": 3,
    "quest_vocab_10": 4,
    "quest_vocab_11": 4,
    "quest_vocab_12": 4,
    "quest_vocab_13": 5,
    "quest_vocab_14": 5,
    "quest_vocab_15": 5,
}


# Five hand-authored levels compress into three. The old top two levels were
# both "competition ready" and differ little.
LADDER_TO_LEVEL = {1: 1, 2: 1, 3: 2, 4: 3, 5: 3}


def track_for(ex_id, task_type):
    """The filename says what a quest exercise is about; the task type does not.
    quest_grammar_* are multiple choice but they are grammar, and
    quest_reading_08/11/14 are comprehension in multiple-choice clothing."""
    if ex_id.startswith("quest_grammar_"):
        return "grammar"
    if ex_id.startswith("quest_reading_"):
        return "reading"
    return TRACK_OF_TYPE.get(task_type)


def practice_level(title):
    t = title.lower()
    if "poziom rejonowy" in t:
        return 5
    if "poziom wojewodzki" in t:
        return 6
    return 4


def collect():
    rows, skipped = [], []

    sources = [
        ("quest", f"{ROOT}/quest"),
        ("practice", f"{ROOT}/practice"),
        ("ojaj", f"{ROOT}/ojaj/practice"),
    ]
    for source, folder in sources:
        for path in sorted(glob.glob(f"{folder}/*.json")):
            name = os.path.basename(path)[:-5]
            if name == "index":
                continue
            d = json.load(open(path))
            tasks = d.get("tasks") or []
            if len(tasks) != 1:
                skipped.append((name, f"{len(tasks)} tasks"))
                continue
            task = tasks[0]
            title = d.get("title") or name
            track = track_for(name, task["type"])
            if not track:
                skipped.append((name, f"type {task['type']}"))
                continue
            if source == "quest":
                # Exercises written after the ladder carry their own placement.
                if name in QUEST_LADDER:
                    level = LADDER_TO_LEVEL[QUEST_LADDER[name]]
                else:
                    level = d["questLevel"]
                    track = d["questTrack"]
            elif source == "ojaj":
                level = 6
            else:
                level = practice_level(title)
            rows.append({
                "id": name,
                "title": title,
                "track": track,
                "level": level,
                "taskType": task["type"],
                "points": task.get("points", 0),
                "items": len(task.get("items") or []),
                "source": source,
            })
    return rows, skipped


if __name__ == "__main__":
    rows, skipped = collect()
    grid = collections.Counter((r["track"], r["level"]) for r in rows)
    print(f"{len(rows)} exercises tagged, {len(skipped)} left out\n")
    print("        L1  L2  L3  L4  L5  L6   total")
    for t in TRACKS:
        counts = [grid[(t['id'], l)] for l in range(1, 7)]
        print(f"{t['id'][:10]:10s}" + "".join(f"{c:4d}" for c in counts) + f"{sum(counts):8d}")
    thin = [(t, l, grid[(t, l)]) for t in (x["id"] for x in TRACKS) for l in range(1, 7)
            if grid[(t, l)] < 4]
    if thin:
        print("\nthin (under 4 exercises, she would run out):")
        for t, l, c in thin:
            print(f"  {t} L{l}: {c}")
    if "--write" in sys.argv:
        out = {"tracks": TRACKS,
               "pool": sorted(rows, key=lambda r: (r["track"], r["level"], r["id"]))}
        with open(f"{ROOT}/quest/index.json", "w") as fh:
            json.dump(out, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\nwrote {ROOT}/quest/index.json")
