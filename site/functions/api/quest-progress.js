// GET /api/quest-progress?user=Lidia  — fetch quest progress from KV
// PUT /api/quest-progress             — merge and store quest progress
//   body: { user, progress }
//
// The stored shape is version 2: a level per track, no star count. A version 1
// blob left in KV is returned as null so the client starts from the placement
// test, and the first version 2 write replaces it.

import { TRACK_IDS, MIN_LEVEL, MAX_LEVEL } from "../../src/lib/questLevels.js";

const ALLOWED_USERS = ["Tadzio", "Zosia", "Lidia"];
const PROGRESS_VERSION = 2;

// Exercise ids come from three folders now (quest_vocab_01, tfni_024,
// ojaj_formation_001), so the old quest-only pattern would reject most of them.
const EXERCISE_ID = /^[a-z][a-z0-9_]{1,48}$/;

export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const user = url.searchParams.get("user");
  if (!user || !ALLOWED_USERS.includes(user)) {
    return Response.json({ error: "invalid user" }, { status: 400 });
  }
  const raw = await context.env.RESULTS.get(`quest:${user}`, "json");
  if (!raw || raw.version !== PROGRESS_VERSION) return Response.json(null);
  return Response.json(normalise(raw));
}

export async function onRequestPut(context) {
  try {
    const body = await context.request.json();
    const { user } = body;
    if (!user || !ALLOWED_USERS.includes(user)) {
      return Response.json({ error: "invalid user" }, { status: 400 });
    }
    if (body.progress?.version !== PROGRESS_VERSION || !body.progress?.tracks) {
      return Response.json({ error: "invalid progress" }, { status: 400 });
    }

    const incoming = normalise(body.progress);
    const key = `quest:${user}`;
    const stored = await context.env.RESULTS.get(key, "json");
    const existing = stored?.version === PROGRESS_VERSION ? normalise(stored) : null;
    const merged = merge(existing, incoming);

    await context.env.RESULTS.put(key, JSON.stringify(merged));
    return Response.json(merged);
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
}

function pct(v) {
  const n = Math.round(Number(v));
  return Number.isFinite(n) ? Math.max(0, Math.min(100, n)) : 0;
}

function level(v) {
  const n = Math.round(Number(v));
  return Number.isFinite(n) ? Math.max(MIN_LEVEL, Math.min(MAX_LEVEL, n)) : MIN_LEVEL;
}

function isoDate(v) {
  return typeof v === "string" && !Number.isNaN(Date.parse(v)) ? v : new Date().toISOString();
}

function normalise(raw) {
  const out = { version: PROGRESS_VERSION, placement: null, tracks: {}, attempts: [] };

  for (const id of TRACK_IDS) {
    const t = raw?.tracks?.[id] || {};
    const seen = {};
    for (const [exId, s] of Object.entries(t.seen || {})) {
      if (!EXERCISE_ID.test(exId)) continue;
      seen[exId] = {
        first: pct(s?.first),
        best: pct(s?.best),
        attempts: Math.max(1, Math.round(Number(s?.attempts)) || 1),
        lastDate: isoDate(s?.lastDate),
      };
    }
    out.tracks[id] = { level: level(t.level), seen };
  }

  for (const a of raw?.attempts || []) {
    if (!EXERCISE_ID.test(a?.exerciseId || "")) continue;
    if (!TRACK_IDS.includes(a?.track)) continue;
    out.attempts.push({
      attemptId: typeof a.attemptId === "string" ? a.attemptId : crypto.randomUUID(),
      exerciseId: a.exerciseId,
      track: a.track,
      level: level(a.level),
      date: isoDate(a.date),
      score: Number(a.score) || 0,
      maxScore: Number(a.maxScore) || 0,
      percentage: pct(a.percentage),
      isFirst: !!a.isFirst,
      levelBefore: level(a.levelBefore),
      levelAfter: level(a.levelAfter),
    });
  }

  if (raw?.placement?.levels) {
    const levels = {};
    for (const id of TRACK_IDS) levels[id] = level(raw.placement.levels[id]);
    out.placement = { date: isoDate(raw.placement.date), levels, scores: {} };
    for (const [k, v] of Object.entries(raw.placement.scores || {})) {
      if (/^[a-z]+_[0-9]$/.test(k)) out.placement.scores[k] = pct(v);
    }
  }

  // Carried through untouched: the version 1 blob, kept as a record.
  if (raw?.archived) out.archived = raw.archived;

  return out;
}

/** Same rule as the client: best score per exercise, attempts unioned by id, and
 *  a track's level taken from whichever copy has seen more of that track. */
function merge(existing, incoming) {
  if (!existing) return incoming;
  const merged = structuredClone(incoming);

  for (const id of TRACK_IDS) {
    const mine = merged.tracks[id];
    const theirs = existing.tracks[id];
    for (const [exId, s] of Object.entries(theirs.seen)) {
      const have = mine.seen[exId];
      mine.seen[exId] = have
        ? {
            first: have.first,
            best: Math.max(have.best, s.best),
            attempts: Math.max(have.attempts, s.attempts),
            lastDate: have.lastDate > s.lastDate ? have.lastDate : s.lastDate,
          }
        : s;
    }
    if (Object.keys(theirs.seen).length > Object.keys(incoming.tracks[id].seen).length) {
      mine.level = theirs.level;
    }
  }

  const seenAttempts = new Set(merged.attempts.map((a) => a.attemptId));
  for (const a of existing.attempts) {
    if (a.attemptId && !seenAttempts.has(a.attemptId)) {
      merged.attempts.push(a);
      seenAttempts.add(a.attemptId);
    }
  }
  merged.attempts.sort((a, b) => (a.date < b.date ? -1 : 1));

  if (!merged.placement && existing.placement) merged.placement = existing.placement;
  if (!merged.archived && existing.archived) merged.archived = existing.archived;

  return merged;
}
