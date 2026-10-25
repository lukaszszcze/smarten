// The mistake record: what each online test got wrong, item by item and by
// mistake type (CONTEXT.md). It is worked out from the attempts every time it
// is needed, so there is nothing to store or keep in step: an online attempt
// saves which vault items it held and the verdict on each, and the record is
// those verdicts added up.
//
// The two attempts saved before verdicts were (Tests 01 and 02 of the old
// fixed vault, 2026-10-24) are re-marked from the key, which every task but
// the transformations allows.

import { normalizeAnswer, scoreTest } from "./scoring.js";
import { isOnlineAttempt } from "./ojajOnline.js";

// --- the type of a miss ------------------------------------------------------------

// Typed tasks, where the answer itself can show what went wrong.
const TYPED_TASKS = ["word_formation", "word_spelling"];

// Longest first, so "dis" is not read as "di" + something.
const NEGATIVE_PREFIXES = ["dis", "non", "un", "in", "im", "il", "ir"];

// What may follow the letter an e or a y/i slip is at, for the slip to count as
// one at the join with an ending (knowledgable, lazyness, definitly).
const ENDINGS = new Set([
  "able", "ably", "ability", "ible", "ibly", "ibility", "ment", "ments", "ness", "ly",
  "ful", "fully", "less", "lessly", "ous", "ously", "ing", "ings", "ed", "er", "ers",
  "est", "ity", "ities", "al", "ally", "ance", "ence", "ive", "ively", "ion", "ions",
  "ation", "ish", "ies", "ier", "iest", "ily",
]);

const negativePrefix = (word) => NEGATIVE_PREFIXES.find((p) => word.startsWith(p)) || "";

// Both words with one ending written the same way; equal afterwards means the
// two differed only there.
const ANCE_ENCE = /[ae]n(ce|ces|cy|cies|t|ts|tly)$/;
const ABLE_IBLE = /[ai]b(le|les|ly|ility|ilities)$/;
const sameOnceRewritten = (a, k, re, to) =>
  a.replace(re, (_, tail) => to + tail) === k.replace(re, (_, tail) => to + tail);

function eAtEnding(a, k) {
  const [long, short] = a.length > k.length ? [a, k] : [k, a];
  if (long.length !== short.length + 1) return false;
  for (let i = 0; i <= short.length; i++) {
    if (long[i] === "e" && long.slice(0, i) + long.slice(i + 1) === short &&
      ENDINGS.has(short.slice(i))) return true;
  }
  return false;
}

function yToIAtEnding(a, k) {
  if (a.length !== k.length) return false;
  const diffs = [...a].map((c, i) => i).filter((i) => a[i] !== k[i]);
  if (diffs.length !== 1) return false;
  const i = diffs[0];
  return [a[i], k[i]].sort().join("") === "iy" && ENDINGS.has(k.slice(i + 1));
}

const collapseDoubles = (w) => w.replace(/(.)\1+/g, "$1");
const consonants = (w) => w.replace(/[aeiouy]/g, "");

// The rules, first match wins. Each compares his answer `a` with the closest
// accepted spelling `k`; both are lower case and differ.
const RULES = [
  // Another negative prefix, or none, with the rest of the word right.
  ["negative-prefix", (a, k) => {
    const pa = negativePrefix(a);
    const pk = negativePrefix(k);
    return pa !== pk && a.slice(pa.length) === k.slice(pk.length);
  }],
  ["ance-ence", (a, k) => sameOnceRewritten(a, k, ANCE_ENCE, "en")],
  ["able-ible", (a, k) => sameOnceRewritten(a, k, ABLE_IBLE, "ab")],
  // The base word kept whole where the key changes it inside (pronounc-,
  // repair, decid-). A final e or y is left off the base, since dropping or
  // changing that one is the next rule's.
  ["base-change", (a, k, item) => {
    if (!item.wordBase) return false;
    const stem = item.wordBase.toLowerCase().replace(/[ey]$/, "");
    return a.includes(stem) && !k.includes(stem);
  }],
  ["suffix-spelling", (a, k) => eAtEnding(a, k) || yToIAtEnding(a, k)],
  ["double-letters", (a, k) => collapseDoubles(a) === collapseDoubles(k)],
  ["vowels", (a, k) => consonants(a) === consonants(k)],
];

function editDistance(a, b) {
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const row = [i];
    for (let j = 1; j <= b.length; j++) {
      row[j] = Math.min(row[j - 1] + 1, prev[j] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    }
    prev = row;
  }
  return prev[b.length];
}

/**
 * The mistake type a miss counts for.
 *
 * A typed miss in word formation or wisielec takes its type from the answer
 * compared with the key, by the first rule that matches: the negative prefix;
 * -ance/-ence; -able/-ible; the base word left unchanged; an e kept or dropped,
 * or y to i, at an ending; a letter doubled or not; only vowels differing. A
 * blank, a miss no rule explains, and every miss in the other tasks take the
 * item's own type.
 *
 * @param {string} taskType the task's type, e.g. "word_formation"
 * @param {object} item the vault item, with `answer`, `mistakeType` and, in
 *   word formation, `wordBase`
 * @param {string} answer what he wrote or chose
 * @returns {string} a mistake type key, e.g. "suffix-spelling"
 *
 * @example
 * missType("word_formation", { wordBase: "KNOW", answer: ["knowledgeable"],
 *   mistakeType: "suffix-spelling" }, "knowledgable") // "suffix-spelling"
 */
export function missType(taskType, item, answer) {
  const own = item.mistakeType;
  const a = normalizeAnswer(answer);
  if (!TYPED_TASKS.includes(taskType) || !a) return own;
  const accepted = item.answer.map(normalizeAnswer);
  const k = accepted.reduce((best, s) => (editDistance(a, s) < editDistance(a, best) ? s : best));
  if (a === k) return own;
  const rule = RULES.find(([, matches]) => matches(a, k, item));
  return rule ? rule[0] : own;
}

// --- the verdicts in one attempt ----------------------------------------------------

// An attempt at one of the old fixed tests, e.g. ojaj/online/02. The vault keeps
// their items as "02-14", the test's number and the question's.
const FIXED_TEST = /^ojaj\/online\/(\d+)$/;

function vaultItems(vault) {
  const out = new Map();
  for (const task of vault.tasks) {
    for (const item of task.items) out.set(item.id, { task, item });
  }
  return out;
}

const phrasing = (s) => normalizeAnswer(s).replace(/\s+/g, " ");
const isListedPhrasing = (answer, key) =>
  String(key).split(" / ").some((p) => phrasing(p) === phrasing(answer));

// The old fixed test, marked again from the vault's copies of its items.
// Transformations were marked by the AI and the verdicts were not saved: an
// answer matching a listed phrasing counts right, and the rest count wrong when
// the task's points equal the number of matching answers. When they do not, the
// AI accepted something unlisted and which one is unknown, so the rest are null.
function remarkFixedTest(number, attempt, vault) {
  const prefix = `${number}-`;
  const { answers } = attempt;
  const out = [];
  for (const task of vault.tasks) {
    const items = task.items.filter((it) => it.id.startsWith(prefix));
    if (items.length === 0) continue;
    const asked = (it) => it.id.slice(prefix.length);
    if (task.type === "sentence_transformation") {
      const listed = items.map((it) => isListedPhrasing(answers[asked(it)] || "", it.answer));
      const earned = attempt.taskBreakdown?.find((b) => b.taskId === task.id)?.earned;
      const agree = earned === listed.filter(Boolean).length;
      items.forEach((it, i) => out.push({
        vaultId: it.id,
        answer: answers[asked(it)] || "",
        correct: listed[i] ? true : agree ? false : null,
      }));
      continue;
    }
    const numbered = items.map((it) => ({ ...it, id: asked(it) }));
    const asTest = { tasks: [{ ...task, points: items.length, items: numbered }] };
    const marked = scoreTest(asTest, answers).tasks[0].items;
    items.forEach((it, i) => out.push({
      vaultId: it.id, answer: answers[asked(it)] || "", correct: marked[i].correct,
    }));
  }
  return out;
}

/**
 * Every verdict in one online attempt, in question order.
 *
 * @param {object} attempt a saved attempt of any kind
 * @param {object} vault the vault of own items (online/vault.json)
 * @returns {{vaultId: string, answer: string, correct: boolean|null}[]} null
 *   where the verdict was not saved and cannot be worked out; empty for an
 *   attempt that is not at an online test. Items no longer in the vault are
 *   left out.
 */
export function attemptVerdicts(attempt, vault) {
  if (!isOnlineAttempt(attempt)) return [];
  if (Array.isArray(attempt.items)) {
    const known = vaultItems(vault);
    return attempt.items.filter((s) => known.has(s.vaultId)).map((s) => ({
      vaultId: s.vaultId, answer: attempt.answers?.[s.number] ?? "", correct: s.correct,
    }));
  }
  const fixed = FIXED_TEST.exec(attempt.testId);
  return fixed ? remarkFixedTest(fixed[1], attempt, vault) : [];
}

// --- the record --------------------------------------------------------------------

/**
 * The record of every online attempt, oldest first.
 *
 * Per item: how often it was in a test, how often it was missed, and the latest
 * verdict, with the type that miss counted for. Per mistake type: how many
 * answers counted for it and how many of them were wrong. Each verdict counts
 * for one type: a right answer for the item's own, a miss for missType's.
 *
 * @param {object} vault the vault of own items
 * @param {object[]} attempts the user's attempts, of any kind, synced first
 * @returns {{items: Object<string, {seen: number, misses: number,
 *   lastCorrect: boolean|null, lastMissType: string|null}>,
 *   types: Object<string, {answered: number, wrong: number}>}}
 */
export function mistakeRecord(vault, attempts) {
  const known = vaultItems(vault);
  const items = {};
  const types = {};
  const online = attempts.filter(isOnlineAttempt)
    .sort((a, b) => String(a.date).localeCompare(String(b.date)));
  for (const attempt of online) {
    for (const verdict of attemptVerdicts(attempt, vault)) {
      const { task, item } = known.get(verdict.vaultId);
      const entry = (items[verdict.vaultId] ||= {
        seen: 0, misses: 0, lastCorrect: null, lastMissType: null,
      });
      entry.seen += 1;
      if (verdict.correct === null) continue;
      const type = verdict.correct ? item.mistakeType : missType(task.type, item, verdict.answer);
      const tally = (types[type] ||= { answered: 0, wrong: 0 });
      tally.answered += 1;
      if (!verdict.correct) {
        tally.wrong += 1;
        entry.misses += 1;
      }
      entry.lastCorrect = verdict.correct;
      entry.lastMissType = verdict.correct ? null : type;
    }
  }
  return { items, types };
}

/**
 * How weak a type is, as the draw weighs it: wrong / (answered + 1). The extra
 * answer damps a short record, so one miss in one answer counts 50%, three in
 * three 75%, ten in ten 91%.
 */
export function typeShare({ answered, wrong }) {
  return wrong / (answered + 1);
}

/**
 * The types with at least one miss, weakest first (the vault's order on a
 * tie), each with how many of its missed items wait to come back: those whose
 * latest answer was a miss of this type, and its link, the page to read about
 * it (a study page or a section of the UK notebook), or null.
 *
 * @returns {{key: string, label: string, link: string|null, share: number,
 *   answered: number, wrong: number, waiting: number}[]}
 */
export function weakTypes(vault, record) {
  const waiting = {};
  for (const entry of Object.values(record.items)) {
    if (entry.lastCorrect === false) {
      waiting[entry.lastMissType] = (waiting[entry.lastMissType] || 0) + 1;
    }
  }
  return vault.mistakeTypes
    .filter(({ key }) => record.types[key]?.wrong > 0)
    .map(({ key, label, link }) => ({
      key, label, link, share: typeShare(record.types[key]), ...record.types[key],
      waiting: waiting[key] || 0,
    }))
    .sort((x, y) => y.share - x.share);
}
