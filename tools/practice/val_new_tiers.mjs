// Score every new per-sentence exercise with the real scorer: a perfect
// attempt must reach full marks, and a plausible wrong form must not.
//
// Example call:
//   node tools/practice/val_new_tiers.mjs
import { readFileSync } from "node:fs";
import { scoreTest } from "../../site/src/lib/scoring.js";

const BASE = "pub/konkursy/angielski/data/practice";
const ids = Array.from({ length: 9 }, (_, i) => `formation_${String(35 + i).padStart(3, "0")}`);

let bad = 0;
for (const id of ids) {
  const data = JSON.parse(readFileSync(`${BASE}/${id}.json`, "utf8"));
  const task = data.tasks[0];

  const perfect = {};
  const shouted = {};
  const wrong = {};
  for (const it of task.items) {
    const key = Array.isArray(it.answer) ? it.answer[0] : it.answer;
    perfect[it.id] = key;
    shouted[it.id] = `  ${key.toUpperCase()} `;   // stray case and spaces
    wrong[it.id] = it.wordBase.toLowerCase();      // the untransformed base word
  }

  const p = scoreTest(data, perfect);
  const s = scoreTest(data, shouted);
  const w = scoreTest(data, wrong);
  const flag = p.earned === task.points && s.earned === task.points && w.earned === 0 ? "ok" : "FAIL";
  if (flag === "FAIL") bad++;
  console.log(`${flag}  ${id}  perfect=${p.earned}/${p.max}  messy=${s.earned}  base-word-only=${w.earned}`);
}

// Every accepted variant must also score (British/American spellings).
for (const id of ids) {
  const data = JSON.parse(readFileSync(`${BASE}/${id}.json`, "utf8"));
  for (const it of data.tasks[0].items) {
    const accepted = Array.isArray(it.answer) ? it.answer : [it.answer];
    for (const variant of accepted) {
      const r = scoreTest(data, { [it.id]: variant });
      if (r.earned !== 1) {
        console.log(`FAIL  ${id} ${it.id}: accepted variant "${variant}" scored ${r.earned}`);
        bad++;
      }
    }
  }
}

console.log(bad === 0 ? "\nall new exercises score correctly" : `\n${bad} problem(s)`);
