// Run with: npm test  (node --test, no extra dependencies)
import test from "node:test";
import assert from "node:assert/strict";

import { assembleTest, drawTest } from "./ojajDraw.js";

// Math.random returns a value in [0, 1); fixing it makes a weighted pick land
// on a known candidate. One mock per test, its value changed through the
// setter: a second mock of the same method in one test is left in place
// after the test ends.
function fixRandom(t) {
  let value = 0;
  t.mock.method(Math, "random", () => value);
  return (v) => {
    value = v;
  };
}

const NO_RECORD = { items: {}, types: {} };

// The level profile of tasks 1-4 (tmp/_ojaj_online.py, check_profile).
const PROFILE = { B1: [0, 2], B2: [3, 5], C1: [4, 5], C2: [0, 1] };

const vaultOf = (...tasks) => ({ label: "Test online", timeMinutes: 45, mistakeTypes: [], tasks });
const choiceTask = (count, items, extra = {}) => ({
  id: "4", type: "multiple_choice", instruction: "Wybierz.", count, items, ...extra,
});
const cultureTask = (count, items) => ({
  id: "5", type: "knowledge_questions", instruction: "Odpowiedz.", count, items,
});
const it = (id, mistakeType = "tenses", extra = {}) => ({
  id, stem: `Stem ${id} __________.`, options: ["A) a", "B) b", "C) c", "D) d"], answer: "A",
  mistakeType, ...extra,
});

const missed = (misses) => ({ seen: misses, misses, lastCorrect: false, lastMissType: "tenses" });
const answered = (seen) => ({ seen, misses: 0, lastCorrect: true, lastMissType: null });

const idsOf = (test, task = 0) => test.tasks[task].items.map((q) => q.vaultId).sort();
const draws = (n, f) => Array.from({ length: n }, f);

// --- putting the chosen items together ------------------------------------------------

test("a test numbers its questions 1 up through the tasks, keeping each item's vault id", () => {
  const vault = vaultOf(
    { id: "1", type: "word_formation", instruction: "Utworz.", count: 2, items: [] },
    choiceTask(1, []),
  );
  const a = { id: "01-1", sentence: "A __________.", wordBase: "A", answer: ["a"], level: "B2" };
  const b = { id: "01-2", sentence: "B __________.", wordBase: "B", answer: ["b"], level: "C1" };
  const c = it("02-31");
  const record = { items: { "01-2": answered(1) }, types: {} };

  const test = assembleTest(vault, [[a, b], [c]], record);

  assert.equal(test.label, "Test online");
  assert.equal(test.timeMinutes, 45);
  assert.equal(test.maxPoints, 3);
  assert.deepEqual(test.tasks.map((t) => [t.id, t.type, t.points, t.instruction]), [
    ["1", "word_formation", 2, "Utworz."],
    ["4", "multiple_choice", 1, "Wybierz."],
  ]);
  assert.deepEqual(test.tasks.flatMap((t) => t.items.map((q) => [q.id, q.vaultId, q.seenBefore])), [
    ["1", "01-1", false],
    ["2", "01-2", true],
    ["3", "02-31", false],
  ]);
  // The item itself is unchanged apart from its number.
  assert.equal(test.tasks[0].items[0].sentence, "A __________.");
  assert.deepEqual(test.tasks[0].items[0].answer, ["a"]);
});

// --- unseen first ------------------------------------------------------------------------

test("with no record, every task gets its count of items, none seen before", () => {
  const vault = vaultOf(choiceTask(3, [it("a"), it("b"), it("c"), it("d"), it("e")]),
    cultureTask(2, [it("f"), it("g"), it("h")]));
  const test = drawTest(vault, NO_RECORD);
  assert.equal(test.tasks[0].items.length, 3);
  assert.equal(test.tasks[1].items.length, 2);
  assert.deepEqual(test.tasks.flatMap((t) => t.items.map((q) => q.id)), ["1", "2", "3", "4", "5"]);
  assert.ok(test.tasks.every((t) => t.items.every((q) => q.seenBefore === false)));
});

test("unseen items come before items answered right", () => {
  const vault = vaultOf(choiceTask(3, [it("a"), it("b"), it("c"), it("d"), it("e"), it("f")]));
  const record = { items: { a: answered(1), c: answered(1), e: answered(2) }, types: {} };
  for (const _ of draws(20)) {
    assert.deepEqual(idsOf(drawTest(vault, record)), ["b", "d", "f"]);
  }
});

test("once the unseen items run out, the least seen come next", () => {
  const vault = vaultOf(choiceTask(3, [it("a"), it("b"), it("c"), it("d"), it("e")]));
  const record = {
    items: { a: answered(1), b: answered(3), c: answered(2), d: answered(1) },
    types: {},
  };
  for (const _ of draws(20)) {
    const test = drawTest(vault, record);
    assert.deepEqual(idsOf(test), ["a", "d", "e"]);
    assert.deepEqual(test.tasks[0].items.map((q) => q.seenBefore).sort(), [false, true, true]);
  }
});

test("a seen item fills a task only where the unseen ones cannot meet its profile", () => {
  // One C1 is needed and no unseen item is C1: the seen C1 is taken, the
  // B2 that is also seen is not.
  const levels = { levels: { B2: [1, 2], C1: [1, 2] } };
  const vault = vaultOf(choiceTask(3, [
    it("u1", "tenses", { level: "B2" }), it("u2", "tenses", { level: "B2" }),
    it("s1", "tenses", { level: "C1" }), it("s2", "tenses", { level: "B2" }),
  ], levels));
  const record = { items: { s1: answered(2), s2: answered(1) }, types: {} };
  for (const _ of draws(20)) {
    assert.deepEqual(idsOf(drawTest(vault, record)), ["s1", "u1", "u2"]);
  }
});

test("an item at a level outside the task's profile is never drawn", () => {
  const vault = vaultOf(choiceTask(2, [
    it("a", "tenses", { level: "B2" }), it("x", "tenses", { level: "A2" }),
    it("b", "tenses", { level: "B2" }),
  ], { levels: { B2: [0, 2] } }));
  // Even missed, so the draw would like it back.
  const record = { items: { x: missed(3) }, types: {} };
  for (const _ of draws(20)) {
    assert.deepEqual(idsOf(drawTest(vault, record)), ["a", "b"]);
  }
});

// --- same item ---------------------------------------------------------------------------

test("an item whose latest answer was a miss comes back, marked seen before", () => {
  const vault = vaultOf(choiceTask(3, ["m", "a", "b", "c", "d", "e", "f"].map((x) => it(x))));
  const record = { items: { m: missed(1) }, types: {} };
  for (const _ of draws(20)) {
    const test = drawTest(vault, record);
    const m = test.tasks[0].items.find((q) => q.vaultId === "m");
    assert.ok(m, "the missed item is in the test");
    assert.equal(m.seenBefore, true);
  }
});

test("one right answer takes an item off the list", () => {
  const vault = vaultOf(choiceTask(3, ["m", "a", "b", "c", "d", "e"].map((x) => it(x))));
  // Missed twice, then right.
  const record = {
    items: { m: { seen: 3, misses: 2, lastCorrect: true, lastMissType: null } },
    types: {},
  };
  for (const _ of draws(20)) {
    assert.ok(!idsOf(drawTest(vault, record)).includes("m"));
  }
});

test("at most two items come back per task", () => {
  const vault = vaultOf(choiceTask(6,
    ["m1", "m2", "m3", "m4", "a", "b", "c", "d", "e", "f"].map((x) => it(x, "tenses"))));
  const record = {
    items: { m1: missed(1), m2: missed(1), m3: missed(2), m4: missed(1) },
    types: {},
  };
  for (const _ of draws(20)) {
    assert.equal(drawTest(vault, record).tasks[0].items.filter((q) => q.seenBefore).length, 2);
  }
});

test("a missed item's chance grows with how often it was missed", (t) => {
  // A missed three times, B and C once: of 5 chances A holds the first 3.
  const vault = vaultOf(choiceTask(2, [it("A"), it("B"), it("C"), it("d"), it("e")]));
  const record = { items: { A: missed(3), B: missed(1), C: missed(1) }, types: {} };
  const random = fixRandom(t);
  random(0.59); // 2.95 of 5: A; then 1.18 of B and C's 2: C
  assert.deepEqual(idsOf(drawTest(vault, record)), ["A", "C"]);
  random(0.61); // 3.05 of 5: B; then 2.44 of A and C's 4: A
  assert.deepEqual(idsOf(drawTest(vault, record)), ["A", "B"]);
  random(0.99); // 4.95 of 5: C; then 3.96 of A and B's 4: B
  assert.deepEqual(idsOf(drawTest(vault, record)), ["B", "C"]);
});

// --- same type ---------------------------------------------------------------------------

test("unseen items of a missed type fill the repeat slots; a type never missed is not targeted",
  () => {
    // Three repeat slots, no missed item in this task: all three go to the
    // unseen vowels items, none to the never-missed double-letters ones.
    const vault = vaultOf(choiceTask(3, [
      it("v1", "vowels"), it("d1", "double-letters"), it("v2", "vowels"),
      it("d2", "double-letters"), it("v3", "vowels"), it("d3", "double-letters"),
    ]));
    const record = { items: {}, types: { vowels: { answered: 2, wrong: 1 } } };
    for (const _ of draws(20)) {
      assert.deepEqual(idsOf(drawTest(vault, record)), ["v1", "v2", "v3"]);
    }
  });

test("type picks stop at three repeats, and the rest of the task is filled as usual", (t) => {
  // At 0.999 each weighted pick takes the last candidate and the shuffle leaves
  // the order alone, so the fill takes the first unseen item left, n1.
  const vault = vaultOf(choiceTask(4, [
    it("n1", "modals"), it("n2", "modals"),
    ...["w1", "w2", "w3", "w4", "w5"].map((x) => it(x, "vowels")),
  ]));
  const record = { items: {}, types: { vowels: { answered: 1, wrong: 1 } } };
  fixRandom(t)(0.999);
  assert.deepEqual(idsOf(drawTest(vault, record)), ["n1", "w3", "w4", "w5"]);
});

test("a weaker type is likelier to be targeted", (t) => {
  // vowels 1 of 1 wrong (0.5), double letters 1 of 3 (0.25): of 0.75 the
  // vowels item holds the first 0.5.
  const vault = vaultOf(choiceTask(1, [it("v", "vowels"), it("d", "double-letters")]));
  const record = {
    items: {},
    types: { vowels: { answered: 1, wrong: 1 }, "double-letters": { answered: 3, wrong: 1 } },
  };
  const random = fixRandom(t);
  random(0.6); // 0.45
  assert.deepEqual(idsOf(drawTest(vault, record)), ["v"]);
  random(0.7); // 0.525
  assert.deepEqual(idsOf(drawTest(vault, record)), ["d"]);
});

// --- the level profile -----------------------------------------------------------------

test("a repeat that would break a level quota is skipped", () => {
  const vault = vaultOf(choiceTask(3, [
    it("m1", "tenses", { level: "B1" }), it("m2", "tenses", { level: "B1" }),
    it("a", "modals", { level: "B2" }), it("b", "modals", { level: "B2" }),
    it("c", "modals", { level: "C1" }), it("d", "modals", { level: "C1" }),
  ], { levels: { B1: [0, 1], B2: [1, 2], C1: [1, 2] } }));
  const record = { items: { m1: missed(1), m2: missed(1) }, types: {} };
  for (const _ of draws(20)) {
    const ids = idsOf(drawTest(vault, record));
    assert.equal(ids.filter((x) => x.startsWith("m")).length, 1, ids.join(","));
  }
});

// A vault the size of the real one: 10 + 10 + 10 + 10 + 5 slots from 30 items a
// task, with the real level profile and idiom counts.
function fullVault() {
  const levels = ["B1", "B2", "B2", "C1", "C1", "C2", "B2", "C1", "B1", "C1"];
  const tasks = [
    ["1", "word_formation", 10, PROFILE, undefined],
    ["2", "word_spelling", 10, PROFILE, [3, 4]],
    ["3", "sentence_transformation", 10, PROFILE, undefined],
    ["4", "multiple_choice", 10, PROFILE, [3, 4]],
    ["5", "knowledge_questions", 5, undefined, undefined],
  ];
  return vaultOf(...tasks.map(([id, type, count, profile, focus]) => ({
    id, type, instruction: "", count, levels: profile, focus,
    items: Array.from({ length: 30 }, (_, i) => it(`${id}-${i}`, `type-${id}-${i % 4}`, {
      ...(profile ? { level: levels[i % levels.length] } : {}),
      ...(focus && i % 3 === 0 ? { focus: "idiom" } : {}),
    })),
  })));
}

function checkProfile(task, spec) {
  assert.equal(task.items.length, spec.count, `task ${task.id} size`);
  for (const [level, [min, max]] of Object.entries(spec.levels || {})) {
    const n = task.items.filter((q) => q.level === level).length;
    assert.ok(n >= min && n <= max, `task ${task.id}: ${n} ${level}`);
  }
  if (spec.focus) {
    const n = task.items.filter((q) => q.focus).length;
    assert.ok(n >= spec.focus[0] && n <= spec.focus[1], `task ${task.id}: ${n} focus items`);
  }
}

test("every drawn test keeps the level profile and the idiom counts", () => {
  const vault = fullVault();
  for (const _ of draws(50)) {
    const test = drawTest(vault, NO_RECORD);
    test.tasks.forEach((task, i) => checkProfile(task, vault.tasks[i]));
    assert.equal(test.maxPoints, 45);
  }
});

test("with many misses waiting, a test holds at most 2 per task and 1 in culture", () => {
  const vault = fullVault();
  const record = { items: {}, types: {} };
  for (const task of vault.tasks) {
    for (const item of task.items.slice(0, 12)) {
      record.items[item.id] = missed(1 + (item.id.length % 3));
    }
    for (const n of [0, 1, 2, 3]) {
      record.types[`type-${task.id}-${n}`] = { answered: 5, wrong: n + 1 };
    }
  }
  for (const _ of draws(50)) {
    const test = drawTest(vault, record);
    test.tasks.forEach((task, i) => {
      checkProfile(task, vault.tasks[i]);
      const back = task.items.filter((q) => q.seenBefore).length;
      assert.equal(back, task.type === "knowledge_questions" ? 1 : 2, `task ${task.id}`);
    });
    assert.equal(new Set(test.tasks.flatMap((t) => t.items.map((q) => q.vaultId))).size, 45);
  }
});

test("an item that comes back is mixed in among the new ones", () => {
  const vault = vaultOf(choiceTask(3, ["m", "a", "b", "c", "d", "e"].map((x) => it(x))));
  const record = { items: { m: missed(1) }, types: {} };
  const positions = new Set(draws(60, () =>
    drawTest(vault, record).tasks[0].items.findIndex((q) => q.vaultId === "m")));
  assert.ok(positions.size > 1, "the repeat is not always in the same place");
});

test("a vault that cannot meet the profile is an error, not a short test", () => {
  const vault = vaultOf(choiceTask(3, [
    it("a", "tenses", { level: "C1" }), it("b", "tenses", { level: "B2" }),
    it("c", "tenses", { level: "B2" }), it("d", "tenses", { level: "B2" }),
  ], { levels: { B2: [0, 3], C1: [2, 3] } }));
  assert.throws(() => drawTest(vault, NO_RECORD), /task 4/);
});

test("a vault without enough items for a task is an error", () => {
  const vault = vaultOf(choiceTask(3, [it("a"), it("b")]));
  assert.throws(() => drawTest(vault, NO_RECORD), /task 4/);
});

// --- culture -------------------------------------------------------------------------------

test("culture: one missed question comes back, and then no branch is targeted", () => {
  const vault = vaultOf(cultureTask(1, [
    it("m1", "uk-politics"), it("m2", "uk-politics"), it("u", "uk-politics"), it("o", "uk-parks"),
  ]));
  const record = {
    items: { m1: missed(1), m2: missed(2) },
    types: { "uk-politics": { answered: 2, wrong: 2 } },
  };
  for (const _ of draws(20)) {
    const ids = idsOf(drawTest(vault, record));
    assert.equal(ids.length, 1);
    assert.ok(["m1", "m2"].includes(ids[0]), ids[0]);
  }
});

test("culture: with no missed question waiting, an unseen one of a weak branch is drawn", () => {
  const vault = vaultOf(cultureTask(1, [it("m", "uk-politics"), it("u", "uk-politics"),
    it("o", "uk-parks")]));
  const record = {
    items: { m: { seen: 2, misses: 1, lastCorrect: true, lastMissType: null } },
    types: { "uk-politics": { answered: 2, wrong: 1 } },
  };
  for (const _ of draws(20)) {
    assert.deepEqual(idsOf(drawTest(vault, record)), ["u"]);
  }
});
