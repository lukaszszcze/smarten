import test from "node:test";
import assert from "node:assert/strict";

import {
  isOjajAttempt,
  ojajStageTitle,
  OJAJ_PRACTICE_CONFIG,
  OJAJ_TEST_CONFIG,
} from "./ojaj.js";

// isOjajAttempt decides which competition an attempt is averaged into and which
// route its history row links to. Getting it wrong sends a student to the wrong
// paper, so both the tagged and the untagged shape are pinned here.

test("an OJAJ attempt is recognised by its tag", () => {
  assert.equal(isOjajAttempt({ competition: "ojaj", testId: "2024-2025/szkolny" }), true);
});

test("an OJAJ attempt is recognised by its testId alone", () => {
  assert.equal(isOjajAttempt({ testId: "ojaj/2024-2025/szkolny" }), true);
  assert.equal(isOjajAttempt({ testId: "ojaj/practice/ojaj_choice_001" }), true);
});

test("a kuratoryjny attempt is not OJAJ", () => {
  assert.equal(isOjajAttempt({ testId: "2024-2025/szkolny" }), false);
  assert.equal(isOjajAttempt({ testId: "practice/cloze_001" }), false);
});

test("a missing or malformed attempt is not OJAJ", () => {
  for (const a of [null, undefined, {}, { testId: null }, { testId: "" }]) {
    assert.equal(isOjajAttempt(a), false);
  }
});

test("the OJAJ test config addresses OJAJ files and OJAJ testIds", () => {
  assert.equal(
    OJAJ_TEST_CONFIG.dataPath("2024-2025", "szkolny"),
    "/konkursy/angielski/data/ojaj/2024-2025/szkolny.json"
  );
  const testId = OJAJ_TEST_CONFIG.testId("2024-2025", "szkolny");
  assert.equal(testId, "ojaj/2024-2025/szkolny");
  // The history row routes on the testId, so it has to read back as a route.
  assert.equal(isOjajAttempt({ testId }), true);
});

test("the OJAJ practice config addresses OJAJ files and its own pool", () => {
  assert.equal(
    OJAJ_PRACTICE_CONFIG.dataPath("ojaj_choice_001"),
    "/konkursy/angielski/data/ojaj/practice/ojaj_choice_001.json"
  );
  const testId = `${OJAJ_PRACTICE_CONFIG.testIdPrefix}/ojaj_choice_001`;
  assert.equal(testId, "ojaj/practice/ojaj_choice_001");
  assert.equal(testId.startsWith(OJAJ_PRACTICE_CONFIG.pool.prefix), true);
  assert.equal(OJAJ_PRACTICE_CONFIG.showLadder, false);
});

test("a stage title names the part when the paper has one", () => {
  assert.equal(ojajStageTitle({ stage: "szkolny", part: "1" }), "Etap szkolny, czesc 1");
  assert.equal(ojajStageTitle({ stage: "szkolny" }), "Etap szkolny");
  assert.equal(ojajStageTitle({ stage: "final" }), "Final");
});

test("a stage with its own label uses it instead of the slug", () => {
  // Two papers of the same stage need two route slugs, and "szkolny-a" has no
  // name worth deriving, so the index labels those stages itself.
  assert.equal(
    ojajStageTitle({ stage: "szkolny-a", part: "1", label: "Etap szkolny, cz. 1 (grupa A)" }),
    "Etap szkolny, cz. 1 (grupa A)"
  );
  assert.equal(ojajStageTitle({ stage: "szkolny-a", part: "1" }), "szkolny-a, czesc 1");
});
