// Per-task share wrong in his online attempts, overall and since a date.
// Run: node tools/ojaj/task_acc.mjs <results.json> [since]
import fs from "node:fs";

const vault = JSON.parse(fs.readFileSync("pub/konkursy/angielski/data/ojaj/online/vault.json"));
const taskOf = {};
vault.tasks.forEach((t) => t.items.forEach((it) => { taskOf[it.id] = t.type; }));
const raw = JSON.parse(fs.readFileSync(process.argv[2]));
const attempts = (raw.attempts || raw).filter((a) => Array.isArray(a.items) && a.items.length);
const since = process.argv[3] || "2026-11-12";
const tally = {};
for (const a of attempts) {
  const recent = String(a.date) >= since;
  for (const it of a.items) {
    const k = taskOf[it.vaultId];
    if (!k) continue;
    tally[k] ??= { all: [0, 0], recent: [0, 0] };
    tally[k].all[1]++; if (!it.correct) tally[k].all[0]++;
    if (recent) { tally[k].recent[1]++; if (!it.correct) tally[k].recent[0]++; }
  }
}
for (const [k, v] of Object.entries(tally)) {
  const pct = (x) => `${Math.round((100 * x[0]) / Math.max(1, x[1]))}% ${x[0]}/${x[1]}`;
  console.log(k.padEnd(24), "all", pct(v.all).padEnd(14), `since ${since}`, pct(v.recent));
}
