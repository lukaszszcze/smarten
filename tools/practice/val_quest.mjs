// Every exercise the quest can serve must score full marks when fed its own
// answer key, and every placement probe must too. Catches broken keys, items the
// renderer cannot reach, and gap labels that no longer match their item ids.
//
// Run: node tools/practice/val_quest.mjs
import fs from "node:fs";
const { scoreTest } = await import("../../site/src/lib/scoring.js");
const { parseGapText } = await import("../../site/src/lib/gapText.js");

const DATA = "pub/konkursy/angielski/data";
const DIR = { quest: "quest", practice: "practice", ojaj: "ojaj/practice" };
const index = JSON.parse(fs.readFileSync(`${DATA}/quest/index.json`, "utf8"));

/** The answers a student would give if she knew every answer. */
function answerKey(task, into = {}) {
  for (const item of task.items || []) {
    if (Array.isArray(item.answers)) into[item.id] = item.answers;
    else if (Array.isArray(item.answer)) into[item.id] = item.answer[0];
    else if (item.answer !== undefined) into[item.id] = item.answer;
    if (item.secondAnswer !== undefined) into[item.id + "_b"] = item.secondAnswer;
  }
  for (const item of task.vocabItems || []) {
    into[item.id] = Array.isArray(item.answer) ? item.answer[0] : item.answer;
  }
  return into;
}

/** For the text-with-gaps renderers, every item must be reachable from a gap. */
function gapProblems(task) {
  if (!task.text || !["open_cloze", "word_formation"].includes(task.type)) return null;
  const mapped = parseGapText(task.text, task.items || [])
    .filter((p) => p.type === "gap")
    .map((p) => p.id);
  const ids = (task.items || []).map((i) => String(i.id));
  const unreachable = ids.filter((id) => !mapped.includes(id));
  const dupes = mapped.filter((id, i) => mapped.indexOf(id) !== i);
  if (unreachable.length === 0 && dupes.length === 0) return null;
  return `${unreachable.length} item(s) with no gap, ${dupes.length} gap(s) sharing an item`;
}

let checked = 0;
const failures = [];

for (const entry of index.pool) {
  const path = `${DATA}/${DIR[entry.source]}/${entry.id}.json`;
  let doc;
  try {
    doc = JSON.parse(fs.readFileSync(path, "utf8"));
  } catch (e) {
    failures.push([entry.id, `cannot be loaded: ${e.message}`]);
    continue;
  }
  const answers = {};
  for (const t of doc.tasks) answerKey(t, answers);
  const res = scoreTest(doc, answers, { acceptNearMiss: true });
  checked++;

  if (res.percentage !== 100) {
    failures.push([entry.id, `answer key scores ${res.earned}/${res.max} (${res.percentage}%)`]);
  }
  for (const t of doc.tasks) {
    const g = gapProblems(t);
    if (g) failures.push([entry.id, g]);
  }
  const ids = doc.tasks.flatMap((t) => (t.items || []).map((i) => i.id));
  if (new Set(ids).size !== ids.length) failures.push([entry.id, "duplicate item ids"]);
}

// The placement test: one page carrying eight tasks, so its ids must not collide
// across probes and each probe must mark on its own.
const placement = JSON.parse(fs.readFileSync(`${DATA}/quest/placement.json`, "utf8"));
const pAnswers = {};
for (const t of placement.tasks) answerKey(t, pAnswers);
const pIds = placement.tasks.flatMap((t) => (t.items || []).map((i) => i.id));
if (new Set(pIds).size !== pIds.length) failures.push(["placement", "item ids collide across probes"]);
for (const t of placement.tasks) {
  const g = gapProblems(t);
  if (g) failures.push([`placement/${t.id}`, g]);
  const res = scoreTest({ tasks: [t] }, pAnswers, { acceptNearMiss: true });
  if (res.percentage !== 100) {
    failures.push([`placement/${t.id}`, `answer key scores ${res.percentage}%`]);
  }
}

console.log(`${checked} pool exercises + ${placement.tasks.length} placement probes checked`);
if (failures.length === 0) {
  console.log("all score full marks against their own answer key");
} else {
  console.log(`\n${failures.length} problem(s):`);
  for (const [id, why] of failures) console.log(`  ${id.padEnd(24)} ${why}`);
  process.exitCode = 1;
}
