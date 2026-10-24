// GET    /api/results?user=Tadzio  — fetch all results for a user
// POST   /api/results              — append a single new result
// PUT    /api/results              — merge full attempts array (sync)
// DELETE /api/results?user=Tadzio  — clear all results for a user
// DELETE /api/results?user=Tadzio&attemptId=ID — delete one attempt for good

const ALLOWED_USERS = ["Tadzio", "Zosia", "Lidia"];

// Attempts deleted one at a time. Every device keeps its own copy of the
// attempts and sends the whole list at each sync, so a deleted attempt would
// come back from any device that still holds it. The server therefore keeps
// the deleted ids and refuses them; a syncing device adopts the list the
// server returns, which drops the attempt on that device too.
const deletedKey = (user) => `deleted:${user}`;

async function loadDeleted(env, user) {
  return new Set((await env.RESULTS.get(deletedKey(user), "json")) || []);
}

function normalizeAttempt(raw, index) {
  const a = { ...raw };
  if (!a.attemptId) {
    const base = `${a.testId || ""}_${a.date || ""}`;
    a.attemptId = base === "_" ? `legacy_${index ?? crypto.randomUUID()}` : base;
  }
  if (!a.kind) {
    a.kind = a.testId?.startsWith("practice/") ? "practice" : "competition";
  }
  if (a.kind === "competition" && !a.year) {
    const parts = (a.testId || "").split("/");
    a.year = parts[0] || "";
    a.stage = parts[1] || "";
  }
  if (a.kind === "practice" && !a.exerciseId) {
    a.exerciseId = (a.testId || "").replace("practice/", "");
  }
  // Clamp percentage
  if (typeof a.percentage === "number") {
    a.percentage = Math.max(0, Math.min(100, Math.round(a.percentage)));
  }
  return a;
}

function mergeAttempts(existing, incoming) {
  if (!existing || existing.length === 0) return incoming;
  const merged = [...incoming];
  const seen = new Set(incoming.map((a) => a.attemptId));
  for (const a of existing) {
    if (a.attemptId && !seen.has(a.attemptId)) {
      merged.push(a);
      seen.add(a.attemptId);
    }
  }
  return merged;
}

export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const user = url.searchParams.get("user");
  if (!user || !ALLOWED_USERS.includes(user)) {
    return Response.json({ error: "invalid user" }, { status: 400 });
  }
  const raw = await context.env.RESULTS.get(`user:${user}`, "json") || [];
  return Response.json(raw.map ? raw.map((a, i) => normalizeAttempt(a, i)) : []);
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const { user, ...entry } = body;

    if (!user || !ALLOWED_USERS.includes(user)) {
      return Response.json({ error: "invalid user" }, { status: 400 });
    }
    if (!entry.testId && !entry.attemptId) {
      return Response.json({ error: "testId or attemptId required" }, { status: 400 });
    }

    const key = `user:${user}`;
    const existing = await context.env.RESULTS.get(key, "json") || [];
    const normalized = normalizeAttempt(entry);

    // Dedupe by attemptId, and never store a deleted attempt again
    const isDupe = existing.some((a) => a.attemptId && a.attemptId === normalized.attemptId);
    const isDeleted = (await loadDeleted(context.env, user)).has(normalized.attemptId);
    if (!isDupe && !isDeleted) {
      existing.push(normalized);
      await context.env.RESULTS.put(key, JSON.stringify(existing));
    }

    return Response.json({ ok: true, count: existing.length });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
}

export async function onRequestPut(context) {
  try {
    const body = await context.request.json();
    const { user, attempts } = body;

    if (!user || !ALLOWED_USERS.includes(user)) {
      return Response.json({ error: "invalid user" }, { status: 400 });
    }
    if (!Array.isArray(attempts)) {
      return Response.json({ error: "attempts array required" }, { status: 400 });
    }

    const key = `user:${user}`;
    const incoming = attempts.map((a, i) => normalizeAttempt(a, i));
    const rawExisting = await context.env.RESULTS.get(key, "json") || [];
    const existing = rawExisting.map ? rawExisting.map((a, i) => normalizeAttempt(a, i)) : [];

    const deleted = await loadDeleted(context.env, user);
    const merged = mergeAttempts(existing, incoming).filter((a) => !deleted.has(a.attemptId));
    await context.env.RESULTS.put(key, JSON.stringify(merged));

    return Response.json({ ok: true, attempts: merged });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
}

export async function onRequestDelete(context) {
  const url = new URL(context.request.url);
  const user = url.searchParams.get("user");
  if (!user || !ALLOWED_USERS.includes(user)) {
    return Response.json({ error: "invalid user" }, { status: 400 });
  }
  const attemptId = url.searchParams.get("attemptId");
  if (!attemptId) {
    await context.env.RESULTS.delete(`user:${user}`);
    return Response.json({ ok: true });
  }

  const deleted = await loadDeleted(context.env, user);
  deleted.add(attemptId);
  await context.env.RESULTS.put(deletedKey(user), JSON.stringify([...deleted]));
  const key = `user:${user}`;
  const existing = (await context.env.RESULTS.get(key, "json")) || [];
  const kept = existing.filter((a) => a.attemptId !== attemptId);
  await context.env.RESULTS.put(key, JSON.stringify(kept));
  return Response.json({ ok: true, removed: existing.length - kept.length });
}
