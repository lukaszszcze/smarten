export function normalizeAnswer(answer) {
  if (typeof answer !== "string") return "";
  return answer.trim().toLowerCase();
}

// The shortest word a one-letter slip is still recognisable in. Below this,
// "cat" and "cut" are one letter apart and both are words, so a near miss there
// is a wrong answer rather than a slip.
const NEAR_MISS_MIN_LENGTH = 5;

/**
 * One edit apart, counting a swap of two neighbouring letters as one edit.
 * Catches the slips a confident reader makes when writing a word down for the
 * first time: a doubled letter (freezeing), a dropped one (thundr), a swapped
 * pair (recieve).
 */
export function isNearMiss(user, correct) {
  if (correct.length < NEAR_MISS_MIN_LENGTH) return false;
  if (Math.abs(user.length - correct.length) > 1) return false;
  if (user[0] !== correct[0]) return false;
  if (user === correct) return false;

  // Damerau-Levenshtein, stopping as soon as a second edit is needed.
  const n = user.length, m = correct.length;
  let prev2 = null, prev = new Array(m + 1).fill(0).map((_, j) => j);
  for (let i = 1; i <= n; i++) {
    const row = new Array(m + 1);
    row[0] = i;
    for (let j = 1; j <= m; j++) {
      const cost = user[i - 1] === correct[j - 1] ? 0 : 1;
      row[j] = Math.min(row[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost);
      if (i > 1 && j > 1 && user[i - 1] === correct[j - 2] && user[i - 2] === correct[j - 1]) {
        row[j] = Math.min(row[j], prev2[j - 2] + 1);
      }
    }
    if (Math.min(...row) > 1) return false;
    prev2 = prev;
    prev = row;
  }
  return prev[m] === 1;
}

/**
 * Does the answer count?
 *
 * `nearMiss` accepts a one-letter slip on a typed word. It is on for quest
 * practice and off for the competition test players, which have to mark the way
 * the real paper does. Marking a slip identically to a blank box is what turned
 * a reader who knows the word into someone scoring nothing.
 */
function matchesAnswer(userAnswer, correctAnswer, nearMiss = false) {
  const user = normalizeAnswer(userAnswer);
  if (!user) return false;
  const accepted = (Array.isArray(correctAnswer) ? correctAnswer : [correctAnswer])
    .map(normalizeAnswer);
  if (accepted.includes(user)) return true;
  return nearMiss && accepted.some((a) => isNearMiss(user, a));
}

/** True when the answer only got through on the one-letter allowance, so the
 *  renderer can show the right spelling alongside the tick. */
function wasNearMiss(userAnswer, correctAnswer, nearMiss) {
  if (!nearMiss) return false;
  const user = normalizeAnswer(userAnswer);
  if (!user) return false;
  const accepted = (Array.isArray(correctAnswer) ? correctAnswer : [correctAnswer])
    .map(normalizeAnswer);
  return !accepted.includes(user) && accepted.some((a) => isNearMiss(user, a));
}

function countCorrect(items, userAnswers) {
  return items.filter((item) => matchesAnswer(userAnswers[item.id], item.answer)).length;
}

function applyScoringScheme(correct, scheme) {
  for (const [range, pts] of Object.entries(scheme)) {
    if (range.includes("-")) {
      const [lo, hi] = range.split("-").map(Number);
      const min = Math.min(lo, hi);
      const max = Math.max(lo, hi);
      if (correct >= min && correct <= max) return pts;
    } else if (Number(range) === correct) {
      return pts;
    }
  }
  return 0;
}

// Types that have NO local scoring at all — they must be graded by the AI
// endpoint and score 0 locally until it responds.
//
// open_cloze and word_formation are deliberately NOT here: they score locally
// by exact match against the answer key (see their switch cases below), so a
// fully-correct attempt still scores even if the AI endpoint is unavailable.
// The AI grading layer (see the players) runs on top and can only raise the
// score by accepting synonyms / spelling variants beyond the key.
const AI_CHECKED_TYPES = ["sentence_transformation", "grammar_gaps", "writing"];

function scoreTask(task, userAnswers, options = {}) {
  // Only typed-word answers get the one-letter allowance. A multiple choice or a
  // matching answer is picked from a list, so there is no slip to forgive.
  // `task.exactSpelling` opts an exercise out: where the whole lesson is one
  // letter -- a doubled consonant, a silent letter -- forgiving that letter
  // leaves nothing to practise.
  const nearMiss = !!options.acceptNearMiss && !task.exactSpelling &&
    ["word_spelling", "word_formation", "open_cloze"].includes(task.type);
  const isAIType = AI_CHECKED_TYPES.includes(task.type);
  const hasItems = task.items && task.items.length > 0;

  // AI tasks with items: not skipped, but scored 0 locally (AI will grade them)
  if (isAIType && hasItems) {
    return { taskId: task.id, type: task.type, earned: 0, max: task.points, skipped: false, items: [] };
  }

  if (task.skipped || (isAIType && !hasItems)) {
    return { taskId: task.id, type: task.type, earned: 0, max: task.points, skipped: true, items: [] };
  }

  const result = { taskId: task.id, type: task.type, max: task.points, items: [], skipped: false };

  switch (task.type) {
    case "true_false_ni":
    case "gap_fill_sentences":
    case "multiple_choice":
    case "dialogue_choice":
    case "matching":
    case "word_spelling":
    case "word_formation": {
      const items = task.items || [];
      // Multi-answer matching (e.g. 3 options per category)
      const isMultiAnswer = items.length > 0 && Array.isArray(items[0].answers);
      if (isMultiAnswer) {
        let totalCorrect = 0;
        const itemResults = items.map((item) => {
          const userAns = userAnswers[item.id] || [];
          const correctAns = item.answers || [];
          const userSet = new Set(Array.isArray(userAns) ? userAns.map(normalizeAnswer) : []);
          const correctSet = new Set(correctAns.map(normalizeAnswer));
          const matchCount = [...correctSet].filter((a) => userSet.has(a)).length;
          totalCorrect += matchCount;
          return {
            id: item.id,
            correct: matchCount === correctSet.size,
            userAnswer: Array.isArray(userAns) ? userAns.join(", ") : userAns,
            correctAnswer: correctAns.join(", "),
          };
        });
        result.items = itemResults;
        result.earned = task.scoringScheme
          ? applyScoringScheme(totalCorrect, task.scoringScheme)
          : totalCorrect;
        break;
      }
      const itemResults = items.map((item) => ({
        id: item.id,
        correct: matchesAnswer(userAnswers[item.id], item.answer, nearMiss),
        nearMiss: wasNearMiss(userAnswers[item.id], item.answer, nearMiss),
        userAnswer: userAnswers[item.id] || "",
        correctAnswer: Array.isArray(item.answer) ? item.answer[0] : item.answer,
      }));
      result.items = itemResults;
      const correct = itemResults.filter((r) => r.correct).length;

      if (task.scoringScheme) {
        result.earned = applyScoringScheme(correct, task.scoringScheme);
      } else {
        result.earned = correct;
      }

      // Handle T/F/NI tasks with vocab sub-items
      if (task.vocabItems) {
        const vocabResults = task.vocabItems.map((item) => ({
          id: item.id,
          correct: matchesAnswer(userAnswers[item.id], item.answer),
          userAnswer: userAnswers[item.id] || "",
          correctAnswer: Array.isArray(item.answer) ? item.answer[0] : item.answer,
        }));
        result.items = [...result.items, ...vocabResults];
        const vocabCorrect = vocabResults.filter((r) => r.correct).length;
        // T/F/NI scored via scheme + vocab scored 1pt each
        result.earned += vocabCorrect;
      }

      // Handle open question (skipped in auto-check)
      if (task.openQuestion) {
        result.items.push({
          id: task.openQuestion.id,
          correct: false,
          userAnswer: userAnswers[task.openQuestion.id] || "",
          correctAnswer: task.openQuestion.modelAnswer,
          skipped: true,
        });
      }
      break;
    }

    case "open_cloze": {
      const items = task.items || [];
      const itemResults = items.map((item) => ({
        id: item.id,
        correct: matchesAnswer(userAnswers[item.id], item.answer, nearMiss),
        nearMiss: wasNearMiss(userAnswers[item.id], item.answer, nearMiss),
        userAnswer: userAnswers[item.id] || "",
        correctAnswer: Array.isArray(item.answer) ? item.answer[0] : item.answer,
      }));
      result.items = itemResults;
      const correct = itemResults.filter((r) => r.correct).length;
      result.earned = task.scoringScheme
        ? applyScoringScheme(correct, task.scoringScheme)
        : correct;
      break;
    }

    case "matching_columns": {
      const items = task.items || [];
      const itemResults = items.map((item) => {
        const userAns = userAnswers[item.id] || [];
        const correctAns = item.answers || [];
        const userSet = new Set(Array.isArray(userAns) ? userAns.map(normalizeAnswer) : []);
        const correctSet = new Set(correctAns.map(normalizeAnswer));
        const allCorrect = correctSet.size === userSet.size && [...correctSet].every((a) => userSet.has(a));
        return {
          id: item.id,
          correct: allCorrect,
          userAnswer: Array.isArray(userAns) ? userAns.join(", ") : userAns,
          correctAnswer: correctAns.join(", "),
        };
      });
      result.items = itemResults;
      result.earned = itemResults.filter((r) => r.correct).length;
      break;
    }

    case "knowledge_questions": {
      const items = task.items || [];
      let totalEarned = 0;
      const itemResults = items.map((item) => {
        const isCorrect = matchesAnswer(userAnswers[item.id], item.answer);
        let secondCorrect = false;
        if (item.secondAnswer) {
          secondCorrect = matchesAnswer(userAnswers[item.id + "_b"], item.secondAnswer);
        }
        const pts = item.points || 1;
        let earned = 0;
        if (item.secondAnswer) {
          // Two-part question: 1pt each
          earned = (isCorrect ? 1 : 0) + (secondCorrect ? 1 : 0);
        } else if (pts === 2 && item.answer.length >= 2) {
          // Two answers needed (e.g. two states)
          const userParts = (userAnswers[item.id] || "").split(/[,;]+/).map((s) => s.trim().toLowerCase());
          earned = item.answer.filter((a) => userParts.includes(normalizeAnswer(a))).length;
          earned = Math.min(earned, pts);
        } else {
          earned = isCorrect ? pts : 0;
        }
        totalEarned += earned;
        return {
          id: item.id,
          correct: earned === pts,
          userAnswer: userAnswers[item.id] || "",
          correctAnswer: Array.isArray(item.answer) ? item.answer[0] : item.answer,
          earned,
          max: pts,
        };
      });
      result.items = itemResults;
      // Never award more than the task is worth: a few competition papers carry
      // more 1-point items than the task's stated maximum.
      result.earned = Math.min(totalEarned, result.max);
      break;
    }

    default:
      result.earned = 0;
      result.skipped = true;
  }

  return result;
}

/**
 * Mark a whole paper.
 *
 * `options.acceptNearMiss` forgives a one-letter slip on a typed word. The quest
 * players pass it; the competition players do not, because a practice test has
 * to mark the way the real paper marks.
 */
export function scoreTest(testData, userAnswers, options = {}) {
  const taskResults = testData.tasks.map((task) => scoreTask(task, userAnswers, options));
  return totalise(taskResults);
}

function totalise(taskResults) {
  const earned = taskResults.reduce((sum, r) => sum + r.earned, 0);
  const max = taskResults.filter((r) => !r.skipped).reduce((sum, r) => sum + r.max, 0);
  return { earned, max, percentage: max > 0 ? Math.round((earned / max) * 100) : 0, tasks: taskResults };
}

// The /api/check grading layer runs on top of this local answer-key marking and
// may only ever raise a score: it sees the passage as well as the answers, so it
// can accept a synonym or spelling variant the key does not list. A dropped
// item, a truncated response or a model slip must never take back a point the
// answer key itself awarded — a learner who sees five correct answers marked
// zero stops trusting the marking, and stops finishing the exercise.
//
// Taking the higher of the two totals is exact here, not merely cautious: for
// the locally-marked types (open_cloze, word_formation) check.js pre-accepts
// every exact key match itself and only sends the rest to the model, so its
// correct set always contains the local one; for the types with no local
// marking at all the local total is 0.
export function mergeAiTaskResult(localResult, aiResult) {
  if (!aiResult) return localResult;

  // A response we cannot read a score out of is treated as no response.
  const aiEarned = aiResult.earned;
  if (typeof aiEarned !== "number" || !Number.isFinite(aiEarned)) return localResult;
  const aiMax = typeof aiResult.max === "number" && Number.isFinite(aiResult.max)
    ? aiResult.max
    : localResult.max;

  const aiItems = aiResult.items || [];
  const aiById = new Map(aiItems.map((it) => [it.id, it]));
  const localIds = new Set((localResult.items || []).map((it) => it.id));

  const items = (localResult.items || []).map((local) => {
    const ai = aiById.get(local.id);
    // Keeping the local item when the model disagrees drops an explanation that
    // would contradict the tick beside it.
    if (!ai || (local.correct && !ai.correct)) return local;
    return { ...ai, correct: local.correct || !!ai.correct };
  });
  // Types with no local marking (writing) carry their items only on the response.
  items.push(...aiItems.filter((it) => !localIds.has(it.id)));

  return {
    ...localResult,
    earned: Math.max(localResult.earned, aiEarned),
    max: aiMax,
    skipped: false,
    items,
  };
}

// Merge every graded task back into an attempt and recompute its total.
// `aiByTaskId` maps task id -> the /api/check response, or nothing for the
// tasks that were never sent or whose request failed.
export function applyAiResults(testResult, aiByTaskId) {
  return totalise(
    testResult.tasks.map((t) => mergeAiTaskResult(t, aiByTaskId.get(t.taskId) || null))
  );
}
