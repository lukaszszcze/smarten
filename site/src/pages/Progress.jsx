import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { useDocumentHead } from "../hooks";
import { useUser } from "../App";
import { loadRewards, computePracticeStars, getPracticeTitle, getTypeMastery, PRACTICE_TITLES } from "../lib/practiceRewards";
import { percentageToStars, clampPercentage } from "../lib/questStars";
import { competitionAttempts, practiceAttempts, loadAttempts } from "../lib/resultsModel";
import { syncAttempts, clearRemoteAttempts } from "../lib/resultsSync";

const STAGE_LABELS = { szkolny: "Etap szkolny", rejonowy: "Etap rejonowy", wojewodzki: "Etap wojewodzki" };
const STAGE_COLORS = { szkolny: "#50d890", rejonowy: "#42b4f5", wojewodzki: "#a78bfa" };

const TYPE_LABELS = {
  true_false_ni: "Prawda / Falsz / Brak informacji",
  gap_fill_sentences: "Wstawianie zdan w luki",
  multiple_choice: "Wybor A/B/C",
  dialogue_choice: "Dialogi A/B/C",
  open_cloze: "Uzupelnianie luk (jedno slowo)",
  word_spelling: "Literowanie wyrazow",
  word_formation: "Slowotworstwo",
  matching: "Dopasowywanie",
  matching_columns: "Laczenie kolumn",
  knowledge_questions: "Pytania z wiedzy o krajach",
  vocab_from_text: "Slownictwo z tekstu",
};

const PRACTICE_TYPE_LABELS = {
  knowledge_questions: "Wiedza o krajach",
  true_false_ni: "Prawda / Falsz / NI",
  gap_fill_sentences: "Luki w zdaniach",
  multiple_choice: "Wybor A/B/C",
  open_cloze: "Uzupelnianie luk",
  word_spelling: "Literowanie",
  word_formation: "Slowotworstwo",
  matching: "Dopasowywanie",
  dialogue_choice: "Dialogi",
};

function getSkillStats(attempts) {
  const stats = {};
  for (const attempt of attempts) {
    if (!attempt.taskBreakdown) continue;
    for (const task of attempt.taskBreakdown) {
      if (task.skipped) continue;
      if (!stats[task.type]) {
        stats[task.type] = { earned: 0, max: 0, count: 0 };
      }
      stats[task.type].earned += task.earned;
      stats[task.type].max += task.max;
      stats[task.type].count += 1;
    }
  }
  return Object.entries(stats)
    .map(([type, s]) => ({
      type,
      label: TYPE_LABELS[type] || type,
      earned: s.earned,
      max: s.max,
      pct: s.max > 0 ? Math.round((s.earned / s.max) * 100) : 0,
      count: s.count,
    }))
    .sort((a, b) => a.pct - b.pct);
}

function ScoreChart({ attempts }) {
  if (attempts.length < 2) return null;

  const W = 680, H = 200, PAD_L = 40, PAD_R = 16, PAD_T = 20, PAD_B = 32;
  const plotW = W - PAD_L - PAD_R;
  const plotH = H - PAD_T - PAD_B;

  const points = attempts.map((a, i) => ({
    x: PAD_L + (i / (attempts.length - 1)) * plotW,
    y: PAD_T + plotH - (a.percentage / 100) * plotH,
    pct: a.percentage,
    date: new Date(a.date),
    stage: a.stage || a.testId?.split("/")[1],
  }));

  const pathD = points.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ");
  const areaD = pathD + ` L${points[points.length - 1].x},${PAD_T + plotH} L${points[0].x},${PAD_T + plotH} Z`;

  const yTicks = [0, 25, 50, 75, 100];

  return (
    <div style={{ marginBottom: 32 }}>
      <h2 style={styles.sectionTitle}>Wyniki w czasie</h2>
      <div style={{ background: "#13131a", border: "1px solid #1e1e2e", borderRadius: 10, padding: "16px 8px", overflowX: "auto" }}>
        <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto", display: "block" }}>
          {yTicks.map((t) => {
            const y = PAD_T + plotH - (t / 100) * plotH;
            return (
              <g key={t}>
                <line x1={PAD_L} x2={W - PAD_R} y1={y} y2={y} stroke="#1e1e2e" strokeWidth={1} />
                <text x={PAD_L - 6} y={y + 4} textAnchor="end" fill="#5a5a6a" fontSize={10} fontFamily="DM Sans, sans-serif">{t}%</text>
              </g>
            );
          })}

          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#42b4f5" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#42b4f5" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d={areaD} fill="url(#areaGrad)" />
          <path d={pathD} fill="none" stroke="#42b4f5" strokeWidth={2} strokeLinejoin="round" />

          {points.map((p, i) => (
            <g key={i}>
              <circle cx={p.x} cy={p.y} r={4} fill={STAGE_COLORS[p.stage] || "#42b4f5"} stroke="#13131a" strokeWidth={2} />
              {(i === 0 || i === points.length - 1 || attempts.length <= 8) && (
                <text
                  x={p.x}
                  y={PAD_T + plotH + 16}
                  textAnchor="middle"
                  fill="#5a5a6a"
                  fontSize={9}
                  fontFamily="DM Sans, sans-serif"
                >
                  {p.date.toLocaleDateString("pl-PL", { day: "numeric", month: "short" })}
                </text>
              )}
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}

function StarsOverTimeChart({ practices }) {
  const sorted = [...practices]
    .filter((a) => a.exerciseId && a.date)
    .sort((a, b) => new Date(a.date) - new Date(b.date));
  const best = {};
  // Collapse to one end-of-day point: cumulative stars are monotonic, so the
  // last attempt of each calendar day carries that day's final total. Keyed by
  // local day; later writes for the same day overwrite while preserving order.
  const byDay = new Map();
  for (const a of sorted) {
    const pct = clampPercentage(a.percentage);
    const prev = best[a.exerciseId];
    if (prev === undefined || pct > prev) best[a.exerciseId] = pct;
    let stars = 0;
    for (const p of Object.values(best)) stars += percentageToStars(p);
    const d = new Date(a.date);
    const dayKey = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    byDay.set(dayKey, { date: d, stars });
  }
  const points = [...byDay.values()];
  if (points.length < 2) return null;

  const W = 680, H = 240, PAD_L = 40, PAD_R = 100, PAD_T = 20, PAD_B = 32;
  const plotW = W - PAD_L - PAD_R;
  const plotH = H - PAD_T - PAD_B;

  const maxStars = points[points.length - 1].stars;
  // Show up to the next milestone above current, so progress is visible
  const nextIdx = PRACTICE_TITLES.findIndex((t) => t.stars > maxStars);
  const ceiling = nextIdx === -1
    ? PRACTICE_TITLES[PRACTICE_TITLES.length - 1].stars
    : PRACTICE_TITLES[nextIdx].stars;
  const yMax = Math.max(ceiling, maxStars, 20);

  const t0 = points[0].date.getTime();
  const t1 = points[points.length - 1].date.getTime();
  const tSpan = t1 - t0 || 1;

  const xy = points.map((p) => ({
    x: PAD_L + ((p.date.getTime() - t0) / tSpan) * plotW,
    y: PAD_T + plotH - (p.stars / yMax) * plotH,
    stars: p.stars,
    date: p.date,
  }));

  const pathD = xy.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ");
  const areaD = pathD + ` L${xy[xy.length - 1].x},${PAD_T + plotH} L${xy[0].x},${PAD_T + plotH} Z`;

  // Hide the crowded low tiers: show only the current tier (and one below for
  // context) up to the ceiling, so labels stop overlapping at the bottom.
  let currentTierIdx = 0;
  for (let i = PRACTICE_TITLES.length - 1; i >= 0; i--) {
    if (maxStars >= PRACTICE_TITLES[i].stars) { currentTierIdx = i; break; }
  }
  const minLabelStars = PRACTICE_TITLES[Math.max(0, currentTierIdx - 1)].stars;
  const visibleMilestones = PRACTICE_TITLES.filter(
    (m) => m.stars <= yMax && m.stars >= minLabelStars
  );

  return (
    <div style={{ marginBottom: 32 }}>
      <h2 style={styles.sectionTitle}>Gwiazdki w czasie</h2>
      <div style={{ background: "#13131a", border: "1px solid #1e1e2e", borderRadius: 10, padding: "16px 8px", overflowX: "auto" }}>
        <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto", display: "block" }}>
          <defs>
            <linearGradient id="starsAreaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f5a623" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#f5a623" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Milestone horizontal lines */}
          {visibleMilestones.map((m) => {
            const y = PAD_T + plotH - (m.stars / yMax) * plotH;
            const reached = maxStars >= m.stars;
            return (
              <g key={m.title}>
                <line
                  x1={PAD_L}
                  x2={W - PAD_R}
                  y1={y}
                  y2={y}
                  stroke={reached ? "#3a2e1a" : "#1e1e2e"}
                  strokeWidth={1}
                  strokeDasharray="4 3"
                />
                <text x={PAD_L - 6} y={y + 4} textAnchor="end" fill="#5a5a6a" fontSize={10} fontFamily="DM Sans, sans-serif">
                  {m.stars}
                </text>
                <text
                  x={W - PAD_R + 6}
                  y={y + 4}
                  textAnchor="start"
                  fill={reached ? "#f5a623" : "#5a5a6a"}
                  fontSize={10}
                  fontWeight={reached ? 700 : 400}
                  fontFamily="DM Sans, sans-serif"
                >
                  {m.title}
                </text>
              </g>
            );
          })}

          {/* Stars line */}
          <path d={areaD} fill="url(#starsAreaGrad)" />
          <path d={pathD} fill="none" stroke="#f5a623" strokeWidth={2} strokeLinejoin="round" />

          {xy.map((p, i) => (
            <g key={i}>
              <circle cx={p.x} cy={p.y} r={3} fill="#f5a623" stroke="#13131a" strokeWidth={1.5} />
              {(i === 0 || i === xy.length - 1) && (
                <text
                  x={p.x}
                  y={PAD_T + plotH + 16}
                  textAnchor={i === 0 ? "start" : "end"}
                  fill="#5a5a6a"
                  fontSize={9}
                  fontFamily="DM Sans, sans-serif"
                >
                  {p.date.toLocaleDateString("pl-PL", { day: "numeric", month: "short" })}
                </text>
              )}
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}

function PracticeStarSummary({ bestScores }) {
  const totalStars = computePracticeStars(bestScores);
  if (totalStars === 0) return null;

  const info = getPracticeTitle(totalStars);
  const progressPct = info.nextStars
    ? Math.round(((totalStars - info.stars) / (info.nextStars - info.stars)) * 100)
    : 100;

  return (
    <div style={{
      background: "#13131a", border: "1px solid #1e1e2e", borderRadius: 12,
      padding: "16px 20px", marginBottom: 32,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <span style={{ color: "#e8e8f0", fontWeight: 700, fontSize: 16 }}>
          Gwiazdki z cwiczen
        </span>
        <span style={{ color: "#f5a623", fontWeight: 700, fontSize: 15 }}>
          {info.title}
        </span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <span style={{ color: "#f5a623", fontSize: 22, fontWeight: 900, fontFamily: "'Playfair Display', serif" }}>
          ★ {totalStars}
        </span>
        <span style={{ color: "#7a7a90", fontSize: 13 }}>/ 525</span>
      </div>
      <div style={{ height: 6, background: "#1e1e2e", borderRadius: 3, overflow: "hidden" }}>
        <div style={{
          height: "100%", borderRadius: 3,
          width: `${progressPct}%`,
          background: "linear-gradient(90deg, #f5a623, #f5c842)",
          transition: "width 0.5s ease",
        }} />
      </div>
      {info.nextTitle && (
        <div style={{ color: "#7a7a90", fontSize: 11, marginTop: 6 }}>
          Nastepny tytul: {info.nextTitle} ({info.nextStars}★)
        </div>
      )}
    </div>
  );
}

export default function Progress() {
  useDocumentHead("Postepy", "Twoje wyniki z testow konkursowych");
  const user = useUser();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const [competitions, setCompetitions] = useState([]);
  const [practices, setPractices] = useState([]);
  const [confirmClear, setConfirmClear] = useState(false);
  const [bestScores, setBestScores] = useState({});
  const [exerciseIndex, setExerciseIndex] = useState([]);
  const clearedRef = useRef(false);

  useEffect(() => {
    // Show local data immediately
    setCompetitions(competitionAttempts(storageKey));
    setPractices(practiceAttempts(storageKey));
    setBestScores(loadRewards(storageKey));

    // Sync with remote if logged in, then recompute
    if (user?.name) {
      clearedRef.current = false;
      syncAttempts(user.name, storageKey).then((merged) => {
        if (clearedRef.current) return; // user cleared history while sync was in flight
        setCompetitions(merged.filter((a) => a.kind === "competition"));
        setPractices(merged.filter((a) => a.kind === "practice"));
      }).catch(() => {});
    }
  }, [storageKey, user?.name]);

  useEffect(() => {
    fetch("/konkursy/angielski/data/practice/index.json")
      .then((r) => r.json())
      .then((data) => setExerciseIndex(data.exercises || []))
      .catch(() => {});
  }, []);

  const handleClear = () => {
    if (!confirmClear) {
      setConfirmClear(true);
      return;
    }
    clearedRef.current = true;
    localStorage.removeItem(storageKey);
    setCompetitions([]);
    setPractices([]);
    setBestScores({});
    setConfirmClear(false);
    // Also clear remote so sync doesn't restore on next load
    if (user?.name) {
      clearRemoteAttempts(user.name).catch(() => {});
    }
  };

  const skills = getSkillStats(competitions);
  const totalTests = competitions.length;
  const avgScore = totalTests > 0
    ? Math.round(competitions.reduce((s, a) => s + a.percentage, 0) / totalTests)
    : 0;
  const bestScore = totalTests > 0
    ? Math.max(...competitions.map((a) => a.percentage))
    : 0;
  const hasAnyData = competitions.length > 0 || practices.length > 0;

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
        rel="stylesheet"
      />

      <Link to="/" style={styles.back}>&larr; Powrot do testow</Link>
      <h1 style={styles.title}>Twoje postepy</h1>

      {!hasAnyData ? (
        <div style={styles.emptyState}>
          <p style={{ color: "#7a7a90", fontSize: 15, marginBottom: 16 }}>
            Nie masz jeszcze zadnych wynikow. Rozwiaz test, zeby zobaczyc swoje postepy!
          </p>
          <Link to="/" style={styles.startBtn}>Wybierz test</Link>
        </div>
      ) : (
        <>
          {/* Competition summary cards */}
          {totalTests > 0 && (
            <div style={styles.summaryGrid}>
              <div style={styles.summaryCard}>
                <div style={styles.summaryValue}>{totalTests}</div>
                <div style={styles.summaryLabel}>Rozwiazanych testow</div>
              </div>
              <div style={styles.summaryCard}>
                <div style={{ ...styles.summaryValue, color: "#42b4f5" }}>{avgScore}%</div>
                <div style={styles.summaryLabel}>Sredni wynik</div>
              </div>
              <div style={styles.summaryCard}>
                <div style={{ ...styles.summaryValue, color: "#50d890" }}>{bestScore}%</div>
                <div style={styles.summaryLabel}>Najlepszy wynik</div>
              </div>
            </div>
          )}

          {/* Practice stars */}
          <PracticeStarSummary bestScores={bestScores} />

          {/* Stars over time — practice only */}
          <StarsOverTimeChart practices={practices} />

          {/* Score over time chart — competition only */}
          <ScoreChart attempts={competitions} />

          {/* Skill breakdown — competition only */}
          {skills.length > 0 && (
            <div style={{ marginBottom: 32 }}>
              <h2 style={styles.sectionTitle}>Umiejetnosci (testy konkursowe)</h2>
              <p style={{ color: "#7a7a90", fontSize: 13, marginBottom: 16 }}>
                Posortowane od najslabszych — pracuj nad nimi!
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {skills
                  .map((skill) => ({
                    skill,
                    mastery: exerciseIndex.length > 0
                      ? getTypeMastery(bestScores, exerciseIndex, skill.type)
                      : null,
                  }))
                  .sort((a, b) => {
                    // Sort by exercise (practice star) results, weakest first.
                    // Types without a practice pool go last; ties fall back to competition pct.
                    const am = a.mastery && a.mastery.max > 0 ? a.mastery.earned / a.mastery.max : Infinity;
                    const bm = b.mastery && b.mastery.max > 0 ? b.mastery.earned / b.mastery.max : Infinity;
                    if (am !== bm) return am - bm;
                    return a.skill.pct - b.skill.pct;
                  })
                  .map(({ skill, mastery }) => {
                  return (
                    <div key={skill.type} style={styles.skillRow}>
                      <div style={styles.skillInfo}>
                        <span style={styles.skillLabel}>{skill.label}</span>
                        <span style={styles.skillScore}>
                          {skill.earned}/{skill.max} ({skill.pct}%)
                          {mastery && mastery.max > 0 && (
                            <span style={{ color: "#f5a623", marginLeft: 8 }}>
                              ★ {mastery.earned}/{mastery.max}
                            </span>
                          )}
                        </span>
                      </div>
                      <div style={styles.barBg}>
                        <div
                          style={{
                            ...styles.barFill,
                            width: `${skill.pct}%`,
                            background: skill.pct >= 70 ? "#50d890" : skill.pct >= 40 ? "#f5a623" : "#e05050",
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Competition history */}
          {competitions.length > 0 && (
            <>
              <h2 style={styles.sectionTitle}>Historia testow konkursowych</h2>
              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 32 }}>
                {[...competitions].reverse().map((attempt, i) => {
                  const stg = attempt.stage;
                  const yr = attempt.year;
                  const color = STAGE_COLORS[stg] || "#50d890";
                  const pctColor = attempt.percentage >= 70 ? "#50d890" : attempt.percentage >= 40 ? "#f5a623" : "#e05050";
                  return (
                    <Link
                      key={attempt.attemptId || i}
                      to={`/${yr}/${stg}`}
                      style={{ ...styles.historyRow, textDecoration: "none" }}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                          <span style={{ ...styles.stageBadge, background: color + "20", color }}>
                            {STAGE_LABELS[stg] || stg}
                          </span>
                          <span style={{ color: "#c8c8d8", fontSize: 14, fontWeight: 600 }}>
                            {yr}
                          </span>
                        </div>
                        <span style={{ color: "#5a5a6a", fontSize: 12 }}>
                          {new Date(attempt.date).toLocaleDateString("pl-PL", {
                            day: "numeric",
                            month: "long",
                            year: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ color: pctColor, fontSize: 20, fontWeight: 800 }}>
                          {attempt.percentage}%
                        </div>
                        <div style={{ color: "#7a7a90", fontSize: 12 }}>
                          {attempt.score}/{attempt.maxScore} pkt
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </>
          )}

          {/* Practice history */}
          {practices.length > 0 && (
            <>
              <h2 style={styles.sectionTitle}>Historia cwiczen</h2>
              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 32 }}>
                {[...practices].reverse().map((attempt, i) => {
                  const exId = attempt.exerciseId || "";
                  const exMeta = exerciseIndex.find((e) => e.id === exId);
                  const exType = attempt.exerciseType || exMeta?.taskType || "";
                  const pctColor = attempt.percentage >= 70 ? "#50d890" : attempt.percentage >= 40 ? "#f5a623" : "#e05050";
                  return (
                    <Link
                      key={attempt.attemptId || i}
                      to={exType ? `/cwiczenia/${exType}/${exId}` : "/cwiczenia"}
                      style={{ ...styles.historyRow, textDecoration: "none" }}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                          <span style={{ ...styles.stageBadge, background: "#f5a62320", color: "#f5a623" }}>
                            Cwiczenie
                          </span>
                          <span style={{ color: "#c8c8d8", fontSize: 14, fontWeight: 600 }}>
                            {PRACTICE_TYPE_LABELS[exType] || exType || exId}
                          </span>
                        </div>
                        <span style={{ color: "#5a5a6a", fontSize: 12 }}>
                          {new Date(attempt.date).toLocaleDateString("pl-PL", {
                            day: "numeric",
                            month: "long",
                            year: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ color: pctColor, fontSize: 20, fontWeight: 800 }}>
                          {attempt.percentage}%
                        </div>
                        <div style={{ color: "#7a7a90", fontSize: 12 }}>
                          {attempt.score}/{attempt.maxScore} pkt
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </>
          )}

          {/* Clear history */}
          <div style={{ textAlign: "center", marginTop: 32 }}>
            {confirmClear ? (
              <div style={{ display: "flex", gap: 8, justifyContent: "center", alignItems: "center" }}>
                <span style={{ color: "#e05050", fontSize: 13 }}>Na pewno usunac?</span>
                <button onClick={handleClear} style={styles.clearBtnConfirm}>Tak, usun</button>
                <button onClick={() => setConfirmClear(false)} style={styles.clearBtnCancel}>Anuluj</button>
              </div>
            ) : (
              <button onClick={handleClear} style={styles.clearBtn}>Wyczysc historie</button>
            )}
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  page: {
    maxWidth: 720,
    margin: "0 auto",
    padding: "48px 20px",
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
    marginBottom: 24,
  },
  emptyState: {
    background: "#13131a",
    border: "1px solid #1e1e2e",
    borderRadius: 12,
    padding: 32,
    textAlign: "center",
  },
  startBtn: {
    display: "inline-block",
    background: "linear-gradient(135deg, #50d890, #42b4f5)",
    color: "#0d0d14",
    border: "none",
    borderRadius: 10,
    padding: "12px 36px",
    fontSize: 15,
    fontWeight: 700,
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
    textDecoration: "none",
  },
  summaryGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: 12,
    marginBottom: 32,
  },
  summaryCard: {
    background: "#13131a",
    border: "1px solid #1e1e2e",
    borderRadius: 12,
    padding: "20px 16px",
    textAlign: "center",
  },
  summaryValue: {
    fontSize: 28,
    fontWeight: 900,
    color: "#e8e8f0",
    fontFamily: "'Playfair Display', serif",
  },
  summaryLabel: {
    fontSize: 12,
    color: "#7a7a90",
    marginTop: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: "#c8c8d8",
    marginBottom: 12,
  },
  skillRow: {
    background: "#13131a",
    border: "1px solid #1e1e2e",
    borderRadius: 10,
    padding: "12px 16px",
  },
  skillInfo: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  skillLabel: {
    color: "#c8c8d8",
    fontSize: 13,
    fontWeight: 600,
  },
  skillScore: {
    color: "#7a7a90",
    fontSize: 12,
  },
  barBg: {
    height: 6,
    background: "#1e1e2e",
    borderRadius: 3,
    overflow: "hidden",
  },
  barFill: {
    height: "100%",
    borderRadius: 3,
    transition: "width 0.5s ease",
  },
  historyRow: {
    display: "flex",
    alignItems: "center",
    background: "#13131a",
    border: "1px solid #1e1e2e",
    borderRadius: 10,
    padding: "14px 16px",
  },
  stageBadge: {
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 700,
  },
  clearBtn: {
    background: "none",
    border: "1px solid #2a2a3a",
    borderRadius: 8,
    padding: "8px 20px",
    color: "#5a5a6a",
    fontSize: 13,
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
  },
  clearBtnConfirm: {
    background: "#e05050",
    border: "none",
    borderRadius: 8,
    padding: "8px 20px",
    color: "#fff",
    fontSize: 13,
    fontWeight: 700,
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
  },
  clearBtnCancel: {
    background: "none",
    border: "1px solid #2a2a3a",
    borderRadius: 8,
    padding: "8px 20px",
    color: "#7a7a90",
    fontSize: 13,
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
  },
};
