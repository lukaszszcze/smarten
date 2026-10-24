import { applyAiResults, isAiOnlyTask, isUsableAiResult } from "./scoring.js";

/**
 * Send a submitted attempt's open tasks to /api/check and merge the marks into
 * the answer-key result.
 *
 * `unmarkedTaskIds` lists the tasks whose only marking is the AI (sentence
 * transformation, grammar gaps, writing) and that got no usable response: the
 * request failed, came back with an error status, or carried no score. Their
 * score in `result` is the placeholder 0, so a caller must neither show nor save
 * `result` while the list is non-empty. A task the answer key also marks keeps
 * its key score when its check fails, and is not listed.
 *
 * @param {object} localResult the answer-key result from scoreTest()
 * @param {object[]} aiTasks the tasks to send for AI marking
 * @param {object} answers the learner's answers, keyed by item id
 * @returns {Promise<{result: object, unmarkedTaskIds: string[]}>}
 *
 * @example
 * const { result, unmarkedTaskIds } = await markWithAi(scoreTest(data, answers), aiTasks, answers);
 * if (unmarkedTaskIds.length > 0) showRetryMessage();
 * else save(result);
 */
export async function markWithAi(localResult, aiTasks, answers) {
  const responses = await Promise.allSettled(
    aiTasks.map((task) =>
      fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: task.type, task, answers }),
      }).then((r) => (r.ok ? r.json() : null))
    )
  );

  const aiByTaskId = new Map();
  aiTasks.forEach((task, i) => {
    const response = responses[i];
    if (response.status === "fulfilled" && isUsableAiResult(response.value)) {
      aiByTaskId.set(task.id, response.value);
    }
  });

  const unmarkedTaskIds = aiTasks
    .filter((task) => isAiOnlyTask(task) && !aiByTaskId.has(task.id))
    .map((task) => task.id);

  return { result: applyAiResults(localResult, aiByTaskId), unmarkedTaskIds };
}
