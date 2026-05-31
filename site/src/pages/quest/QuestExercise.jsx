import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useUser } from "../../App";
import StarDisplay from "../../components/StarDisplay";
import { useDocumentHead } from "../../hooks";
import { scoreTest } from "../../lib/scoring";
import { loadProgress, saveProgress, processResult, getPlayerTitle, pushRemoteProgress } from "../../lib/questProgress";
import { getExerciseLevel, getNextExercise } from "../../lib/questData";
import { percentageToStars } from "../../lib/questStars";
import TaskRenderer, { AI_CHECKED_TYPES } from "../../components/konkursy/TaskRenderer";

export default function QuestExercise() {
  const { branch, id } = useParams();
  const user = useUser();
  const [data, setData] = useState(null);
  const [index, setIndex] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [starInfo, setStarInfo] = useState(null);
  const [aiChecking, setAiChecking] = useState(false);

  useDocumentHead("Quest Exercise", "SmartEn Quest exercise");

  useEffect(() => {
    document.body.style.background = "#f8f9fc";
    return () => { document.body.style.background = "#0a0a12"; };
  }, []);

  useEffect(() => {
    fetch(`/konkursy/angielski/data/quest/${id}.json`)
      .then((r) => r.json())
      .then(setData)
      .catch(console.error);
  }, [id]);

  useEffect(() => {
    fetch("/konkursy/angielski/data/quest/index.json")
      .then((r) => r.json())
      .then(setIndex)
      .catch(console.error);
  }, []);

  const handleChange = (itemId, value) => {
    setAnswers((prev) => ({ ...prev, [itemId]: value }));
  };

  const finalize = (finalRes) => {
    setResult(finalRes);
    const progress = loadProgress(user?.name);
    const info = processResult(progress, branch, id, finalRes.earned, finalRes.max);
    saveProgress(user?.name, progress);
    setStarInfo(info);

    pushRemoteProgress(user?.name, progress).then((merged) => {
      if (merged) {
        saveProgress(user?.name, merged);
      }
    });
  };

  const handleSubmit = async () => {
    const res = scoreTest(data, answers);

    const aiTasks = data.tasks.filter(
      (t) => AI_CHECKED_TYPES.includes(t.type) && t.items && t.items.length > 0
    );

    if (aiTasks.length === 0) {
      finalize(res);
      return;
    }

    // Show local results immediately, then overlay AI results
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

    setAiChecking(false);
    finalize(finalRes);
  };

  const handleRetry = () => {
    setAnswers({});
    setResult(null);
    setStarInfo(null);
    window.scrollTo(0, 0);
  };

  if (!data) {
    return <div style={styles.page}><p style={{ color: "#5a5e72" }}>Loading...</p></div>;
  }

  const branchData = index?.branches?.find((b) => b.id === branch);
  const levelNum = branchData ? getExerciseLevel(branchData, id) : null;
  const next = branchData ? getNextExercise(branchData, id) : null;

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Fredoka:wght@400;500;600;700&display=swap"
        rel="stylesheet"
      />

      <Link to="/quest" style={styles.back}>&larr; Back to Quest</Link>

      {branchData && levelNum && (
        <div style={styles.levelContext}>
          <span style={{ color: branchData.color }}>{branchData.name}</span>
          <span style={{ color: "#9ca3af" }}> — Level {levelNum}</span>
        </div>
      )}

      <h1 style={styles.title}>{data.title}</h1>

      {/* Result banner */}
      {result && (
        <div style={{
          ...styles.resultBanner,
          borderColor: result.percentage >= 70 ? "#22c55e" : result.percentage >= 40 ? "#f59e0b" : "#ef4444",
        }}>
          <div style={styles.resultScore}>{result.earned}/{result.max}</div>
          <div style={styles.resultPercent}>{result.percentage}%</div>

          {/* Stars earned */}
          {starInfo && (
            <div style={styles.starResult}>
              <div style={{ color: "#f59e0b" }}>
                <StarDisplay count={starInfo.exerciseStars} size={24} />
              </div>
              {starInfo.starsEarned > 0 && (
                <span style={styles.starBadge}>+{starInfo.starsEarned} star{starInfo.starsEarned === 1 ? "" : "s"}</span>
              )}
              {starInfo.titleUp && (
                <span style={styles.titleUpBadge}>New title: {starInfo.newTitle.title}!</span>
              )}
            </div>
          )}

          <div style={{
            ...styles.resultLabel,
            color: result.percentage >= 70 ? "#22c55e" : result.percentage >= 40 ? "#f59e0b" : "#ef4444",
          }}>
            {result.percentage >= 70 ? "Great job!" : result.percentage >= 40 ? "Good effort!" : "Keep practising!"}
          </div>
        </div>
      )}

      {/* Tasks */}
      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {data.tasks.map((task) => {
          const taskRes = result?.tasks?.find((r) => r.taskId === task.id);
          return (
            <div key={task.id}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <span style={{ color: "#1a1a2e", fontSize: 16, fontWeight: 700 }}>Task {task.id}</span>
                <span style={{ color: "#6b7280", fontSize: 13, fontWeight: 600 }}>
                  {result && taskRes ? (
                    <span style={{ color: taskRes.earned === taskRes.max ? "#22c55e" : taskRes.earned > 0 ? "#f59e0b" : "#ef4444" }}>
                      {taskRes.earned}/{taskRes.max} pts
                    </span>
                  ) : (
                    `0\u2013${task.points} pts`
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
          <button onClick={handleSubmit} style={styles.submitBtn}>Check answers</button>
        </div>
      )}

      {aiChecking && (
        <div style={{ textAlign: "center", marginTop: 16 }}>
          <p style={{ color: "#7c3aed", fontSize: 14 }}>Checking with AI...</p>
        </div>
      )}

      {result && (
        <div style={{ display: "flex", justifyContent: "center", gap: 16, marginTop: 32, flexWrap: "wrap" }}>
          <button onClick={handleRetry} style={styles.retryBtn}>Try again</button>
          {next && (
            <Link to={`/quest/${next.branchId}/${next.exerciseId}`} style={styles.submitBtn}>
              Next exercise &rarr;
            </Link>
          )}
          <Link to="/quest" style={next ? styles.retryBtn : styles.submitBtn}>Back to Quest</Link>
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
    fontFamily: "'DM Sans', sans-serif",
  },
  back: {
    color: "#6b7280",
    textDecoration: "none",
    fontSize: 14,
    display: "inline-block",
    marginBottom: 8,
  },
  levelContext: {
    fontSize: 14,
    fontWeight: 600,
    marginBottom: 4,
  },
  title: {
    fontFamily: "'Fredoka', sans-serif",
    fontSize: 26,
    fontWeight: 700,
    color: "#1a1a2e",
    marginBottom: 20,
  },
  resultBanner: {
    background: "#ffffff",
    border: "2px solid",
    borderRadius: 16,
    padding: "24px",
    textAlign: "center",
    marginBottom: 32,
  },
  resultScore: {
    fontSize: 36,
    fontWeight: 900,
    color: "#1a1a2e",
    fontFamily: "'Fredoka', sans-serif",
  },
  resultPercent: {
    fontSize: 20,
    fontWeight: 700,
    color: "#374151",
  },
  resultLabel: {
    fontSize: 16,
    fontWeight: 600,
    marginTop: 8,
  },
  starResult: {
    marginTop: 12,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 8,
  },
  starBadge: {
    display: "inline-block",
    background: "linear-gradient(135deg, #f59e0b, #f97316)",
    color: "#fff",
    fontWeight: 700,
    fontSize: 14,
    padding: "6px 16px",
    borderRadius: 20,
  },
  titleUpBadge: {
    display: "inline-block",
    background: "linear-gradient(135deg, #8b5cf6, #3b82f6)",
    color: "#fff",
    fontWeight: 700,
    fontSize: 14,
    padding: "6px 16px",
    borderRadius: 20,
  },
  submitBtn: {
    display: "inline-block",
    background: "linear-gradient(135deg, #22c55e, #3b82f6)",
    color: "#fff",
    border: "none",
    borderRadius: 10,
    padding: "14px 48px",
    fontSize: 16,
    fontWeight: 700,
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
    textDecoration: "none",
  },
  retryBtn: {
    display: "inline-block",
    background: "#e5e7eb",
    color: "#374151",
    border: "none",
    borderRadius: 10,
    padding: "14px 48px",
    fontSize: 16,
    fontWeight: 700,
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
    textDecoration: "none",
  },
};
