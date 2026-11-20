// End-to-end check of the quest level model against the real content index.
//
// Simulates a student with a known true ability per track, runs her through the
// placement test and then twenty-five exercises, and checks two things:
//   1. the placement lands within one level of her true ability
//   2. the level rule holds her near it, scoring in the intended 55-85% band
//
// Run: node tools/practice/sim_quest.mjs
import fs from "node:fs";
// node 22 already provides globalThis.crypto with randomUUID.
globalThis.localStorage = {
  store: new Map(),
  getItem(k) { return this.store.get(k) ?? null; },
  setItem(k, v) { this.store.set(k, v); },
};

const { emptyProgress, applyPlacement, recordResult, placeTrack } =
  await import("../../site/src/lib/questProgress.js");
const { pickExercise, TRACK_IDS, trackCeiling } = await import("../../site/src/lib/questLevels.js");

const DATA = "pub/konkursy/angielski/data/quest";
const index = JSON.parse(fs.readFileSync(`${DATA}/index.json`, "utf8"));
const placement = JSON.parse(fs.readFileSync(`${DATA}/placement.json`, "utf8"));

// Deterministic generator, so a failure is reproducible.
let seed = 20260905;
const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;

// Chance of getting one item right: even odds when the exercise sits at her
// ability, sliding either way from there, floored at the guess rate of the type.
const GUESS = { multiple_choice: 1 / 3, dialogue_choice: 1 / 3, true_false_ni: 1 / 3,
  matching: 1 / 3, gap_fill_sentences: 1 / 6 };
function itemChance(ability, level, type) {
  const p = 0.55 + 0.28 * (ability - level);
  return Math.max(GUESS[type] ?? 0.02, Math.min(0.97, p));
}
function sit(ability, level, type, nItems) {
  const p = itemChance(ability, level, type);
  let correct = 0;
  for (let i = 0; i < nItems; i++) if (rnd() < p) correct++;
  return { score: correct, max: nItems, pct: Math.round((correct / nItems) * 100) };
}

function runOne(abilities, label) {
  const progress = emptyProgress();

  // The placement test.
  const probeScores = {};
  for (const task of placement.tasks) {
    const n = (task.items || []).length;
    probeScores[task.id] = sit(abilities[task.track], task.probeLevel, task.type, n).pct;
  }
  const ceilings = Object.fromEntries(TRACK_IDS.map((id) => [id, trackCeiling(index.pool, id)]));
  const placed = applyPlacement(progress, probeScores, ceilings);

  // Twenty-five exercises, spread evenly over the four tracks.
  const scores = { reading: [], vocabulary: [], grammar: [], spelling: [] };
  for (let i = 0; i < 25; i++) {
    const track = TRACK_IDS[i % TRACK_IDS.length];
    const state = progress.tracks[track];
    const entry = pickExercise(index.pool, track, state.level, state.seen, rnd);
    if (!entry) continue;
    const r = sit(abilities[track], entry.level, entry.taskType, entry.items || 6);
    recordResult(progress, entry, r.score, r.max, ceilings[track]);
    scores[track].push(r.pct);
  }

  console.log(`\n${label}`);
  console.log("  track        true  placed  settled  ceiling   last-3 scores");
  let worst = 0;
  for (const id of TRACK_IDS) {
    const final = progress.tracks[id].level;
    const last = scores[id].slice(-3);
    const err = Math.abs(final - Math.min(abilities[id], ceilings[id]));
    worst = Math.max(worst, err);
    console.log(`  ${id.padEnd(12)} ${String(abilities[id]).padStart(4)} ${String(placed[id]).padStart(7)} ${String(final).padStart(8)} ${String(ceilings[id]).padStart(8)}   ${last.join(", ")}`);
  }
  return worst;
}

// Placement rule, exhaustively: no pair of probe scores may place someone lower
// than a strictly worse pair.
let monotone = true;
for (let a = 0; a <= 100; a += 5) {
  for (let b = 0; b <= 100; b += 5) {
    if (a < 100 && placeTrack(a + 5, b) < placeTrack(a, b)) monotone = false;
    if (b < 100 && placeTrack(a, b + 5) < placeTrack(a, b)) monotone = false;
  }
}
console.log(`placement rule monotone in both probes: ${monotone}`);

// Lidia's expected shape from her history: strong reading and vocabulary, weaker
// grammar, spelling well behind.
const profiles = [
  [{ reading: 5, vocabulary: 4, grammar: 3, spelling: 2 }, "a wide reader who cannot spell (Lidia's expected shape)"],
  [{ reading: 2, vocabulary: 2, grammar: 2, spelling: 2 }, "a beginner across the board"],
  [{ reading: 6, vocabulary: 6, grammar: 6, spelling: 6 }, "at the top of every track"],
  [{ reading: 1, vocabulary: 3, grammar: 5, spelling: 4 }, "a lopsided profile"],
];
let worstAll = 0;
for (const [ab, label] of profiles) worstAll = Math.max(worstAll, runOne(ab, label));
console.log(`\nworst settled-level error across all profiles: ${worstAll} level(s)`);
