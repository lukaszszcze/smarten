// Dump the visible text of a few of the new OJAJ tasks, to read what a student
// actually sees. Run through tools/ojaj/peek_ojaj.sh.
import { renderToString } from "react-dom/server";
import fs from "fs";
import WordFormation from "COMPDIR/WordFormation.jsx";
import TrueFalseNI from "COMPDIR/TrueFalseNI.jsx";
import MultipleChoice from "COMPDIR/MultipleChoice.jsx";
import Matching from "COMPDIR/Matching.jsx";
import GrammarGaps from "COMPDIR/GrammarGaps.jsx";

const COMP = {
  word_formation: WordFormation,
  true_false_ni: TrueFalseNI,
  multiple_choice: MultipleChoice,
  matching: Matching,
  grammar_gaps: GrammarGaps,
};

const visible = (h) => h
  .replace(/<input[^>]*>/g, " [input] ")
  .replace(/<select[^>]*>/g, " [select] ")
  .replace(/<[^>]+>/g, " ")
  .replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&")
  .replace(/\s+/g, " ").trim();

for (const id of process.argv.slice(2)) {
  const doc = JSON.parse(fs.readFileSync(`DATADIR/ojaj/practice/${id}.json`, "utf8"));
  for (const task of doc.tasks) {
    const Comp = COMP[task.type];
    const html = renderToString(
      <Comp task={task} answers={{}} onChange={() => {}} showResults={false} />
    );
    console.log(`\n===== ${id} (${task.type}) =====`);
    console.log(visible(html));
  }
}
