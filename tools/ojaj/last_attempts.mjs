// List his last online attempts: date, score, items held, and how many of the
// items were from batches at or above a given batch number. Temporary helper.
// Run: node tools/ojaj/last_attempts.mjs <results.json> [n] [fromBatch]
import fs from "node:fs";

const raw = JSON.parse(fs.readFileSync(process.argv[2]));
const n = Number(process.argv[3] || 6);
const from = Number(process.argv[4] || 34);
const attempts = (raw.attempts || raw).filter((a) => Array.isArray(a.items) && a.items.length);
attempts.sort((a, b) => String(a.date).localeCompare(String(b.date)));
for (const a of attempts.slice(-n)) {
  const fresh = a.items.filter((it) => Number(String(it.vaultId).split("-")[0]) >= from);
  const freshWrong = fresh.filter((it) => !it.correct);
  const wrong = a.items.filter((it) => !it.correct).map((it) => it.vaultId);
  console.log(`${a.date}  ${a.score}/${a.maxScore ?? a.items.length}  items ${a.items.length}`
    + `  from batch ${from}+: ${fresh.length} (wrong ${freshWrong.length})`);
  console.log(`   wrong: ${wrong.join(" ")}`);
}
