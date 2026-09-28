// OJAJ — Olimpiada Jezyka Angielskiego dla Juniorow (ojaj.wsjo.pl).
//
// A second competition alongside the Mazowieckie kuratoryjny one the rest of
// the app covers. It is a separate section rather than more rows in the same
// list because almost nothing about it lines up: it runs at B2-C1+ against
// B1-C1, its stages are named differently, its papers are marked out of 45
// rather than 40/60, and mixing its scores into the kuratoryjny average would
// describe neither competition.

// Extension included so this module also loads under plain Node, which the
// test runner uses; Vite resolves either form.
import { OJAJ_POOL } from "./practiceRewards.js";

export const OJAJ_DATA_ROOT = "/konkursy/angielski/data/ojaj";
export const OJAJ_INDEX_PATH = `${OJAJ_DATA_ROOT}/index.json`;

// Attempts are tagged so the home page can keep the two competitions apart in
// its averages. `competition` is absent on every attempt saved before OJAJ
// existed, which is exactly what "kuratoryjny" means there.
export const OJAJ_COMPETITION = "ojaj";

export const OJAJ_STAGE_LABELS = {
  szkolny: "Etap szkolny",
  okregowy: "Etap okregowy",
  final: "Final",
};

export const OJAJ_STAGE_COLORS = {
  szkolny: "#50d890",
  "szkolny-a": "#50d890",
  "szkolny-b": "#50d890",
  okregowy: "#42b4f5",
  final: "#a78bfa",
};

export const OJAJ_ACCENT = "#e0704a";

// Passed to KonkursTest so it reads OJAJ papers and files its attempts under
// their own testId space.
export const OJAJ_TEST_CONFIG = {
  competition: OJAJ_COMPETITION,
  dataPath: (year, stage) => `${OJAJ_DATA_ROOT}/${year}/${stage}.json`,
  testId: (year, stage) => `ojaj/${year}/${stage}`,
  stageLabels: OJAJ_STAGE_LABELS,
  backTo: "/ojaj",
  backLabel: "Powrot do OJAJ",
};

// Passed to PracticeExercise for the OJAJ exercises. They keep their own best
// scores, so they neither inflate nor are counted by the practice title ladder,
// which is calibrated against the 325-exercise Mazowieckie pool.
export const OJAJ_PRACTICE_CONFIG = {
  dataPath: (id) => `${OJAJ_DATA_ROOT}/practice/${id}.json`,
  indexPath: OJAJ_INDEX_PATH,
  testIdPrefix: "ojaj/practice",
  competition: OJAJ_COMPETITION,
  pool: OJAJ_POOL,
  showLadder: false,
  backTo: () => "/ojaj",
  backLabel: "Powrot do OJAJ",
};

/**
 * Whether an attempt belongs to OJAJ.
 *
 * The kuratoryjny pages average, chart and rank their attempts; an OJAJ score
 * sits on a different scale, so it is filtered out of those aggregates and
 * reported in the OJAJ section instead. It still appears in the raw history,
 * where each row says which competition it came from.
 *
 * Attempts saved before OJAJ existed carry no `competition` field, so the
 * testId prefix is checked too — the same attempt round-trips through the
 * results API, which only ever spreads unknown fields through.
 */
export function isOjajAttempt(attempt) {
  return (
    attempt?.competition === OJAJ_COMPETITION ||
    Boolean(attempt?.testId?.startsWith("ojaj/"))
  );
}

function ojajStageLabel(stage) {
  return OJAJ_STAGE_LABELS[stage] || stage;
}

/**
 * A stage's display name, including the part number where the paper has one.
 *
 * A year with two papers of the same stage needs two route slugs, so those
 * carry their own `label` in the index -- "szkolny-a" has no useful name to
 * derive.
 */
export function ojajStageTitle(stage) {
  if (stage.label) return stage.label;
  const label = ojajStageLabel(stage.stage);
  return stage.part ? `${label}, czesc ${stage.part}` : label;
}
