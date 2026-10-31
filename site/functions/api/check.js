// POST /api/check — AI-grade a task
// body: { type, task, answers }
// Returns: { items: [{ id, earned, max, feedback }], earned, max }

const HAIKU = "claude-haiku-4-5-20251001";
const SONNET = "claude-sonnet-4-6";

export async function onRequestPost(context) {
  const apiKey = context.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return Response.json({ error: "API key not configured" }, { status: 500 });
  }

  // Reject oversized payloads (100 KB limit)
  const contentLength = parseInt(context.request.headers.get("content-length") || "0", 10);
  if (contentLength > 100_000) {
    return Response.json({ error: "payload too large" }, { status: 413 });
  }

  try {
    const { type, task, answers } = await context.request.json();

    if (typeof type !== "string" || typeof task !== "object" || !task || typeof answers !== "object" || !answers) {
      return Response.json({ error: "type (string), task (object), and answers (object) required" }, { status: 400 });
    }

    if (type === "sentence_transformation") {
      return Response.json(await gradeSentenceTransformation(apiKey, task, answers));
    } else if (type === "grammar_gaps") {
      return Response.json(await gradeGrammarGaps(apiKey, task, answers));
    } else if (type === "open_cloze") {
      return Response.json(await gradeOpenCloze(apiKey, task, answers));
    } else if (type === "word_formation") {
      return Response.json(await gradeWordFormation(apiKey, task, answers));
    } else if (type === "knowledge_questions") {
      return Response.json(await gradeKnowledgeQuestions(apiKey, task, answers));
    } else if (type === "writing") {
      const prompt = buildWritingPrompt(task, answers);
      const result = await callClaude(apiKey, SONNET, prompt);
      return Response.json(result);
    } else {
      return Response.json({ error: `Unsupported type: ${type}` }, { status: 400 });
    }
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
}

// ---------- Normalization & pre-check helpers ----------

function normalize(s) {
  return String(s || "").trim().toLowerCase().replace(/\s+/g, " ");
}

// Canonical form of a grammar-gap answer: strip " (...)" parentheticals.
// "had ('d) already started" -> "had already started"
// "did not (didn't) own"      -> "did not own"
function canonicalGapAnswer(ans) {
  return String(ans || "")
    .replace(/\s*\([^)]*\)/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function countGaps(context) {
  const m = String(context || "").match(/_{2,}/g);
  return m ? m.length : 1;
}

// Several accepted phrasings may be stored as a list, or as one string joined
// with " / " (the OJAJ papers and the online vault). Everything downstream
// wants either all of them or one readable line.
function acceptedAnswers(ans) {
  return (Array.isArray(ans) ? ans : [ans])
    .flatMap((a) => String(a || "").split(" / "))
    .map((a) => a.trim())
    .filter(Boolean);
}

function answerText(ans) {
  return acceptedAnswers(ans).join(" / ");
}

function keywordUsed(studentAnswer, keyword) {
  if (!keyword) return true;
  const esc = (w) => String(w).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  // A contracted keyword still counts as used — the papers' own answer keys
  // list "needn't have bought" beside "need not have bought" for keyword NEED.
  // Whole word, or the word carrying an "n't"; NOT covers the "n't" itself.
  const forms = [`\\b${esc(keyword)}\\b`, `\\b${esc(keyword)}n['’]t\\b`];
  if (/^not$/i.test(keyword)) forms.push(`\\w+n['’]t\\b`);
  const text = String(studentAnswer || "");
  return forms.some((f) => new RegExp(f, "i").test(text));
}

// ---------- Sentence transformation ----------

async function gradeSentenceTransformation(apiKey, task, answers) {
  const items = task.items || [];
  const results = new Array(items.length);
  const toAI = [];

  items.forEach((item, idx) => {
    const student = answers[item.id] || "";
    const studentNorm = normalize(student);
    const accepted = acceptedAnswers(item.answer);

    if (!keywordUsed(student, item.keyword)) {
      console.log(`[check] ${task.id || "?"} ${item.id} pre-checked-wrong (keyword missing)`);
      results[idx] = {
        id: item.id,
        earned: 0,
        max: 1,
        correct: false,
        feedback: `Keyword "${item.keyword}" not used.`,
        correctAnswer: answerText(item.answer),
      };
      return;
    }

    // Any of the accepted phrasings scores without an AI call. Comparing the
    // list as one value never matched, so every such item went to the AI.
    if (studentNorm && accepted.some((a) => normalize(a) === studentNorm)) {
      console.log(`[check] ${task.id || "?"} ${item.id} pre-checked-correct`);
      results[idx] = {
        id: item.id,
        earned: 1,
        max: 1,
        correct: true,
        feedback: "Poprawna odpowiedź.",
        correctAnswer: answerText(item.answer),
      };
      return;
    }

    console.log(`[check] ${task.id || "?"} ${item.id} sent-to-ai`);
    toAI.push({ idx, item });
  });

  if (toAI.length > 0) {
    const prompt = buildSentenceTransformationPrompt(task, answers, toAI.map((x) => x.item));
    const aiResult = await callClaude(apiKey, SONNET, prompt);
    const aiById = new Map((aiResult.items || []).map((it) => [it.id, it]));
    for (const { idx, item } of toAI) {
      const ai = aiById.get(item.id);
      if (ai) {
        results[idx] = {
          id: item.id,
          earned: ai.earned ?? 0,
          max: 1,
          correct: ai.correct ?? (ai.earned === 1),
          feedback: ai.feedback || "",
          correctAnswer: ai.correctAnswer || answerText(item.answer),
        };
      } else {
        results[idx] = {
          id: item.id,
          earned: 0,
          max: 1,
          correct: false,
          feedback: "grading error",
          correctAnswer: answerText(item.answer),
        };
      }
    }
  }

  const earned = results.reduce((s, r) => s + (r.earned || 0), 0);
  const max = results.reduce((s, r) => s + (r.max || 0), 0);
  return { items: results, earned, max };
}

function buildSentenceTransformationPrompt(task, answers, itemsToGrade) {
  const items = itemsToGrade.map((item) => ({
    id: item.id,
    original: item.original,
    keyword: item.keyword,
    gappedSentence: item.transformed,
    expectedAnswers: acceptedAnswers(item.answer),
    studentAnswer: answers[item.id] || "",
  }));

  return `You are grading an English sentence transformation exercise for a Polish middle school competition.

Each item has:
- An original sentence
- A keyword (must be used, unchanged)
- A gapped sentence to complete
- The expected answers (every phrasing the answer key accepts — other phrasings that preserve meaning are also acceptable)
- The student's answer

Grade each item: 1 point if correct, 0 if wrong. The student's answer is correct if ALL of these hold:
1. The keyword appears in the completed sentence (case-insensitive, as a whole word, no form changes). A contraction of the keyword counts as using it: "needn't" uses NEED, "shouldn't" uses SHOULD, and "hadn't" uses NOT.
2. The completed sentence has the same meaning as the original
3. It is grammatically correct
4. It fits naturally in the gap

Evaluate each criterion independently before deciding. Be lenient with minor spelling errors if the grammar structure is clearly correct. Accept alternative phrasings that preserve meaning.

Items to grade:
${JSON.stringify(items, null, 2)}

Respond with ONLY this JSON (no other text):
{
  "items": [
    { "id": "...", "earned": 0 or 1, "max": 1, "correct": true/false, "feedback": "brief explanation in Polish", "correctAnswer": "expected answer" }
  ]
}`;
}

// ---------- Grammar gaps ----------

async function gradeGrammarGaps(apiKey, task, answers) {
  const items = task.items || [];
  const results = new Array(items.length);
  const toAI = [];

  items.forEach((item, idx) => {
    const expected = Array.isArray(item.answer) ? item.answer : [item.answer];
    const nGaps = expected.length || countGaps(item.context);

    // Gather student answers per gap, with fallback to item.id for single-gap items.
    const studentPerGap = [];
    let allMatch = true;
    for (let i = 0; i < nGaps; i++) {
      const key = nGaps === 1 && answers[item.id] !== undefined ? item.id : `${item.id}_${i}`;
      const student = answers[key] !== undefined ? answers[key] : answers[item.id] || "";
      studentPerGap.push(student);
      const canonical = normalize(canonicalGapAnswer(expected[i]));
      if (!canonical || normalize(student) !== canonical) {
        allMatch = false;
      }
    }

    if (allMatch) {
      console.log(`[check] ${task.id || "?"} ${item.id} pre-checked-correct (${nGaps} gaps)`);
      results[idx] = {
        id: item.id,
        earned: nGaps,
        max: nGaps,
        correct: true,
        feedback: "Poprawna odpowiedź.",
        correctAnswer: expected.join("; "),
      };
    } else {
      console.log(`[check] ${task.id || "?"} ${item.id} sent-to-ai (${nGaps} gaps)`);
      toAI.push({ idx, item, nGaps });
    }
  });

  if (toAI.length > 0) {
    const prompt = buildGrammarGapsPrompt(task, answers, toAI.map((x) => x.item));
    const aiResult = await callClaude(apiKey, SONNET, prompt);
    const aiById = new Map((aiResult.items || []).map((it) => [it.id, it]));
    for (const { idx, item, nGaps } of toAI) {
      const ai = aiById.get(item.id);
      const expected = Array.isArray(item.answer) ? item.answer : [item.answer];
      if (ai) {
        results[idx] = {
          id: item.id,
          earned: Math.max(0, Math.min(nGaps, ai.earned ?? 0)),
          max: nGaps,
          correct: ai.correct ?? (ai.earned === nGaps),
          feedback: ai.feedback || "",
          correctAnswer: ai.correctAnswer || expected.join("; "),
        };
      } else {
        results[idx] = {
          id: item.id,
          earned: 0,
          max: nGaps,
          correct: false,
          feedback: "grading error",
          correctAnswer: expected.join("; "),
        };
      }
    }
  }

  const earned = results.reduce((s, r) => s + (r.earned || 0), 0);
  const max = results.reduce((s, r) => s + (r.max || 0), 0);
  return { items: results, earned, max };
}

function buildGrammarGapsPrompt(task, answers, itemsToGrade) {
  const items = itemsToGrade.map((item) => {
    const studentAnswers = {};
    for (const [key, val] of Object.entries(answers)) {
      if (key === item.id || key.startsWith(item.id + "_")) {
        studentAnswers[key] = val;
      }
    }
    return {
      id: item.id,
      context: item.context,
      expectedAnswers: item.answer,
      studentAnswers,
    };
  });

  return `You are grading an English grammar exercise for a Polish middle school competition.

Each item has a sentence with gaps. The student must fill in the correct grammatical forms of words given in brackets.

Notation: accepted answers may list alternative forms in parentheses. The full form of the preceding word(s) and the contracted form in parentheses are BOTH acceptable:
- "has ('s) just passed" → accept both "has just passed" and "'s just passed"
- "had ('d) already started" → accept both "had already started" and "'d already started"
- "will ('ll) have finished" → accept both "will have finished" and "'ll have finished"
- "did not (didn't) own" → accept both "did not own" and "didn't own"
- "have ('ve) been" → accept both "have been" and "'ve been"
In general, "X (Y) Z" means the preceding word(s) may be written as either the original form or the alternative form in parentheses.

Examples:
- Expected "had ('d) already started", student wrote "'d already started" → correct (1 point)
- Expected "had ('d) already started", student wrote "had already start" → wrong (missing -ed)
- Expected "arrived", student wrote "arrive" → wrong (tense)
- Expected "arrived", student wrote "arived" → wrong (misspelled; grammar exercise requires correct spelling)

Grade each gap: 1 point if correct, 0 if wrong. Require correct spelling. A student answer is correct if it is grammatically equivalent to the expected form (including any alternative in parentheses) and correctly spelled.

Items to grade:
${JSON.stringify(items, null, 2)}

Count the total number of individual gaps across all items (one per element in expectedAnswers). Each gap is worth 1 point.

Respond with ONLY this JSON (no other text):
{
  "items": [
    { "id": "...", "earned": points_for_this_item, "max": number_of_gaps_in_item, "correct": true/false, "feedback": "brief explanation per gap, in Polish", "correctAnswer": "expected answers joined with ; " }
  ]
}`;
}

// ---------- Open cloze (single-word gap fill — synonyms accepted) ----------

function applyScoringScheme(correct, scheme) {
  if (!scheme || typeof scheme !== "object") return correct;
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

async function gradeOpenCloze(apiKey, task, answers) {
  const items = task.items || [];
  const itemResults = new Array(items.length);
  const toAI = [];

  items.forEach((item, idx) => {
    const expected = Array.isArray(item.answer) ? item.answer : [item.answer];
    const student = answers[item.id] || "";
    const studentNorm = normalize(student);
    const acceptedExact = expected.some((a) => normalize(a) === studentNorm && studentNorm !== "");

    if (acceptedExact) {
      itemResults[idx] = {
        id: item.id,
        correct: true,
        userAnswer: student,
        correctAnswer: expected[0],
      };
      return;
    }
    if (!studentNorm) {
      itemResults[idx] = {
        id: item.id,
        correct: false,
        userAnswer: "",
        correctAnswer: expected.join(" / "),
      };
      return;
    }
    toAI.push({ idx, item });
  });

  if (toAI.length > 0) {
    const prompt = buildOpenClozePrompt(task, answers, toAI.map((x) => x.item));
    const aiResult = await callClaude(apiKey, SONNET, prompt);
    const aiById = new Map((aiResult.items || []).map((it) => [it.id, it]));
    for (const { idx, item } of toAI) {
      const ai = aiById.get(item.id);
      const expected = Array.isArray(item.answer) ? item.answer : [item.answer];
      const student = answers[item.id] || "";
      if (ai) {
        itemResults[idx] = {
          id: item.id,
          correct: !!ai.correct,
          userAnswer: student,
          correctAnswer: ai.correctAnswer || expected.join(" / "),
          feedback: ai.feedback || "",
        };
      } else {
        itemResults[idx] = {
          id: item.id,
          correct: false,
          userAnswer: student,
          correctAnswer: expected.join(" / "),
          feedback: "grading error",
        };
      }
    }
  }

  const correctCount = itemResults.filter((r) => r.correct).length;
  const max = task.points || itemResults.length;
  const earned = task.scoringScheme
    ? applyScoringScheme(correctCount, task.scoringScheme)
    : Math.min(correctCount, max);

  return { items: itemResults, earned, max };
}

function buildOpenClozePrompt(task, answers, itemsToGrade) {
  const items = itemsToGrade.map((item) => ({
    id: item.id,
    expectedAnswers: Array.isArray(item.answer) ? item.answer : [item.answer],
    studentAnswer: answers[item.id] || "",
  }));

  return `You are grading an English open-cloze exercise for a Polish middle school competition. Each gap must be filled with a SINGLE English word that fits the context grammatically and semantically.

Full text with gaps (gaps appear as e.g. "1.4. _________"):
${task.text}

For each gap below you are given a list of expected answers (the official key) and the student's answer. Award 1 point if the student's answer is:
1. A single English word (no extra words), correctly spelled
2. Grammatically correct in the gap
3. Semantically appropriate in the context — i.e. it preserves the meaning of the sentence as a whole

CRITICAL: accept synonyms and equivalent words that are not in the key but would be a valid completion. For example, if the key is "loss" and the student writes "degradation" or "destruction" in a sentence about habitat, both should be accepted if they fit naturally. Be reasonably lenient on synonyms, strict on grammar and spelling.

Items to grade:
${JSON.stringify(items, null, 2)}

Respond with ONLY this JSON (no other text):
{
  "items": [
    { "id": "...", "correct": true/false, "feedback": "brief explanation in Polish — for accepted synonyms note the synonym; for wrong answers explain why briefly", "correctAnswer": "expected answer(s) joined with ' / '" }
  ]
}`;
}

// ---------- Word formation (derivation — spelling/derivation variants accepted) ----------

async function gradeWordFormation(apiKey, task, answers) {
  const items = task.items || [];
  const itemResults = new Array(items.length);
  const toAI = [];

  items.forEach((item, idx) => {
    const expected = Array.isArray(item.answer) ? item.answer : [item.answer];
    const student = answers[item.id] || "";
    const studentNorm = normalize(student);
    const acceptedExact = expected.some((a) => normalize(a) === studentNorm && studentNorm !== "");

    if (acceptedExact) {
      itemResults[idx] = {
        id: item.id,
        correct: true,
        userAnswer: student,
        correctAnswer: expected[0],
      };
      return;
    }
    if (!studentNorm) {
      itemResults[idx] = {
        id: item.id,
        correct: false,
        userAnswer: "",
        correctAnswer: expected.join(" / "),
      };
      return;
    }
    toAI.push({ idx, item });
  });

  if (toAI.length > 0) {
    const prompt = buildWordFormationPrompt(task, answers, toAI.map((x) => x.item));
    const aiResult = await callClaude(apiKey, SONNET, prompt);
    const aiById = new Map((aiResult.items || []).map((it) => [it.id, it]));
    for (const { idx, item } of toAI) {
      const ai = aiById.get(item.id);
      const expected = Array.isArray(item.answer) ? item.answer : [item.answer];
      const student = answers[item.id] || "";
      if (ai) {
        itemResults[idx] = {
          id: item.id,
          correct: !!ai.correct,
          userAnswer: student,
          correctAnswer: ai.correctAnswer || expected.join(" / "),
          feedback: ai.feedback || "",
        };
      } else {
        itemResults[idx] = {
          id: item.id,
          correct: false,
          userAnswer: student,
          correctAnswer: expected.join(" / "),
          feedback: "grading error",
        };
      }
    }
  }

  const correctCount = itemResults.filter((r) => r.correct).length;
  const max = task.points || itemResults.length;
  const earned = task.scoringScheme
    ? applyScoringScheme(correctCount, task.scoringScheme)
    : Math.min(correctCount, max);

  return { items: itemResults, earned, max };
}

function buildWordFormationPrompt(task, answers, itemsToGrade) {
  const items = itemsToGrade.map((item) => ({
    id: item.id,
    // Data uses either `baseWord` (flowing-text shape) or `wordBase` (per-sentence shape).
    baseWord: item.baseWord || item.wordBase || null,
    // Per-sentence shape carries the gap context on the item itself.
    sentence: item.sentence || undefined,
    expectedAnswer: Array.isArray(item.answer) ? item.answer : [item.answer],
    studentAnswer: answers[item.id] || "",
  }));

  return `You are grading an English word-formation exercise for a Polish middle school competition. The student must transform a given base word (in CAPITALS) into the form that fits the context grammatically and semantically.

${task.text ? `Full text with gaps (gaps appear as e.g. "1.4. _________"):\n${task.text}` : "Each item below has its own sentence with one gap."}

Word bank (the words shown to the student): ${JSON.stringify(task.wordBank || [])}

For each gap you are given the base word, the official expected answer, and the student's answer. Award 1 point if the student's answer is:
1. Derived from the given base word (different word stems are wrong)
2. Grammatically correct in the gap and semantically appropriate
3. Correctly spelled

CRITICAL: accept both British and American spelling variants (e.g. industrialisation / industrialization, organisation / organization, recognise / recognize). Accept alternative valid derivations from the same base word when they fit the context equally well (e.g. "innovation" vs "innovations" depending on number). Be strict about grammar and spelling otherwise.

Items to grade:
${JSON.stringify(items, null, 2)}

Respond with ONLY this JSON (no other text):
{
  "items": [
    { "id": "...", "correct": true/false, "feedback": "brief explanation in Polish — for accepted variants note that; for wrong answers explain why briefly", "correctAnswer": "expected answer" }
  ]
}`;
}

// ---------- Knowledge questions ----------

// Local marking, mirroring the knowledge_questions branch of src/lib/scoring.js.
// Kept in step with it deliberately: the client overwrites its own score with
// whatever this endpoint returns, so the endpoint must never mark lower.
function localKnowledgeScore(item, answers) {
  const max = item.secondAnswer ? 2 : item.points || 1;
  const expected = Array.isArray(item.answer) ? item.answer : [item.answer];
  const student = answers[item.id] || "";

  if (item.secondAnswer) {
    const expected2 = Array.isArray(item.secondAnswer) ? item.secondAnswer : [item.secondAnswer];
    const student2 = answers[item.id + "_b"] || "";
    const first = expected.some((a) => normalize(a) === normalize(student) && normalize(student) !== "");
    const second = expected2.some((a) => normalize(a) === normalize(student2) && normalize(student2) !== "");
    return { earned: (first ? 1 : 0) + (second ? 1 : 0), max };
  }

  // points === 2 with several keys means every key is required, typed as one
  // comma- or semicolon-separated answer — not a list of alternatives.
  if (max === 2 && expected.length >= 2) {
    const parts = String(student).split(/[,;]+/).map((s) => normalize(s));
    const hit = expected.filter((a) => parts.includes(normalize(a))).length;
    return { earned: Math.min(hit, max), max };
  }

  const ok = expected.some((a) => normalize(a) === normalize(student) && normalize(student) !== "");
  return { earned: ok ? max : 0, max };
}

async function gradeKnowledgeQuestions(apiKey, task, answers) {
  const items = task.items || [];
  const itemResults = new Array(items.length);
  const toAI = [];

  items.forEach((item, idx) => {
    const expected = Array.isArray(item.answer) ? item.answer : [item.answer];
    const student = answers[item.id] || "";
    const student2 = answers[item.id + "_b"] || "";
    const { earned, max } = localKnowledgeScore(item, answers);

    const base = {
      id: item.id,
      correct: earned === max,
      userAnswer: student,
      correctAnswer: expected.join(" / "),
      earned,
      max,
    };

    // Multiple-choice items are letter picks — there is nothing for the AI to
    // judge, and sending them would only invite it to second-guess the key.
    const isMultipleChoice = Array.isArray(item.options) && item.options.length > 0;
    const blank = !normalize(student) && !normalize(student2);

    if (isMultipleChoice || earned === max || blank) {
      itemResults[idx] = base;
      return;
    }
    itemResults[idx] = base;
    toAI.push({ idx, item });
  });

  if (toAI.length > 0) {
    const prompt = buildKnowledgeQuestionsPrompt(task, answers, toAI.map((x) => x.item));
    const aiResult = await callClaude(apiKey, SONNET, prompt);
    const aiById = new Map((aiResult.items || []).map((it) => [it.id, it]));
    for (const { idx, item } of toAI) {
      const ai = aiById.get(item.id);
      if (!ai) continue; // keep the local mark
      const local = itemResults[idx];
      const awarded = Math.max(0, Math.min(Number(ai.earned) || 0, local.max));
      // The AI can only raise a mark, never lower one.
      const earned = Math.max(local.earned, awarded);
      itemResults[idx] = {
        ...local,
        correct: earned === local.max,
        earned,
        feedback: ai.feedback || "",
      };
    }
  }

  const max = task.points || itemResults.reduce((sum, r) => sum + r.max, 0);
  const earned = Math.min(itemResults.reduce((sum, r) => sum + r.earned, 0), max);
  return { items: itemResults, earned, max };
}

function buildKnowledgeQuestionsPrompt(task, answers, itemsToGrade) {
  const items = itemsToGrade.map((item) => {
    const expected = Array.isArray(item.answer) ? item.answer : [item.answer];
    const out = {
      id: item.id,
      question: item.question,
      acceptedAnswers: expected,
      studentAnswer: answers[item.id] || "",
      maxPoints: item.secondAnswer ? 2 : item.points || 1,
    };
    if (item.secondAnswer) {
      out.secondPartAcceptedAnswers = Array.isArray(item.secondAnswer)
        ? item.secondAnswer
        : [item.secondAnswer];
      out.studentAnswerSecondPart = answers[item.id + "_b"] || "";
    }
    return out;
  });

  return `You are grading a general-knowledge quiz about English-speaking countries, written in English by Polish pupils aged 10-14 for a regional competition. The pupils type their answers freely, so they will almost never match the official answer key word for word.

Award points for the KNOWLEDGE shown, not for the wording. For each item you are given the question, the official accepted answer(s), the student's answer, and the maximum points.

Award full points when the student's answer means the same as an accepted answer:
1. Paraphrases and the student's own words are fine ("a cap you wear when you graduate" for an academic cap).
2. Ignore spelling, capitalisation, articles and word order, including misspelled proper nouns that are clearly recognisable ("Filadelfia" for Philadelphia, "Bill Gats" for Bill Gates).
3. Accept a Polish word for the key term only if the rest of the answer shows the pupil knows the fact.
4. Accept a shorter answer than the key when it still contains the essential fact. The key is often a long model answer; the pupil does not have to reproduce all of it.

Award ZERO when the answer names the wrong person, place, date or thing, is empty, or is too vague to show the fact was known ("a food", "some building").

Where maxPoints is 2 the question asks for two things. Award 1 point per part the student got right. Some of these have a separate second input box (shown as studentAnswerSecondPart); others expect both parts in the one answer.

Items to grade:
${JSON.stringify(items, null, 2)}

Respond with ONLY this JSON (no other text):
{
  "items": [
    { "id": "...", "earned": 0, "feedback": "brief explanation in Polish - why the answer was accepted or rejected" }
  ]
}`;
}

// ---------- Writing ----------

function buildWritingPrompt(task, answers) {
  const studentText = answers.writing || answers[task.id + "_writing"] || "";

  return `You are grading a writing task for a Polish middle school English competition.

Task instruction (in Polish):
${task.instruction}

Maximum points: ${task.points}

Student's response:
${studentText}

Grade the response using this rubric. Score each criterion separately, then sum to the total (rounded to a whole number, capped at ${task.points}):

1. Task completion — did they address all required content points? (share of total)
2. Coherence and organization
3. Vocabulary range and accuracy
4. Grammar accuracy
5. Appropriate register and format

Be fair but rigorous — this is a competition, not a classroom exercise. Deduct for missing required content points, significant grammar errors, limited vocabulary, or poor organization. If the response is empty or completely off-topic, give 0 points.

Respond with ONLY this JSON (no other text):
{
  "items": [
    {
      "id": "${task.id}",
      "earned": total_points,
      "max": ${task.points},
      "correct": false,
      "feedback": "Per-criterion feedback in Polish: 1) Task completion: X/Y — ... 2) Coherence: X/Y — ... 3) Vocabulary: X/Y — ... 4) Grammar: X/Y — ... 5) Register: X/Y — ... Total: total_points/${task.points}",
      "correctAnswer": "n/a"
    }
  ],
  "earned": total_points,
  "max": ${task.points}
}`;
}

// ---------- Claude call ----------

async function callClaude(apiKey, model, prompt) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model,
      max_tokens: 4096,
      temperature: 0,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Claude API error: ${res.status} ${err}`);
  }

  const data = await res.json();
  const text = data.content?.[0]?.text || "";
  return parseJsonFromText(text);
}

// Balanced-braces scan, falling back to greedy regex.
function parseJsonFromText(text) {
  const start = text.indexOf("{");
  if (start >= 0) {
    let depth = 0;
    let inStr = false;
    let esc = false;
    for (let i = start; i < text.length; i++) {
      const c = text[i];
      if (inStr) {
        if (esc) esc = false;
        else if (c === "\\") esc = true;
        else if (c === '"') inStr = false;
      } else {
        if (c === '"') inStr = true;
        else if (c === "{") depth++;
        else if (c === "}") {
          depth--;
          if (depth === 0) {
            try {
              return JSON.parse(text.slice(start, i + 1));
            } catch {
              break;
            }
          }
        }
      }
    }
  }
  const m = text.match(/\{[\s\S]*\}/);
  if (!m) throw new Error("No JSON in Claude response");
  return JSON.parse(m[0]);
}
