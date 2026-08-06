// Stars needed per level to unlock the next level, out of 3 exercises × 5★ = 15.
// 9 = three exercises at 3★ (60-79%) each. At 10 a student who scored 60-79%
// on all three was one star short and could never open the next level.
export const STARS_TO_UNLOCK = 9;

// Global titles based on total stars (max 225 = 3 branches × 5 levels × 3 exercises × 5★)
export const STAR_TITLES = [
  { stars: 0, title: "Explorer" },
  { stars: 15, title: "Learner" },
  { stars: 35, title: "Student" },
  { stars: 60, title: "Scholar" },
  { stars: 100, title: "Adventurer" },
  { stars: 145, title: "Champion" },
  { stars: 190, title: "Master" },
  { stars: 225, title: "Legend" },
];

// Task type display names (for bridge links)
export const TYPE_LABELS = {
  word_spelling: "Word Spelling",
  word_formation: "Word Formation",
  multiple_choice: "Multiple Choice",
  open_cloze: "Open Cloze",
  true_false_ni: "True / False / NI",
  matching: "Matching",
};

// --- Shared helpers for nested level traversal ---

/** Flatten all exercises across all levels in a branch */
export function flattenExercises(branch) {
  if (!branch.levels) return branch.exercises || [];
  return branch.levels.flatMap((lvl) => lvl.exercises);
}

/** Find which level number an exercise belongs to */
export function getExerciseLevel(branch, exerciseId) {
  if (!branch.levels) return 1;
  for (const lvl of branch.levels) {
    if (lvl.exercises.some((ex) => ex.id === exerciseId)) return lvl.level;
  }
  return 1;
}

/** Get the next exercise in the same level, or null if at end of level */
export function getNextExercise(branch, currentExerciseId) {
  if (!branch.levels) return null;
  for (const lvl of branch.levels) {
    const idx = lvl.exercises.findIndex((ex) => ex.id === currentExerciseId);
    if (idx !== -1 && idx < lvl.exercises.length - 1) {
      return { exerciseId: lvl.exercises[idx + 1].id, branchId: branch.id };
    }
    if (idx !== -1) return null; // last exercise in level
  }
  return null;
}
