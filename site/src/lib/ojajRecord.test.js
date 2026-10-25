// Run with: npm test  (node --test, no extra dependencies)
import test from "node:test";
import assert from "node:assert/strict";

import {
  attemptVerdicts,
  missType,
  mistakeRecord,
  typeShare,
  weakTypes,
} from "./ojajRecord.js";

// --- the type of a miss ----------------------------------------------------------

// His 13 typed misses in Tests 01 and 02, with the type the rules give
// (tmp/HANDOFF_ojaj_mistakes.md). The rules run in order, and the order
// matters: unrecogniseable also differs from the key only in a vowel, and has
// to stop at the e rule first.
const TYPED_MISSES = [
  // [where, task type, base word, key, item's type, he wrote, rules give]
  ["02/1", "word_formation", "RESEMBLE", ["resemblance"], "ance-ence", "resemblence", "ance-ence"],
  ["02/3", "word_formation", "ACCESS", ["inaccessible"], "negative-prefix", "unaccessible",
    "negative-prefix"],
  ["02/4", "word_formation", "PRONOUNCE", ["pronunciation"], "base-change", "pronounciation",
    "base-change"],
  ["02/10", "word_formation", "KNOW", ["knowledgeable"], "suffix-spelling", "knowledgable",
    "suffix-spelling"],
  ["02/14", "word_spelling", undefined, ["mischievous"], "vowels", "mischevious", "vowels"],
  ["01/1", "word_formation", "RECOGNISE", ["unrecognisable", "unrecognizable"], "negative-prefix",
    "unrecogniseable", "suffix-spelling"],
  ["01/3", "word_formation", "SPEAK", ["speechless"], "base-change", "speachless", "vowels"],
  ["01/4", "word_formation", "EMBARRASS", ["embarrassment"], "double-letters", "emberrassment",
    "vowels"],
  ["01/5", "word_formation", "REPAIR", ["irreparable"], "negative-prefix", "irrepairable",
    "base-change"],
  ["01/6", "word_formation", "CHILD", ["childish"], "word-ending", "childlish", "word-ending"],
  ["01/7", "word_formation", "DECIDE", ["indecisive"], "negative-prefix", "indecidous",
    "base-change"],
  ["01/8", "word_formation", "FORGET", ["unforgettable"], "double-letters", "unforgetable",
    "double-letters"],
  ["01/10", "word_formation", "ACCIDENT", ["accidentally"], "suffix-spelling", "accidentaly",
    "double-letters"],
];

for (const [where, type, wordBase, answer, own, wrote, expected] of TYPED_MISSES) {
  test(`his miss ${where}, "${wrote}", is typed ${expected}`, () => {
    const item = { wordBase, answer, mistakeType: own };
    assert.equal(missType(type, item, wrote), expected);
  });
}

const item = (answer, mistakeType, wordBase) => ({ answer, mistakeType, wordBase });

test("a blank takes the item's own type", () => {
  const it = item(["inaccessible"], "negative-prefix", "ACCESS");
  assert.equal(missType("word_formation", it, ""), "negative-prefix");
  assert.equal(missType("word_formation", it, "   "), "negative-prefix");
  assert.equal(missType("word_formation", it, undefined), "negative-prefix");
});

test("a miss no rule explains takes the item's own type", () => {
  // A different word altogether is not a prefix, a suffix or a spelling slip.
  const it = item(["inaccessible"], "negative-prefix", "ACCESS");
  assert.equal(missType("word_formation", it, "unreachable"), "negative-prefix");
});

test("transformations, choice and culture always take the item's own type", () => {
  for (const type of ["sentence_transformation", "multiple_choice", "knowledge_questions"]) {
    // Even an answer that would match a spelling rule in a typed task.
    const it = { answer: "accidentally", mistakeType: "tenses" };
    assert.equal(missType(type, it, "accidentaly"), "tenses");
  }
});

test("the prefix rule needs the rest of the word right", () => {
  const it = item(["inaccessible"], "vowels", "ACCESS");
  // Left off altogether, or another negative prefix: the prefix.
  assert.equal(missType("word_formation", it, "accessible"), "negative-prefix");
  assert.equal(missType("word_formation", it, "imaccessible"), "negative-prefix");
  // The right prefix with a slip later on is that slip, not the prefix.
  assert.equal(missType("word_formation", it, "inacessible"), "double-letters");
  // A word the key does not start with a prefix: a prefix added in front.
  const valuable = item(["valuable"], "vowels", "VALUE");
  assert.equal(missType("word_formation", valuable, "invaluable"), "negative-prefix");
});

test("the -ance/-ence rule covers -ant/-ent and -ancy/-ency at the end of the word", () => {
  const it = item(["relevant"], "vowels", "RELEVANCE");
  assert.equal(missType("word_formation", it, "relevent"), "ance-ence");
  const fluency = item(["fluency"], "vowels", "FLUENT");
  assert.equal(missType("word_formation", fluency, "fluancy"), "ance-ence");
  // Mid-word it is a vowel, not the ending.
  const chance = item(["chancellor"], "word-ending", undefined);
  assert.equal(missType("word_spelling", chance, "chencellor"), "vowels");
});

test("the -able/-ible rule", () => {
  const it = item(["accessible"], "vowels", "ACCESS");
  assert.equal(missType("word_formation", it, "accessable"), "able-ible");
  const gullible = item(["gullible"], "vowels", undefined);
  assert.equal(missType("word_spelling", gullible, "gullable"), "able-ible");
});

test("the base-word rule takes the base without a final e or y", () => {
  // DENY kept as deny- in front of -able is the base unchanged; the key
  // changes the y, so a y kept there is the y rule, not the base rule.
  const it = item(["undeniable"], "negative-prefix", "DENY");
  assert.equal(missType("word_formation", it, "undenyable"), "suffix-spelling");
  // HINDER kept whole where the key drops its e.
  const hindrance = item(["hindrance"], "vowels", "HINDER");
  assert.equal(missType("word_formation", hindrance, "hinderance"), "base-change");
  // Wisielec has no base word, so the rule never applies there: the same
  // slip as 02/4 falls through to the vowels.
  const spelt = item(["pronunciation"], "silent-letters", undefined);
  assert.equal(missType("word_spelling", spelt, "pronounciation"), "vowels");
});

test("the e and y rule applies only where an ending joins", () => {
  const lazy = item(["laziness"], "word-ending", "LAZY");
  assert.equal(missType("word_formation", lazy, "lazyness"), "suffix-spelling");
  const definitely = item(["definitely"], "vowels", undefined);
  assert.equal(missType("word_spelling", definitely, "definitly"), "suffix-spelling");
  // An e missing at the very end is not at a join: the vowel rule.
  const genuine = item(["genuine"], "silent-letters", undefined);
  assert.equal(missType("word_spelling", genuine, "genuin"), "vowels");
});

test("the doubled-letter rule counts any number of doubled or undoubled letters", () => {
  const it = item(["accommodation"], "vowels", undefined);
  assert.equal(missType("word_spelling", it, "accomodation"), "double-letters");
  assert.equal(missType("word_spelling", it, "acomodation"), "double-letters");
  // A letter added away from its twin is not a doubling (01/6, childlish).
  const rhythm = item(["rhythm"], "silent-letters", undefined);
  assert.equal(missType("word_spelling", rhythm, "rythm"), "silent-letters");
});

test("a right answer has no miss of its own to type", () => {
  // The record only asks about misses; a right answer gets the item's type.
  const it = item(["resemblance"], "ance-ence", "RESEMBLE");
  assert.equal(missType("word_formation", it, "Resemblance"), "ance-ence");
});

test("a miss is compared with the closest accepted spelling", () => {
  const it = item(["unrecognisable", "unrecognizable"], "negative-prefix", "RECOGNISE");
  // Closest to the -ize spelling, where it is an e kept before -able.
  assert.equal(missType("word_formation", it, "unrecognizeable"), "suffix-spelling");
  // Capitals and spaces around the word do not matter.
  assert.equal(missType("word_formation", it, "  Unrecogniseable "), "suffix-spelling");
});

// --- verdicts per attempt ----------------------------------------------------------

// A small vault: the items of an old fixed test keep its number after the
// dash, so its saved answers, keyed by question number, still find them.
const VAULT = {
  // Each type links to what to read about it, or to nothing yet.
  mistakeTypes: [
    { key: "negative-prefix", label: "przedrostki przeczace", link: "/ojaj_study/negative-prefix" },
    {
      key: "suffix-spelling", label: "pisownia przy koncowce", link: "/ojaj_study/suffix-spelling",
    },
    { key: "double-letters", label: "podwojne litery", link: "/ojaj_study/double-letters" },
    { key: "vowels", label: "samogloski", link: "/ojaj_study/vowels" },
    { key: "phrasal-verb", label: "czasowniki frazowe", link: null },
    { key: "tenses", label: "czasy", link: "/ojaj_study/transformations" },
    { key: "uk-politics", label: "UK: parlament i polityka", link: "/ojaj_uk#parliament" },
  ],
  tasks: [
    {
      id: "1", type: "word_formation", instruction: "", count: 2,
      items: [
        {
          id: "01-1", sentence: "It was __________.", wordBase: "RECOGNISE",
          answer: ["unrecognisable", "unrecognizable"], level: "C1",
          mistakeType: "negative-prefix",
        },
        {
          id: "01-2", sentence: "I __________ did it.", wordBase: "ACCIDENT",
          answer: ["accidentally"], level: "B2", mistakeType: "suffix-spelling",
        },
      ],
    },
    {
      id: "3", type: "sentence_transformation", instruction: "", count: 2,
      items: [
        {
          id: "01-3", original: "I tolerate it.", keyword: "PUT", transformed: "I _________ it.",
          answer: "put up with / am putting up with", level: "B2", focus: "phrasal verb",
          mistakeType: "phrasal-verb",
        },
        {
          id: "01-4", original: "I came here in May.", keyword: "BEEN",
          transformed: "I _________ May.", answer: "have been here since", level: "B2",
          mistakeType: "tenses",
        },
      ],
    },
    {
      id: "4", type: "multiple_choice", instruction: "", count: 1,
      items: [{
        id: "01-5", stem: "She __________ here.", options: ["A) a", "B) b", "C) c", "D) d"],
        answer: "B", level: "C1", mistakeType: "tenses",
      }],
    },
    {
      id: "5", type: "knowledge_questions", instruction: "", count: 1,
      items: [
        {
          id: "01-6", question: "Who?", options: ["A. a", "B. b", "C. c", "D. d"], answer: "C",
          mistakeType: "uk-politics",
        },
        {
          id: "02-1", question: "Where?", options: ["A. a", "B. b", "C. c", "D. d"], answer: "A",
          mistakeType: "uk-politics",
        },
      ],
    },
  ],
};

// An attempt at the old fixed Test 01, saved before attempts held verdicts.
const oldAttempt = (answers, transformationsEarned) => ({
  attemptId: "old", kind: "competition", competition: "ojaj", testId: "ojaj/online/01",
  date: "2026-10-24T17:07:44.112Z", answers,
  taskBreakdown: [
    { taskId: "1", type: "word_formation" },
    { taskId: "3", type: "sentence_transformation", earned: transformationsEarned },
    { taskId: "4", type: "multiple_choice" },
    { taskId: "5", type: "knowledge_questions" },
  ],
});

test("an attempt that saved its verdicts is read as saved", () => {
  const attempt = {
    testId: "ojaj/online/drawn", date: "2026-10-26T10:00:00Z",
    answers: { 1: "unrecogniseable", 2: "C" },
    items: [
      { number: "1", vaultId: "01-1", correct: false },
      { number: "2", vaultId: "01-5", correct: true },
    ],
  };
  assert.deepEqual(attemptVerdicts(attempt, VAULT), [
    { vaultId: "01-1", answer: "unrecogniseable", correct: false },
    { vaultId: "01-5", answer: "C", correct: true },
  ]);
});

test("a saved item no longer in the vault is left out", () => {
  const attempt = {
    testId: "ojaj/online/drawn", answers: {},
    items: [{ number: "1", vaultId: "09-9", correct: false }],
  };
  assert.deepEqual(attemptVerdicts(attempt, VAULT), []);
});

test("an old attempt is re-marked from the strict key, blanks included", () => {
  const attempt = oldAttempt(
    { 1: "unrecogniseable", 2: "accidentally", 3: "put up with", 4: "", 5: "B", 6: "A" },
    1,
  );
  const verdicts = attemptVerdicts(attempt, VAULT);
  assert.deepEqual(verdicts, [
    { vaultId: "01-1", answer: "unrecogniseable", correct: false },
    { vaultId: "01-2", answer: "accidentally", correct: true },
    { vaultId: "01-3", answer: "put up with", correct: true },
    { vaultId: "01-4", answer: "", correct: false },
    { vaultId: "01-5", answer: "B", correct: true },
    { vaultId: "01-6", answer: "A", correct: false },
  ]);
});

test("an old transformation not listed counts wrong when the points agree", () => {
  // One listed phrasing, one point: the AI marked the other answer wrong.
  const attempt = oldAttempt({ 3: " Am  putting up WITH ", 4: "have lived here since" }, 1);
  const byId = Object.fromEntries(attemptVerdicts(attempt, VAULT).map((v) => [v.vaultId, v]));
  assert.equal(byId["01-3"].correct, true);
  assert.equal(byId["01-4"].correct, false);
});

test("an old transformation is left unknown when the points do not agree", () => {
  // Two points but one listed phrasing: the AI accepted an unlisted answer,
  // and which one it was is not saved.
  const attempt = oldAttempt({ 3: "tolerate", 4: "have lived here since" }, 1);
  const byId = Object.fromEntries(attemptVerdicts(attempt, VAULT).map((v) => [v.vaultId, v]));
  assert.equal(byId["01-3"].correct, null);
  assert.equal(byId["01-4"].correct, null);
  // The other tasks are still marked.
  assert.equal(byId["01-1"].correct, false);
});

test("an old attempt at another test finds only that test's items", () => {
  // Old Test 02 has one item in this vault, question 1 of task 5.
  const attempt = { ...oldAttempt({ 1: "A" }, 0), testId: "ojaj/online/02" };
  assert.deepEqual(attemptVerdicts(attempt, VAULT), [
    { vaultId: "02-1", answer: "A", correct: true },
  ]);
});

test("a drawn attempt that saved no verdicts has none", () => {
  const attempt = { testId: "ojaj/online/drawn", answers: { 1: "x" } };
  assert.deepEqual(attemptVerdicts(attempt, VAULT), []);
});

test("attempts at papers and exercises have no verdicts here", () => {
  assert.deepEqual(attemptVerdicts({ testId: "ojaj/2024-2025/szkolny", answers: {} }, VAULT), []);
  assert.deepEqual(attemptVerdicts({ testId: "2024-2025/szkolny", answers: {} }, VAULT), []);
});

// --- the record --------------------------------------------------------------------

const drawn = (date, items, answers = {}) => ({
  attemptId: date, kind: "competition", competition: "ojaj", testId: "ojaj/online/drawn",
  date, answers, items,
});
const v = (number, vaultId, correct) => ({ number, vaultId, correct });

test("the record counts each item's misses and keeps its latest verdict", () => {
  const attempts = [
    drawn("2026-10-26", [v("1", "01-5", false), v("2", "01-4", false)]),
    drawn("2026-10-27", [v("1", "01-5", false), v("2", "01-4", true)]),
  ];
  const { items } = mistakeRecord(VAULT, attempts);
  assert.deepEqual(items["01-5"], {
    seen: 2, misses: 2, lastCorrect: false, lastMissType: "tenses",
  });
  // One right answer takes it off the list, the old miss still counted.
  assert.deepEqual(items["01-4"], { seen: 2, misses: 1, lastCorrect: true, lastMissType: null });
  assert.equal(items["01-1"], undefined);
});

test("the record reads attempts in date order, whatever order they are stored in", () => {
  const attempts = [
    drawn("2026-10-27", [v("1", "01-4", true)]),
    drawn("2026-10-26", [v("1", "01-4", false)]),
  ];
  assert.equal(mistakeRecord(VAULT, attempts).items["01-4"].lastCorrect, true);
});

test("a typed miss counts for the type its answer shows, not the item's own", () => {
  // 01-1 is a negative-prefix item; "unrecogniseable" is an e kept at the
  // ending, so it is one wrong answer for suffix-spelling and nothing for the
  // negative prefix.
  const attempts = [drawn("2026-10-26", [v("1", "01-1", false), v("2", "01-2", true)],
    { 1: "unrecogniseable", 2: "accidentally" })];
  const { items, types } = mistakeRecord(VAULT, attempts);
  assert.deepEqual(types, { "suffix-spelling": { answered: 2, wrong: 1 } });
  assert.equal(items["01-1"].lastMissType, "suffix-spelling");
});

test("a blank is a miss of the item's own type", () => {
  const attempts = [drawn("2026-10-26", [v("1", "01-1", false)], { 1: "" })];
  assert.deepEqual(mistakeRecord(VAULT, attempts).types, {
    "negative-prefix": { answered: 1, wrong: 1 },
  });
});

test("an unknown verdict makes an item seen and counts for nothing else", () => {
  const attempt = oldAttempt({ 3: "tolerate", 4: "have lived here since" }, 1);
  const { items, types } = mistakeRecord(VAULT, [attempt]);
  assert.deepEqual(items["01-3"], { seen: 1, misses: 0, lastCorrect: null, lastMissType: null });
  assert.equal(types["phrasal-verb"], undefined);
});

test("other attempts are not part of the record", () => {
  const attempts = [{ testId: "ojaj/2024-2025/szkolny", date: "2026-10-01", answers: {} }];
  assert.deepEqual(mistakeRecord(VAULT, attempts), { items: {}, types: {} });
});

test("a type's share is damped by one extra answer", () => {
  assert.equal(typeShare({ answered: 1, wrong: 1 }), 0.5);
  assert.equal(typeShare({ answered: 3, wrong: 3 }), 0.75);
  assert.equal(typeShare({ answered: 10, wrong: 10 }), 10 / 11);
  assert.equal(typeShare({ answered: 4, wrong: 0 }), 0);
});

// --- the weak types the OJAJ page lists ------------------------------------------------

test("the weak types are the missed ones, highest share first, with what waits and a link", () => {
  const attempts = [
    drawn("2026-10-26", [
      v("1", "01-4", false), v("2", "01-5", false), v("3", "01-6", false),
      v("4", "01-2", true), v("5", "01-3", true),
    ], { 1: "", 2: "A", 3: "A" }),
    drawn("2026-10-27", [v("1", "01-4", true)]),
  ];
  assert.deepEqual(weakTypes(VAULT, mistakeRecord(VAULT, attempts)), [
    // uk-politics: 1 of 1 wrong, 50%; tenses: 2 of 3 wrong, 50%, in the
    // vault's order on a tie; one tenses item waits, the other was answered.
    {
      key: "tenses", label: "czasy", link: "/ojaj_study/transformations",
      share: 0.5, answered: 3, wrong: 2, waiting: 1,
    },
    {
      key: "uk-politics", label: "UK: parlament i polityka", link: "/ojaj_uk#parliament",
      share: 0.5, answered: 1, wrong: 1, waiting: 1,
    },
  ]);
});

test("a weak type whose missed items were all answered since has none waiting", () => {
  const attempts = [
    drawn("2026-10-26", [v("1", "01-4", false)], { 1: "" }),
    drawn("2026-10-27", [v("1", "01-4", true)]),
  ];
  assert.deepEqual(weakTypes(VAULT, mistakeRecord(VAULT, attempts)), [
    {
      key: "tenses", label: "czasy", link: "/ojaj_study/transformations",
      share: 1 / 3, answered: 2, wrong: 1, waiting: 0,
    },
  ]);
});

test("a weak type with nothing to read yet has no link", () => {
  const attempts = [drawn("2026-10-26", [v("1", "01-3", false)], { 1: "" })];
  const [phrasal] = weakTypes(VAULT, mistakeRecord(VAULT, attempts));
  assert.equal(phrasal.key, "phrasal-verb");
  assert.equal(phrasal.link, null);
});

test("a type with no miss is not a weak type", () => {
  const attempts = [drawn("2026-10-26", [v("1", "01-2", true)])];
  assert.deepEqual(weakTypes(VAULT, mistakeRecord(VAULT, attempts)), []);
});

test("weak types sort by share", () => {
  const attempts = [drawn("2026-10-26", [
    v("1", "01-4", false), v("2", "01-5", false),
    v("3", "01-6", false), v("4", "02-1", false),
  ], { 1: "", 2: "A", 3: "A", 4: "B" })];
  // tenses 2 of 2 (67%) and uk-politics 2 of 2 (67%), then nothing else.
  const listed = weakTypes(VAULT, mistakeRecord(VAULT, attempts));
  assert.deepEqual(listed.map((t) => t.key), ["tenses", "uk-politics"]);

  const more = [...attempts, drawn("2026-10-27", [v("1", "01-6", false)], { 1: "B" })];
  // uk-politics now 3 of 3 (75%) goes first.
  assert.deepEqual(weakTypes(VAULT, mistakeRecord(VAULT, more)).map((t) => t.key),
    ["uk-politics", "tenses"]);
});
