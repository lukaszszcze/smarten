// Run with: npm test  (node --test, no extra dependencies)
import test from "node:test";
import assert from "node:assert/strict";

import { onRequestPost } from "../../functions/api/check.js";

const post = (body) =>
  onRequestPost({
    env: { ANTHROPIC_API_KEY: "test-key" },
    request: new Request("https://smarten.test/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  });

// The online vault's shape: every accepted phrasing in one string, joined
// with " / " (tmp/_ojaj_online.py).
const transformation = (answer) => ({
  id: "3",
  type: "sentence_transformation",
  items: [{
    id: "29",
    original: "Sam is the best football player in our team.",
    keyword: "ANYONE",
    transformed: "Sam plays football better _________ our team.",
    answer,
  }],
});

const noAi = (t) =>
  t.mock.method(globalThis, "fetch", async () => {
    throw new Error("the AI should not be called");
  });

test("a phrasing listed in a ' / ' key scores without an AI call", async (t) => {
  const fetchMock = noAi(t);
  const res = await post({
    type: "sentence_transformation",
    task: transformation("than anyone else in / than anyone in / than anyone on"),
    answers: { 29: "Than anyone  on" },
  });
  const body = await res.json();
  assert.equal(fetchMock.mock.callCount(), 0);
  assert.equal(body.items[0].correct, true);
  assert.equal(body.earned, 1);
  assert.equal(body.items[0].correctAnswer,
    "than anyone else in / than anyone in / than anyone on");
});

test("a key stored as a list still accepts each listed phrasing", async (t) => {
  const fetchMock = noAi(t);
  const res = await post({
    type: "sentence_transformation",
    task: transformation(["than anyone else in", "than anyone in"]),
    answers: { 29: "than anyone in" },
  });
  const body = await res.json();
  assert.equal(fetchMock.mock.callCount(), 0);
  assert.equal(body.items[0].correct, true);
  assert.equal(body.items[0].correctAnswer, "than anyone else in / than anyone in");
});
