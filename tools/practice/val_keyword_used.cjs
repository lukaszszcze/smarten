// Exercise check.js's keyword rule against the cases that matter, including
// the ones it must still reject.
//
// The rule decides a point before any AI call: a student answer without the
// keyword scores 0 outright. Loosening it to accept contractions must not
// loosen it into accepting a different word.
//
// Usage: node tools/practice/val_keyword_used.cjs
const fs = require("fs");
const path = require("path");

const SRC = fs.readFileSync(
  path.join(__dirname, "..", "..", "site/functions/api/check.js"), "utf8");

function lift(name) {
  const start = SRC.indexOf(`function ${name}(`);
  let depth = 0;
  for (let j = SRC.indexOf("{", start); j < SRC.length; j++) {
    if (SRC[j] === "{") depth++;
    else if (SRC[j] === "}" && --depth === 0) return SRC.slice(start, j + 1);
  }
  throw new Error(`unbalanced braces in ${name}`);
}

const { keywordUsed } = new Function(
  `${lift("keywordUsed")}\nreturn { keywordUsed };`)();

const CASES = [
  // [keyword, student answer, should count as used, why]
  ["NEED", "need not have bought", true, "plain keyword"],
  ["NEED", "needn't have bought", true, "contraction of the keyword"],
  ["NEED", "needn’t have bought", true, "contraction with a curly apostrophe"],
  ["SHOULD", "should not have told", true, "plain keyword"],
  ["SHOULD", "shouldn't have told", true, "contraction of the keyword"],
  ["NOT", "had not helped", true, "plain keyword"],
  ["NOT", "hadn't helped", true, "the n't that stands for not"],
  ["NOT", "wasn't helping", true, "the n't that stands for not"],
  ["MANAGE", "manage to stay", true, "plain keyword"],
  ["DECORATED", "has had the cake decorated", true, "keyword later in the answer"],
  ["HAD", "had better read more recipes", true, "keyword first"],

  ["NEED", "needed to buy", false, "a different form of the word"],
  ["NEED", "needs to buy", false, "a different form of the word"],
  ["NEED", "did not have to buy", false, "keyword absent"],
  ["NOT", "nothing helped", false, "keyword is only a prefix of another word"],
  ["NOT", "had never helped", false, "keyword absent"],
  ["MANAGE", "managed to stay", false, "a different form of the word"],
  ["SHOULD", "ought to have told", false, "keyword absent"],
  ["", "anything at all", true, "no keyword given"],
];

let bad = 0;
for (const [kw, ans, want, why] of CASES) {
  const got = keywordUsed(ans, kw);
  if (got !== want) {
    bad++;
    console.log(`  FAIL  keyword ${JSON.stringify(kw)} vs ${JSON.stringify(ans)}`
      + ` -> ${got}, expected ${want} (${why})`);
  }
}
console.log(`${CASES.length} case(s), ${bad} failure(s)`);
process.exit(bad ? 1 : 0);
