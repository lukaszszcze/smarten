// Run with: npm test  (node --test, no extra dependencies)
import test from "node:test";
import assert from "node:assert/strict";

import { markWithAi } from "./aiMarking.js";
import { scoreTest } from "./scoring.js";

// Sentence transformation has no answer-key marking: its local score is a
// placeholder 0 until the AI marks it.
const transformTask = {
  id: "1",
  type: "sentence_transformation",
  points: 2,
  items: [
    { id: "1.1", answer: "must have forgotten" },
    { id: "1.2", answer: "is said to be" },
  ],
};

const grammarTask = {
  id: "2",
  type: "grammar_gaps",
  points: 2,
  items: [{ id: "2.1", answer: ["should not (shouldn't) have told", "should have kept"] }],
};

// Open cloze is marked against the answer key first; the AI can only add to it.
const clozeTask = {
  id: "3",
  type: "open_cloze",
  points: 2,
  items: [
    { id: "3.1", answer: ["that", "which"] },
    { id: "3.2", answer: "from" },
  ],
};

const answers = {
  "1.1": "must have forgotten",
  "1.2": "is said to be",
  "2.1_0": "shouldn't have told",
  "2.1_1": "should have kept",
  "3.1": "that",
  "3.2": "of",
};

const fullMarks = (task) => ({
  earned: task.points,
  max: task.points,
  items: task.items.map((it) => ({ id: it.id, correct: true })),
});

// Replaces fetch for one test. `reply(task)` returns the response object for
// the task in the request body, or throws to simulate a network failure.
function mockCheck(t, reply) {
  const calls = [];
  t.mock.method(globalThis, "fetch", async (url, options) => {
    const body = JSON.parse(options.body);
    calls.push({ url, body });
    return reply(body.task);
  });
  return calls;
}

const ok = (payload) => ({ ok: true, status: 200, json: async () => payload });

test("an AI-only task takes the AI's marks when the check succeeds", async (t) => {
  const calls = mockCheck(t, (task) => ok(fullMarks(task)));
  const data = { tasks: [transformTask] };

  const { result, unmarkedTaskIds } = await markWithAi(
    scoreTest(data, answers), data.tasks, answers
  );

  assert.deepEqual(unmarkedTaskIds, []);
  assert.equal(result.earned, 2);
  assert.equal(result.percentage, 100);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "/api/check");
  assert.deepEqual(calls[0].body, {
    type: "sentence_transformation", task: transformTask, answers,
  });
});

test("a network failure leaves an AI-only task unmarked", async (t) => {
  mockCheck(t, () => {
    throw new TypeError("Failed to fetch");
  });
  const data = { tasks: [transformTask] };

  const { unmarkedTaskIds } = await markWithAi(scoreTest(data, answers), data.tasks, answers);

  assert.deepEqual(unmarkedTaskIds, ["1"]);
});

test("an error status leaves an AI-only task unmarked", async (t) => {
  mockCheck(t, () => ({
    ok: false, status: 500, json: async () => ({ error: "Claude API error" }),
  }));
  const data = { tasks: [grammarTask] };

  const { unmarkedTaskIds } = await markWithAi(scoreTest(data, answers), data.tasks, answers);

  assert.deepEqual(unmarkedTaskIds, ["2"]);
});

test("a response with no score in it leaves an AI-only task unmarked", async (t) => {
  mockCheck(t, () => ok({ feedback: "Good effort" }));
  const data = { tasks: [transformTask] };

  const { unmarkedTaskIds } = await markWithAi(scoreTest(data, answers), data.tasks, answers);

  assert.deepEqual(unmarkedTaskIds, ["1"]);
});

test("a response that is not JSON leaves an AI-only task unmarked", async (t) => {
  mockCheck(t, () => ({
    ok: true, status: 200, json: async () => { throw new SyntaxError("bad"); },
  }));
  const data = { tasks: [transformTask] };

  const { unmarkedTaskIds } = await markWithAi(scoreTest(data, answers), data.tasks, answers);

  assert.deepEqual(unmarkedTaskIds, ["1"]);
});

test("a task the answer key marks keeps its key score when the check fails", async (t) => {
  mockCheck(t, () => {
    throw new TypeError("Failed to fetch");
  });
  const data = { tasks: [clozeTask] };
  const local = scoreTest(data, answers);

  const { result, unmarkedTaskIds } = await markWithAi(local, data.tasks, answers);

  assert.deepEqual(unmarkedTaskIds, []);
  assert.ok(local.earned > 0, "the key should award the 'that' gap");
  assert.equal(result.earned, local.earned);
});

test("only the tasks whose check failed are listed as unmarked", async (t) => {
  mockCheck(t, (task) => (task.id === "2" ? ok({ error: "parse" }) : ok(fullMarks(task))));
  const data = { tasks: [transformTask, grammarTask, clozeTask] };

  const { result, unmarkedTaskIds } = await markWithAi(
    scoreTest(data, answers), data.tasks, answers
  );

  assert.deepEqual(unmarkedTaskIds, ["2"]);
  assert.equal(result.tasks.find((r) => r.taskId === "1").earned, 2);
  assert.equal(result.tasks.find((r) => r.taskId === "2").earned, 0);
});
