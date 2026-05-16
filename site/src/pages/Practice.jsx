import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { useDocumentHead } from "../hooks";
import { useUser } from "../App";
import StarDisplay from "../components/StarDisplay";
import TaskRenderer, { AI_CHECKED_TYPES } from "../components/konkursy/TaskRenderer";
import { scoreTest } from "../lib/scoring";
import {
  computePracticeStars,
  getPracticeTitle,
  getTypeMastery,
  loadRewards,
  migrateFromAttempts,
  updateBestScore,
} from "../lib/practiceRewards";
import { percentageToStars } from "../lib/questStars";
import { makeAttemptId, practiceAttempts } from "../lib/resultsModel";

const TYPE_COLORS = {
  knowledge_questions: "#a78bfa",
  word_spelling: "#f5a623",
  word_formation: "#e05080",
  true_false_ni: "#50d890",
  open_cloze: "#42b4f5",
  matching: "#e05080",
  gap_fill_sentences: "#50d890",
  multiple_choice: "#42b4f5",
  dialogue_choice: "#e05080",
  sentence_transformation: "#f5a623",
  grammar_gaps: "#a78bfa",
  writing: "#42b4f5",
};

const TYPE_LABELS = {
  knowledge_questions: "Wiedza o krajach",
  true_false_ni: "Prawda / Falsz / NI",
  gap_fill_sentences: "Luki w zdaniach",
  multiple_choice: "Wybor A/B/C",
  open_cloze: "Uzupelnianie luk",
  word_spelling: "Literowanie",
  word_formation: "Slowotworstwo",
  matching: "Dopasowywanie",
  dialogue_choice: "Dialogi",
  sentence_transformation: "Transformacje zdan",
  grammar_gaps: "Luki gramatyczne",
  writing: "Wypowiedz pisemna",
};

const TYPE_DESCRIPTIONS = {
  knowledge_questions: "Pytania wielokrotnego wyboru o krajach anglojezycznych",
  word_spelling: "Uzupelnij brakujace slowo na podstawie kontekstu i podanych liter",
  word_formation: "Przeksztalc wyraz w odpowiednia forme gramatyczna",
  true_false_ni: "Przeczytaj tekst i zdecyduj: prawda, falsz lub brak informacji",
  open_cloze: "Uzupelnij luki w tekscie jednym slowem",
  matching: "Dopasuj elementy do odpowiednich kategorii",
  multiple_choice: "Wybierz poprawna odpowiedz A, B lub C",
  dialogue_choice: "Uzupelnij wypowiedzi idiomami i wyrazeniami",
  gap_fill_sentences: "Dopasuj zdania do luk w tekscie",
  sentence_transformation: "Przeksztalc zdania uzywajac podanego slowa kluczowego",
  grammar_gaps: "Uzupelnij luki odpowiednia forma gramatyczna",
  writing: "Napisz e-mail lub wypowiedz na zadany temat",
};

function getResultAccent(percentage) {
  if (percentage >= 70) return "#50d890";
  if (percentage >= 40) return "#f5a623";
  return "#e05050";
}

function useExercises() {
  const [exercises, setExercises] = useState(null);
  useEffect(() => {
    fetch("/konkursy/angielski/data/practice/index.json")
      .then((r) => r.json())
      .then(setExercises)
      .catch(console.error);
  }, []);
  return exercises;
}

function useStats() {
  const user = useUser();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const [stats, setStats] = useState({});
  useEffect(() => {
    const byExercise = {};
    for (const a of practiceAttempts(storageKey)) {
      const id = a.exerciseId;
      if (!id) continue;
      if (!byExercise[id]) byExercise[id] = [];
      byExercise[id].push(a);
    }
    setStats(byExercise);
  }, [storageKey]);
  return stats;
}

function useBestScores() {
  const user = useUser();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const [bestScores, setBestScores] = useState({});
  useEffect(() => {
    setBestScores(loadRewards(storageKey));
  }, [storageKey]);
  return bestScores;
}

const MASTERY_COLORS = {
  1: "#7a7a90",
  2: "#42b4f5",
  3: "#50d890",
  4: "#f5a623",
  5: "#a78bfa",
};

function PracticeList() {
  useDocumentHead("Cwiczenia", "Cwiczenia do konkursu angielskiego");
  const exercises = useExercises();
  const stats = useStats();
  const bestScores = useBestScores();
  const exerciseList = exercises?.exercises || [];

  const groups = {};
  if (exercises) {
    for (const ex of exercises.exercises) {
      if (!groups[ex.taskType]) groups[ex.taskType] = [];
      groups[ex.taskType].push(ex);
    }
  }

  function typeStats(items) {
    let completed = 0, totalPct = 0;
    for (const ex of items) {
      const attempts = stats[ex.id];
      if (attempts && attempts.length > 0) {
        completed++;
        const best = Math.max(...attempts.map((a) => a.percentage));
        totalPct += best;
      }
    }
    return { completed, total: items.length, avgBest: completed > 0 ? Math.round(totalPct / completed) : null };
  }

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
        rel="stylesheet"
      />
      <Link to="/" style={styles.back}>&larr; Powrot do strony glownej</Link>
      <h1 style={styles.title}>Cwiczenia</h1>
      <p style={styles.subtitle}>Wybierz typ zadania, ktory chcesz cwiczc.</p>

      {!exercises && <p style={{ color: "#7a7a90" }}>Ladowanie...</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {Object.entries(groups).map(([type, items]) => {
          const color = TYPE_COLORS[type] || "#f5a623";
          const ts = typeStats(items);
          const mastery = exerciseList.length > 0
            ? getTypeMastery(bestScores, exerciseList, type)
            : null;
          return (
            <Link
              key={type}
              to={`/cwiczenia/${type}`}
              style={{ ...styles.card, textDecoration: "none", color: "inherit" }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = color + "66"; e.currentTarget.style.transform = "translateY(-2px)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = "#1e1e2e"; e.currentTarget.style.transform = "translateY(0)"; }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                    <span style={{ color, fontSize: 17, fontWeight: 700 }}>
                      {TYPE_LABELS[type] || type}
                    </span>
                    {mastery && mastery.level > 0 && (
                      <span style={{
                        fontSize: 11,
                        fontWeight: 700,
                        color: MASTERY_COLORS[mastery.level] || "#7a7a90",
                        background: (MASTERY_COLORS[mastery.level] || "#7a7a90") + "18",
                        border: `1px solid ${(MASTERY_COLORS[mastery.level] || "#7a7a90")}35`,
                        borderRadius: 999,
                        padding: "2px 8px",
                      }}>
                        {mastery.label}
                      </span>
                    )}
                  </div>
                  <div style={{ color: "#7a7a90", fontSize: 13 }}>
                    {TYPE_DESCRIPTIONS[type] || ""}
                  </div>
                </div>
                <div style={{ textAlign: "right", marginLeft: 16, whiteSpace: "nowrap" }}>
                  {mastery && (mastery.earned > 0 || ts.completed > 0) ? (
                    <>
                      <div style={{ fontSize: 14, fontWeight: 700, color: mastery.earned > 0 ? "#f5a623" : "#5a5a6a" }}>
                        ★ {mastery.earned}/{mastery.max}
                      </div>
                      <div style={{ fontSize: 12, color: "#7a7a90" }}>
                        {ts.completed}/{ts.total} ukonczone
                      </div>
                    </>
                  ) : mastery && mastery.max > 0 ? (
                    <div style={{ fontSize: 14, fontWeight: 700, color: "#5a5a6a" }}>
                      ★ 0/{mastery.max}
                    </div>
                  ) : (
                    <span style={{ color: "#5a5a6a", fontSize: 13 }}>
                      {items.length} cwiczen &rarr;
                    </span>
                  )}
                </div>
              </div>
              {ts.completed > 0 && (
                <div style={{ marginTop: 8, height: 4, borderRadius: 2, background: "#1e1e2e", overflow: "hidden" }}>
                  <div style={{
                    height: "100%", borderRadius: 2,
                    width: `${(ts.completed / ts.total) * 100}%`,
                    background: color,
                    transition: "width 0.3s",
                  }} />
                </div>
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function PracticeTypeList() {
  const { type } = useParams();
  const label = TYPE_LABELS[type] || type;
  const color = TYPE_COLORS[type] || "#f5a623";
  useDocumentHead(label, `Cwiczenia: ${label}`);
  const exercises = useExercises();
  const stats = useStats();
  const bestScores = useBestScores();
  const exerciseList = exercises?.exercises || [];

  const items = exerciseList.filter((ex) => ex.taskType === type);
  const mastery = exerciseList.length > 0
    ? getTypeMastery(bestScores, exerciseList, type)
    : null;

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
        rel="stylesheet"
      />
      <Link to="/cwiczenia" style={styles.back}>&larr; Powrot do cwiczen</Link>
      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <h1 style={{ ...styles.title, color, marginBottom: 0 }}>{label}</h1>
        {mastery && mastery.level > 0 && (
          <span style={{
            fontSize: 13,
            fontWeight: 700,
            color: MASTERY_COLORS[mastery.level] || "#7a7a90",
            background: (MASTERY_COLORS[mastery.level] || "#7a7a90") + "18",
            border: `1px solid ${(MASTERY_COLORS[mastery.level] || "#7a7a90")}35`,
            borderRadius: 999,
            padding: "4px 12px",
          }}>
            {mastery.label}
          </span>
        )}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 4, marginBottom: 24 }}>
        <span style={styles.subtitle}>{TYPE_DESCRIPTIONS[type] || ""}</span>
        {mastery && mastery.max > 0 && (
          <span style={{ color: "#f5a623", fontSize: 14, fontWeight: 700, whiteSpace: "nowrap" }}>
            ★ {mastery.earned}/{mastery.max}
          </span>
        )}
      </div>

      {!exercises && <p style={{ color: "#7a7a90" }}>Ladowanie...</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {items.map((ex) => {
          const attempts = stats[ex.id] || [];
          const bestPct = bestScores[ex.id];
          const stars = bestPct !== undefined ? percentageToStars(bestPct) : -1;
          const bestScore = attempts.length > 0 ? attempts.reduce((b, a) => a.percentage > b.percentage ? a : b).score : null;
          const bestMax = attempts.length > 0 ? attempts.reduce((b, a) => a.percentage > b.percentage ? a : b).maxScore : null;
          return (
            <Link
              key={ex.id}
              to={`/cwiczenia/${type}/${ex.id}`}
              style={{ ...styles.card, textDecoration: "none", color: "inherit" }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = color + "66"; e.currentTarget.style.transform = "translateY(-2px)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = "#1e1e2e"; e.currentTarget.style.transform = "translateY(0)"; }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ color: "#e8e8f0", fontSize: 15, fontWeight: 600 }}>
                      {ex.title}
                    </span>
                    {stars >= 0 && (
                      <StarDisplay count={stars} size={14} color="#f5a623" letterSpacing={1} />
                    )}
                  </div>
                  {attempts.length > 0 && (
                    <div style={{ color: "#5a5a6a", fontSize: 12, marginTop: 2 }}>
                      {attempts.length === 1 ? "1 podejscie" : `${attempts.length} podejsc`}
                    </div>
                  )}
                </div>
                <div style={{ textAlign: "right", marginLeft: 12 }}>
                  {bestScore !== null ? (
                    <span style={{
                      fontSize: 14, fontWeight: 700,
                      color: bestPct >= 70 ? "#50d890" : bestPct >= 40 ? "#f5a623" : "#e05050",
                    }}>
                      {bestScore}/{bestMax}
                    </span>
                  ) : (
                    <span style={{ color: "#7a7a90", fontSize: 14 }}>{ex.points} pkt</span>
                  )}
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function PracticeExercise() {
  const { type, id } = useParams();
  const user = useUser();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const exerciseIndex = useExercises();
  const [data, setData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [rewardInfo, setRewardInfo] = useState(null);
  const [aiChecking, setAiChecking] = useState(false);

  useDocumentHead("Cwiczenie", "Cwiczenie do konkursu angielskiego");

  useEffect(() => {
    fetch(`/konkursy/angielski/data/practice/${id}.json`)
      .then((r) => r.json())
      .then(setData)
      .catch(console.error);
  }, [id]);

  const handleChange = (itemId, value) => {
    setAnswers((prev) => ({ ...prev, [itemId]: value }));
  };

  const saveResult = (res) => {
    const attemptStars = percentageToStars(res.percentage);
    let rewardSummary = {
      attemptStars,
      starsEarned: 0,
      masteryUp: null,
      titleUp: null,
    };

    const entry = {
      attemptId: makeAttemptId(),
      kind: "practice",
      testId: `practice/${id}`,
      exerciseId: id,
      exerciseType: type,
      date: new Date().toISOString(),
      score: res.earned,
      maxScore: res.max,
      percentage: res.percentage,
      answers,
      taskBreakdown: res.tasks.map((t) => ({
        taskId: t.taskId,
        type: t.type,
        earned: t.earned,
        max: t.max,
        skipped: t.skipped,
      })),
    };

    try {
      const stored = JSON.parse(localStorage.getItem(storageKey) || "{}");
      const attempts = Array.isArray(stored.attempts) ? stored.attempts : [];
      const previousBestScores = stored.rewards?.bestScores
        ? { ...stored.rewards.bestScores }
        : migrateFromAttempts(attempts);

      stored.attempts = [...attempts, entry];
      stored.rewards = {
        ...(stored.rewards || {}),
        bestScores: { ...previousBestScores },
      };

      const bestUpdate = updateBestScore(stored, id, res.percentage);
      const totalStarsBefore = computePracticeStars(previousBestScores);
      const totalStarsAfter = computePracticeStars(stored.rewards.bestScores);
      const previousTitle = getPracticeTitle(totalStarsBefore);
      const nextTitle = getPracticeTitle(totalStarsAfter);
      const exerciseList = exerciseIndex?.exercises || [];
      const previousMastery = exerciseList.length > 0
        ? getTypeMastery(previousBestScores, exerciseList, type)
        : null;
      const nextMastery = exerciseList.length > 0
        ? getTypeMastery(stored.rewards.bestScores, exerciseList, type)
        : null;

      rewardSummary = {
        attemptStars,
        starsEarned: Math.max(0, bestUpdate.newStars - bestUpdate.prevStars),
        masteryUp: previousMastery && nextMastery && nextMastery.level > previousMastery.level ? nextMastery : null,
        titleUp: nextTitle.title !== previousTitle.title ? nextTitle : null,
      };

      localStorage.setItem(storageKey, JSON.stringify(stored));
    } catch (e) {
      console.error("Failed to save results:", e);
    }

    fetch("/api/results", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user: user?.name, ...entry }),
    }).catch(() => {});

    return rewardSummary;
  };

  const handleSubmit = async () => {
    setRewardInfo(null);
    const res = scoreTest(data, answers);

    const aiTasks = data.tasks.filter(
      (t) => AI_CHECKED_TYPES.includes(t.type) && t.items && t.items.length > 0
    );

    if (aiTasks.length === 0) {
      setResult(res);
      setRewardInfo(saveResult(res));
      return;
    }

    setResult(res);
    setAiChecking(true);

    const aiResults = await Promise.allSettled(
      aiTasks.map((task) =>
        fetch("/api/check", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ type: task.type, task, answers }),
        }).then((r) => r.ok ? r.json() : null)
      )
    );

    let updatedTasks = [...res.tasks];
    aiTasks.forEach((task, i) => {
      const aiRes = aiResults[i].status === "fulfilled" ? aiResults[i].value : null;
      if (!aiRes) return;
      const idx = updatedTasks.findIndex((t) => t.taskId === task.id);
      if (idx === -1) return;
      updatedTasks[idx] = {
        ...updatedTasks[idx],
        earned: aiRes.earned,
        max: aiRes.max,
        skipped: false,
        items: aiRes.items,
      };
    });

    const earned = updatedTasks.reduce((sum, r) => sum + r.earned, 0);
    const max = updatedTasks.filter((r) => !r.skipped).reduce((sum, r) => sum + r.max, 0);
    const finalRes = {
      earned,
      max,
      percentage: max > 0 ? Math.round((earned / max) * 100) : 0,
      tasks: updatedTasks,
    };

    setResult(finalRes);
    setAiChecking(false);
    setRewardInfo(saveResult(finalRes));
  };

  if (!data) {
    return (
      <div style={styles.page}>
        <p style={{ color: "#7a7a90" }}>Ladowanie...</p>
      </div>
    );
  }

  const backTo = type ? `/cwiczenia/${type}` : "/cwiczenia";

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
        rel="stylesheet"
      />

      <Link to={backTo} style={styles.back}>&larr; Powrot do listy</Link>
      <h1 style={styles.title}>{data.title}</h1>

      {result && (
        <div style={{
          ...styles.resultBanner,
          borderColor: getResultAccent(result.percentage),
        }}>
          <div style={{ fontSize: 36, fontWeight: 900, color: "#e8e8f0", fontFamily: "'Playfair Display', serif" }}>
            {result.earned}/{result.max}
          </div>
          <div style={{ fontSize: 20, fontWeight: 700, color: "#c8c8d8" }}>{result.percentage}%</div>

          {!aiChecking && rewardInfo && (
            <div style={styles.rewardSummary}>
              <div style={styles.rewardRow}>
                <StarDisplay count={rewardInfo.attemptStars} size={24} color="#f5a623" />
                <span style={styles.rewardText}>{rewardInfo.attemptStars}/5 gwiazdek za te probe</span>
                {rewardInfo.starsEarned > 0 && (
                  <span style={styles.rewardBadge}>+{rewardInfo.starsEarned}★</span>
                )}
              </div>

              {rewardInfo.masteryUp && (
                <div style={styles.rewardNotice}>
                  Nowy poziom: {rewardInfo.masteryUp.label} w {TYPE_LABELS[type] || type}!
                </div>
              )}

              {rewardInfo.titleUp && (
                <div style={styles.rewardNotice}>
                  Nowy tytul Practice: {rewardInfo.titleUp.title}!
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {data.tasks.map((task) => {
          const taskRes = result?.tasks?.find((r) => r.taskId === task.id);
          return (
            <div key={task.id}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <span style={{ color: "#e8e8f0", fontSize: 16, fontWeight: 700 }}>Zadanie {task.id}</span>
                <span style={{ color: "#7a7a90", fontSize: 13, fontWeight: 600 }}>
                  {result && taskRes ? (
                    <span style={{ color: taskRes.earned === taskRes.max ? "#50d890" : taskRes.earned > 0 ? "#f5a623" : "#e05050" }}>
                      {taskRes.earned}/{taskRes.max} pkt
                    </span>
                  ) : (
                    `0\u2013${task.points} pkt`
                  )}
                </span>
              </div>
              <TaskRenderer
                task={task}
                answers={answers}
                onChange={handleChange}
                showResults={!!result}
                taskResult={taskRes}
              />
            </div>
          );
        })}
      </div>

      {!result && (
        <div style={{ textAlign: "center", marginTop: 32 }}>
          <button onClick={handleSubmit} style={styles.submitBtn}>Sprawdz odpowiedzi</button>
        </div>
      )}

      {aiChecking && (
        <div style={{ textAlign: "center", marginTop: 16 }}>
          <p style={{ color: "#a78bfa", fontSize: 14 }}>Sprawdzanie przez AI...</p>
        </div>
      )}

      {result && (
        <div style={{ display: "flex", justifyContent: "center", gap: 16, marginTop: 32 }}>
          <button
            onClick={() => { setAnswers({}); setResult(null); setRewardInfo(null); window.scrollTo(0, 0); }}
            style={{ ...styles.submitBtn, background: "#2a2a3a", color: "#e8e8f0" }}
          >
            Sprobuj ponownie
          </button>
          <Link to={backTo} style={styles.submitBtn}>Powrot do listy</Link>
        </div>
      )}
    </div>
  );
}

export { PracticeList, PracticeTypeList, PracticeExercise };

const styles = {
  page: {
    maxWidth: 800,
    margin: "0 auto",
    padding: "20px 20px 60px",
    fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
  },
  back: {
    color: "#7a7a90",
    textDecoration: "none",
    fontSize: 14,
    display: "inline-block",
    marginBottom: 16,
  },
  title: {
    fontFamily: "'Playfair Display', Georgia, serif",
    fontSize: 28,
    fontWeight: 900,
    color: "#e8e8f0",
    marginBottom: 8,
  },
  subtitle: { color: "#7a7a90", fontSize: 15, marginBottom: 24 },
  card: {
    display: "block",
    background: "#13131a",
    border: "1px solid #1e1e2e",
    borderRadius: 12,
    padding: "16px 20px",
    transition: "border-color 0.2s, transform 0.2s",
  },
  submitBtn: {
    display: "inline-block",
    background: "linear-gradient(135deg, #50d890, #42b4f5)",
    color: "#0d0d14",
    border: "none",
    borderRadius: 10,
    padding: "14px 48px",
    fontSize: 16,
    fontWeight: 700,
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
    textDecoration: "none",
  },
  resultBanner: {
    background: "#13131a",
    border: "2px solid",
    borderRadius: 16,
    padding: "24px",
    textAlign: "center",
    marginBottom: 32,
  },
  rewardSummary: {
    marginTop: 16,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 10,
  },
  rewardRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    flexWrap: "wrap",
  },
  rewardText: {
    color: "#c8c8d8",
    fontSize: 13,
    fontWeight: 700,
  },
  rewardBadge: {
    background: "rgba(245, 166, 35, 0.14)",
    border: "1px solid rgba(245, 166, 35, 0.35)",
    borderRadius: 999,
    color: "#f5a623",
    fontSize: 13,
    fontWeight: 800,
    padding: "6px 12px",
  },
  rewardNotice: {
    background: "#161622",
    border: "1px solid #2b2b3d",
    borderRadius: 999,
    color: "#e8e8f0",
    fontSize: 13,
    fontWeight: 700,
    padding: "6px 12px",
  },
};
