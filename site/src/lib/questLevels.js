// The quest level model.
//
// A track groups exercises by what they ask a student to DO, not by subject.
// Reading and Vocabulary ask her to understand and choose; Spelling asks her to
// produce the word from nothing. A student can be years apart on those two, so
// each track carries its own level and they move independently. One level per
// subject would keep handing her sentences that are babyish in meaning and
// vicious in spelling, which is the pair of complaints this replaces.
//
// Levels are within-track, 1-6. L1-3 come from the young-learner quest set,
// L4-6 from the competition and olympiad practice sets. See tmp/_tag_quest.py.

export const TRACK_IDS = ["reading", "vocabulary", "grammar", "spelling"];

export const MIN_LEVEL = 1;
export const MAX_LEVEL = 6;

// What each level means, shown on the home screen so a level is a place rather
// than a number.
export const LEVEL_NAMES = {
  1: "Getting started",
  2: "Building up",
  3: "Confident",
  4: "Competition: etap szkolny",
  5: "Competition: etap rejonowy",
  6: "Olympiad level",
};

// Where an exercise's JSON lives, by the `source` its index entry carries.
const SOURCE_PATHS = {
  quest: "/konkursy/angielski/data/quest",
  practice: "/konkursy/angielski/data/practice",
  ojaj: "/konkursy/angielski/data/ojaj/practice",
};

export function exercisePath(entry) {
  const base = SOURCE_PATHS[entry?.source];
  if (!base) throw new Error(`unknown exercise source: ${entry?.source}`);
  return `${base}/${entry.id}.json`;
}

// --- The level rule -------------------------------------------------------
//
// Aim for roughly 70% correct: hard enough to be worth doing, not so hard it
// stops being worth starting. Only a FIRST attempt moves the level, so replaying
// an exercise until the answers are memorised cannot climb the ladder — that is
// what the old star count paid for and it taught nothing.

export const LEVEL_UP_AT = 85;
export const LEVEL_DOWN_BELOW = 50;

// Why these two numbers, and why the level jitters by one either way:
//
// An exercise is six items, so a score can only land on 0, 17, 33, 50, 67, 83 or
// 100. On six items a student getting 55% of items right goes up 13% of the time
// and down 26%; at 70% she goes up 42% and down 7%. The rule therefore settles
// her wherever she gets around 63% right, which is the level to aim for.
//
// The jitter that comes with it looks like something to damp -- requiring two
// bad results before dropping, say. Do not: halving the downward rate moves the
// settling point to about 50% right, which is harder content and a worse
// experience. The jitter is the price of the target being in the right place.

export function nextLevel(currentLevel, percentage, ceiling = MAX_LEVEL) {
  if (percentage >= LEVEL_UP_AT) return Math.min(ceiling, currentLevel + 1);
  if (percentage < LEVEL_DOWN_BELOW) return Math.max(MIN_LEVEL, currentLevel - 1);
  return Math.min(currentLevel, ceiling);
}

/**
 * The highest level a track actually has exercises at.
 *
 * Not every track reaches the top: the olympiad set has no open cloze, so
 * Grammar stops at 5. Without this a student promoted past the content would sit
 * on a level that does not exist, being handed easier work than her level claims.
 */
export function trackCeiling(pool, track) {
  let top = MIN_LEVEL;
  for (const e of pool) {
    if (e.track === track && e.level > top) top = e.level;
  }
  return top;
}

/** How the result is described back to her, given what it did to the level. */
export function levelVerdict(before, after, percentage) {
  if (after > before) return { move: "up", text: `Level ${after} unlocked` };
  if (after < before) return { move: "down", text: `Back to level ${after} for a bit` };
  if (percentage >= LEVEL_UP_AT) return { move: "top", text: "Top level — nothing harder here" };
  return { move: "same", text: `Still level ${before}` };
}

// --- Picking the next exercise --------------------------------------------

/**
 * Pick an exercise from `pool` for this track. Prefer one she has never done at
 * her current level; widen to the neighbouring levels before repeating anything,
 * and only then fall back to whatever she has done least recently.
 *
 * `seen` maps exercise id -> { attempts, lastDate }.
 */
export function pickExercise(pool, track, level, seen, random = Math.random) {
  const inTrack = pool.filter((e) => e.track === track);
  const unseenAt = (lvl) => inTrack.filter((e) => e.level === lvl && !seen[e.id]);

  for (const lvl of [level, level + 1, level - 1]) {
    if (lvl < MIN_LEVEL || lvl > MAX_LEVEL) continue;
    const candidates = unseenAt(lvl);
    if (candidates.length > 0) {
      return candidates[Math.floor(random() * candidates.length)];
    }
  }
  // Everything at and around her level has been done: revisit the one she has
  // not touched for longest, so a repeat is at least a genuine test of memory.
  const atLevel = inTrack.filter((e) => e.level === level);
  const fallback = atLevel.length > 0 ? atLevel : inTrack;
  if (fallback.length === 0) return null;
  return [...fallback].sort(
    (a, b) => (seen[a.id]?.lastDate || "") < (seen[b.id]?.lastDate || "") ? -1 : 1
  )[0];
}

/** How much of a track's level she has worked through, for the home screen. */
export function trackCounts(pool, track, level, seen) {
  const atLevel = pool.filter((e) => e.track === track && e.level === level);
  const done = atLevel.filter((e) => seen[e.id]).length;
  return { done, total: atLevel.length };
}
