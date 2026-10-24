/**
 * Remote results sync — modeled after questProgress.js sync flow.
 *
 * Pattern: optimistic local save → fetch remote → merge → push merged → apply server response.
 * Merge strategy: union attempts by attemptId (no duplicates).
 */

// Extension included so this module also loads under plain Node, which the
// test runner uses; Vite resolves either form.
import { normalizeAttempt, loadAttempts } from "./resultsModel.js";

// Per-user dedup: only one sync in flight at a time
const inflightSyncs = new Map();

/**
 * Save a finished attempt: append it to the user's local attempts, then send
 * it to the results API without waiting.
 *
 * The local copy is the one that counts. A send that fails is not retried
 * here; the next syncAttempts() pushes every local attempt the server lacks.
 *
 * @param {string} storageKey the user's local-storage key, `smarten_konkursy_{name}`
 * @param {string} username the user the server files the attempt under
 * @param {object} entry the attempt record
 */
export function saveAttempt(storageKey, username, entry) {
  try {
    const stored = JSON.parse(localStorage.getItem(storageKey) || "{}");
    stored.attempts = [...(stored.attempts || []), entry];
    localStorage.setItem(storageKey, JSON.stringify(stored));
  } catch (e) {
    console.error("Failed to save results:", e);
  }
  fetch("/api/results", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user: username, ...entry }),
  }).catch(() => {});
}

export function mergeAttempts(local, remote) {
  if (!remote || remote.length === 0) return local;
  if (!local || local.length === 0) return remote.map(normalizeAttempt);

  const merged = [...local];
  const seen = new Set(local.map((a) => a.attemptId));

  for (const raw of remote) {
    const a = normalizeAttempt(raw);
    if (a.attemptId && !seen.has(a.attemptId)) {
      merged.push(a);
      seen.add(a.attemptId);
    }
  }

  return merged;
}

export async function fetchRemoteAttempts(username) {
  try {
    const res = await fetch(`/api/results?user=${encodeURIComponent(username)}`);
    if (!res.ok) return null;
    const data = await res.json();
    return Array.isArray(data) ? data : null;
  } catch {
    return null;
  }
}

export function pushRemoteAttempts(username, attempts) {
  return fetch("/api/results", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user: username, attempts }),
  })
    .then((r) => (r.ok ? r.json() : null))
    .catch(() => null);
}

export function clearRemoteAttempts(username) {
  return fetch(`/api/results?user=${encodeURIComponent(username)}`, {
    method: "DELETE",
  })
    .then((r) => (r.ok ? r.json() : null))
    .catch(() => null);
}

/**
 * Full sync cycle: load local → fetch remote → merge → save local → push to server.
 * Returns the merged attempts array.
 * Deduplicates concurrent calls for the same user.
 */
export function syncAttempts(username, storageKey) {
  const existing = inflightSyncs.get(username);
  if (existing) return existing;

  const promise = _doSync(username, storageKey).finally(() => {
    inflightSyncs.delete(username);
  });
  inflightSyncs.set(username, promise);
  return promise;
}

async function _doSync(username, storageKey) {
  const local = loadAttempts(storageKey);
  const remote = await fetchRemoteAttempts(username);
  const merged = mergeAttempts(local, remote);

  // Save merged back to localStorage
  try {
    const stored = JSON.parse(localStorage.getItem(storageKey) || "{}");
    stored.attempts = merged;
    localStorage.setItem(storageKey, JSON.stringify(stored));
  } catch {}

  // Push to server; server merges again and returns canonical copy
  const serverResult = await pushRemoteAttempts(username, merged);
  if (serverResult && Array.isArray(serverResult.attempts)) {
    const final = serverResult.attempts.map(normalizeAttempt);
    try {
      const stored = JSON.parse(localStorage.getItem(storageKey) || "{}");
      stored.attempts = final;
      localStorage.setItem(storageKey, JSON.stringify(stored));
    } catch {}
    return final;
  }

  return merged;
}
