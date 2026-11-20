// Tadzio's record per mistake type within one task type (transformations, choice).
// Run: node tools/ojaj/rec_task.mjs <results.json>
import fs from "node:fs";
import { attemptVerdicts } from "../../site/src/lib/ojajRecord.js";

const vault = JSON.parse(fs.readFileSync("pub/konkursy/angielski/data/ojaj/online/vault.json"));
const attempts = JSON.parse(fs.readFileSync(process.argv[2]));
const byId = new Map();
for (const task of vault.tasks) for (const item of task.items) byId.set(item.id, { task, item });

const online = attempts.filter((a) => String(a.testId).startsWith("ojaj/online"))
  .sort((a, b) => String(a.date).localeCompare(String(b.date)));
const stats = {};
const misses = {};
for (const a of online) {
  for (const v of attemptVerdicts(a, vault)) {
    if (v.correct === undefined || v.correct === null) continue;
    const { task, item } = byId.get(v.vaultId);
    if (!["sentence_transformation", "multiple_choice"].includes(task.type)) continue;
    const k = `${task.type}|${item.mistakeType}`;
    stats[k] ||= { answered: 0, wrong: 0 };
    stats[k].answered += 1;
    if (v.correct === false) {
      stats[k].wrong += 1;
      (misses[k] ||= []).push(`${a.date.slice(5, 10)} ${v.vaultId} his=${JSON.stringify(v.answer).slice(0, 60)}`);
    }
  }
}
for (const tt of ["sentence_transformation", "multiple_choice"]) {
  console.log(`\n${tt}`);
  const rows = Object.entries(stats).filter(([k]) => k.startsWith(tt))
    .map(([k, s]) => [k.split("|")[1], s, s.wrong / (s.answered + 1)])
    .sort((x, y) => y[2] - x[2]);
  for (const [type, s, share] of rows) {
    console.log(`  ${type.padEnd(18)} ${(100 * share).toFixed(0).padStart(3)}%  ${s.wrong}/${s.answered}`);
  }
  const items = vault.tasks.filter((t) => t.type === tt).flatMap((t) => t.items);
  const count = {};
  for (const it of items) count[it.mistakeType] = (count[it.mistakeType] || 0) + 1;
  console.log(`  vault items per type: ${JSON.stringify(count)}`);
}
console.log("\nmisses:");
for (const [k, list] of Object.entries(misses)) {
  console.log(`  ${k}`);
  for (const m of list) console.log(`    ${m}`);
}
