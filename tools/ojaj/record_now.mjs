// Tadzio's mistake record today, worked out with the app's own code.
// Run: node tools/ojaj/record_now.mjs <results.json>
import fs from "node:fs";
import { mistakeRecord, weakTypes, attemptVerdicts } from "../../site/src/lib/ojajRecord.js";

const vault = JSON.parse(fs.readFileSync("pub/konkursy/angielski/data/ojaj/online/vault.json"));
const attempts = JSON.parse(fs.readFileSync(process.argv[2]));
const record = mistakeRecord(vault, attempts);

console.log("weak types (share, wrong/answered, waiting):");
for (const t of weakTypes(vault, record)) {
  console.log(`  ${t.key.padEnd(20)} ${(100 * t.share).toFixed(0).padStart(3)}%  ` +
    `${t.wrong}/${t.answered}  waiting ${t.waiting}`);
}
console.log("\ntypes never missed:");
for (const { key } of vault.mistakeTypes) {
  const t = record.types[key];
  if (!t || !t.wrong) console.log(`  ${key.padEnd(20)} answered ${t ? t.answered : 0}`);
}

const byId = new Map();
for (const task of vault.tasks) for (const item of task.items) byId.set(item.id, { task, item });
const seenCounts = Object.values(record.items).map((e) => e.seen);
console.log(`\nitems seen: ${Object.keys(record.items).length} of ${byId.size}; ` +
  `times seen min ${Math.min(...seenCounts)} max ${Math.max(...seenCounts)}`);

console.log("\nevery miss (item, key, his answer):");
const online = attempts.filter((a) => String(a.testId).startsWith("ojaj/online"))
  .sort((a, b) => String(a.date).localeCompare(String(b.date)));
for (const a of online) {
  for (const v of attemptVerdicts(a, vault)) {
    if (v.correct !== false) continue;
    const { task, item } = byId.get(v.vaultId);
    const key = Array.isArray(item.answer) ? item.answer[0] : item.answer;
    console.log(`  ${a.date.slice(0, 10)} ${v.vaultId.padEnd(6)} ${task.type.padEnd(24)} ` +
      `${item.mistakeType.padEnd(18)} key=${String(key).slice(0, 40)} | ` +
      `his=${JSON.stringify(v.answer).slice(0, 50)}`);
  }
}
