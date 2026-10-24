import { test } from "node:test";
import assert from "node:assert/strict";
import { AOE_UNITS, aoeUnitForPercentage, nextAoeUnit, usesAoeMarks } from "./aoeRanks.js";

test("one unit per score on a ten-question quiz, weakest first", () => {
  assert.equal(AOE_UNITS.length, 11);
  assert.equal(aoeUnitForPercentage(0).name, "Sheep");
  assert.equal(aoeUnitForPercentage(10).name, "Villager");
  assert.equal(aoeUnitForPercentage(80).name, "Knight");
  assert.equal(aoeUnitForPercentage(100).name, "Paladin");
});

test("percentages between steps round to the nearest unit and are clamped", () => {
  assert.equal(aoeUnitForPercentage(84).name, "Knight");
  assert.equal(aoeUnitForPercentage(86).name, "Champion");
  assert.equal(aoeUnitForPercentage(-5).name, "Sheep");
  assert.equal(aoeUnitForPercentage(140).name, "Paladin");
});

test("next unit is the one above, and there is none above the Paladin", () => {
  assert.equal(nextAoeUnit(80).name, "Champion");
  assert.equal(nextAoeUnit(100), null);
});

test("only the UK quizzes use the unit marks", () => {
  assert.equal(usesAoeMarks("ojaj_uk_symbole"), true);
  assert.equal(usesAoeMarks("ojaj_uk_postacie"), true);
  assert.equal(usesAoeMarks("ojaj_gl_1"), false);
  assert.equal(usesAoeMarks(undefined), false);
});
