import test from "node:test";
import assert from "node:assert/strict";

// loadProgress and saveProgress touch localStorage; the rest of the module does
// not, so a minimal stub is enough and has to be in place before the import.
globalThis.localStorage = {
  store: new Map(),
  getItem(k) { return this.store.get(k) ?? null; },
  setItem(k, v) { this.store.set(k, String(v)); },
  clear() { this.store.clear(); },
};

const {
  emptyProgress, loadProgress, saveProgress, placeTrack, applyPlacement,
  recordResult, mergeProgress, recentActivity, PROGRESS_VERSION,
} = await import("./questProgress.js");
const {
  nextLevel, pickExercise, trackCounts, MIN_LEVEL, MAX_LEVEL, exercisePath,
} = await import("./questLevels.js");

const POOL = [
  { id: "a1", track: "spelling", level: 1, source: "quest", items: 6 },
  { id: "a2", track: "spelling", level: 1, source: "quest", items: 6 },
  { id: "b1", track: "spelling", level: 2, source: "quest", items: 6 },
  { id: "c1", track: "spelling", level: 3, source: "quest", items: 6 },
  { id: "r1", track: "reading", level: 4, source: "practice", items: 4 },
];

// --- the level rule -------------------------------------------------------

test("a strong first attempt moves the level up, a weak one moves it down", () => {
  assert.equal(nextLevel(3, 85), 4);
  assert.equal(nextLevel(3, 100), 4);
  assert.equal(nextLevel(3, 84), 3);
  assert.equal(nextLevel(3, 50), 3);
  assert.equal(nextLevel(3, 49), 2);
  assert.equal(nextLevel(3, 0), 2);
});

test("the level never leaves the ladder", () => {
  assert.equal(nextLevel(MAX_LEVEL, 100), MAX_LEVEL);
  assert.equal(nextLevel(MIN_LEVEL, 0), MIN_LEVEL);
});

// --- placement ------------------------------------------------------------

test("each probe moves her up at most two steps, and 2 is the bottom", () => {
  assert.equal(placeTrack(0, 0), 2);
  assert.equal(placeTrack(50, 0), 3);
  assert.equal(placeTrack(85, 0), 4);
  assert.equal(placeTrack(100, 100), 6);
  assert.equal(placeTrack(85, 50), 5);
});

test("one lucky probe cannot place her at the top on its own", () => {
  // Most items offer three choices, so a student who knows nothing still scores
  // about a third. A fluke on the harder probe must not carry her to level 6.
  assert.equal(placeTrack(0, 100), 4);
  assert.equal(placeTrack(0, 60), 3);
  assert.ok(placeTrack(0, 100) < placeTrack(100, 100));
});

test("placement never rewards a worse pair of scores with a higher level", () => {
  for (let a = 0; a <= 100; a += 5) {
    for (let b = 0; b <= 100; b += 5) {
      if (a < 100) assert.ok(placeTrack(a + 5, b) >= placeTrack(a, b));
      if (b < 100) assert.ok(placeTrack(a, b + 5) >= placeTrack(a, b));
    }
  }
});

test("applying a placement sets every track and records what was scored", () => {
  const p = emptyProgress();
  const levels = applyPlacement(p, {
    reading_3: 100, reading_5: 90,
    vocabulary_3: 80, vocabulary_5: 20,
    grammar_3: 60, grammar_5: 0,
    spelling_3: 10, spelling_5: 0,
  });
  assert.deepEqual(levels, { reading: 6, vocabulary: 3, grammar: 3, spelling: 2 });
  assert.equal(p.tracks.reading.level, 6);
  assert.equal(p.tracks.spelling.level, 2);
  assert.equal(p.placement.scores.reading_3, 100);
});

// --- recording a result ---------------------------------------------------

function placedAt(level) {
  const p = emptyProgress();
  for (const t of Object.values(p.tracks)) t.level = level;
  p.placement = { date: new Date().toISOString(), levels: {}, scores: {} };
  return p;
}

test("a first attempt moves the level and a repeat does not", () => {
  const p = placedAt(3);
  const entry = POOL[3]; // spelling, level 3

  const first = recordResult(p, entry, 6, 6);
  assert.equal(first.isFirst, true);
  assert.equal(first.levelAfter, 4);
  assert.equal(p.tracks.spelling.level, 4);

  // Replaying the same exercise perfectly must not climb again -- this is what
  // the old star count paid for and what the history showed her doing.
  const again = recordResult(p, entry, 6, 6);
  assert.equal(again.isFirst, false);
  assert.equal(again.verdict.move, "practice");
  assert.equal(p.tracks.spelling.level, 4);
});

test("a repeat still records a better best score", () => {
  const p = placedAt(3);
  recordResult(p, POOL[3], 2, 6);
  assert.equal(p.tracks.spelling.seen.c1.best, 33);
  const second = recordResult(p, POOL[3], 5, 6);
  assert.equal(p.tracks.spelling.seen.c1.best, 83);
  assert.equal(p.tracks.spelling.seen.c1.first, 33, "the first score is kept");
  assert.equal(p.tracks.spelling.seen.c1.attempts, 2);
  assert.equal(second.improved, true);
});

test("every attempt is recorded with the level it was taken at", () => {
  const p = placedAt(2);
  recordResult(p, POOL[2], 3, 6);
  assert.equal(p.attempts.length, 1);
  const a = p.attempts[0];
  assert.equal(a.exerciseId, "b1");
  assert.equal(a.track, "spelling");
  assert.equal(a.level, 2);
  assert.equal(a.percentage, 50);
  assert.equal(a.levelBefore, 2);
  assert.equal(a.levelAfter, 2);
});

test("an exercise with no points scores zero rather than NaN", () => {
  const p = placedAt(2);
  const r = recordResult(p, POOL[2], 0, 0);
  assert.equal(r.percentage, 0);
  assert.ok(Number.isFinite(p.attempts[0].percentage));
});

// --- picking --------------------------------------------------------------

test("picking prefers something unseen at her own level", () => {
  const pick = pickExercise(POOL, "spelling", 1, {}, () => 0);
  assert.equal(pick.level, 1);
});

test("picking widens to the neighbouring levels before repeating anything", () => {
  const seen = { a1: { lastDate: "2026-01-01" }, a2: { lastDate: "2026-01-02" } };
  const pick = pickExercise(POOL, "spelling", 1, seen, () => 0);
  assert.equal(pick.id, "b1", "steps up rather than handing back a done one");
});

test("with everything done it returns the least recently seen, not nothing", () => {
  const seen = {
    a1: { lastDate: "2026-01-05" }, a2: { lastDate: "2026-01-02" },
    b1: { lastDate: "2026-01-09" }, c1: { lastDate: "2026-01-07" },
  };
  const pick = pickExercise(POOL, "spelling", 1, seen, () => 0);
  assert.ok(pick, "never leaves her with no button to press");
  assert.equal(pick.id, "a2");
});

test("an empty track yields nothing rather than throwing", () => {
  assert.equal(pickExercise(POOL, "grammar", 3, {}, () => 0), null);
});

test("the counts describe her current level only", () => {
  const counts = trackCounts(POOL, "spelling", 1, { a1: { best: 50 } });
  assert.deepEqual(counts, { done: 1, total: 2 });
});

test("an exercise is fetched from the folder its source names", () => {
  assert.match(exercisePath({ id: "tfni_024", source: "practice" }), /\/practice\/tfni_024\.json$/);
  assert.match(exercisePath({ id: "ojaj_x", source: "ojaj" }), /\/ojaj\/practice\/ojaj_x\.json$/);
  assert.throws(() => exercisePath({ id: "x", source: "nowhere" }));
});

// --- storage and merging --------------------------------------------------

test("a version 1 blob is not read as progress, but is kept", () => {
  localStorage.clear();
  localStorage.setItem("smarten_quest_Lidia", JSON.stringify({
    stars: 28,
    branches: { vocabulary: { bestScores: { quest_vocab_01: 100 } } },
    attempts: [{ attemptId: "x", exerciseId: "quest_vocab_01", percentage: 100 }],
  }));
  const p = loadProgress("Lidia");
  assert.equal(p.version, PROGRESS_VERSION);
  assert.equal(p.placement, null, "she is sent to the placement test");
  assert.deepEqual(p.tracks.vocabulary.seen, {});
  assert.equal(p.archived.stars, 28, "the old record is kept, not thrown away");
});

test("unreadable storage yields empty progress rather than throwing", () => {
  localStorage.clear();
  localStorage.setItem("smarten_quest_Lidia", "{not json");
  assert.equal(loadProgress("Lidia").version, PROGRESS_VERSION);
});

test("a saved blob comes back as it went in", () => {
  localStorage.clear();
  const p = placedAt(4);
  recordResult(p, POOL[4], 4, 4);
  saveProgress("Zosia", p);
  const back = loadProgress("Zosia");
  assert.equal(back.tracks.reading.level, 5);
  assert.equal(back.attempts.length, 1);
});

test("merging keeps the better score and unions the attempts", () => {
  const a = placedAt(3);
  recordResult(a, POOL[3], 2, 6);
  const b = placedAt(3);
  recordResult(b, POOL[3], 5, 6);
  const merged = mergeProgress(a, b);
  assert.equal(merged.tracks.spelling.seen.c1.best, 83);
  assert.equal(merged.attempts.length, 2);
});

test("merging takes the level from whichever copy has seen more of the track", () => {
  const local = placedAt(2);
  const remote = placedAt(2);
  recordResult(remote, POOL[0], 6, 6);   // remote has watched her; level 2 -> 3
  recordResult(remote, POOL[2], 1, 6);   // ... and back down to 2
  const merged = mergeProgress(local, remote);
  assert.equal(Object.keys(merged.tracks.spelling.seen).length, 2);
  assert.equal(merged.tracks.spelling.level, remote.tracks.spelling.level);
});

test("a version 1 copy on the server is ignored rather than merged in", () => {
  const local = placedAt(3);
  const merged = mergeProgress(local, { version: 1, branches: {}, attempts: [] });
  assert.equal(merged, local);
});

test("the week's activity counts exercises and the days they fell on", () => {
  const p = placedAt(3);
  const today = new Date().toISOString();
  const old = new Date(Date.now() - 30 * 864e5).toISOString();
  p.attempts = [
    { date: today, attemptId: "1" }, { date: today, attemptId: "2" },
    { date: old, attemptId: "3" },
  ];
  assert.deepEqual(recentActivity(p, 7), { exercises: 2, days: 1 });
});
