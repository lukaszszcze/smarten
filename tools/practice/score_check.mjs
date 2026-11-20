// Score every new auto-scored exercise with the app's own scoring.js, feeding
// it the answer key as if a student had typed it perfectly. Anything that does
// not come back at full marks is unscoreable in the real app, whatever the
// static validators say.
//
// The AI-graded types (sentence_transformation, grammar_gaps) are not covered
// here - they go to Claude at runtime - so they are only shape-checked.
//
// Usage: node tools/practice/score_check.mjs
import { readFileSync } from "node:fs";
import { scoreTest } from "../../site/src/lib/scoring.js";

const BASE = "pub/konkursy/angielski/data/practice";
const AUTO = [];
for (let n = 25; n <= 32; n++) AUTO.push(`spelling_${String(n).padStart(3, "0")}`);
for (let n = 25; n <= 32; n++) AUTO.push(`knowledge_${String(n).padStart(3, "0")}`);

let bad = 0;
for (const id of AUTO) {
  const doc = JSON.parse(readFileSync(`${BASE}/${id}.json`, "utf8"));
  for (const task of doc.tasks) {
    const answers = {};
    for (const item of task.items) {
      // Type the first accepted variant, exactly as a student would.
      const first = Array.isArray(item.answer) ? item.answer[0] : item.answer;
      if (task.type === "knowledge_questions" && item.points === 2 && !item.secondAnswer) {
        // Required-parts shape: all of them, comma separated in one box.
        answers[item.id] = item.answer.join(", ");
      } else {
        answers[item.id] = first;
      }
      if (item.secondAnswer) {
        const s = Array.isArray(item.secondAnswer) ? item.secondAnswer[0] : item.secondAnswer;
        answers[`${item.id}_b`] = s;
      }
    }
    let res;
    try {
      res = scoreTest({ tasks: [task] }, answers);
    } catch (e) {
      console.log(`  CRASH  ${id} ${task.type}: ${e.message}`);
      bad++;
      continue;
    }
    const max = res.max ?? task.points;
    if (res.earned !== max) {
      bad++;
      console.log(`  SHORT  ${id} ${task.type}: perfect answers score ${res.earned}/${max}`);
      for (const ir of res.items || []) {
        if (!ir.correct) console.log(`           ${ir.id}: typed ${JSON.stringify(ir.userAnswer)} want ${JSON.stringify(ir.correctAnswer)}`);
      }
    } else {
      console.log(`  ok     ${id} ${task.type}: ${res.earned}/${max}`);
    }
  }
}
console.log(bad === 0
  ? "\nall new auto-scored exercises reach full marks on their own key"
  : `\n${bad} exercise(s) cannot be scored correctly`);
