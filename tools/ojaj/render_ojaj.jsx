// Render every OJAJ task through the real components and check what the student
// actually gets on screen. Same shape as tools/practice/render_quest.jsx.
//
// Per task it checks: the component does not throw, the instruction and every
// item's prompt reach the page, every option is shown, and the number of answer
// controls matches the number of things graded.
//
// The failure this exists for is silent: GrammarGaps and SentenceTransformation
// split their text on a literal run of nine underscores, so a gap written with
// eight renders as a sentence with the input stranded at the end, and nothing
// else in the pipeline notices.
//
// See tools/ojaj/render_ojaj.sh.
import { renderToString } from "react-dom/server";
import fs from "fs";
import path from "path";
import WordFormation from "COMPDIR/WordFormation.jsx";
import WordSpelling from "COMPDIR/WordSpelling.jsx";
import GrammarGaps from "COMPDIR/GrammarGaps.jsx";
import MultipleChoice from "COMPDIR/MultipleChoice.jsx";
import KnowledgeQuestions from "COMPDIR/KnowledgeQuestions.jsx";
import SentenceTransformation from "COMPDIR/SentenceTransformation.jsx";
import Matching from "COMPDIR/Matching.jsx";
import TrueFalseNI from "COMPDIR/TrueFalseNI.jsx";
import { onlineQuestions } from "COMPDIR/../../lib/ojajOnline.js";
import { assembleTest } from "COMPDIR/../../lib/ojajDraw.js";

const BASE = "DATADIR/ojaj";
const COMP = {
  word_formation: WordFormation,
  word_spelling: WordSpelling,
  grammar_gaps: GrammarGaps,
  multiple_choice: MultipleChoice,
  knowledge_questions: KnowledgeQuestions,
  sentence_transformation: SentenceTransformation,
  matching: Matching,
  true_false_ni: TrueFalseNI,
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

function shown(text, s, chars = 40) {
  const want = norm(s).slice(0, chars);
  return want.length === 0 || text.includes(want);
}

const rows = [];
let tasksChecked = 0;
let itemsChecked = 0;

const files = [];
for (const entry of fs.readdirSync(BASE, { withFileTypes: true })) {
  if (entry.isDirectory()) {
    for (const n of fs.readdirSync(path.join(BASE, entry.name))) {
      if (n.endsWith(".json")) files.push(path.join(entry.name, n));
    }
  } else if (entry.name.endsWith(".json") && entry.name !== "index.json") {
    files.push(entry.name);
  }
}
files.sort();

// The online player shows one item per screen, each screen's task cut down to
// its item by onlineQuestions(). The vault itself is never shown: the player
// shows a test put together from it. So each batch of the vault is put
// together as one test, by the app's own assembleTest, and its screens are
// rendered, labelled batch#number. The renderer prints the item id as the
// number, so the two have to agree.
function tasksToRender(doc, src) {
  if (src !== "online/vault") {
    return (doc.tasks || []).map((task) => ({ task, label: String(task.id) }));
  }
  const batches = [...new Set(doc.tasks.flatMap((t) => t.items.map((it) => it.id.split("-")[0])))];
  return batches.flatMap((batch) => {
    const chosen = doc.tasks.map((t) => t.items.filter((it) => it.id.startsWith(`${batch}-`)));
    const test = assembleTest(doc, chosen, { items: {}, types: {} });
    return onlineQuestions(test).map((q) => {
      if (q.item.id !== String(q.number)) {
        rows.push([src, q.task.type, `${batch}#${q.number}`, `item id ${q.item.id} is shown as the number`]);
      }
      return { task: q.task, label: `${batch}#${q.number}` };
    });
  });
}

for (const rel of files) {
  const doc = JSON.parse(fs.readFileSync(path.join(BASE, rel), "utf8"));
  const src = rel.replace(/\.json$/, "").replace(/\\/g, "/");

  for (const { task, label } of tasksToRender(doc, src)) {
    const Comp = COMP[task.type];
    const problems = [];
    if (!Comp) {
      rows.push([src, task.type, label, "no component for this type"]);
      continue;
    }
    const items = task.items || [];

    let html;
    try {
      html = renderToString(
        <Comp task={task} answers={{}} onChange={() => {}} showResults={false} />
      );
    } catch (e) {
      rows.push([src, task.type, label,
        `THREW ${e.constructor.name}: ${e.message}`.slice(0, 90)]);
      continue;
    }
    tasksChecked++;
    const text = norm(visible(html));

    if (!shown(text, task.instruction)) problems.push("instruction not shown");

    const inputs = (html.match(/<input/g) || []).length;
    let want = 0;

    for (const it of items) {
      itemsChecked++;

      if (task.type === "word_formation" && task.text) {
        // Word-bank shape: one shared text, and the bank is the whole prompt.
        want += 1;

      } else if (task.type === "word_formation") {
        want += 1;
        if (!it.sentence) problems.push(`${it.id}: no sentence`);
        else if (!shown(text, it.sentence.split(/_{2,}/)[0])) {
          problems.push(`${it.id}: sentence not shown`);
        }
        const base = it.wordBase || it.baseWord;
        if (!base) problems.push(`${it.id}: no base word`);
        else if (!text.includes(base)) problems.push(`${it.id}: base word ${base} not shown`);

      } else if (task.type === "true_false_ni") {
        // The renderer offers T, F and NI unless the task narrows the list; a
        // paper with two answers must not show a third column.
        if (!it.statement) problems.push(`${it.id}: no statement`);
        else if (!shown(text, it.statement, 50)) problems.push(`${it.id}: statement not shown`);
        if (task.text && !shown(text, task.text, 60)) problems.push("passage not shown");
        const offered = (html.match(new RegExp(`name="tfni-${it.id}"`, "g")) || []).length;
        const expected = (task.options || ["T", "F", "NI"]).length;
        if (offered !== expected) {
          problems.push(`${it.id}: ${offered} radio buttons, expected ${expected}`);
        }

      } else if (task.type === "word_spelling") {
        want += 1;
        const stem = it.stem || it.clue || it.sentence;
        if (!stem) problems.push(`${it.id}: no stem`);
        else if (!shown(text, stem)) problems.push(`${it.id}: stem not shown`);
        // The letter pattern is the task; losing it leaves an unguessable blank.
        if (it.hint && !visible(html).includes(it.hint)) {
          problems.push(`${it.id}: letter pattern not shown`);
        }

      } else if (task.type === "grammar_gaps") {
        const gaps = (String(it.context).match(/_________/g) || []).length;
        if (gaps === 0) problems.push(`${it.id}: no gap the renderer can split on`);
        want += gaps;
        if (!shown(text, String(it.context).split("_________")[0])) {
          problems.push(`${it.id}: context not shown`);
        }
        // The bracketed words are the prompt; without them the gap is unanswerable.
        const brackets = String(it.context).match(/\([^)]*\)/g) || [];
        for (const b of brackets) {
          if (!visible(html).includes(b)) problems.push(`${it.id}: prompt ${b} not shown`);
        }

      } else if (task.type === "sentence_transformation") {
        want += 1;
        if (!String(it.transformed).includes("_________")) {
          problems.push(`${it.id}: no gap the renderer can split on`);
        }
        if (!shown(text, it.original)) problems.push(`${it.id}: original sentence not shown`);
        if (!it.keyword) problems.push(`${it.id}: no keyword`);
        else if (!text.includes(it.keyword)) problems.push(`${it.id}: keyword not shown`);

      } else if (task.type === "multiple_choice") {
        const prompt = it.stem || it.prompt || it.context;
        if (!prompt) problems.push(`${it.id}: no prompt field`);
        else if (!shown(text, prompt, 50)) problems.push(`${it.id}: prompt not shown`);
        // Reading-comprehension tasks put the passage on the task; without it
        // the questions ask about a text the student never sees.
        if (task.text && !shown(text, task.text, 60)) problems.push("passage not shown");
        for (const opt of it.options || []) {
          const o = norm(String(opt).replace(/^[A-D]\)\s*/, ""));
          if (o && !text.includes(o)) problems.push(`${it.id}: option "${o}" not shown`);
        }
        if (!/^[A-D]$/.test(String(it.answer))) {
          problems.push(`${it.id}: answer ${it.answer} not a letter`);
        }

      } else if (task.type === "matching") {
        // The row label and the option list are both on screen or the student
        // is matching a number against nothing.
        const label = it.name || it.statement || it.label;
        if (!label) problems.push(`${it.id}: no row label`);
        else if (!shown(text, label, 50)) problems.push(`${it.id}: row label not shown`);
        for (const opt of task.options || []) {
          if (!text.includes(norm(opt.text))) {
            problems.push(`option ${opt.letter} not shown`);
          }
        }

      } else if (task.type === "knowledge_questions") {
        if (!it.question) problems.push(`${it.id}: no question`);
        else if (!shown(text, it.question, 50)) problems.push(`${it.id}: question not shown`);
        for (const opt of it.options || []) {
          // The renderer reads the letter off an "A." prefix.
          if (!/^[A-D]\. /.test(opt)) problems.push(`${it.id}: option "${opt}" lacks an "A." prefix`);
          if (!text.includes(norm(opt))) problems.push(`${it.id}: option "${opt}" not shown`);
        }
      }
    }

    if (["word_formation", "word_spelling", "grammar_gaps", "sentence_transformation"].includes(task.type)) {
      if (inputs !== want) problems.push(`${inputs} inputs, expected ${want}`);
    }
    if (task.type === "word_formation" && task.text) {
      // The bank is the only prompt this shape has: without it every gap is an
      // open question, and without the passage there is nothing to fill in.
      // Compare up to the first gap only -- past it the renderer interleaves
      // item ids and inputs that the source text does not carry.
      if (!shown(text, task.text.split(/(?:\d+\.\s*)?_{2,}/)[0], 30)) {
        problems.push("passage not shown");
      }
      for (const word of task.wordBank || []) {
        if (!text.includes(word)) problems.push(`word bank is missing ${word}`);
      }
    }
    if (task.type === "matching") {
      const selects = (html.match(/<select/g) || []).length;
      if (selects !== items.length) {
        problems.push(`${selects} dropdowns, expected ${items.length}`);
      }
    }

    if (problems.length) {
      rows.push([src, task.type, label,
        [...new Set(problems)].slice(0, 4).join("; ").slice(0, 120)]);
    }
  }
}

console.log(`rendered ${tasksChecked} OJAJ task(s), ${itemsChecked} item(s)`);
console.log(`problems: ${rows.length}`);
for (const r of rows) {
  console.log("  " + r[0].padEnd(24) + r[1].padEnd(24) + String(r[2]).padEnd(4) + r[3]);
}
process.exit(rows.length === 0 ? 0 : 1);
