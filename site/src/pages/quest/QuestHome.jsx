import { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import { useUser } from "../../App";
import { useDocumentHead } from "../../hooks";
import {
  loadProgress, saveProgress, fetchRemoteProgress, pushRemoteProgress,
  mergeProgress, recentActivity,
} from "../../lib/questProgress";
import {
  LEVEL_NAMES, MIN_LEVEL, MAX_LEVEL, pickExercise, trackCounts, trackCeiling,
} from "../../lib/questLevels";

// The quest home screen: one card per track, each showing where she is and one
// button that starts the next thing.
//
// There are no locked levels. The old screen had fifteen of them and her history
// shows what that produced: stuck three exercises from the end of one branch,
// replaying the same one seven times to earn the stars to move, and never once
// opening the other two branches.

export default function QuestHome() {
  const user = useUser();
  const [index, setIndex] = useState(null);
  const [progress, setProgress] = useState(null);

  useDocumentHead("SmartEn Quest", "English practice pitched where you are");

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

  useEffect(() => {
    if (!user) return;
    const local = loadProgress(user.name);
    setProgress(local);

    fetchRemoteProgress(user.name).then((remote) => {
      const merged = mergeProgress(local, remote);
      setProgress(merged);
      saveProgress(user.name, merged);
      pushRemoteProgress(user.name, merged).then((fromServer) => {
        if (fromServer) {
          setProgress(fromServer);
          saveProgress(user.name, fromServer);
        }
      });
    });
  }, [user]);

  // Picked once per visit rather than per render, so the button does not point
  // somewhere new every time the page re-draws.
  const picks = useMemo(() => {
    if (!index || !progress) return {};
    const out = {};
    for (const track of index.tracks) {
      const t = progress.tracks[track.id];
      out[track.id] = pickExercise(index.pool, track.id, t.level, t.seen);
    }
    return out;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [index, progress?.placement?.date, Object.keys(progress?.tracks || {}).length]);

  if (!index || !progress) {
    return <div style={styles.page}><p style={{ color: "#5a5e72" }}>Loading...</p></div>;
  }

  if (!progress.placement) {
    return (
      <div style={styles.page}>
        <Fonts />
        <div style={styles.header}>
          <h1 style={styles.title}>SmartEn Quest</h1>
        </div>
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>First, where to start you</h2>
          <p style={styles.lead}>
            A short test works out your level in four separate things, so reading
            can be hard while spelling stays gentle. It takes about fifteen
            minutes and the score is not kept.
          </p>
          <Link to="/quest/placement" style={styles.primaryBtn}>Take the test</Link>
        </div>
      </div>
    );
  }

  const activity = recentActivity(progress, 7);

  return (
    <div style={styles.page}>
      <Fonts />

      <div style={styles.header}>
        <h1 style={styles.title}>SmartEn Quest</h1>
        <p style={styles.subtitle}>
          {activity.exercises === 0
            ? "Pick anything below and see how it goes."
            : `${activity.exercises} exercise${activity.exercises === 1 ? "" : "s"} in the last week, on ${activity.days} day${activity.days === 1 ? "" : "s"}.`}
        </p>
      </div>

      <div style={styles.tracks}>
        {index.tracks.map((track) => {
          const state = progress.tracks[track.id];
          const counts = trackCounts(index.pool, track.id, state.level, state.seen);
          const pick = picks[track.id];
          return (
            <div key={track.id} style={{ ...styles.card, borderTopColor: track.colour }}>
              <div style={styles.cardHead}>
                <h2 style={{ ...styles.trackName, color: track.colour }}>{track.name}</h2>
                <span style={styles.levelPill}>Level {state.level}</span>
              </div>
              <p style={styles.blurb}>{track.blurb}</p>

              <Ladder
                level={state.level}
                ceiling={trackCeiling(index.pool, track.id)}
                colour={track.colour}
              />
              <p style={styles.levelName}>{LEVEL_NAMES[state.level]}</p>

              {pick ? (
                <>
                  <Link to={`/quest/${track.id}/${pick.id}`} style={styles.startBtn}>
                    {state.seen[pick.id] ? "Practise again" : "Start"}
                  </Link>
                  <p style={styles.nextTitle}>{pick.title}</p>
                </>
              ) : (
                <p style={styles.nextTitle}>Nothing here yet.</p>
              )}

              <p style={styles.counts}>
                {counts.done} of {counts.total} done at this level
              </p>
            </div>
          );
        })}
      </div>

      <div style={styles.footer}>
        <Link to="/quest/placement" style={styles.footerLink}>Take the placement test again</Link>
      </div>
    </div>
  );
}

/** The six levels as a row of blocks, so a level is a position rather than a
 *  number she has to hold in her head. */
function Ladder({ level, ceiling, colour }) {
  const rungs = [];
  for (let i = MIN_LEVEL; i <= MAX_LEVEL; i++) {
    // A level this track has no exercises at is drawn hollow, so the ladder does
    // not promise a step that is not there.
    const beyondContent = i > ceiling;
    rungs.push(
      <div
        key={i}
        style={{
          flex: 1,
          height: 8,
          borderRadius: 4,
          border: beyondContent ? "1px dashed #d1d5db" : "none",
          background: beyondContent ? "transparent"
            : i < level ? `${colour}66` : i === level ? colour : "#e5e7eb",
        }}
      />
    );
  }
  return <div style={{ display: "flex", gap: 4, margin: "14px 0 6px" }}>{rungs}</div>;
}

function Fonts() {
  return (
    <link
      href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Fredoka:wght@400;500;600;700&display=swap"
      rel="stylesheet"
    />
  );
}

const styles = {
  page: {
    maxWidth: 900,
    margin: "0 auto",
    padding: "20px 20px 60px",
    fontFamily: "'DM Sans', sans-serif",
  },
  header: { marginBottom: 24 },
  title: {
    fontFamily: "'Fredoka', sans-serif",
    fontSize: 30,
    fontWeight: 700,
    color: "#1a1a2e",
    marginBottom: 4,
  },
  subtitle: { fontSize: 15, color: "#6b7280" },
  panel: {
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    borderRadius: 16,
    padding: "28px 32px",
  },
  panelTitle: {
    fontFamily: "'Fredoka', sans-serif",
    fontSize: 22,
    fontWeight: 700,
    color: "#1a1a2e",
    marginBottom: 12,
  },
  lead: { fontSize: 16, lineHeight: 1.7, color: "#374151", marginBottom: 20 },
  tracks: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
    gap: 16,
  },
  card: {
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    borderTop: "4px solid",
    borderRadius: 14,
    padding: "20px 22px",
    display: "flex",
    flexDirection: "column",
  },
  cardHead: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "baseline",
    gap: 8,
  },
  trackName: {
    fontFamily: "'Fredoka', sans-serif",
    fontSize: 19,
    fontWeight: 700,
    margin: 0,
  },
  levelPill: {
    background: "#f3f4f6",
    borderRadius: 20,
    padding: "3px 12px",
    fontSize: 13,
    fontWeight: 700,
    color: "#374151",
    whiteSpace: "nowrap",
  },
  blurb: { fontSize: 14, color: "#6b7280", marginTop: 6, lineHeight: 1.5 },
  levelName: { fontSize: 13, color: "#6b7280", marginBottom: 16 },
  startBtn: {
    display: "block",
    textAlign: "center",
    background: "linear-gradient(135deg, #22c55e, #3b82f6)",
    color: "#fff",
    border: "none",
    borderRadius: 10,
    padding: "12px 20px",
    fontSize: 15,
    fontWeight: 700,
    cursor: "pointer",
    textDecoration: "none",
    marginTop: "auto",
  },
  nextTitle: {
    fontSize: 13,
    color: "#4b5563",
    textAlign: "center",
    marginTop: 8,
    fontWeight: 600,
  },
  counts: { fontSize: 12, color: "#9ca3af", textAlign: "center", marginTop: 6 },
  footer: { marginTop: 28, textAlign: "center" },
  footerLink: { fontSize: 13, color: "#6b7280", textDecoration: "underline" },
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
    textDecoration: "none",
  },
};
