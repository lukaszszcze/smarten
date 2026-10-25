// Run with: npm test  (node --test, no extra dependencies)
import test from "node:test";
import assert from "node:assert/strict";

import {
  DRAWN_TEST_ID,
  ONLINE_VAULT_PATH,
  initialPlayerState,
  isAnswered,
  isOnlineAttempt,
  markOnlineTest,
  newQuestionScore,
  onlineAttempt,
  onlineAttemptLabel,
  onlineQuestions,
  playerReducer,
  secondsLeft,
} from "./ojajOnline.js";

// --- ids and paths -----------------------------------------------------------

test("drawn tests are saved under one testId, and the vault has one path", () => {
  assert.equal(DRAWN_TEST_ID, "ojaj/online/drawn");
  assert.equal(ONLINE_VAULT_PATH, "/konkursy/angielski/data/ojaj/online/vault.json");
});

test("an online attempt is told apart from papers and exercises", () => {
  assert.equal(isOnlineAttempt({ testId: DRAWN_TEST_ID }), true);
  // The old fixed tests, done before tests were drawn from single items.
  assert.equal(isOnlineAttempt({ testId: "ojaj/online/01" }), true);
  assert.equal(isOnlineAttempt({ testId: "ojaj/2024-2025/szkolny" }), false);
  assert.equal(isOnlineAttempt({ testId: "ojaj/practice/ojaj_choice_001" }), false);
  assert.equal(isOnlineAttempt({ testId: "2024-2025/szkolny" }), false);
  for (const a of [null, undefined, {}, { testId: null }]) {
    assert.equal(isOnlineAttempt(a), false);
  }
});

// --- one question per screen -------------------------------------------------

// A cut-down online test: the real one has 10 + 10 + 10 + 10 + 5 items.
const TEST = {
  id: "01",
  timeMinutes: 45,
  tasks: [
    {
      id: "1", type: "word_formation", points: 2, instruction: "Utwórz wyraz.",
      items: [
        { id: "1", sentence: "It was __________.", wordBase: "COMFORT", answer: ["uncomfortable"] },
        { id: "2", sentence: "She was __________.", wordBase: "SPEAK", answer: ["speechless"] },
      ],
    },
    {
      id: "2", type: "multiple_choice", points: 1, instruction: "Wybierz.",
      items: [{
        id: "3", stem: "It __________ stolen.",
        options: ["A) a", "B) b", "C) c", "D) d"], answer: "B",
      }],
    },
  ],
};

test("a test becomes one screen per item, numbered across the test", () => {
  const qs = onlineQuestions(TEST);
  assert.deepEqual(qs.map((q) => q.number), [1, 2, 3]);
  assert.deepEqual(qs.map((q) => q.item.id), ["1", "2", "3"]);
  assert.deepEqual(qs.map((q) => q.firstOfTask), [true, false, true]);
});

test("each screen's task is its own task cut down to that one item", () => {
  const [, second, third] = onlineQuestions(TEST);
  // The renderers take a task, so each screen gets the task with one item:
  // the same id, type and instruction, so the instruction repeats per screen.
  assert.equal(second.task.id, "1");
  assert.equal(second.task.type, "word_formation");
  assert.equal(second.task.instruction, "Utwórz wyraz.");
  assert.deepEqual(second.task.items, [TEST.tasks[0].items[1]]);
  assert.equal(third.task.id, "2");
  assert.deepEqual(third.task.items, [TEST.tasks[1].items[0]]);
  // The test itself is left whole: scoring still reads every item.
  assert.equal(TEST.tasks[0].items.length, 2);
});

test("a question counts as answered once it holds something other than blanks", () => {
  const item = { id: "7" };
  assert.equal(isAnswered({}, item), false);
  assert.equal(isAnswered({ 7: "" }, item), false);
  assert.equal(isAnswered({ 7: "   " }, item), false);
  assert.equal(isAnswered({ 7: "B" }, item), true);
  assert.equal(isAnswered({ 7: " put up with " }, item), true);
});

// --- the clock -----------------------------------------------------------------

test("the clock counts down from the test's time by the wall clock", () => {
  const start = 1_000_000;
  assert.equal(secondsLeft(start, start, 45), 2700);
  assert.equal(secondsLeft(start, start + 1, 45), 2700);
  assert.equal(secondsLeft(start, start + 61_500, 45), 2639);
  // A tab in the background gets its timers slowed; reading the wall clock
  // means the time it was away is still counted.
  assert.equal(secondsLeft(start, start + 30 * 60_000, 45), 900);
});

test("the clock stops at zero when the time is up", () => {
  const start = 1_000_000;
  assert.equal(secondsLeft(start, start + 45 * 60_000 - 1, 45), 1);
  assert.equal(secondsLeft(start, start + 45 * 60_000, 45), 0);
  assert.equal(secondsLeft(start, start + 50 * 60_000, 45), 0);
});

// --- the player's rules ----------------------------------------------------------

const run = (...actions) => actions.reduce(playerReducer, initialPlayerState);
const started = () => run({ type: "start", now: 5000 });

test("the player starts on the intro screen with no answers", () => {
  assert.equal(initialPlayerState.phase, "intro");
  assert.equal(initialPlayerState.current, 0);
  assert.deepEqual(initialPlayerState.answers, {});
});

test("starting records the start time and shows the first question", () => {
  const s = started();
  assert.equal(s.phase, "running");
  assert.equal(s.startedAt, 5000);
  assert.equal(s.current, 0);
  // A second start does not reset the clock.
  assert.equal(playerReducer(s, { type: "start", now: 9000 }).startedAt, 5000);
});

test("answers are kept while the test runs", () => {
  const s = run(
    { type: "start", now: 0 },
    { type: "answer", id: "1", value: "uncomfortable" },
    { type: "answer", id: "3", value: "B" },
    { type: "answer", id: "3", value: "C" },
  );
  assert.deepEqual(s.answers, { 1: "uncomfortable", 3: "C" });
});

test("nothing can be answered before the start", () => {
  const s = run({ type: "answer", id: "1", value: "x" });
  assert.deepEqual(s.answers, {});
});

test("the panel jumps to any question, earlier ones included", () => {
  const s = run({ type: "start", now: 0 }, { type: "go", index: 30 }, { type: "go", index: 2 });
  assert.equal(s.current, 2);
});

test("submitting locks the answers and hands them to the marking", () => {
  const s = run(
    { type: "start", now: 0 },
    { type: "answer", id: "1", value: "uncomfortable" },
    { type: "submit" },
    { type: "answer", id: "1", value: "changed" },
    { type: "go", index: 5 },
  );
  assert.equal(s.phase, "marking");
  assert.deepEqual(s.answers, { 1: "uncomfortable" });
  assert.equal(s.current, 0);
});

test("a second submit, as when the clock runs out during the first, changes nothing", () => {
  const once = run({ type: "start", now: 0 }, { type: "submit" });
  assert.equal(playerReducer(once, { type: "submit" }), once);
});

test("a test cannot be submitted before it starts", () => {
  assert.equal(run({ type: "submit" }).phase, "intro");
});

test("a marked test shows its result", () => {
  const result = { earned: 30, max: 45, percentage: 67, tasks: [] };
  const s = run({ type: "start", now: 0 }, { type: "submit" }, { type: "marked", result });
  assert.equal(s.phase, "done");
  assert.equal(s.result, result);
});

test("a failed marking keeps the locked answers and offers a retry", () => {
  const failed = run(
    { type: "start", now: 0 },
    { type: "answer", id: "21", value: "put up with" },
    { type: "submit" },
    { type: "markingFailed" },
  );
  assert.equal(failed.phase, "failed");
  assert.equal(playerReducer(failed, { type: "answer", id: "21", value: "x" }), failed);

  const retried = playerReducer(failed, { type: "retry" });
  assert.equal(retried.phase, "marking");
  assert.deepEqual(retried.answers, { 21: "put up with" });
});

test("a marking that answers late, after the result is in, is ignored", () => {
  const result = { earned: 30, max: 45, percentage: 67, tasks: [] };
  const done = run({ type: "start", now: 0 }, { type: "submit" }, { type: "marked", result });
  assert.equal(playerReducer(done, { type: "markingFailed" }), done);
  assert.equal(playerReducer(done, { type: "marked", result: { earned: 0 } }), done);
  assert.equal(playerReducer(done, { type: "retry" }), done);
});

test("an unknown action is an error", () => {
  assert.throws(() => playerReducer(initialPlayerState, { type: "nope" }), /nope/);
});

// --- marking -------------------------------------------------------------------

// One item of each kind of marking: a typed word on the key, a transformation
// only the AI marks, a culture question on its letter. Drawn: each item keeps
// its vault id, and the first was in an earlier test.
const MARKED = {
  label: "Test online",
  tasks: [
    {
      id: "1", type: "word_formation", points: 1, instruction: "",
      items: [{
        id: "1", sentence: "It was __________.", wordBase: "REPAIR", answer: ["irreparable"],
        vaultId: "01-5", seenBefore: true,
      }],
    },
    {
      id: "3", type: "sentence_transformation", points: 1, instruction: "",
      items: [{
        id: "2", original: "I tolerate it.", keyword: "PUT", transformed: "I _________ it.",
        answer: "put up with", vaultId: "03-23", seenBefore: false,
      }],
    },
    {
      id: "5", type: "knowledge_questions", points: 1, instruction: "",
      items: [{
        id: "3", question: "Q?", options: ["A. a", "B. b", "C. c", "D. d"], answer: "B",
        vaultId: "02-44", seenBefore: false,
      }],
    },
  ],
};

const ok = (payload) => ({ ok: true, status: 200, json: async () => payload });

function mockCheck(t, reply) {
  const calls = [];
  t.mock.method(globalThis, "fetch", async (url, options) => {
    const body = JSON.parse(options.body);
    calls.push({ url, body });
    return reply(body.task);
  });
  return calls;
}

test("only the transformations go to the AI marking", async (t) => {
  const calls = mockCheck(t, () => ok({ earned: 1, max: 1, items: [{ id: "2", correct: true }] }));
  const answers = { 1: "irreparable", 2: "put up with", 3: "B" };

  const { result, unmarkedTaskIds } = await markOnlineTest(MARKED, answers);

  assert.deepEqual(unmarkedTaskIds, []);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "/api/check");
  assert.equal(calls[0].body.type, "sentence_transformation");
  assert.equal(result.earned, 3);
  assert.equal(result.max, 3);
});

test("a typed word outside the key scores nothing, as the key was approved strict", async (t) => {
  // The paper player sends word formation to the AI too, which accepts
  // variants the key does not list. The online test does not: 1.5 of Test 01
  // takes "irreparable" only.
  mockCheck(t, () => ok({ earned: 0, max: 1, items: [{ id: "2", correct: false }] }));
  const answers = { 1: "unrepairable", 2: "stand", 3: "A" };

  const { result } = await markOnlineTest(MARKED, answers);

  assert.equal(result.earned, 0);
  assert.equal(result.tasks.find((r) => r.taskId === "1").items[0].correct, false);
});

test("a failed AI marking reports the transformation task as unmarked", async (t) => {
  mockCheck(t, () => {
    throw new TypeError("Failed to fetch");
  });

  const { unmarkedTaskIds } = await markOnlineTest(MARKED, { 1: "irreparable", 2: "put up with" });

  assert.deepEqual(unmarkedTaskIds, ["3"]);
});

// --- the attempt record ----------------------------------------------------------

// The AI marks the transformation right; the culture answer is wrong.
async function marked(t) {
  mockCheck(t, () => ok({ earned: 1, max: 1, items: [{ id: "2", correct: true }] }));
  const answers = { 1: "irreparable", 2: "put up with", 3: "A" };
  const { result } = await markOnlineTest(MARKED, answers);
  return { answers, result };
}

test("an online attempt is filed as an OJAJ competition attempt at a drawn test", async (t) => {
  const { answers, result } = await marked(t);
  t.mock.timers.enable({ apis: ["Date"], now: Date.UTC(2026, 10, 2, 9, 45) });

  const entry = onlineAttempt(MARKED, answers, result);

  assert.equal(typeof entry.attemptId, "string");
  assert.ok(entry.attemptId.length > 0);
  assert.equal(entry.kind, "competition");
  assert.equal(entry.competition, "ojaj");
  assert.equal(entry.testId, "ojaj/online/drawn");
  assert.equal(isOnlineAttempt(entry), true);
  assert.equal(entry.date, "2026-11-02T09:45:00.000Z");
  assert.equal(entry.score, 2);
  assert.equal(entry.maxScore, 3);
  assert.equal(entry.percentage, 67);
  assert.deepEqual(entry.answers, answers);
  assert.deepEqual(entry.taskBreakdown, [
    { taskId: "1", type: "word_formation", earned: 1, max: 1, skipped: false },
    { taskId: "3", type: "sentence_transformation", earned: 1, max: 1, skipped: false },
    { taskId: "5", type: "knowledge_questions", earned: 0, max: 1, skipped: false },
  ]);
});

test("an online attempt saves which vault items it held and the verdict on each", async (t) => {
  // The transformation's verdict is the AI's, merged into the result.
  const { answers, result } = await marked(t);
  assert.deepEqual(onlineAttempt(MARKED, answers, result).items, [
    { number: "1", vaultId: "01-5", correct: true },
    { number: "2", vaultId: "03-23", correct: true },
    { number: "3", vaultId: "02-44", correct: false },
  ]);
});

test("an attempt is not saved while a question has no verdict", () => {
  // As when the AI's reply leaves the transformation task without items.
  const result = {
    earned: 1, max: 3, percentage: 33,
    tasks: [
      { taskId: "1", earned: 1, max: 1, items: [{ id: "1", correct: true }] },
      { taskId: "3", earned: 0, max: 1, items: [] },
      { taskId: "5", earned: 0, max: 1, items: [{ id: "3", correct: false }] },
    ],
  };
  assert.throws(() => onlineAttempt(MARKED, {}, result), /question 2/);
});

test("two attempts at drawn tests get different ids", async (t) => {
  const { answers, result } = await marked(t);
  const first = onlineAttempt(MARKED, answers, result);
  const second = onlineAttempt(MARKED, answers, result);
  assert.notEqual(first.attemptId, second.attemptId);
});

test("the score on new questions leaves out the ones seen before", async (t) => {
  // Question 1, right, was in an earlier test; of the two new ones, one is right.
  const { result } = await marked(t);
  assert.deepEqual(newQuestionScore(MARKED, result), { earned: 1, max: 2 });
});

test("an online attempt names its test in the history", () => {
  assert.equal(onlineAttemptLabel({ testId: DRAWN_TEST_ID }), "Test online");
  // The old fixed tests keep their number.
  assert.equal(onlineAttemptLabel({ testId: "ojaj/online/02" }), "Test online 02");
});
