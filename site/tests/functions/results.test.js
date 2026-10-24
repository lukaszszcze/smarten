// Run with: npm test  (node --test, no extra dependencies)
import test from "node:test";
import assert from "node:assert/strict";

import {
  onRequestDelete, onRequestGet, onRequestPost, onRequestPut,
} from "../../functions/api/results.js";

// A stand-in for the RESULTS KV namespace, backed by a Map of JSON strings.
function fakeKv(initial = {}) {
  const data = new Map(Object.entries(initial).map(([k, v]) => [k, JSON.stringify(v)]));
  return {
    data,
    async get(key, type) {
      if (!data.has(key)) return null;
      return type === "json" ? JSON.parse(data.get(key)) : data.get(key);
    },
    async put(key, value) {
      data.set(key, value);
    },
    async delete(key) {
      data.delete(key);
    },
  };
}

const BASE = "https://smarten.test/api/results";
const call = (handler, kv, { method = "GET", query = "", body } = {}) =>
  handler({
    env: { RESULTS: kv },
    request: new Request(`${BASE}${query}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  });

const del = (kv, query) => call(onRequestDelete, kv, { method: "DELETE", query });
// A device's sync: it sends its whole list and adopts the one returned.
const sync = (kv, attempts) =>
  call(onRequestPut, kv, { method: "PUT", body: { user: "Tadzio", attempts } });

const mine = { attemptId: "mine", kind: "competition", testId: "ojaj/online/03", score: 6 };
const his = { attemptId: "his", kind: "competition", testId: "ojaj/online/02", score: 32 };
const ids = (attempts) => attempts.map((a) => a.attemptId);
const stored = (kv) => JSON.parse(kv.data.get("user:Tadzio") || "[]");

test("one attempt can be deleted, and the others stay", async () => {
  const kv = fakeKv({ "user:Tadzio": [mine, his] });

  const res = await del(kv, "?user=Tadzio&attemptId=mine");

  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true, removed: 1 });
  assert.deepEqual(ids(stored(kv)), ["his"]);
  const listed = await (await call(onRequestGet, kv, { query: "?user=Tadzio" })).json();
  assert.deepEqual(ids(listed), ["his"]);
});

test("a device holding a deleted attempt cannot sync it back, and is told to drop it", async () => {
  const kv = fakeKv({ "user:Tadzio": [mine, his] });
  await del(kv, "?user=Tadzio&attemptId=mine");

  const res = await sync(kv, [mine, his]);

  assert.deepEqual(ids((await res.json()).attempts), ["his"]);
  assert.deepEqual(ids(stored(kv)), ["his"]);
});

test("a deleted attempt cannot be posted again either", async () => {
  const kv = fakeKv({ "user:Tadzio": [his] });
  await del(kv, "?user=Tadzio&attemptId=mine");

  const res = await call(onRequestPost, kv, { method: "POST", body: { user: "Tadzio", ...mine } });

  assert.equal(res.status, 200);
  assert.deepEqual(ids(stored(kv)), ["his"]);
});

test("an attempt that was never deleted is still stored when posted", async () => {
  const kv = fakeKv({ "user:Tadzio": [his] });
  await del(kv, "?user=Tadzio&attemptId=mine");

  const next = { attemptId: "next", kind: "competition", testId: "ojaj/online/01", score: 30 };
  await call(onRequestPost, kv, { method: "POST", body: { user: "Tadzio", ...next } });

  assert.deepEqual(ids(stored(kv)), ["his", "next"]);
});

test("deleting the same attempt twice changes nothing the second time", async () => {
  const kv = fakeKv({ "user:Tadzio": [mine, his] });
  await del(kv, "?user=Tadzio&attemptId=mine");

  const res = await del(kv, "?user=Tadzio&attemptId=mine");

  assert.deepEqual(await res.json(), { ok: true, removed: 0 });
  assert.deepEqual(JSON.parse(kv.data.get("deleted:Tadzio")), ["mine"]);
  assert.deepEqual(ids(stored(kv)), ["his"]);
});

test("a delete with no attemptId still clears every result, as before", async () => {
  const kv = fakeKv({ "user:Tadzio": [mine, his] });

  const res = await del(kv, "?user=Tadzio");

  assert.deepEqual(await res.json(), { ok: true });
  assert.equal(kv.data.has("user:Tadzio"), false);
});

test("a delete for an unknown user is refused", async () => {
  const kv = fakeKv({ "user:Tadzio": [mine] });

  const res = await del(kv, "?user=Nobody&attemptId=mine");

  assert.equal(res.status, 400);
  assert.deepEqual(ids(stored(kv)), ["mine"]);
});
