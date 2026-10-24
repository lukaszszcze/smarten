import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useUser } from "../../App";
import { useDocumentHead } from "../../hooks";
import { scoreTest } from "../../lib/scoring";
import { markWithAi } from "../../lib/aiMarking";
import {
  loadProgress, saveProgress, recordResult, pushRemoteProgress,
} from "../../lib/questProgress";
import { LEVEL_NAMES, exercisePath, pickExercise, trackCeiling } from "../../lib/questLevels";
import TaskRenderer, { AI_CHECKED_TYPES } from "../../components/konkursy/TaskRenderer";

// One quest exercise, from whichever of the three content folders it lives in.
//
// The result banner reports what the score did to her level, not a star count.
// Only a first attempt moves the level, so replaying to memorise the answers
// cannot climb the ladder — which is exactly what the old star count paid for.

export default function QuestExercise() {
  const { track, id } = useParams();
  const user = useUser();
  const [index, setIndex] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [outcome, setOutcome] = useState(null);
  const [aiChecking, setAiChecking] = useState(false);
  const [markingFailed, setMarkingFailed] = useState(false);

  useDocumentHead("Quest Exercise", "SmartEn Quest exercise");

  useEffect(() => {
    document.body.style.background = "#f8f9fc";
    return () => { document.body.style.background = "#0a0a12"; };
  }, []);

  useEffect(() => {
    fetch("/konkursy/angielski/data/quest/index.json")
      .then((r) => r.json())
      .then(setIndex)
      .catch(console.error);
  }, []);

  const entry = index?.pool?.find((e) => e.id === id);
  const trackInfo = index?.tracks?.find((t) => t.id === track);

  useEffect(() => {
    if (!entry) return;
    fetch(exercisePath(entry))
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`${r.status}`))))
      .then(setData)
      .catch((e) => setError(e.message));
  }, [entry?.id]);

  const handleChange = (itemId, value) =>
    setAnswers((prev) => ({ ...prev, [itemId]: value }));

  const finalize = (finalRes) => {
    setResult(finalRes);
    const progress = loadProgress(user?.name);
    const info = recordResult(
      progress, entry, finalRes.earned, finalRes.max, trackCeiling(index.pool, track)
    );
    saveProgress(user?.name, progress);
    setOutcome({ ...info, nextPick: pickNext(progress) });
    pushRemoteProgress(user?.name, progress).then((merged) => {
      if (merged) saveProgress(user?.name, merged);
    });
  };

  const pickNext = (progress) => {
    if (!index) return null;
    const t = progress.tracks[track];
    return pickExercise(index.pool, track, t.level, t.seen);
  };

  const handleSubmit = async () => {
    // The one-letter allowance is on here and off in the competition players:
    // this is practice, and marking a slip the same as a blank box is what
    // turned a reader who knows the word into someone scoring nothing.
    setMarkingFailed(false);
    const res = scoreTest(data, answers, { acceptNearMiss: true });

    const aiTasks = data.tasks.filter(
      (t) => AI_CHECKED_TYPES.includes(t.type) && t.items && t.items.length > 0
    );
    if (aiTasks.length === 0) return finalize(res);

    setResult(res);
    setAiChecking(true);

    const { result: finalRes, unmarkedTaskIds } = await markWithAi(res, aiTasks, answers);
    setAiChecking(false);

    // An open task the AI could not mark would be recorded as 0, so nothing is
    // recorded: the answers stay on the page and the learner can check again.
    if (unmarkedTaskIds.length > 0) {
      setResult(null);
      setMarkingFailed(true);
      return;
    }

    finalize(finalRes);
  };

  const handleRetry = () => {
    setAnswers({});
    setResult(null);
    setOutcome(null);
    window.scrollTo(0, 0);
  };

  if (error) {
    return (
      <div style={styles.page}>
        <Link to="/quest" style={styles.back}>&larr; Back to Quest</Link>
        <p style={{ color: "#b91c1c" }}>That exercise could not be loaded ({error}).</p>
      </div>
    );
  }
  if (!data || !entry) {
    return <div style={styles.page}><p style={{ color: "#5a5e72" }}>Loading...</p></div>;
  }

  const nearMisses = (result?.tasks || [])
    .flatMap((t) => t.items || [])
    .filter((i) => i.nearMiss);

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Fredoka:wght@400;500;600;700&display=swap"
        rel="stylesheet"
      />

      <Link to="/quest" style={styles.back}>&larr; Back to Quest</Link>

      {trackInfo && (
        <div style={styles.levelContext}>
          <span style={{ color: trackInfo.colour }}>{trackInfo.name}</span>
          <span style={{ color: "#9ca3af" }}>
            {" "}&middot; Level {entry.level} &middot; {LEVEL_NAMES[entry.level]}
          </span>
        </div>
      )}

      <h1 style={styles.title}>{data.title}</h1>

      {result && (
        <div
          style={{
            ...styles.resultBanner,
            borderColor: result.percentage >= 70 ? "#22c55e"
              : result.percentage >= 40 ? "#f59e0b" : "#ef4444",
          }}
        >
          <div style={styles.resultScore}>{result.earned}/{result.max}</div>
          <div style={styles.resultPercent}>{result.percentage}%</div>

          {outcome && (
            <div style={styles.verdictRow}>
              <span style={{ ...styles.verdictBadge, ...verdictStyle(outcome.verdict.move) }}>
                {outcome.verdict.text}
              </span>
              {!outcome.isFirst && outcome.improved && (
                <span style={styles.subtleNote}>Better than last time</span>
              )}
            </div>
          )}

          {nearMisses.length > 0 && (
            <p style={styles.nearMissNote}>
              {nearMisses.length === 1 ? "One word was" : `${nearMisses.length} words were`}{" "}
              a letter out — counted right, but worth another look:{" "}
              {nearMisses.map((i) => i.correctAnswer).join(", ")}
            </p>
          )}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {data.tasks.map((task) => {
          const taskRes = result?.tasks?.find((r) => r.taskId === task.id);
          return (
            <div key={task.id}>
              <div style={styles.taskHead}>
                <span style={styles.taskLabel}>Task {task.id}</span>
                <span style={styles.taskPoints}>
                  {result && taskRes ? (
                    <span style={{
                      color: taskRes.earned === taskRes.max ? "#22c55e"
                        : taskRes.earned > 0 ? "#f59e0b" : "#ef4444",
                    }}>
                      {taskRes.earned}/{taskRes.max} pts
                    </span>
                  ) : (
                    `0–${task.points} pts`
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
          {markingFailed && (
            <p style={{ color: "#b91c1c", fontSize: 14, marginBottom: 16 }}>
              The open answers could not be checked. Your answers are still here and
              nothing was saved. Press "Check answers" to try again.
            </p>
          )}
          <button onClick={handleSubmit} style={styles.submitBtn}>Check answers</button>
        </div>
      )}

      {aiChecking && (
        <div style={{ textAlign: "center", marginTop: 16 }}>
          <p style={{ color: "#7c3aed", fontSize: 14 }}>Checking with AI...</p>
        </div>
      )}

      {result && (
        <div style={styles.actions}>
          {outcome?.nextPick && (
            <Link to={`/quest/${track}/${outcome.nextPick.id}`} style={styles.submitBtn}>
              Next in {trackInfo?.name || track} &rarr;
            </Link>
          )}
          <button onClick={handleRetry} style={styles.retryBtn}>Try this one again</button>
          <Link to="/quest" style={styles.retryBtn}>Back to Quest</Link>
        </div>
      )}
    </div>
  );
}

function verdictStyle(move) {
  if (move === "up") return { background: "linear-gradient(135deg, #22c55e, #16a34a)" };
  if (move === "down") return { background: "#6b7280" };
  if (move === "top") return { background: "linear-gradient(135deg, #8b5cf6, #3b82f6)" };
  if (move === "practice") return { background: "#9ca3af" };
  return { background: "#f59e0b" };
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
  levelContext: { fontSize: 14, fontWeight: 600, marginBottom: 4 },
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
  resultPercent: { fontSize: 20, fontWeight: 700, color: "#374151" },
  verdictRow: {
    marginTop: 14,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 8,
  },
  verdictBadge: {
    display: "inline-block",
    color: "#fff",
    fontWeight: 700,
    fontSize: 15,
    padding: "8px 20px",
    borderRadius: 20,
  },
  subtleNote: { fontSize: 13, color: "#6b7280" },
  nearMissNote: {
    marginTop: 14,
    fontSize: 13,
    color: "#92400e",
    background: "#fef3c7",
    borderRadius: 8,
    padding: "10px 14px",
    lineHeight: 1.6,
  },
  taskHead: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  taskLabel: { color: "#1a1a2e", fontSize: 16, fontWeight: 700 },
  taskPoints: { color: "#6b7280", fontSize: 13, fontWeight: 600 },
  actions: {
    display: "flex",
    justifyContent: "center",
    gap: 16,
    marginTop: 32,
    flexWrap: "wrap",
  },
  submitBtn: {
    display: "inline-block",
    background: "linear-gradient(135deg, #22c55e, #3b82f6)",
    color: "#fff",
    border: "none",
    borderRadius: 10,
    padding: "14px 40px",
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
    padding: "14px 40px",
    fontSize: 16,
    fontWeight: 700,
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
    textDecoration: "none",
  },
};
