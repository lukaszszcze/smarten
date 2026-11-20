// Render every quest task through the real components and check what the
// student actually gets on screen.
//
// The quest section had never been through this sweep — every validator
// globbed data/20*/ plus data/practice/ and stopped there. This covers the
// five types quest uses.
//
// Per task it checks: the component does not throw, the task's own passage
// reaches the page when the data carries one, every item's prompt is visible,
// and the number of answer controls matches the number of things graded.
//
// See tools/practice/render_quest.sh.
import { renderToString } from "react-dom/server";
import fs from "fs";
import path from "path";
import MultipleChoice from "COMPDIR/MultipleChoice.jsx";
import TrueFalseNI from "COMPDIR/TrueFalseNI.jsx";
import WordSpelling from "COMPDIR/WordSpelling.jsx";
import OpenCloze from "COMPDIR/OpenCloze.jsx";
import Matching from "COMPDIR/Matching.jsx";

const BASE = "DATADIR/quest";
const COMP = {
  multiple_choice: MultipleChoice,
  true_false_ni: TrueFalseNI,
  word_spelling: WordSpelling,
  open_cloze: OpenCloze,
  matching: Matching,
};

function visible(html) {
  return html
    .replace(/<input[^>]*>/g, " ␣ ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&#x27;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();
}

function norm(s) {
  return String(s || "").replace(/[␣_*]+/g, " ").replace(/\s+/g, " ").trim();
}

const rows = [];
let tasksChecked = 0;
let itemsChecked = 0;

const files = fs.readdirSync(BASE)
  .filter((n) => n.endsWith(".json") && n !== "index.json")
  .sort();

for (const name of files) {
  const doc = JSON.parse(fs.readFileSync(path.join(BASE, name), "utf8"));
  const src = name.replace(/\.json$/, "");

  for (const task of doc.tasks || []) {
    const Comp = COMP[task.type];
    const problems = [];
    if (!Comp) {
      rows.push([src, task.type, String(task.id), "no component for this type"]);
      continue;
    }
    const items = task.items || [];

    let html;
    try {
      html = renderToString(
        <Comp task={task} answers={{}} onChange={() => {}} showResults={false} />
      );
    } catch (e) {
      rows.push([src, task.type, String(task.id),
        `THREW ${e.constructor.name}: ${e.message}`.slice(0, 90)]);
      continue;
    }
    tasksChecked++;
    const text = norm(visible(html));

    // The task-level passage, when the data has one.
    if (task.text) {
      // open_cloze turns each "1.1. _________" marker into an input, so only
      // the prose before the first marker survives verbatim.
      const head = norm(String(task.text).split(/\d+\.\d+\.\s*_/)[0]).slice(0, 60);
      if (head && !text.includes(head)) problems.push("PASSAGE NOT SHOWN");
    }
    if (task.instruction && !text.includes(norm(task.instruction).slice(0, 40))) {
      problems.push("instruction not shown");
    }

    const inputs = (html.match(/<input/g) || []).length;
    const selects = (html.match(/<select/g) || []).length;
    // MultipleChoice and TrueFalseNI use clickable divs, not form controls, so
    // the option text itself is what has to be counted.
    let want = 0;

    for (const it of items) {
      itemsChecked++;
      if (task.type === "multiple_choice") {
        const prompt = norm(it.stem || it.prompt || it.context);
        if (!prompt) problems.push(`${it.id}: no prompt field`);
        else if (!text.includes(prompt.slice(0, 50))) problems.push(`${it.id}: prompt not shown`);
        for (const opt of it.options || []) {
          const o = norm(String(opt).replace(/^[A-D]\)\s*/, ""));
          if (o && !text.includes(o)) problems.push(`${it.id}: option "${o}" not shown`);
        }
        if (!/^[A-D]$/.test(String(it.answer))) problems.push(`${it.id}: answer ${it.answer} not a letter`);
      } else if (task.type === "true_false_ni") {
        const prompt = norm(it.statement);
        if (!prompt) problems.push(`${it.id}: no statement`);
        else if (!text.includes(prompt.slice(0, 50))) problems.push(`${it.id}: statement not shown`);
        if (!/^(T|F|NI)$/.test(String(it.answer))) problems.push(`${it.id}: answer ${it.answer} unexpected`);
      } else if (task.type === "word_spelling") {
        want += 1;
        const prompt = norm(it.stem || it.clue || it.sentence);
        if (!prompt) problems.push(`${it.id}: no stem`);
        else if (!text.includes(prompt.slice(0, 40))) problems.push(`${it.id}: stem not shown`);
      } else if (task.type === "matching") {
        const label = it.category || it.name || it.statement || it.label || it.id;
        if (!label) problems.push(`${it.id}: no label`);
        else if (!text.includes(norm(label))) problems.push(`${it.id}: label not shown`);
        want += Array.isArray(it.answers) ? it.answers.length : 1;
      }
    }

    if (task.type === "open_cloze") {
      const gaps = (String(task.text || "").match(/\d+\.\d+\.\s*_+/g) || []).length;
      want = gaps;
      if (gaps !== items.length) problems.push(`${gaps} gaps in text vs ${items.length} items`);
    }

    if (task.type === "matching") {
      const optLetters = (task.options || []).map((o) => o.letter);
      if (!optLetters.length) problems.push("no options to match against");
      for (const it of items) {
        for (const a of it.answers || []) {
          if (!optLetters.includes(a)) problems.push(`${it.id}: answer ${a} not an option`);
        }
      }
      if (selects !== want) problems.push(`${selects} selects, expected ${want}`);
    } else if (task.type === "word_spelling" || task.type === "open_cloze") {
      if (inputs !== want) problems.push(`${inputs} inputs, expected ${want}`);
    }

    if (problems.length) {
      rows.push([src, task.type, String(task.id),
        [...new Set(problems)].slice(0, 4).join("; ").slice(0, 110)]);
    }
  }
}

console.log(`rendered ${tasksChecked} quest task(s), ${itemsChecked} item(s)`);
console.log(`problems: ${rows.length}`);
for (const r of rows) {
  console.log("  " + r[0].padEnd(20) + r[1].padEnd(18) + String(r[2]).padEnd(4) + r[3]);
}
