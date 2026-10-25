// Online tests: the app's rehearsals of OJAJ etap I, czesc II (CONTEXT.md).
//
// The real etap I, czesc II is a 45-minute online test generated for each
// student from a pool of tasks. Its pool is not published, so the app keeps a
// vault of its own items and puts a test together from it at each draw, aimed
// at the user's mistakes (ojajDraw.js, ojajRecord.js).

// Extensions included so this module also loads under plain Node, which the
// test runner uses; Vite resolves either form.
import { OJAJ_COMPETITION, OJAJ_DATA_ROOT } from "./ojaj.js";
import { isAiOnlyTask, scoreTest } from "./scoring.js";
import { markWithAi } from "./aiMarking.js";
import { makeAttemptId } from "./resultsModel.js";

const ONLINE_TEST_PREFIX = "ojaj/online/";

/**
 * The testId every drawn online test is saved under. The three fixed tests
 * done before tests were drawn from single items (2026-10-24) were saved under
 * their number, ojaj/online/01 to 03.
 */
export const DRAWN_TEST_ID = `${ONLINE_TEST_PREFIX}drawn`;

/** Where the vault of own items is served from. */
export const ONLINE_VAULT_PATH = `${OJAJ_DATA_ROOT}/online/vault.json`;

/**
 * Whether an attempt is at an online test, as opposed to an OJAJ paper or
 * exercise. Online attempts are reached only through the draw, so the history
 * does not link them.
 */
export function isOnlineAttempt(attempt) {
  return Boolean(attempt?.testId?.startsWith(ONLINE_TEST_PREFIX));
}

/** An online attempt's name in the history: "Test online", or "Test online 02"
 *  for one of the old fixed tests. */
export function onlineAttemptLabel(attempt) {
  if (attempt.testId === DRAWN_TEST_ID) return "Test online";
  return `Test online ${attempt.testId.slice(ONLINE_TEST_PREFIX.length)}`;
}

/**
 * The test as the platform shows it: one question per screen, numbered 1-45
 * across the tasks.
 *
 * The task renderers each take a whole task, so a screen gets its task cut
 * down to the one item, with the task's id, type and instruction unchanged:
 * the instruction repeats on every screen of the task, as on the platform.
 *
 * @param {object} test an online test, as drawTest puts it together
 * @returns {{number: number, task: object, item: object, firstOfTask: boolean}[]}
 */
export function onlineQuestions(test) {
  const out = [];
  for (const task of test.tasks) {
    task.items.forEach((item, i) => {
      out.push({
        number: out.length + 1, task: { ...task, items: [item] }, item, firstOfTask: i === 0,
      });
    });
  }
  return out;
}

/** Whether a question holds an answer, for the panel's marks. */
export function isAnswered(answers, item) {
  const value = answers[item.id];
  return typeof value === "string" && value.trim() !== "";
}

/**
 * Whole seconds left on the clock, read off the wall clock rather than
 * counted down by a timer, which a background tab slows.
 *
 * @param {number} startedAt when the test started, in ms since the epoch
 * @param {number} now the current time, in ms since the epoch
 * @param {number} minutes the test's time limit
 */
export function secondsLeft(startedAt, now, minutes) {
  return Math.max(0, Math.ceil((startedAt + minutes * 60_000 - now) / 1000));
}

/**
 * Mark a submitted online test.
 *
 * Only the tasks with no answer key of their own (the key word
 * transformations) go to /api/check. The paper player also sends word
 * formation and knowledge questions there, and the AI accepts variants the key
 * does not list; the online test is marked the way the platform marks, on the
 * key alone, and its keys were approved strict on that basis.
 *
 * @returns {Promise<{result: object, unmarkedTaskIds: string[]}>} as markWithAi;
 *   while `unmarkedTaskIds` is non-empty the result must be neither shown nor saved
 */
export function markOnlineTest(test, answers) {
  const aiTasks = test.tasks.filter(isAiOnlyTask);
  return markWithAi(scoreTest(test, answers), aiTasks, answers);
}

// Each question's verdict in a marked result, by question number.
function verdicts(result) {
  return new Map(result.tasks.flatMap((t) => t.items.map((r) => [r.id, r.correct === true])));
}

/**
 * The attempt record saved for a marked online test, in the shape the paper
 * player saves, so the history and the results API take it unchanged, plus
 * the vault item behind each question and its verdict, which the mistake
 * record is worked out from.
 *
 * @param {object} test the drawn test
 * @param {object} answers the submitted answers, keyed by question number
 * @param {object} result the marked result, with no task left unmarked
 * @throws when a question has no verdict in `result`, so a record with a
 *   hole in it is never saved
 */
export function onlineAttempt(test, answers, result) {
  const marked = verdicts(result);
  const items = test.tasks.flatMap((task) => task.items.map((item) => {
    if (!marked.has(item.id)) throw new Error(`question ${item.id} has no verdict`);
    return { number: item.id, vaultId: item.vaultId, correct: marked.get(item.id) };
  }));
  return {
    attemptId: makeAttemptId(),
    kind: "competition",
    competition: OJAJ_COMPETITION,
    testId: DRAWN_TEST_ID,
    date: new Date().toISOString(),
    score: result.earned,
    maxScore: result.max,
    percentage: result.percentage,
    answers,
    taskBreakdown: result.tasks.map((t) => ({
      taskId: t.taskId,
      type: t.type,
      earned: t.earned,
      max: t.max,
      skipped: t.skipped,
    })),
    items,
  };
}

/**
 * The score on the questions he had not seen before, the type-targeted ones
 * included; the review shows it next to the total.
 *
 * @returns {{earned: number, max: number}} one point a question
 */
export function newQuestionScore(test, result) {
  const marked = verdicts(result);
  const fresh = test.tasks.flatMap((t) => t.items).filter((item) => !item.seenBefore);
  return { earned: fresh.filter((item) => marked.get(item.id)).length, max: fresh.length };
}

/**
 * The player's state. `phase` runs intro -> running -> marking -> done, with
 * marking -> failed -> marking when the AI marking does not answer.
 */
export const initialPlayerState = {
  phase: "intro",
  current: 0,
  answers: {},
  startedAt: null,
  result: null,
};

/**
 * The rules of the player, apart from the clock and the network.
 *
 * Answers can change only while the test runs. From the submit on they are
 * locked: the time may be up, so a retry after a failed marking re-runs the
 * marking on the same answers instead of reopening the test. Every action
 * that arrives in the wrong phase returns the state unchanged, so a clock
 * that runs out during a submit cannot submit twice.
 */
export function playerReducer(state, action) {
  switch (action.type) {
    case "start":
      if (state.phase !== "intro") return state;
      return { ...state, phase: "running", startedAt: action.now };
    case "answer":
      if (state.phase !== "running") return state;
      return { ...state, answers: { ...state.answers, [action.id]: action.value } };
    case "go":
      if (state.phase !== "running") return state;
      return { ...state, current: action.index };
    case "submit":
      if (state.phase !== "running") return state;
      return { ...state, phase: "marking" };
    case "marked":
      if (state.phase !== "marking") return state;
      return { ...state, phase: "done", result: action.result };
    case "markingFailed":
      if (state.phase !== "marking") return state;
      return { ...state, phase: "failed" };
    case "retry":
      if (state.phase !== "failed") return state;
      return { ...state, phase: "marking" };
    default:
      throw new Error(`unknown player action: ${action.type}`);
  }
}
