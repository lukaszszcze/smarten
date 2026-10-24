// Run with: npm test  (node --test, no extra dependencies)
import test from "node:test";
import assert from "node:assert/strict";

import { saveAttempt } from "./resultsSync.js";

const KEY = "smarten_konkursy_Tadzio";

// Node has no localStorage; each test gets a fresh one backed by a Map.
function useStorage(t, initial = {}) {
  const data = new Map(Object.entries(initial));
  globalThis.localStorage = {
    getItem: (k) => (data.has(k) ? data.get(k) : null),
    setItem: (k, v) => data.set(k, String(v)),
  };
  t.after(() => delete globalThis.localStorage);
  return data;
}

function mockPost(t, reply = async () => ({ ok: true, status: 200 })) {
  const calls = [];
  t.mock.method(globalThis, "fetch", async (url, options) => {
    calls.push({ url, options });
    return reply();
  });
  return calls;
}

const entry = { attemptId: "a2", kind: "competition", testId: "ojaj/online/01", score: 30 };

test("an attempt is added to the user's stored attempts, keeping the rest", (t) => {
  const stored = { attempts: [{ attemptId: "a1" }], ojajRewards: { bestScores: { x: 50 } } };
  const data = useStorage(t, { [KEY]: JSON.stringify(stored) });
  mockPost(t);

  saveAttempt(KEY, "Tadzio", entry);

  const after = JSON.parse(data.get(KEY));
  assert.deepEqual(after.attempts, [{ attemptId: "a1" }, entry]);
  assert.deepEqual(after.ojajRewards, { bestScores: { x: 50 } });
});

test("the first attempt of a new user starts the list", (t) => {
  const data = useStorage(t);
  mockPost(t);

  saveAttempt(KEY, "Tadzio", entry);

  assert.deepEqual(JSON.parse(data.get(KEY)).attempts, [entry]);
});

test("the attempt is sent to the results API under the user's name", (t) => {
  useStorage(t);
  const calls = mockPost(t);

  saveAttempt(KEY, "Tadzio", entry);

  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "/api/results");
  assert.equal(calls[0].options.method, "POST");
  assert.deepEqual(JSON.parse(calls[0].options.body), { user: "Tadzio", ...entry });
});

test("a failed send keeps the local copy, which the next sync sends again", async (t) => {
  const data = useStorage(t);
  mockPost(t, async () => {
    throw new TypeError("Failed to fetch");
  });

  saveAttempt(KEY, "Tadzio", entry);
  await new Promise((resolve) => setImmediate(resolve));

  assert.deepEqual(JSON.parse(data.get(KEY)).attempts, [entry]);
});

test("unreadable local storage is reported and the attempt still goes to the API", (t) => {
  useStorage(t, { [KEY]: "{not json" });
  const calls = mockPost(t);
  const errors = [];
  t.mock.method(console, "error", (...args) => errors.push(args));

  saveAttempt(KEY, "Tadzio", entry);

  assert.equal(errors.length, 1);
  assert.equal(calls.length, 1);
});
