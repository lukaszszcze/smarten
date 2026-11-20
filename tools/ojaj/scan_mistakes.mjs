// Count Tadzio's wrong answers in past attempts, per task type, by re-marking
// the saved answers against today's keys (strict, no AI).
// Run: node tools/ojaj/scan_mistakes.mjs <results.json>
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { scoreTest } from "../../site/src/lib/scoring.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.join(here, "..", "..", "pub", "konkursy", "angielski", "data");
const attempts = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));

function dataPath(testId) {
  if (testId.startsWith("ojaj/")) return path.join(DATA, "ojaj", testId.slice(5) + ".json");
  return path.join(DATA, testId + ".json");
}

const rows = {};
let missing = 0;
const examples = {};
for (const a of attempts) {
  const p = dataPath(a.testId);
  if (!fs.existsSync(p)) { missing++; continue; }
  const test = JSON.parse(fs.readFileSync(p, "utf8"));
  const res = scoreTest(test, a.answers || {});
  const comp = a.testId.startsWith("ojaj/") ? "ojaj" : "kur";
  for (const t of res.tasks) {
    if (!t.items || t.items.length === 0) continue;
    const key = `${comp} ${t.type}`;
    const r = (rows[key] ||= { items: 0, wrong: 0, blank: 0 });
    for (const it of t.items) {
      if (it.skipped) continue;
      r.items++;
      if (!it.correct) {
        const ua = String(it.userAnswer || "").trim();
        if (!ua) r.blank++;
        else {
          r.wrong++;
          (examples[key] ||= []).push(`${ua} -> ${it.correctAnswer}`);
        }
      }
    }
  }
}
console.log("attempts without a data file:", missing);
console.log("competition type                      items  wrong  blank");
for (const [k, r] of Object.entries(rows).sort()) {
  console.log(k.padEnd(36), String(r.items).padStart(6), String(r.wrong).padStart(6),
    String(r.blank).padStart(6));
}
for (const k of ["ojaj word_formation", "ojaj word_spelling", "kur word_formation",
  "kur word_spelling"]) {
  console.log(`\n${k}, typed and wrong:`);
  for (const e of (examples[k] || [])) console.log("  ", e);
}
