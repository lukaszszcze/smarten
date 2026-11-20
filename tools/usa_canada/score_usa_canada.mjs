// Score the USA and Canada exercises with the app's own scoring.js, typing the
// answer key the way a student would. Every accepted variant of an open answer
// is tried on its own, so a variant the marking cannot accept shows up here.
//
// Usage: node tools/usa_canada/score_usa_canada.mjs
import { readFileSync } from "node:fs";
import { scoreTest } from "../../site/src/lib/scoring.js";

const BASE = "pub/konkursy/angielski/data/practice";
const IDS = [
  "knowledge_033", "knowledge_034", "knowledge_035", "knowledge_036", "knowledge_037",
  "knowledge_038", "matching_025", "matching_026", "matching_027", "matching_028",
  "matching_029", "matching_030", "mc_017", "tfni_037", "spelling_033",
];
const list = (a) => (Array.isArray(a) ? a : [a]);

let bad = 0;
for (const id of IDS) {
  const task = JSON.parse(readFileSync(`${BASE}/${id}.json`, "utf8")).tasks[0];
  // Full marks on the first variant of every answer.
  const answers = {};
  for (const item of task.items) {
    answers[item.id] = list(item.answer)[0];
    if (item.secondAnswer) answers[`${item.id}_b`] = list(item.secondAnswer)[0];
  }
  const res = scoreTest({ tasks: [task] }, answers);
  const max = res.max ?? task.points;
  const ok = res.earned === max;
  if (!ok) bad++;
  console.log(`${ok ? "ok   " : "SHORT"} ${id} ${task.type}: ${res.earned}/${max}`);
  // Each further variant on its own must still earn the item's points.
  if (task.type !== "knowledge_questions") continue;
  for (const item of task.items) {
    for (const key of ["answer", "secondAnswer"]) {
      if (!item[key]) continue;
      for (const v of list(item[key]).slice(1)) {
        const typed = { ...answers, [key === "answer" ? item.id : `${item.id}_b`]: v };
        const r = scoreTest({ tasks: [task] }, typed);
        if (r.earned !== max) {
          bad++;
          console.log(`  variant not accepted: ${id} ${item.id} ${JSON.stringify(v)}`);
        }
      }
    }
  }
}
console.log(bad === 0 ? "\nevery key and every variant scores full marks" : `\n${bad} problem(s)`);
