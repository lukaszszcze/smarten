// Online tests: the app's rehearsals of OJAJ etap I, czesc II (CONTEXT.md).
//
// The real etap I, czesc II is a 45-minute online test generated for each
// student from a pool of tasks. Its pool is not published, so the app keeps a
// vault of its own online tests and draws one at random, unseen ones first.

// Extensions included so this module also loads under plain Node, which the
// test runner uses; Vite resolves either form.
import { OJAJ_COMPETITION, OJAJ_DATA_ROOT } from "./ojaj.js";
import { isAiOnlyTask, scoreTest } from "./scoring.js";
import { markWithAi } from "./aiMarking.js";
import { makeAttemptId } from "./resultsModel.js";

const ONLINE_TEST_PREFIX = "ojaj/online/";

/** The testId an online test's attempts are filed under. */
export function onlineTestId(id) {
  return `${ONLINE_TEST_PREFIX}${id}`;
}

/** Where an online test's JSON is served from. */
export function onlineTestPath(id) {
  return `${OJAJ_DATA_ROOT}/online/${id}.json`;
}

/**
 * Whether an attempt is at an online test, as opposed to an OJAJ paper or
 * exercise. Online attempts are reached only through the draw, so the history
 * does not link them.
 */
export function isOnlineAttempt(attempt) {
  return Boolean(attempt?.testId?.startsWith(ONLINE_TEST_PREFIX));
}

/** An online attempt's name in the history, e.g. "Test online 07". */
export function onlineAttemptLabel(attempt) {
  return `Test online ${attempt.testId.slice(ONLINE_TEST_PREFIX.length)}`;
}

/**
 * How many submitted attempts each test in the vault has.
 *
 * Attempts are saved only on submit, so every saved attempt counts as done; a
 * test opened and abandoned leaves nothing behind and stays unseen. Attempts
 * at a test no longer in the vault are ignored.
 *
 * @param {string[]} vaultIds the ids of the tests in the vault, e.g. ["01", "02"]
 * @param {object[]} attempts the user's attempts, of any kind
 * @returns {Object<string, number>} id -> number of attempts
 */
export function doneCounts(vaultIds, attempts) {
  const counts = Object.fromEntries(vaultIds.map((id) => [id, 0]));
  for (const a of attempts) {
    if (!isOnlineAttempt(a)) continue;
    const id = a.testId.slice(ONLINE_TEST_PREFIX.length);
    if (id in counts) counts[id] += 1;
  }
  return counts;
}

/**
 * Draw an online test: at random among the unseen ones, and once every test
 * is done, at random among those done least often.
 *
 * Both rules are one rule: pick among the tests with the fewest attempts,
 * which is zero for as long as any test is unseen.
 *
 * @param {string[]} vaultIds the ids of the tests in the vault
 * @param {object[]} attempts the user's attempts, synced first, or a test done
 *   on another device counts as unseen
 * @returns {string} the drawn test's id
 */
export function drawOnlineTest(vaultIds, attempts) {
  if (vaultIds.length === 0) throw new Error("the vault is empty");
  const counts = doneCounts(vaultIds, attempts);
  const fewest = Math.min(...Object.values(counts));
  const candidates = vaultIds.filter((id) => counts[id] === fewest);
  return candidates[Math.floor(Math.random() * candidates.length)];
}

/**
 * The test as the platform shows it: one question per screen, numbered 1-45
 * across the tasks.
 *
 * The task renderers each take a whole task, so a screen gets its task cut
 * down to the one item, with the task's id, type and instruction unchanged:
 * the instruction repeats on every screen of the task, as on the platform.
 *
 * @param {object} test an online test, as served from online/NN.json
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

/**
 * The attempt record saved for a marked online test, in the shape the paper
 * player saves, so the history and the results API take it unchanged.
 *
 * @param {object} test the online test
 * @param {object} answers the submitted answers, keyed by item id
 * @param {object} result the marked result, with no task left unmarked
 */
export function onlineAttempt(test, answers, result) {
  return {
    attemptId: makeAttemptId(),
    kind: "competition",
    competition: OJAJ_COMPETITION,
    testId: onlineTestId(test.id),
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
  };
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
