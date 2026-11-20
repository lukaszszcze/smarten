// Score every sentence_transformation and grammar_gaps item's *own official
// answer* with the grader's real code, and report the ones that do not score
// full marks.
//
// The grader has two checks that run before any AI call. For sentence
// transformation it awards 0 outright when the keyword is absent from the
// student's text, and 1 outright when the text matches the official answer.
// So the official answer is the best possible submission: if it does not score,
// no student can. This catches the case where the keyword is printed outside
// the box, or the answer is stored in a shape the exact-match check cannot see.
//
// The helper functions are lifted out of check.js by name at run time rather
// than copied, so this cannot drift from the grader.
//
// Usage: node tools/practice/val_official_answer.cjs
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..", "..");
const SRC = fs.readFileSync(
  path.join(ROOT, "site/functions/api/check.js"), "utf8");

function lift(name) {
  const start = SRC.indexOf(`function ${name}(`);
  if (start < 0) throw new Error(`no function ${name} in check.js`);
  let depth = 0, i = SRC.indexOf("{", start);
  for (let j = i; j < SRC.length; j++) {
    if (SRC[j] === "{") depth++;
    else if (SRC[j] === "}" && --depth === 0) {
      return SRC.slice(start, j + 1);
    }
  }
  throw new Error(`unbalanced braces in ${name}`);
}

const { normalize, keywordUsed, canonicalGapAnswer } = new Function(
  `${lift("normalize")}\n${lift("keywordUsed")}\n${lift("canonicalGapAnswer")}
   return { normalize, keywordUsed, canonicalGapAnswer };`)();

// Whether the sentence-transformation grader still treats a list of accepted
// answers as one value. Read off the source so this check retires itself once
// the grader handles the list.
const GRADER = lift("gradeSentenceTransformation");
const ARRAY_STILL_MISHANDLED = /normalize\(item\.answer\)/.test(GRADER)
  || /correctAnswer: item\.answer\b/.test(GRADER);

function walk(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(p));
    else if (e.name.endsWith(".json")) out.push(p);
  }
  return out;
}

const BASE = path.join(ROOT, "pub/konkursy/angielski/data");
const rows = [];
let checked = 0;

for (const f of walk(BASE).sort()) {
  let doc;
  try {
    doc = JSON.parse(fs.readFileSync(f, "utf8"));
  } catch {
    continue;
  }
  if (!doc || !Array.isArray(doc.tasks)) continue;
  const src = f.slice(BASE.length + 1).replace(/\.json$/, "");
  const kind = /^(practice|quest)[\\/]/.test(src) ? "prac" : "real";

  for (const task of doc.tasks) {
    if (task.skipped) continue;

    if (task.type === "sentence_transformation") {
      for (const it of task.items || []) {
        // Every accepted form is checked, not just the first: a list whose
        // later entries fail is just as unscoreable for the student who picks
        // one of them.
        const accepted = Array.isArray(it.answer) ? it.answer : [it.answer];
        for (const official of accepted) {
          checked++;
          if (!keywordUsed(official, it.keyword)) {
            rows.push([src, kind, task.id, it.id,
              `accepted answer "${official}" does not contain keyword "${it.keyword}" -> scored 0 before any AI call`]);
          }
          if (!normalize(official)) {
            rows.push([src, kind, task.id, it.id, "accepted answer is empty"]);
          }
        }
        // The exact-match check normalizes item.answer as one value, so a list
        // is compared as its comma-joined text and can never match. The same
        // list reaches the results page as the correct answer, where React
        // concatenates it into one run-together string.
        if (Array.isArray(it.answer) && ARRAY_STILL_MISHANDLED) {
          rows.push([src, kind, task.id, it.id,
            `answer is a list of ${it.answer.length}; exact match compares the whole list, and the results page runs the forms together`]);
        }
      }
    }

    if (task.type === "grammar_gaps") {
      for (const it of task.items || []) {
        const expected = Array.isArray(it.answer) ? it.answer : [it.answer];
        for (let i = 0; i < expected.length; i++) {
          checked++;
          if (!normalize(canonicalGapAnswer(expected[i]))) {
            rows.push([src, kind, task.id, it.id,
              `gap ${i + 1} official answer "${expected[i]}" reduces to nothing -> can never match`]);
          }
        }
      }
    }
  }
}

console.log(`scored ${checked} official answer(s) with the grader's own code`);
console.log(`problems: ${rows.length}`);
for (const r of rows) {
  console.log("  " + String(r[0]).padEnd(26) + String(r[1]).padEnd(6)
    + String(r[2]).padEnd(4) + String(r[3]).padEnd(6) + r[4]);
}
process.exit(rows.length ? 1 : 0);
