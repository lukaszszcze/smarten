import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../../App";
import { useDocumentHead } from "../../hooks";
import { scoreTest } from "../../lib/scoring";
import {
  loadProgress, saveProgress, applyPlacement, pushRemoteProgress,
} from "../../lib/questProgress";
import { LEVEL_NAMES, TRACK_IDS, trackCeiling } from "../../lib/questLevels";
import TaskRenderer from "../../components/konkursy/TaskRenderer";

// The placement test: eight short probes, two per track, at levels 3 and 5.
//
// One probe per screen and no marking until the very end. A test that marks as
// it goes is a test that can tell an eleven-year-old she has got four things
// wrong before she is halfway, which is the mood this whole section is trying
// to get out of.

const TRACK_NAMES = {
  reading: "Reading",
  vocabulary: "Vocabulary",
  grammar: "Grammar",
  spelling: "Spelling and word building",
};

export default function QuestPlacement() {
  const user = useUser();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [pool, setPool] = useState(null);
  const [step, setStep] = useState(-1); // -1 = the intro screen
  const [answers, setAnswers] = useState({});
  const [levels, setLevels] = useState(null);

  useDocumentHead("Where shall we start?", "A short test to find your starting level");

  useEffect(() => {
    document.body.style.background = "#f8f9fc";
    return () => { document.body.style.background = "#0a0a12"; };
  }, []);

  useEffect(() => {
    fetch("/konkursy/angielski/data/quest/placement.json")
      .then((r) => r.json())
      .then(setData)
      .catch(console.error);
    fetch("/konkursy/angielski/data/quest/index.json")
      .then((r) => r.json())
      .then((idx) => setPool(idx.pool))
      .catch(console.error);
  }, []);

  const tasks = data?.tasks || [];
  const task = step >= 0 && step < tasks.length ? tasks[step] : null;

  const handleChange = (itemId, value) =>
    setAnswers((prev) => ({ ...prev, [itemId]: value }));

  // How many of this probe's items have an answer, so the button can say
  // whether she has left anything blank without making it a rule.
  const answeredHere = useMemo(() => {
    if (!task) return 0;
    return (task.items || []).filter((it) => {
      const a = answers[it.id];
      return Array.isArray(a) ? a.length > 0 : a !== undefined && a !== "";
    }).length;
  }, [task, answers]);

  const finish = () => {
    // Each probe is marked on its own so the two scores per track can be read
    // separately; a single total would not say where in the track she sits.
    const probeScores = {};
    for (const t of tasks) {
      const res = scoreTest({ tasks: [t] }, answers, { acceptNearMiss: true });
      probeScores[t.id] = res.percentage;
    }
    // Not every track reaches level 6, so a probe cleared at the top still only
    // places her as high as that track has exercises.
    const ceilings = Object.fromEntries(
      TRACK_IDS.map((id) => [id, pool ? trackCeiling(pool, id) : 6])
    );
    const progress = loadProgress(user?.name);
    const placed = applyPlacement(progress, probeScores, ceilings);
    saveProgress(user?.name, progress);
    pushRemoteProgress(user?.name, progress).then((merged) => {
      if (merged) saveProgress(user?.name, merged);
    });
    setLevels(placed);
    setStep(tasks.length);
    window.scrollTo(0, 0);
  };

  const advance = () => {
    if (step + 1 >= tasks.length) return finish();
    setStep(step + 1);
    window.scrollTo(0, 0);
  };

  if (!data || !pool) {
    return <div style={styles.page}><p style={{ color: "#5a5e72" }}>Loading...</p></div>;
  }

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Fredoka:wght@400;500;600;700&display=swap"
        rel="stylesheet"
      />

      {step === -1 && (
        <div style={styles.panel}>
          <h1 style={styles.title}>Where shall we start?</h1>
          <p style={styles.lead}>
            Eight short bits, about fifteen minutes. They get harder as they go,
            and they are meant to: the last ones are competition questions and
            nobody is expected to get them all.
          </p>
          <p style={styles.lead}>
            Nothing is marked until the very end, and the score is not kept. All
            this does is work out where to start you in each of the four things
            below, so you never get handed something years too easy or too hard.
          </p>
          <ul style={styles.trackList}>
            {Object.entries(TRACK_NAMES).map(([id, name]) => (
              <li key={id} style={styles.trackItem}>{name}</li>
            ))}
          </ul>
          <button onClick={() => setStep(0)} style={styles.primaryBtn}>Start</button>
        </div>
      )}

      {task && (
        <>
          <div style={styles.progressRow}>
            <span style={styles.progressLabel}>
              {TRACK_NAMES[task.track]} &middot; {step + 1} of {tasks.length}
            </span>
            <div style={styles.progressBarOuter}>
              <div style={{ ...styles.progressBarInner, width: `${(step / tasks.length) * 100}%` }} />
            </div>
          </div>

          <TaskRenderer
            task={task}
            answers={answers}
            onChange={handleChange}
            showResults={false}
          />

          <div style={styles.actions}>
            <button onClick={advance} style={styles.primaryBtn}>
              {step + 1 >= tasks.length ? "Finish" : "Next"}
            </button>
            <p style={styles.skipNote}>
              {answeredHere === 0
                ? "Not sure? Leave it blank and carry on — that tells us something too."
                : `${answeredHere} of ${(task.items || []).length} answered`}
            </p>
          </div>
        </>
      )}

      {levels && (
        <div style={styles.panel}>
          <h1 style={styles.title}>Here is where you start</h1>
          <p style={styles.lead}>
            Each of these moves on its own. Do well and it goes up; find something
            too hard and it comes back down. You do not have to finish one before
            starting another.
          </p>
          <div style={styles.levelGrid}>
            {Object.entries(TRACK_NAMES).map(([id, name]) => (
              <div key={id} style={styles.levelRow}>
                <span style={styles.levelTrack}>{name}</span>
                <span style={styles.levelValue}>
                  Level {levels[id]}
                  <span style={styles.levelName}> &middot; {LEVEL_NAMES[levels[id]]}</span>
                </span>
              </div>
            ))}
          </div>
          <button onClick={() => navigate("/quest")} style={styles.primaryBtn}>
            Let's go
          </button>
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
  panel: {
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    borderRadius: 16,
    padding: "28px 32px",
  },
  title: {
    fontFamily: "'Fredoka', sans-serif",
    fontSize: 28,
    fontWeight: 700,
    color: "#1a1a2e",
    marginBottom: 16,
  },
  lead: {
    fontSize: 16,
    lineHeight: 1.7,
    color: "#374151",
    marginBottom: 16,
  },
  trackList: {
    listStyle: "none",
    padding: 0,
    margin: "0 0 24px",
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
  },
  trackItem: {
    background: "#f3f4f6",
    borderRadius: 20,
    padding: "6px 14px",
    fontSize: 14,
    fontWeight: 600,
    color: "#374151",
  },
  progressRow: { marginBottom: 16 },
  progressLabel: {
    fontSize: 14,
    fontWeight: 700,
    color: "#4b5563",
    display: "block",
    marginBottom: 6,
  },
  progressBarOuter: {
    height: 6,
    background: "#e5e7eb",
    borderRadius: 3,
    overflow: "hidden",
  },
  progressBarInner: {
    height: "100%",
    background: "linear-gradient(90deg, #22c55e, #3b82f6)",
    borderRadius: 3,
    transition: "width 200ms",
  },
  actions: { textAlign: "center", marginTop: 28 },
  skipNote: { fontSize: 13, color: "#6b7280", marginTop: 12 },
  levelGrid: { marginBottom: 24 },
  levelRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "baseline",
    padding: "12px 0",
    borderBottom: "1px solid #f3f4f6",
    gap: 12,
    flexWrap: "wrap",
  },
  levelTrack: { fontSize: 15, fontWeight: 600, color: "#374151" },
  levelValue: {
    fontSize: 16,
    fontWeight: 800,
    color: "#1a1a2e",
    fontFamily: "'Fredoka', sans-serif",
  },
  levelName: { fontSize: 13, fontWeight: 500, color: "#6b7280" },
  primaryBtn: {
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
};
