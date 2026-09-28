import test from "node:test";
import assert from "node:assert/strict";

import {
  PRACTICE_POOL,
  OJAJ_POOL,
  computePracticeStars,
  loadRewards,
  migrateFromAttempts,
  updateBestScore,
} from "./practiceRewards.js";

// The reward pools exist so that two competitions' exercises are scored apart.
// A leak in either direction is invisible in the UI — the totals just quietly
// stop meaning what they say — so each direction is checked explicitly.

const ATTEMPTS = [
  { testId: "practice/cloze_001", percentage: 80 },
  { testId: "practice/cloze_002", percentage: 40 },
  { testId: "ojaj/practice/ojaj_formation_001", percentage: 100 },
  { testId: "ojaj/practice/ojaj_spelling_001", percentage: 60 },
  { testId: "2024-2025/szkolny", percentage: 90 },
  { testId: "ojaj/2024-2025/szkolny", percentage: 55 },
];

test("migrateFromAttempts keeps the practice pool free of OJAJ exercises", () => {
  const best = migrateFromAttempts(ATTEMPTS);
  assert.deepEqual(best, { cloze_001: 80, cloze_002: 40 });
});

test("migrateFromAttempts keeps the OJAJ pool free of practice exercises", () => {
  const best = migrateFromAttempts(ATTEMPTS, OJAJ_POOL);
  assert.deepEqual(best, { ojaj_formation_001: 100, ojaj_spelling_001: 60 });
});

test("migrateFromAttempts strips only the pool's own prefix", () => {
  // "ojaj/practice/x".replace("practice/", "") would yield "ojaj/x" — an id
  // matching no exercise in either index.
  const best = migrateFromAttempts(
    [{ testId: "ojaj/practice/ojaj_choice_001", percentage: 70 }],
    OJAJ_POOL
  );
  assert.deepEqual(Object.keys(best), ["ojaj_choice_001"]);
});

test("a competition attempt never lands in an exercise pool", () => {
  const onlyTests = ATTEMPTS.filter((a) => !a.testId.includes("practice"));
  assert.deepEqual(migrateFromAttempts(onlyTests), {});
  assert.deepEqual(migrateFromAttempts(onlyTests, OJAJ_POOL), {});
});

test("updateBestScore writes its own pool and leaves the other untouched", () => {
  const stored = { rewards: { bestScores: { cloze_001: 80 } } };

  updateBestScore(stored, "ojaj_formation_001", 100, OJAJ_POOL);

  assert.deepEqual(stored.rewards.bestScores, { cloze_001: 80 });
  assert.deepEqual(stored.ojajRewards.bestScores, { ojaj_formation_001: 100 });
});

test("updateBestScore defaults to the practice pool", () => {
  const stored = {};
  updateBestScore(stored, "cloze_001", 60);
  assert.deepEqual(stored[PRACTICE_POOL.key].bestScores, { cloze_001: 60 });
  assert.equal(stored[OJAJ_POOL.key], undefined);
});

test("updateBestScore only ever raises a best score", () => {
  const stored = { ojajRewards: { bestScores: { ojaj_spelling_001: 80 } } };

  const worse = updateBestScore(stored, "ojaj_spelling_001", 30, OJAJ_POOL);
  assert.equal(stored.ojajRewards.bestScores.ojaj_spelling_001, 80);
  assert.equal(worse.isNewBest, false);

  const better = updateBestScore(stored, "ojaj_spelling_001", 95, OJAJ_POOL);
  assert.equal(stored.ojajRewards.bestScores.ojaj_spelling_001, 95);
  assert.equal(better.isNewBest, true);
});

test("OJAJ stars do not enter the practice title total", () => {
  const stored = {};
  updateBestScore(stored, "cloze_001", 100);
  updateBestScore(stored, "ojaj_formation_001", 100, OJAJ_POOL);

  assert.equal(computePracticeStars(stored[PRACTICE_POOL.key].bestScores), 5);
  assert.equal(computePracticeStars(stored[OJAJ_POOL.key].bestScores), 5);
});

test("loadRewards reads each pool from its own key and self-heals from attempts", () => {
  const store = new Map();
  globalThis.localStorage = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, v),
    removeItem: (k) => store.delete(k),
  };
  try {
    store.set("k", JSON.stringify({ attempts: ATTEMPTS }));

    assert.deepEqual(loadRewards("k"), { cloze_001: 80, cloze_002: 40 });
    assert.deepEqual(loadRewards("k", OJAJ_POOL), {
      ojaj_formation_001: 100,
      ojaj_spelling_001: 60,
    });

    // Both pools now persisted, each under its own key.
    const saved = JSON.parse(store.get("k"));
    assert.deepEqual(Object.keys(saved.rewards.bestScores), ["cloze_001", "cloze_002"]);
    assert.deepEqual(Object.keys(saved.ojajRewards.bestScores), [
      "ojaj_formation_001",
      "ojaj_spelling_001",
    ]);
  } finally {
    delete globalThis.localStorage;
  }
});
