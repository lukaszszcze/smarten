import { clampPercentage } from "./questStars.js";

// Age of Empires II units as marks for the UK culture quizzes: one unit per
// possible score on a ten-question quiz, weakest first, so every extra correct
// answer is a promotion he can name. Stars are still stored and counted as
// before; only what the quiz shows changes.

export const AOE_UNITS = [
  { name: "Sheep", icon: "🐑" },
  { name: "Villager", icon: "🧑‍🌾" },
  { name: "Militia", icon: "🗡️" },
  { name: "Spearman", icon: "🔱" },
  { name: "Archer", icon: "🏹" },
  { name: "Man-at-Arms", icon: "🛡️" },
  { name: "Crossbowman", icon: "🎯" },
  { name: "Long Swordsman", icon: "⚔️" },
  { name: "Knight", icon: "🐎" },
  { name: "Champion", icon: "🏆" },
  { name: "Paladin", icon: "👑" },
];

function stepFor(percentage) {
  return Math.round(clampPercentage(percentage) / 10);
}

export function aoeUnitForPercentage(percentage) {
  return AOE_UNITS[stepFor(percentage)];
}

/** The unit one correct answer higher, or null at the top. */
export function nextAoeUnit(percentage) {
  return AOE_UNITS[stepFor(percentage) + 1] || null;
}

export function usesAoeMarks(exerciseId) {
  return typeof exerciseId === "string" && exerciseId.startsWith("ojaj_uk_");
}
