import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { useDocumentHead } from "../hooks";
import { useUser } from "../App";
import StarDisplay from "../components/StarDisplay";
import TaskRenderer, { AI_CHECKED_TYPES } from "../components/konkursy/TaskRenderer";
import { scoreTest, applyAiResults } from "../lib/scoring";
import { percentageToStars } from "../lib/questStars";
import { makeAttemptId } from "../lib/resultsModel";

const STAGE_LABELS = { szkolny: "Etap szkolny", rejonowy: "Etap rejonowy", wojewodzki: "Etap wojewodzki" };

// The Mazowieckie kuratoryjny competition, which this player served alone until
// OJAJ was added. A second competition passes its own config; everything else
// about playing a paper is identical.
const KURATORYJNY = {
  competition: null,
  dataPath: (year, stage) => `/konkursy/angielski/data/${year}/${stage}.json`,
  testId: (year, stage) => `${year}/${stage}`,
  stageLabels: STAGE_LABELS,
  backTo: "/",
  backLabel: "Powrot do listy",
};

function getResultAccent(percentage) {
  if (percentage >= 70) return "#50d890";
  if (percentage >= 40) return "#f5a623";
  return "#e05050";
}

export default function KonkursTest({ config = KURATORYJNY }) {
  const { year, stage } = useParams();
  const stageLabels = config.stageLabels;
  const user = useUser();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const [testData, setTestData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [aiChecking, setAiChecking] = useState(false);
  const [started, setStarted] = useState(false);
  const [timeLeft, setTimeLeft] = useState(null);
  const timerRef = useRef(null);

  // A year with two papers of the same stage needs two route slugs, and
  // "szkolny-a" has no readable name to derive, so those papers name themselves.
  const stageTitle = testData?.label || stageLabels[stage] || stage;

  useDocumentHead(
    `${stageTitle} ${year}`,
    "Test konkursowy z jezyka angielskiego"
  );

  useEffect(() => {
    fetch(config.dataPath(year, stage))
      .then((r) => r.json())
      .then(setTestData)
      .catch(console.error);
  }, [year, stage, config]);

  const startTimer = useCallback(() => {
    if (!testData) return;
    const activePoints = testData.tasks.filter(t => !t.skipped).reduce((s, t) => s + t.points, 0);
    const ratio = testData.maxPoints > 0 ? activePoints / testData.maxPoints : 1;
    setTimeLeft(Math.round(testData.timeMinutes * ratio) * 60);
    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, [testData]);

  useEffect(() => {
    return () => clearInterval(timerRef.current);
  }, []);

  const handleStart = () => {
    setStarted(true);
    startTimer();
  };

  const handleChange = (itemId, value) => {
    setAnswers((prev) => ({ ...prev, [itemId]: value }));
  };

  const saveResult = (res) => {
    const entry = {
      attemptId: makeAttemptId(),
      kind: "competition",
      testId: config.testId(year, stage),
      ...(config.competition ? { competition: config.competition } : {}),
      year,
      stage,
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
      const attempts = stored.attempts || [];
      attempts.push(entry);
      stored.attempts = attempts;
      localStorage.setItem(storageKey, JSON.stringify(stored));
    } catch (e) {
      console.error("Failed to save results:", e);
    }
    fetch("/api/results", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user: user?.name, ...entry }),
    }).catch(() => {});
  };

  const handleSubmit = async () => {
    clearInterval(timerRef.current);
    const res = scoreTest(testData, answers);

    // Find AI tasks that have items
    const aiTasks = testData.tasks.filter(
      (t) => AI_CHECKED_TYPES.includes(t.type) && t.items && t.items.length > 0
    );

    if (aiTasks.length === 0) {
      setResult(res);
      saveResult(res);
      return;
    }

    // Show local results immediately, then overlay AI results
    setResult(res);
    setAiChecking(true);

    // Send AI tasks for grading in parallel
    const aiResults = await Promise.allSettled(
      aiTasks.map((task) =>
        fetch("/api/check", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ type: task.type, task, answers }),
        }).then((r) => r.ok ? r.json() : null)
      )
    );

    // Merge AI results into the score
    const aiByTaskId = new Map();
    aiTasks.forEach((task, i) => {
      const aiRes = aiResults[i].status === "fulfilled" ? aiResults[i].value : null;
      if (aiRes) aiByTaskId.set(task.id, aiRes);
    });
    const finalRes = applyAiResults(res, aiByTaskId);

    setResult(finalRes);
    setAiChecking(false);
    saveResult(finalRes);
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  if (!testData) {
    return (
      <div style={styles.page}>
        <p style={{ color: "#7a7a90" }}>Ladowanie testu...</p>
      </div>
    );
  }

  if (!started) {
    return (
      <div style={styles.page}>
        <link
          href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
          rel="stylesheet"
        />
        <Link to={config.backTo} style={styles.back}>&larr; {config.backLabel}</Link>
        <h1 style={styles.title}>{stageTitle}</h1>
        <p style={styles.subtitle}>{testData.year}</p>
        <div style={styles.infoCard}>
          <div style={styles.infoRow}><span>Czas:</span><strong>{Math.round(testData.timeMinutes * testData.tasks.filter(t => !t.skipped).reduce((s, t) => s + t.points, 0) / testData.maxPoints)} minut</strong></div>
          <div style={styles.infoRow}><span>Maks. punkty:</span><strong>{testData.tasks.filter(t => !t.skipped).reduce((s, t) => s + t.points, 0)} pkt</strong></div>
          <div style={styles.infoRow}><span>Liczba zadan:</span><strong>{testData.tasks.filter(t => !t.skipped).length}/{testData.tasks.length}</strong></div>
        </div>
        <button onClick={handleStart} style={styles.startBtn}>Rozpocznij test</button>
      </div>
    );
  }

  const resultStars = result ? percentageToStars(result.percentage) : 0;

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
        rel="stylesheet"
      />

      <div style={styles.stickyHeader}>
        <Link to={config.backTo} style={{ ...styles.back, margin: 0 }}>&larr;</Link>
        <span style={{ color: "#c8c8d8", fontWeight: 700, fontSize: 15 }}>
          {stageTitle} {testData.year}
        </span>
        {!result && timeLeft !== null && (
          <span style={{
            ...styles.timer,
            color: timeLeft < 300 ? "#e05050" : timeLeft < 600 ? "#f5a623" : "#50d890",
          }}>
            {formatTime(timeLeft)}
          </span>
        )}
        {result && (
          <span style={styles.score}>
            {result.earned}/{result.max} ({result.percentage}%)
          </span>
        )}
      </div>

      {result && (
        <div style={{
          ...styles.resultBanner,
          borderColor: getResultAccent(result.percentage),
        }}>
          <div style={styles.resultScore}>{result.earned}/{result.max}</div>
          <div style={styles.resultPct}>{result.percentage}%</div>
          {!aiChecking && (
            <div style={styles.starResult}>
              <StarDisplay count={resultStars} size={22} color="#f5a623" />
              <span style={styles.starText}>{resultStars}/5 gwiazdek za ten test</span>
            </div>
          )}
          <div style={styles.resultLabel}>
            {result.percentage >= 70 ? "Swietny wynik!" : result.percentage >= 40 ? "Niezly wynik" : "Trenuj dalej!"}
          </div>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {testData.tasks.map((task) => {
          const taskRes = result?.tasks?.find((r) => r.taskId === task.id);
          return (
            <div key={task.id}>
              <div style={styles.taskHeader}>
                <span style={styles.taskNum}>Zadanie {task.id}</span>
                <span style={styles.taskPts}>
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
          <p style={{ color: "#a78bfa", fontSize: 14 }}>Sprawdzanie zadan otwartych przez AI...</p>
        </div>
      )}

      {result && (
        <div style={{ textAlign: "center", marginTop: 32 }}>
          <Link to={config.backTo} style={styles.submitBtn}>{config.backLabel}</Link>
        </div>
      )}
    </div>
  );
}

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
    marginBottom: 4,
  },
  subtitle: { color: "#7a7a90", fontSize: 16, marginBottom: 24 },
  infoCard: {
    background: "#13131a",
    border: "1px solid #1e1e2e",
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
  },
  infoRow: {
    display: "flex",
    justifyContent: "space-between",
    padding: "8px 0",
    borderBottom: "1px solid #1e1e2e",
    color: "#c8c8d8",
    fontSize: 15,
  },
  startBtn: {
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
  stickyHeader: {
    position: "sticky",
    top: 0,
    zIndex: 100,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    background: "#0d0d14ee",
    backdropFilter: "blur(10px)",
    padding: "10px 16px",
    borderRadius: 10,
    marginBottom: 24,
    border: "1px solid #1e1e2e",
  },
  timer: { fontFamily: "monospace", fontSize: 18, fontWeight: 700 },
  score: { color: "#50d890", fontWeight: 700, fontSize: 16 },
  taskHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  taskNum: { color: "#e8e8f0", fontSize: 16, fontWeight: 700 },
  taskPts: { color: "#7a7a90", fontSize: 13, fontWeight: 600 },
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
  resultScore: {
    fontSize: 36,
    fontWeight: 900,
    color: "#e8e8f0",
    fontFamily: "'Playfair Display', serif",
  },
  resultPct: { fontSize: 20, fontWeight: 700, color: "#c8c8d8", marginBottom: 4 },
  starResult: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    flexWrap: "wrap",
    marginBottom: 8,
  },
  starText: {
    color: "#c8c8d8",
    fontSize: 13,
    fontWeight: 700,
  },
  resultLabel: { fontSize: 14, color: "#7a7a90" },
};
