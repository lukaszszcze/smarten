export function normalizeAnswer(answer) {
  if (typeof answer !== "string") return "";
  return answer.trim().toLowerCase();
}

function matchesAnswer(userAnswer, correctAnswer) {
  const user = normalizeAnswer(userAnswer);
  if (Array.isArray(correctAnswer)) {
    return correctAnswer.some((a) => normalizeAnswer(a) === user);
  }
  return user === normalizeAnswer(correctAnswer);
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

function scoreTask(task, userAnswers) {
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
        correct: matchesAnswer(userAnswers[item.id], item.answer),
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
        correct: matchesAnswer(userAnswers[item.id], item.answer),
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
      result.earned = totalEarned;
      break;
    }

    default:
      result.earned = 0;
      result.skipped = true;
  }

  return result;
}

export function scoreTest(testData, userAnswers) {
  const taskResults = testData.tasks.map((task) => scoreTask(task, userAnswers));
  const earned = taskResults.reduce((sum, r) => sum + r.earned, 0);
  const max = taskResults.filter((r) => !r.skipped).reduce((sum, r) => sum + r.max, 0);
  return { earned, max, percentage: max > 0 ? Math.round((earned / max) * 100) : 0, tasks: taskResults };
}
