// Quest progress: what she has done, what level each track sits at, and how a
// result moves it. Stored in localStorage and mirrored to Cloudflare KV.
//
// Version 2 replaced a star count with a level per track. The star count paid
// for replaying an exercise until the answers were memorised, which is what the
// history showed her doing, so nothing here rewards a repeat.

import {
  TRACK_IDS, MIN_LEVEL, MAX_LEVEL, nextLevel, levelVerdict,
} from "./questLevels.js";

const STORAGE_PREFIX = "smarten_quest_";
export const PROGRESS_VERSION = 2;

function storageKey(username) {
  return `${STORAGE_PREFIX}${username || "default"}`;
}

export function emptyProgress() {
  return {
    version: PROGRESS_VERSION,
    placement: null,
    tracks: Object.fromEntries(
      TRACK_IDS.map((id) => [id, { level: MIN_LEVEL, seen: {} }])
    ),
    attempts: [],
  };
}

/** Fill in anything a stored blob is missing, so a new track can be added later
 *  without stranding everyone's saved progress. */
function normalise(p) {
  const out = { ...emptyProgress(), ...p };
  out.version = PROGRESS_VERSION;
  out.tracks = { ...out.tracks };
  for (const id of TRACK_IDS) {
    const t = out.tracks[id] || {};
    out.tracks[id] = {
      level: clampLevel(t.level),
      seen: t.seen || {},
    };
  }
  if (!Array.isArray(out.attempts)) out.attempts = [];
  return out;
}

export function clampLevel(v) {
  const n = Math.round(Number(v));
  if (!Number.isFinite(n)) return MIN_LEVEL;
  return Math.max(MIN_LEVEL, Math.min(MAX_LEVEL, n));
}

/** Version 1 kept a star count over three subject branches. Its scores came
 *  from replaying to 100%, so they say little about her real level and the
 *  placement test starts fresh. The old blob is kept untouched under `archived`
 *  rather than thrown away. */
function migrate(parsed) {
  if (parsed?.version === PROGRESS_VERSION) return normalise(parsed);
  const fresh = emptyProgress();
  if (parsed && (parsed.branches || parsed.attempts)) {
    fresh.archived = parsed.archived || {
      version: 1,
      migratedAt: new Date().toISOString(),
      branches: parsed.branches,
      attempts: parsed.attempts,
      stars: parsed.stars,
    };
  }
  return fresh;
}

export function loadProgress(username) {
  try {
    const raw = localStorage.getItem(storageKey(username));
    if (!raw) return emptyProgress();
    return migrate(JSON.parse(raw));
  } catch {
    return emptyProgress();
  }
}

export function saveProgress(username, progress) {
  try {
    localStorage.setItem(storageKey(username), JSON.stringify(progress));
  } catch (e) {
    console.error("Failed to save quest progress:", e);
  }
}

// --- Placement ------------------------------------------------------------

/**
 * Turn two probe scores into a starting level for one track.
 *
 * Each probe can move her up at most two steps: one for clearing half of it, one
 * more for near enough all of it. So the two have to agree before she starts at
 * the top, and neither can carry her there alone.
 *
 * That matters because most items offer three choices, so a student who knows
 * nothing still scores about a third. Letting the harder probe decide on its own
 * placed a simulated beginner at level 5 roughly a third of the time -- she had
 * guessed three of six. Two probes at two steps each bounds what one lucky run
 * can do, and level 2 rather than 1 is the bottom because starting someone below
 * where they belong is its own discouragement.
 */
export function placeTrack(scoreAtL3, scoreAtL5) {
  const steps = (s) => (s >= 85 ? 2 : s >= 50 ? 1 : 0);
  return MIN_LEVEL + 1 + steps(scoreAtL3) + steps(scoreAtL5);
}

/** Apply a finished placement test. `probeScores` maps "reading_3" -> percentage. */
export function applyPlacement(progress, probeScores, ceilings = {}) {
  const levels = {};
  for (const id of TRACK_IDS) {
    const placed = placeTrack(probeScores[`${id}_3`] ?? 0, probeScores[`${id}_5`] ?? 0);
    levels[id] = Math.min(placed, ceilings[id] ?? MAX_LEVEL);
    progress.tracks[id].level = levels[id];
  }
  progress.placement = {
    date: new Date().toISOString(),
    levels,
    scores: probeScores,
  };
  return levels;
}

// --- Recording a result ---------------------------------------------------

/**
 * Record one finished exercise and move the track's level.
 *
 * Only a first attempt moves the level. A repeat is practice: it updates the
 * best score so she can see herself improve, and changes nothing else.
 */
export function recordResult(progress, entry, score, maxScore, ceiling) {
  const percentage = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;
  const track = progress.tracks[entry.track];
  const prior = track.seen[entry.id];
  const isFirst = !prior;

  const levelBefore = track.level;
  const levelAfter = isFirst ? nextLevel(levelBefore, percentage, ceiling) : levelBefore;
  track.level = levelAfter;

  track.seen[entry.id] = {
    first: prior?.first ?? percentage,
    best: Math.max(prior?.best ?? 0, percentage),
    attempts: (prior?.attempts ?? 0) + 1,
    lastDate: new Date().toISOString(),
  };

  progress.attempts.push({
    attemptId: crypto.randomUUID(),
    exerciseId: entry.id,
    track: entry.track,
    level: entry.level,
    date: new Date().toISOString(),
    score,
    maxScore,
    percentage,
    isFirst,
    levelBefore,
    levelAfter,
  });

  return {
    percentage,
    isFirst,
    levelBefore,
    levelAfter,
    verdict: isFirst
      ? levelVerdict(levelBefore, levelAfter, percentage)
      : { move: "practice", text: "Practice run — your level stays put" },
    improved: prior ? percentage > prior.best : true,
  };
}

/** Exercises done in the last `days` days, for the streak line on the home screen. */
export function recentActivity(progress, days = 7) {
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
  const recent = (progress.attempts || []).filter((a) => Date.parse(a.date) >= cutoff);
  const dayKeys = new Set(recent.map((a) => a.date.slice(0, 10)));
  return { exercises: recent.length, days: dayKeys.size };
}

// --- KV sync --------------------------------------------------------------

export async function fetchRemoteProgress(username) {
  try {
    const res = await fetch(`/api/quest-progress?user=${encodeURIComponent(username)}`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export function pushRemoteProgress(username, progress) {
  return fetch("/api/quest-progress", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user: username, progress }),
  })
    .then((r) => (r.ok ? r.json() : null))
    .catch(() => null);
}

/**
 * Combine two copies of the progress, for the same student on two devices.
 *
 * Best score wins per exercise, attempts are unioned by id, and a track's level
 * comes from whichever copy has seen more exercises in it — that copy is the one
 * that has watched her longest, so its level is the better informed. Levels are
 * not maxed, because a level she was moved down to is the honest one.
 */
export function mergeProgress(local, remote) {
  if (!remote || remote.version !== PROGRESS_VERSION) return local;
  if (!local) return normalise(remote);

  const merged = normalise(local);
  const r = normalise(remote);

  for (const id of TRACK_IDS) {
    const mine = merged.tracks[id];
    const theirs = r.tracks[id];
    for (const [exId, seen] of Object.entries(theirs.seen)) {
      const have = mine.seen[exId];
      mine.seen[exId] = have
        ? {
            first: have.first ?? seen.first,
            best: Math.max(have.best ?? 0, seen.best ?? 0),
            attempts: Math.max(have.attempts ?? 0, seen.attempts ?? 0),
            lastDate: (have.lastDate || "") > (seen.lastDate || "") ? have.lastDate : seen.lastDate,
          }
        : seen;
    }
    if (Object.keys(theirs.seen).length > Object.keys(local.tracks?.[id]?.seen || {}).length) {
      mine.level = theirs.level;
    }
  }

  const seenAttempts = new Set((merged.attempts || []).map((a) => a.attemptId));
  for (const a of r.attempts || []) {
    if (a.attemptId && !seenAttempts.has(a.attemptId)) merged.attempts.push(a);
  }
  merged.attempts.sort((a, b) => (a.date < b.date ? -1 : 1));

  if (!merged.placement && r.placement) merged.placement = r.placement;
  if (!merged.archived && r.archived) merged.archived = r.archived;

  return merged;
}
