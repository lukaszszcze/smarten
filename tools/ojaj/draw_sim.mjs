// How many items new to him each of his next online tests holds, per task,
// with the app's own record and draw. Each simulated test is taken with every
// answer right, so repeats only fall off; averaged over 30 runs.
// Run: node tools/ojaj/draw_sim.mjs <results.json> [tests]
import fs from "node:fs";
import { mistakeRecord } from "../../site/src/lib/ojajRecord.js";
import { drawTest } from "../../site/src/lib/ojajDraw.js";
import { DRAWN_TEST_ID } from "../../site/src/lib/ojajOnline.js";

const vault = JSON.parse(fs.readFileSync("pub/konkursy/angielski/data/ojaj/online/vault.json"));
const real = JSON.parse(fs.readFileSync(process.argv[2]));
const tests = Number(process.argv[3] || 12);
const runs = 30;
const sums = Array.from({ length: tests }, () => vault.tasks.map(() => 0));

for (let r = 0; r < runs; r++) {
  const attempts = [...real];
  for (let t = 0; t < tests; t++) {
    const record = mistakeRecord(vault, attempts);
    const test = drawTest(vault, record);
    test.tasks.forEach((task, i) => {
      sums[t][i] += task.items.filter((it) => !record.items[it.vaultId]).length;
    });
    const items = test.tasks.flatMap((task) =>
      task.items.map((it) => ({ number: it.id, vaultId: it.vaultId, correct: true })));
    attempts.push({
      testId: DRAWN_TEST_ID, competition: "ojaj", date: `2026-11-12T00:${String(t).padStart(2, "0")}`,
      answers: {}, items,
    });
  }
}
console.log("test  " + vault.tasks.map((t) => t.type.padEnd(24)).join(""));
sums.forEach((row, t) => {
  console.log(`${String(t + 1).padStart(4)}  ` +
    row.map((s, i) => `${(s / runs).toFixed(1)} of ${vault.tasks[i].count}`.padEnd(24)).join(""));
});
