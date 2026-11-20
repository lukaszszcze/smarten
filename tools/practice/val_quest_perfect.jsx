// Score every quest task twice through the real scoring.js: once with the
// answer key as the student's answers, once with nothing filled in.
//
// A perfect attempt has to reach the stated maximum and a blank attempt has to
// score zero. This is what catches an unreachable maximum - a scoring scheme
// whose top band is below the task's points, an answer stored in a shape the
// matcher cannot read, or a scheme that pays out for an empty paper.
//
// See tools/practice/val_quest_perfect.sh.
import fs from "fs";
import path from "path";
import { scoreTest } from "SCORINGSRC";

const BASE = "DATADIR/quest";

function perfectAnswers(task) {
  const out = {};
  for (const item of task.items || []) {
    if (Array.isArray(item.answers)) out[item.id] = item.answers;
    else if (Array.isArray(item.answer)) out[item.id] = item.answer[0];
    else out[item.id] = item.answer;
  }
  return out;
}

const rows = [];
let checked = 0;

for (const name of fs.readdirSync(BASE).filter((n) => n.endsWith(".json") && n !== "index.json").sort()) {
  const doc = JSON.parse(fs.readFileSync(path.join(BASE, name), "utf8"));
  const src = name.replace(/\.json$/, "");
  const max = (doc.tasks || []).reduce((s, t) => s + (t.points || 0), 0);

  const full = scoreTest(doc, Object.assign({}, ...(doc.tasks || []).map(perfectAnswers)));
  const blank = scoreTest(doc, {});
  checked++;

  if (full.earned !== max) rows.push([src, `answer key scores ${full.earned} of ${max}`]);
  if (blank.earned !== 0) rows.push([src, `blank attempt scores ${blank.earned}, expected 0`]);
  if (full.max !== max) rows.push([src, `maximum reported ${full.max}, file totals ${max}`]);
}

console.log(`scored ${checked} quest exercise(s) with the real scoring.js`);
console.log(`problems: ${rows.length}`);
for (const r of rows) console.log("  " + r[0].padEnd(24) + r[1]);
