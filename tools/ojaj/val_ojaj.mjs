// Validate the OJAJ data against the app's own scoring and the fields each
// renderer actually reads. Run: node tools/ojaj/val_ojaj.mjs
//
// The two failures this is here to catch:
//   - a paper that cannot be scored full marks even with the key typed in;
//   - an item missing the field its renderer reads, which renders a blank row.

import { readFileSync, readdirSync } from "node:fs";
import { scoreTest } from "../../site/src/lib/scoring.js";
import { assembleTest, drawTest } from "../../site/src/lib/ojajDraw.js";

const DATA = "pub/konkursy/angielski/data/ojaj";
const read = (p) => JSON.parse(readFileSync(`${DATA}/${p}`, "utf8"));

// Types the app grades only through /api/check; they score 0 locally by design.
const AI_CHECKED = ["sentence_transformation", "grammar_gaps", "writing"];

// Field each renderer reads for the item's visible prompt. A missing one is not
// a crash, it is a numbered row with nothing in it.
const PROMPT_FIELDS = {
  word_formation: ["sentence"],
  word_spelling: ["stem", "clue", "sentence"],
  grammar_gaps: ["context"],
  multiple_choice: ["stem", "prompt", "context"],
  dialogue_choice: ["stem", "prompt", "context"],
  knowledge_questions: ["question"],
  sentence_transformation: ["transformed"],
  // Matching rows are labelled by whichever of these the paper gives them;
  // Matching.jsx falls back to the row id when none is set.
  matching: ["name", "statement", "label"],
  true_false_ni: ["statement"],
};

// word_formation has two shapes. Per-sentence items carry their own sentence;
// a word-bank task puts one shared text on the task, and its items carry only
// an id and an answer, so there is no per-item prompt to check.
const sharedPrompt = (task) => task.type === "word_formation" && !!task.text;

let failures = 0;
const fail = (msg) => { console.error(`  FAIL ${msg}`); failures++; };

function perfectAnswers(data) {
  const answers = {};
  for (const task of data.tasks) {
    for (const item of task.items || []) {
      const key = item.answer;
      answers[item.id] = Array.isArray(key) ? key[0] : key;
    }
  }
  return answers;
}

function checkShapes(data, label) {
  for (const task of data.tasks) {
    const fields = PROMPT_FIELDS[task.type];
    if (!fields) fail(`${label} task ${task.id}: unknown type ${task.type}`);

    for (const item of task.items || []) {
      if (fields && !sharedPrompt(task) && !fields.some((f) => item[f])) {
        fail(`${label} ${item.id}: none of ${fields.join("/")} is set`);
      }
      if (item.answer === undefined || item.answer === "") {
        fail(`${label} ${item.id}: no answer`);
      }
      if (task.type === "grammar_gaps") {
        // An array here is read as one answer per gap, not as alternatives.
        if (Array.isArray(item.answer)) {
          const gaps = (item.context.match(/_{2,}/g) || []).length;
          if (item.answer.length !== gaps) {
            fail(`${label} ${item.id}: ${item.answer.length} answers for ${gaps} gaps`);
          }
        } else if ((item.context.match(/_{2,}/g) || []).length !== 1) {
          fail(`${label} ${item.id}: a string answer but not exactly one gap`);
        }
      }
      if (task.type === "multiple_choice" || task.type === "knowledge_questions") {
        if (item.options && !item.options.some((o) => o.startsWith(item.answer))) {
          fail(`${label} ${item.id}: key ${item.answer} matches no option`);
        }
      }
      if (task.type === "matching") {
        // The options live on the task, not the item, and a key pointing at a
        // letter that is not offered leaves the row unanswerable.
        const letters = (task.options || []).map((o) => o.letter);
        if (!letters.includes(item.answer)) {
          fail(`${label} ${item.id}: key ${item.answer} is not an offered letter`);
        }
      }
    }
  }
}

function checkScoring(data, label) {
  const res = scoreTest(data, perfectAnswers(data));
  const autoMax = data.tasks
    .filter((t) => !AI_CHECKED.includes(t.type))
    .reduce((s, t) => s + t.points, 0);
  const aiMax = data.tasks
    .filter((t) => AI_CHECKED.includes(t.type))
    .reduce((s, t) => s + t.points, 0);

  if (res.earned !== autoMax) {
    fail(`${label}: answer key scores ${res.earned}/${autoMax} on the auto-marked tasks`);
    for (const t of res.tasks) {
      if (!AI_CHECKED.includes(t.type) && t.earned !== t.max) {
        const wrong = (t.items || []).filter((i) => !i.correct).map((i) => i.id);
        fail(`  task ${t.taskId} (${t.type}): ${t.earned}/${t.max}, missed ${wrong.join(", ")}`);
      }
    }
  }
  return { earned: res.earned, autoMax, aiMax, max: res.max };
}

console.log("index");
const index = read("index.json");
for (const ex of index.exercises) {
  try {
    read(`practice/${ex.id}.json`);
  } catch {
    fail(`index lists ${ex.id}, but practice/${ex.id}.json does not load`);
  }
}
const listed = new Set(index.exercises.map((e) => e.id));
for (const f of readdirSync(`${DATA}/practice`)) {
  const id = f.replace(/\.json$/, "");
  if (!listed.has(id)) fail(`practice/${f} is not in the index, so nothing links to it`);
}

for (const edition of index.editions) {
  for (const stage of edition.stages) {
    const label = `${edition.yearPath}/${stage.stage}`;
    console.log(`\ntest ${label}`);
    const data = read(`${edition.yearPath}/${stage.stage}.json`);
    if (data.maxPoints !== stage.maxPoints) {
      fail(`${label}: index says ${stage.maxPoints} pkt, the paper says ${data.maxPoints}`);
    }
    if (data.timeMinutes !== stage.timeMinutes) {
      fail(`${label}: index says ${stage.timeMinutes} min, the paper says ${data.timeMinutes}`);
    }
    checkShapes(data, label);
    const s = checkScoring(data, label);
    console.log(`  ${s.earned}/${s.autoMax} auto-marked, ${s.aiMax} pkt left to /api/check`);
  }
}

// The vault of own items the online tests are put together from. online/
// holds the vault and nothing else: the three fixed tests served until
// 2026-10-25 are its first batches now. Each batch is put together as one test
// by the app's own assembleTest and checked like a paper; then fresh draws
// must fill every task to its count and profile. A batch holds all 45 items or
// one task alone, its count of items (wisielec since 2026-11-11, the other
// tasks since later that day).
for (const f of readdirSync(`${DATA}/online`)) {
  if (f !== "vault.json") fail(`online/${f}: only the vault belongs in online/`);
}
console.log("\nonline vault");
const vault = read("online/vault.json");
const typeKeys = new Set(vault.mistakeTypes.map((t) => t.key));
const batches = [...new Set(vault.tasks.flatMap((t) => t.items.map((it) => it.id.split("-")[0])))];
for (const task of vault.tasks) {
  for (const item of task.items) {
    if (!typeKeys.has(item.mistakeType)) fail(`vault ${item.id}: type ${item.mistakeType} unknown`);
  }
}
for (const batch of batches) {
  const label = `online batch ${batch}`;
  const chosen = vault.tasks.map((t) => t.items.filter((it) => it.id.startsWith(`${batch}-`)));
  const data = assembleTest(vault, chosen, { items: {}, types: {} });
  const sizes = chosen.map((items) => items.length);
  const oneAlone = vault.tasks.some((spec, i) =>
    sizes.join() === vault.tasks.map((t, j) => (j === i ? spec.count : 0)).join());
  if (data.maxPoints !== 45 && !oneAlone) {
    fail(`${label}: items per task ${sizes.join(", ")}, not 45 and not one task alone`);
  }
  checkShapes(data, label);
  const s = checkScoring(data, label);
  console.log(`  ${label}: ${s.earned}/${s.autoMax} auto-marked, ${s.aiMax} pkt left to /api/check`);
}
for (let n = 0; n < 50; n++) {
  const data = drawTest(vault, { items: {}, types: {} });
  data.tasks.forEach((task, i) => {
    const spec = vault.tasks[i];
    if (task.items.length !== spec.count) fail(`draw: task ${task.id} has ${task.items.length}`);
    for (const [level, [lo, hi]] of Object.entries(spec.levels || {})) {
      const k = task.items.filter((it) => it.level === level).length;
      if (k < lo || k > hi) fail(`draw: task ${task.id} has ${k} ${level}`);
    }
  });
  const s = checkScoring(data, "draw");
  if (s.earned !== s.autoMax) break;
}
console.log("  50 draws: every task at its count and level profile, the key scores full marks");

for (const ex of index.exercises) {
  console.log(`\nexercise ${ex.id}`);
  const data = read(`practice/${ex.id}.json`);
  const points = data.tasks.reduce((s, t) => s + t.points, 0);
  if (points !== ex.points) fail(`${ex.id}: index says ${ex.points} pkt, the file says ${points}`);
  checkShapes(data, ex.id);
  const s = checkScoring(data, ex.id);
  console.log(`  ${s.earned}/${s.autoMax} auto-marked, ${s.aiMax} pkt left to /api/check`);
}

console.log(failures === 0 ? "\nall checks passed" : `\n${failures} failure(s)`);
process.exit(failures === 0 ? 0 : 1);
