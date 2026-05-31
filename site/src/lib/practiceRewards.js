import { percentageToStars, clampPercentage } from "./questStars.js";

// --- Title ladder ---

export const PRACTICE_TITLES = [
  { stars: 0, title: "Beginner" },
  { stars: 20, title: "Trainee" },
  { stars: 50, title: "Practitioner" },
  { stars: 100, title: "Competitor" },
  { stars: 175, title: "Contender" },
  { stars: 275, title: "Finalist" },
  { stars: 400, title: "Champion" },
];

// --- Mastery levels ---

const MASTERY_LABELS = ["", "Beginner", "Developing", "Competent", "Advanced", "Master"];

// Thresholds: [minStars, minCount] per level (1-5), keyed by exercise pool size
const MASTERY_THRESHOLDS = {
  10: [
    // level 1: ≥1 completed (any score)
    { minStars: 0, minCount: 1 },
    // level 2: ≥3 at ≥3★
    { minStars: 3, minCount: 3 },
    // level 3: ≥5 at ≥3★
    { minStars: 3, minCount: 5 },
    // level 4: ≥7 at ≥4★
    { minStars: 4, minCount: 7 },
    // level 5: ≥8 at ≥4★
    { minStars: 4, minCount: 8 },
  ],
  5: [
    { minStars: 0, minCount: 1 },
    { minStars: 3, minCount: 2 },
    { minStars: 3, minCount: 3 },
    // level 4: ≥3 at ≥4★
    { minStars: 4, minCount: 3 },
    // level 5: ≥4 at ≥4★
    { minStars: 4, minCount: 4 },
  ],
};

// --- Core functions ---

/** Returns { title, stars, nextTitle, nextStars, totalStars } */
export function getPracticeTitle(totalStars) {
  let current = PRACTICE_TITLES[0];
  let next = PRACTICE_TITLES[1] || null;
  for (let i = PRACTICE_TITLES.length - 1; i >= 0; i--) {
    if (totalStars >= PRACTICE_TITLES[i].stars) {
      current = PRACTICE_TITLES[i];
      next = PRACTICE_TITLES[i + 1] || null;
      break;
    }
  }
  return {
    title: current.title,
    stars: current.stars,
    nextTitle: next?.title ?? null,
    nextStars: next?.stars ?? null,
    totalStars,
  };
}

/** Compute total practice stars from bestScores map */
export function computePracticeStars(bestScores) {
  let total = 0;
  for (const pct of Object.values(bestScores || {})) {
    total += percentageToStars(pct);
  }
  return total;
}

/**
 * Compute mastery level (0-5) for a task type.
 * exerciseIndex: the full exercises array from practice/index.json
 * taskType: e.g. "word_spelling"
 * bestScores: the bestScores map { exerciseId: percentage }
 */
export function getTypeMastery(bestScores, exerciseIndex, taskType) {
  const typeExercises = exerciseIndex.filter((ex) => ex.taskType === taskType);
  const poolSize = typeExercises.length;
  if (poolSize === 0) return { level: 0, label: MASTERY_LABELS[0], earned: 0, max: 0 };

  // Collect star counts for exercises in this type
  const starCounts = typeExercises.map((ex) => {
    const pct = bestScores[ex.id];
    return pct !== undefined ? percentageToStars(pct) : -1; // -1 = not attempted
  });

  const attempted = starCounts.filter((s) => s >= 0).length;
  if (attempted === 0) return { level: 0, label: MASTERY_LABELS[0], earned: 0, max: poolSize * 5 };

  const thresholds = MASTERY_THRESHOLDS[poolSize] || MASTERY_THRESHOLDS[10];

  let level = 0;
  for (let i = 0; i < thresholds.length; i++) {
    const { minStars, minCount } = thresholds[i];
    const qualifying = starCounts.filter((s) => s >= minStars).length;
    if (qualifying >= minCount) {
      level = i + 1;
    } else {
      break;
    }
  }

  // Star totals for this type
  const earned = starCounts.reduce((sum, s) => sum + Math.max(0, s), 0);
  const max = poolSize * 5;

  return { level, label: MASTERY_LABELS[level], earned, max };
}

/**
 * Update bestScores in-place inside the stored object.
 * Called inside saveResult()'s read-modify-write cycle.
 * Returns { prevStars, newStars, prevPercentage } for UI feedback.
 */
export function updateBestScore(stored, exerciseId, percentage) {
  if (!stored.rewards) stored.rewards = { bestScores: {} };
  if (!stored.rewards.bestScores) stored.rewards.bestScores = {};

  const pct = clampPercentage(percentage);
  const prev = stored.rewards.bestScores[exerciseId];
  const prevPct = prev ?? -1;
  const prevStars = prevPct >= 0 ? percentageToStars(prevPct) : 0;
  const newStars = percentageToStars(pct);

  if (prevPct < 0 || pct > prevPct) {
    stored.rewards.bestScores[exerciseId] = pct;
  }

  return { prevStars, newStars, isNewBest: prevPct < 0 || pct > prevPct, prevPercentage: prevPct };
}

/**
 * Load rewards from localStorage. Self-heals by merging in any attempts that
 * aren't yet reflected in bestScores — e.g. attempts pulled from the server by
 * syncAttempts on another device, or legacy data from before rewards existed.
 */
export function loadRewards(storageKey) {
  try {
    const stored = JSON.parse(localStorage.getItem(storageKey) || "{}");
    const existing = stored.rewards?.bestScores || null;
    const fromAttempts = migrateFromAttempts(stored.attempts);

    if (existing) {
      let changed = false;
      const merged = { ...existing };
      for (const [exId, pct] of Object.entries(fromAttempts)) {
        if ((merged[exId] ?? -1) < pct) {
          merged[exId] = pct;
          changed = true;
        }
      }
      if (changed) {
        stored.rewards = { ...stored.rewards, bestScores: merged };
        localStorage.setItem(storageKey, JSON.stringify(stored));
      }
      return merged;
    }

    stored.rewards = { bestScores: fromAttempts };
    localStorage.setItem(storageKey, JSON.stringify(stored));
    return fromAttempts;
  } catch (e) {
    console.error("Failed to load practice rewards:", e);
    return {};
  }
}

/**
 * Reconstruct bestScores from an attempts array.
 * Handles: missing percentage, maxScore === 0, NaN, negative values.
 */
export function migrateFromAttempts(attempts) {
  const bestScores = {};
  if (!Array.isArray(attempts)) return bestScores;

  for (const entry of attempts) {
    if (!entry.testId || !entry.testId.startsWith("practice/")) continue;
    const exId = entry.testId.replace("practice/", "");

    let pct = entry.percentage;
    if (pct == null || !Number.isFinite(Number(pct))) {
      // Try to compute from score/maxScore
      if (!entry.maxScore || entry.maxScore === 0) continue;
      pct = (entry.score / entry.maxScore) * 100;
      if (!Number.isFinite(pct)) continue;
    }

    pct = clampPercentage(pct);
    if (pct === 0 && (bestScores[exId] !== undefined)) continue; // don't overwrite with 0
    if (pct > (bestScores[exId] ?? -1)) {
      bestScores[exId] = pct;
    }
  }
  return bestScores;
}
