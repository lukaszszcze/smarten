// Run with: npm test  (node --test, no extra dependencies)
import test from "node:test";
import assert from "node:assert/strict";

import { mergeAiTaskResult, applyAiResults, scoreTest, isNearMiss } from "./scoring.js";

// A locally-scored word_formation task: 5 of 8 blanks matched the answer key.
const localWordFormation = {
  taskId: "1",
  type: "word_formation",
  earned: 5,
  max: 8,
  skipped: false,
  items: [
    { id: "1.1", correct: false, userAnswer: "governing", correctAnswer: "governance" },
    { id: "1.2", correct: false, userAnswer: "population", correctAnswer: "overcrowding" },
    { id: "1.3", correct: true, userAnswer: "unaffordable ", correctAnswer: "unaffordable" },
    { id: "1.4", correct: true, userAnswer: "pollution", correctAnswer: "pollution" },
    { id: "1.5", correct: false, userAnswer: "transport", correctAnswer: "connectivity" },
    { id: "1.6", correct: true, userAnswer: "diversity", correctAnswer: "diversity" },
    { id: "1.7", correct: true, userAnswer: "sustainable", correctAnswer: "sustainable" },
    { id: "1.8", correct: true, userAnswer: "populated", correctAnswer: "populated" },
  ],
};

test("a grading response that marks fewer items correct cannot lower the score", () => {
  const ai = {
    earned: 0,
    max: 8,
    items: localWordFormation.items.map((it) => ({ ...it, correct: false })),
  };

  const merged = mergeAiTaskResult(localWordFormation, ai);

  assert.equal(merged.earned, 5);
  assert.equal(merged.items.filter((it) => it.correct).length, 5);
});

test("a grading response that accepts extra answers raises the score", () => {
  const ai = {
    earned: 6,
    max: 8,
    items: localWordFormation.items.map((it) =>
      it.id === "1.1" ? { ...it, correct: true, feedback: "governing tez przechodzi" } : it
    ),
  };

  const merged = mergeAiTaskResult(localWordFormation, ai);

  assert.equal(merged.earned, 6);
  assert.equal(merged.items.find((it) => it.id === "1.1").correct, true);
  assert.equal(merged.items.find((it) => it.id === "1.1").feedback, "governing tez przechodzi");
});

test("an item accepted only locally keeps its tick", () => {
  const ai = {
    earned: 4,
    max: 8,
    items: [{ id: "1.3", correct: false, userAnswer: "unaffordable ", correctAnswer: "unaffordable" }],
  };

  const merged = mergeAiTaskResult(localWordFormation, ai);

  assert.equal(merged.items.find((it) => it.id === "1.3").correct, true);
  assert.equal(merged.earned, 5);
});

test("a response without a usable earned figure leaves the local score alone", () => {
  for (const ai of [{ items: [] }, { earned: null, items: [] }, { earned: "6", items: [] }, { earned: NaN, items: [] }]) {
    const merged = mergeAiTaskResult(localWordFormation, ai);
    assert.equal(merged.earned, 5, `earned=${ai.earned} must not disturb the local score`);
    assert.ok(Number.isFinite(merged.earned));
  }
});

test("a missing response leaves the local result untouched", () => {
  assert.deepEqual(mergeAiTaskResult(localWordFormation, null), localWordFormation);
});

test("writing and other types with no local marking take the AI score", () => {
  const localWriting = { taskId: "3", type: "writing", earned: 0, max: 10, skipped: true, items: [] };
  const ai = { earned: 7, max: 10, items: [{ id: "3.1", correct: true, earned: 7, max: 10 }] };

  const merged = mergeAiTaskResult(localWriting, ai);

  assert.equal(merged.earned, 7);
  assert.equal(merged.skipped, false);
});

// ---- whole-attempt merge -------------------------------------------------

test("applyAiResults recomputes the attempt total from the merged tasks", () => {
  const local = {
    earned: 5,
    max: 18,
    percentage: 28,
    tasks: [
      localWordFormation,
      { taskId: "2", type: "multiple_choice", earned: 0, max: 10, skipped: false, items: [] },
    ],
  };
  const aiByTaskId = new Map([["1", { earned: 0, max: 8, items: [] }]]);

  const merged = applyAiResults(local, aiByTaskId);

  assert.equal(merged.earned, 5);
  assert.equal(merged.max, 18);
  assert.equal(merged.percentage, 28);
});

test("applyAiResults ignores tasks with no response and never yields NaN", () => {
  const local = {
    earned: 5,
    max: 8,
    percentage: 63,
    tasks: [localWordFormation],
  };

  const merged = applyAiResults(local, new Map([["1", { items: [] }]]));

  assert.equal(merged.earned, 5);
  assert.ok(Number.isFinite(merged.percentage));
});

// --- the one-letter allowance on typed words ------------------------------
//
// Quest practice forgives a slip; the competition players must not, because a
// practice paper has to mark the way the real paper marks.

const spellingTask = {
  id: "1",
  type: "word_spelling",
  points: 6,
  instruction: "Complete each sentence with one word.",
  items: [
    { id: "1.1", stem: "loud _ _ u _ _ _ _ during the storm", answer: "thunder" },
    { id: "1.2", stem: "absolutely _ _ e _ _ _ _ _ outside", answer: "freezing" },
    { id: "1.3", stem: "a gentle _ _ e _ _ _ from the sea", answer: "breeze" },
    { id: "1.4", stem: "did not _ _ c _ _ _ _ the letter", answer: "receive" },
    { id: "1.5", stem: "a big grey _ _ e _ _ _ _ _", answer: "elephant" },
    { id: "1.6", stem: "the _ _ t _ _ caught a mouse", answer: "cat" },
  ],
};

test("a one-letter slip counts as wrong when the allowance is off", () => {
  const answers = {
    "1.1": "thundr", "1.2": "freezeing", "1.3": "breeze",
    "1.4": "recieve", "1.5": "elephant", "1.6": "cat",
  };
  const res = scoreTest({ tasks: [spellingTask] }, answers);
  assert.equal(res.earned, 3, "only the three exact answers score");
});

test("the same paper with the allowance on counts the slips right", () => {
  const answers = {
    "1.1": "thundr", "1.2": "freezeing", "1.3": "breeze",
    "1.4": "recieve", "1.5": "elephant", "1.6": "cat",
  };
  const res = scoreTest({ tasks: [spellingTask] }, answers, { acceptNearMiss: true });
  assert.equal(res.earned, 6);
  const flagged = res.tasks[0].items.filter((i) => i.nearMiss).map((i) => i.correctAnswer);
  assert.deepEqual(flagged, ["thunder", "freezing", "receive"],
    "the three slips are flagged so the right spelling is shown");
});

test("the allowance never turns a blank or a different word into a mark", () => {
  const answers = { "1.1": "", "1.2": "sunny", "1.3": "  ", "1.4": "receiving", "1.5": "elephan" };
  const res = scoreTest({ tasks: [spellingTask] }, answers, { acceptNearMiss: true });
  const correct = res.tasks[0].items.filter((i) => i.correct).map((i) => i.id);
  assert.deepEqual(correct, ["1.5"], "only the genuine one-letter slip gets through");
});

test("short words are not forgiven, because one letter is a different word", () => {
  assert.equal(isNearMiss("cut", "cat"), false);
  assert.equal(isNearMiss("hat", "hot"), false);
  assert.equal(isNearMiss("their", "there"), false, "two edits apart, and both are words");
});

test("the slips a confident reader actually makes are forgiven", () => {
  assert.equal(isNearMiss("freezeing", "freezing"), true, "doubled letter");
  assert.equal(isNearMiss("thundr", "thunder"), true, "dropped letter");
  assert.equal(isNearMiss("recieve", "receive"), true, "swapped pair");
  assert.equal(isNearMiss("sweter", "sweater"), true);
});

test("a wrong first letter is not a slip", () => {
  assert.equal(isNearMiss("xrainbow", "rainbow"), false);
  assert.equal(isNearMiss("brainbow", "rainbow"), false);
});

test("the allowance does not reach answers that were picked from a list", () => {
  const mc = {
    id: "1", type: "multiple_choice", points: 2,
    instruction: "Choose A, B or C.",
    items: [
      { id: "1.1", question: "She ___ to school.", options: ["A) goes", "B) went"], answer: "B" },
      { id: "1.2", question: "We ___ a film.", options: ["A) watched", "B) watch"], answer: "A" },
    ],
  };
  const res = scoreTest({ tasks: [mc] }, { "1.1": "C", "1.2": "A" }, { acceptNearMiss: true });
  assert.equal(res.earned, 1, "a wrong letter is wrong, there is no spelling to slip on");
});

test("an accepted-answer list still works with the allowance on", () => {
  const task = {
    id: "1", type: "open_cloze", points: 2,
    instruction: "One word per gap.", text: "It _____ (1.1) raining. She _____ (1.2) tired.",
    items: [
      { id: "1.1", answer: ["started", "began"] },
      { id: "1.2", answer: "seemed" },
    ],
  };
  const res = scoreTest({ tasks: [task] }, { "1.1": "begann", "1.2": "seemed" },
    { acceptNearMiss: true });
  assert.equal(res.earned, 2);
  assert.equal(res.tasks[0].items[0].nearMiss, true);
  assert.equal(res.tasks[0].items[1].nearMiss, false, "an exact answer is not flagged");
});

test("an exercise whose lesson is the one letter opts out of the allowance", () => {
  const doubling = {
    id: "1", type: "word_formation", points: 3, exactSpelling: true,
    instruction: "Add -ing.",
    items: [
      { id: "1.1", sentence: "He is ____ fast.", wordBase: "RUN", answer: "running" },
      { id: "1.2", sentence: "She ____ the bus.", wordBase: "STOP", answer: "stopped" },
      { id: "1.3", sentence: "We are ____ now.", wordBase: "BEGIN", answer: "beginning" },
    ],
  };
  const answers = { "1.1": "runing", "1.2": "stopped", "1.3": "begining" };
  const res = scoreTest({ tasks: [doubling] }, answers, { acceptNearMiss: true });
  assert.equal(res.earned, 1, "the missing double letter is the whole point");

  // The same answers on an exercise that has not opted out are forgiven.
  const { exactSpelling, ...forgiving } = doubling;
  const soft = scoreTest({ tasks: [forgiving] }, answers, { acceptNearMiss: true });
  assert.equal(soft.earned, 3);
});
