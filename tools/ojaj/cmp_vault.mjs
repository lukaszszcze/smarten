// Compare the committed vault with the regenerated one: every old item must be
// unchanged, and list what else differs at the top level. Temporary helper.
// Run: git show HEAD:pub/konkursy/angielski/data/ojaj/online/vault.json > tmp/_vault_old.json
//      node tools/ojaj/cmp_vault.mjs tmp/_vault_old.json
import fs from "node:fs";

const old = JSON.parse(fs.readFileSync(process.argv[2]));
const now = JSON.parse(fs.readFileSync("pub/konkursy/angielski/data/ojaj/online/vault.json"));
const byId = (v) => new Map(v.tasks.flatMap((t) => t.items.map((i) => [i.id, JSON.stringify(i)])));
const a = byId(old);
const b = byId(now);
let changed = 0;
for (const [id, s] of a) if (b.get(id) !== s) { changed++; console.log("changed", id); }
console.log(`old items ${a.size}, new total ${b.size}, old changed ${changed}`);
for (const k of Object.keys(now)) {
  if (k === "tasks") continue;
  if (JSON.stringify(old[k]) !== JSON.stringify(now[k])) console.log("top-level differs:", k);
}
now.tasks.forEach((t, i) => {
  const o = old.tasks[i];
  for (const k of Object.keys(t)) {
    if (k !== "items" && JSON.stringify(o[k]) !== JSON.stringify(t[k])) console.log(`task ${t.id} differs: ${k}`, JSON.stringify(o[k]), "->", JSON.stringify(t[k]));
  }
});
