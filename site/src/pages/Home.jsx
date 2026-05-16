import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useDocumentHead } from "../hooks";
import { useUser } from "../App";
import {
  loadRewards,
  computePracticeStars,
  getPracticeTitle,
  getTypeMastery,
} from "../lib/practiceRewards";
import { loadAttempts } from "../lib/resultsModel";
import { syncAttempts } from "../lib/resultsSync";
import { loadProgress, getPlayerTitle } from "../lib/questProgress";
import { percentageToStars } from "../lib/questStars";
import ProgressTrendChart from "../components/ProgressTrendChart";

const STAGE_LABELS = { szkolny: "Etap szkolny", rejonowy: "Etap rejonowy", wojewodzki: "Etap wojewodzki" };
const STAGE_COLORS = { szkolny: "#50d890", rejonowy: "#42b4f5", wojewodzki: "#a78bfa" };

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

const MASTERY_COLORS = {
  0: "#3a3a4a",
  1: "#7a7a90",
  2: "#42b4f5",
  3: "#50d890",
  4: "#f5a623",
  5: "#a78bfa",
};

const QUEST_BRANCHES = [
  { id: "vocabulary", label: "Vocabulary", color: "#f59e0b" },
  { id: "grammar", label: "Grammar", color: "#8b5cf6" },
  { id: "reading", label: "Reading", color: "#3b82f6" },
];
const QUEST_BRANCH_MAX_STARS = 75; // 5 levels × 3 exercises × 5★
const QUEST_TOTAL_MAX_STARS = 225;

function PracticeTitleCard() {
  const user = useUser();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const [info, setInfo] = useState(null);

  useEffect(() => {
    const bestScores = loadRewards(storageKey);
    const totalStars = computePracticeStars(bestScores);
    if (totalStars === 0) { setInfo(null); return; }
    setInfo(getPracticeTitle(totalStars));
  }, [storageKey]);

  if (!info) return null;

  const progressPct = info.nextStars
    ? Math.round(((info.totalStars - info.stars) / (info.nextStars - info.stars)) * 100)
    : 100;

  return (
    <Link to="/cwiczenia" style={{
      display: "block", background: "#13131a", border: "1px solid #1e1e2e", borderRadius: 12,
      padding: "16px 20px", marginBottom: 12, textDecoration: "none",
      transition: "border-color 0.2s",
    }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = "#f5a62366"; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = "#1e1e2e"; }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <span style={{ color: "#f5a623", fontWeight: 700, fontSize: 15 }}>
          Cwiczenia: {info.title}
        </span>
        <span style={{ color: "#c8c8d8", fontSize: 13 }}>
          ★ {info.totalStars}/525
        </span>
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
          Nastepny: {info.nextTitle} ({info.nextStars}★)
        </div>
      )}
    </Link>
  );
}

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

function computeStats(all) {
  if (all.length === 0) return null;

  const competitions = all.filter((a) => a.kind === "competition");
  const practice = all.filter((a) => a.kind === "practice");

  // Per-type stats from all attempts (competitions + practice)
  const byType = {};
  for (const a of all) {
    for (const tb of (a.taskBreakdown || [])) {
      if (tb.skipped) continue;
      const t = tb.type;
      if (!byType[t]) byType[t] = { earned: 0, max: 0, count: 0 };
      byType[t].earned += tb.earned;
      byType[t].max += tb.max;
      byType[t].count++;
    }
  }

  // Best % per competition test
  const bestByCompetition = {};
  for (const a of competitions) {
    const key = a.testId;
    if (!bestByCompetition[key] || a.percentage > bestByCompetition[key]) {
      bestByCompetition[key] = a.percentage;
    }
  }
  const allBests = Object.values(bestByCompetition);
  const overallAvg = allBests.length > 0 ? Math.round(allBests.reduce((s, v) => s + v, 0) / allBests.length) : 0;

  // Today's activity
  const today = todayKey();
  const todayCount = all.filter((a) => typeof a.date === "string" && a.date.startsWith(today)).length;

  return {
    totalAttempts: all.length,
    competitionsDone: new Set(competitions.map((a) => a.testId)).size,
    practicesDone: new Set(practice.map((a) => a.testId)).size,
    overallAvg,
    bestByCompetition,
    todayCount,
  };
}

function useHomeData() {
  const user = useUser();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const [data, setData] = useState({ stats: null, bestScores: {}, attempts: [] });

  useEffect(() => {
    const reload = (attempts) => {
      try {
        const all = attempts ?? loadAttempts(storageKey);
        setData({
          stats: computeStats(all),
          bestScores: loadRewards(storageKey),
          attempts: all,
        });
      } catch {
        setData({ stats: null, bestScores: {}, attempts: [] });
      }
    };
    reload();

    if (user?.name) {
      syncAttempts(user.name, storageKey).then((merged) => {
        reload(merged);
      }).catch(() => {});
    }
  }, [storageKey, user?.name]);

  return data;
}

function useExerciseIndex() {
  const [list, setList] = useState(null);
  useEffect(() => {
    fetch("/konkursy/angielski/data/practice/index.json")
      .then((r) => r.json())
      .then((d) => setList(d.exercises || []))
      .catch(() => setList([]));
  }, []);
  return list;
}

function useQuestSnapshot() {
  const user = useUser();
  const [progress, setProgress] = useState(null);
  useEffect(() => {
    if (!user?.name) { setProgress(null); return; }
    setProgress(loadProgress(user.name));
  }, [user?.name]);
  return progress;
}

function TypeMasteryGrid({ bestScores, exerciseList }) {
  if (!exerciseList || exerciseList.length === 0) return null;

  const types = Array.from(new Set(exerciseList.map((e) => e.taskType)));
  const masteries = types
    .map((type) => ({ type, ...getTypeMastery(bestScores, exerciseList, type) }))
    .sort((a, b) => {
      if (a.earned !== b.earned) return b.earned - a.earned;
      if (a.level !== b.level) return b.level - a.level;
      return (TYPE_LABELS[a.type] || a.type).localeCompare(TYPE_LABELS[b.type] || b.type);
    });

  const startedCount = masteries.filter((m) => m.level > 0).length;

  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 12 }}>
        <h2 style={{ fontSize: 16, fontWeight: 700, color: "#c8c8d8", margin: 0 }}>
          Mistrzostwo typow
        </h2>
        <span style={{ color: "#7a7a90", fontSize: 12 }}>
          {startedCount}/{masteries.length} rozpoczetych
        </span>
      </div>
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(170px, 1fr))",
        gap: 8,
      }}>
        {masteries.map((m) => {
          const isAttempted = m.level > 0;
          const accent = isAttempted ? (MASTERY_COLORS[m.level] || "#7a7a90") : "#2a2a3a";
          const pct = m.max > 0 ? Math.round((m.earned / m.max) * 100) : 0;
          const baseBorder = isAttempted ? accent + "44" : "#1e1e2e";
          return (
            <Link
              key={m.type}
              to={`/cwiczenia/${m.type}`}
              style={{
                display: "block",
                background: isAttempted ? "#13131a" : "#0d0d14",
                border: `1px solid ${baseBorder}`,
                borderRadius: 10,
                padding: "10px 12px",
                textDecoration: "none",
                transition: "border-color 0.2s, transform 0.2s",
                opacity: isAttempted ? 1 : 0.6,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = accent;
                e.currentTarget.style.transform = "translateY(-1px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = baseBorder;
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 6, marginBottom: 6 }}>
                <span style={{ color: "#e8e8f0", fontSize: 12, fontWeight: 700, lineHeight: 1.2 }}>
                  {TYPE_LABELS[m.type] || m.type}
                </span>
                {isAttempted ? (
                  <span style={{
                    fontSize: 10, fontWeight: 700,
                    color: accent,
                    background: accent + "1f",
                    border: `1px solid ${accent}3a`,
                    borderRadius: 999,
                    padding: "2px 6px",
                    whiteSpace: "nowrap",
                  }}>
                    {m.label}
                  </span>
                ) : (
                  <span style={{
                    fontSize: 10, fontWeight: 700,
                    color: "#5a5a6a",
                    border: "1px dashed #2a2a3a",
                    borderRadius: 999,
                    padding: "2px 6px",
                    whiteSpace: "nowrap",
                  }}>
                    Nowe
                  </span>
                )}
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 11 }}>
                <span style={{ color: isAttempted ? "#f5a623" : "#5a5a6a", fontWeight: 700 }}>
                  ★ {m.earned}/{m.max}
                </span>
                <span style={{ color: "#5a5a6a" }}>
                  {pct}%
                </span>
              </div>
              <div style={{
                marginTop: 6,
                height: 3, background: "#1e1e2e", borderRadius: 2, overflow: "hidden",
              }}>
                <div style={{
                  height: "100%",
                  width: `${pct}%`,
                  background: isAttempted ? accent : "#2a2a3a",
                  transition: "width 0.5s",
                }} />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function QuestSnapshot({ progress }) {
  if (!progress) {
    return (
      <Link to="/quest" style={{
        display: "block", background: "#13131a", border: "1px solid #1e1e2e",
        borderRadius: 10, padding: "16px 20px", marginBottom: 12, textDecoration: "none",
        transition: "border-color 0.2s",
      }}
        onMouseEnter={(e) => { e.currentTarget.style.borderColor = "#a78bfa66"; }}
        onMouseLeave={(e) => { e.currentTarget.style.borderColor = "#1e1e2e"; }}
      >
        <span style={{ color: "#a78bfa", fontWeight: 700, fontSize: 15 }}>Quest</span>
        <span style={{ color: "#7a7a90", fontSize: 13, display: "block", marginTop: 4 }}>
          Fun English practice &rarr;
        </span>
      </Link>
    );
  }

  const titleInfo = getPlayerTitle(progress.stars || 0);
  const overallPct = Math.round(((progress.stars || 0) / QUEST_TOTAL_MAX_STARS) * 100);

  return (
    <Link to="/quest" style={{
      display: "block", background: "#13131a", border: "1px solid #1e1e2e",
      borderRadius: 12, padding: "16px 20px", marginBottom: 12, textDecoration: "none",
      transition: "border-color 0.2s",
    }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = "#a78bfa66"; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = "#1e1e2e"; }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
        <span style={{ color: "#a78bfa", fontWeight: 700, fontSize: 15 }}>
          Quest: {titleInfo.title}
        </span>
        <span style={{ color: "#c8c8d8", fontSize: 13 }}>
          ★ {progress.stars || 0}/{QUEST_TOTAL_MAX_STARS}
        </span>
      </div>
      <div style={{ display: "flex", gap: 10 }}>
        {QUEST_BRANCHES.map((b) => {
          const scores = progress.branches?.[b.id]?.bestScores || {};
          const branchStars = Object.values(scores).reduce((s, p) => s + percentageToStars(p), 0);
          const pct = Math.round((branchStars / QUEST_BRANCH_MAX_STARS) * 100);
          return (
            <div key={b.id} style={{ flex: 1 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, marginBottom: 3 }}>
                <span style={{ color: b.color, fontWeight: 700 }}>{b.label}</span>
                <span style={{ color: "#7a7a90" }}>{branchStars}★</span>
              </div>
              <div style={{ height: 4, background: "#1e1e2e", borderRadius: 2, overflow: "hidden" }}>
                <div style={{
                  height: "100%",
                  width: `${pct}%`,
                  background: b.color,
                  transition: "width 0.5s",
                }} />
              </div>
            </div>
          );
        })}
      </div>
      {titleInfo.starsForNext > 0 && overallPct < 100 && (
        <div style={{ color: "#7a7a90", fontSize: 11, marginTop: 8 }}>
          {titleInfo.starsForNext - titleInfo.starsInLevel}★ do tytulu nastepnego poziomu
        </div>
      )}
    </Link>
  );
}

export default function Home() {
  useDocumentHead(null, "Testy z konkursow jezyka angielskiego woj. mazowieckiego. Rozwiazuj online i sprawdzaj wyniki!");
  const [tests, setTests] = useState(null);
  const { stats: dashboard, bestScores, attempts } = useHomeData();
  const exerciseList = useExerciseIndex();
  const questProgress = useQuestSnapshot();

  useEffect(() => {
    fetch("/konkursy/angielski/data/tests.json")
      .then((r) => r.json())
      .then(setTests)
      .catch(console.error);
  }, []);

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
        rel="stylesheet"
      />

      <h1 style={styles.title}>Konkurs jezyka angielskiego</h1>
      <p style={styles.subtitle}>
        Wojewodztwo mazowieckie, klasy IV-VIII. Wybierz test i sprawdz swoja wiedze!
      </p>

      <div
        style={{
          background: "#13131a",
          border: "1px solid #1e1e2e",
          borderRadius: 10,
          padding: "16px 20px",
          marginBottom: 40,
          fontSize: 14,
          lineHeight: 1.7,
          color: "#7a7a90",
        }}
      >
        <span style={{ fontWeight: 700, color: "#e8e8f0" }}>Jak korzystac:</span>{" "}
        Wybierz etap konkursu, rozwiaz zadania i sprawdz odpowiedzi.
        Zadania otwarte (sluchanie, transformacje, wypracowania) beda dodane pozniej.
      </div>

      {dashboard && (
        <div style={{
          background: "#13131a", border: "1px solid #1e1e2e", borderRadius: 12,
          padding: "20px 24px", marginBottom: 24,
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <span style={{ color: "#e8e8f0", fontWeight: 700, fontSize: 16 }}>Twoje wyniki</span>
            <span style={{
              fontSize: 28, fontWeight: 900, fontFamily: "'Playfair Display', serif",
              color: dashboard.overallAvg >= 70 ? "#50d890" : dashboard.overallAvg >= 40 ? "#f5a623" : "#e05050",
            }}>
              {dashboard.overallAvg}%
            </span>
          </div>

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 110px", background: "#0d0d14", borderRadius: 8, padding: "10px 14px" }}>
              <div style={{ color: "#7a7a90", fontSize: 11, marginBottom: 2 }}>Testy konkursowe</div>
              <div style={{ color: "#42b4f5", fontSize: 18, fontWeight: 700 }}>{dashboard.competitionsDone}</div>
            </div>
            <div style={{ flex: "1 1 110px", background: "#0d0d14", borderRadius: 8, padding: "10px 14px" }}>
              <div style={{ color: "#7a7a90", fontSize: 11, marginBottom: 2 }}>Cwiczenia</div>
              <div style={{ color: "#f5a623", fontSize: 18, fontWeight: 700 }}>{dashboard.practicesDone}</div>
            </div>
            <div style={{ flex: "1 1 110px", background: "#0d0d14", borderRadius: 8, padding: "10px 14px" }}>
              <div style={{ color: "#7a7a90", fontSize: 11, marginBottom: 2 }}>Podejsc</div>
              <div style={{ color: "#a78bfa", fontSize: 18, fontWeight: 700 }}>{dashboard.totalAttempts}</div>
            </div>
            <div style={{
              flex: "1 1 110px",
              background: dashboard.todayCount > 0 ? "#50d89015" : "#0d0d14",
              border: dashboard.todayCount > 0 ? "1px solid #50d89030" : "1px solid transparent",
              borderRadius: 8, padding: "10px 14px",
            }}>
              <div style={{ color: "#7a7a90", fontSize: 11, marginBottom: 2 }}>Dzisiaj</div>
              <div style={{
                color: dashboard.todayCount > 0 ? "#50d890" : "#5a5a6a",
                fontSize: 18, fontWeight: 700,
              }}>
                {dashboard.todayCount}
              </div>
            </div>
          </div>
        </div>
      )}

      <PracticeTitleCard />

      <ProgressTrendChart attempts={attempts} />

      <TypeMasteryGrid bestScores={bestScores} exerciseList={exerciseList} />

      <QuestSnapshot progress={questProgress} />

      <div style={{ display: "flex", gap: 12, marginBottom: 40 }}>
        <Link
          to="/postepy"
          style={{
            flex: 1,
            display: "block",
            background: "#13131a",
            border: "1px solid #1e1e2e",
            borderRadius: 10,
            padding: "16px 20px",
            textDecoration: "none",
            transition: "border-color 0.2s",
          }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = "#42b4f566"; }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = "#1e1e2e"; }}
        >
          <span style={{ color: "#42b4f5", fontWeight: 700, fontSize: 15 }}>Twoje postepy</span>
          <span style={{ color: "#7a7a90", fontSize: 13, display: "block", marginTop: 4 }}>
            Historia wynikow &rarr;
          </span>
        </Link>
        <Link
          to="/cwiczenia"
          style={{
            flex: 1,
            display: "block",
            background: "#13131a",
            border: "1px solid #1e1e2e",
            borderRadius: 10,
            padding: "16px 20px",
            textDecoration: "none",
            transition: "border-color 0.2s",
          }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = "#f5a62366"; }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = "#1e1e2e"; }}
        >
          <span style={{ color: "#f5a623", fontWeight: 700, fontSize: 15 }}>Cwiczenia</span>
          <span style={{ color: "#7a7a90", fontSize: 13, display: "block", marginTop: 4 }}>
            Dodatkowe zadania &rarr;
          </span>
        </Link>
      </div>

      {!tests && <p style={{ color: "#7a7a90" }}>Ladowanie...</p>}

      {tests?.tests.map((yearGroup) => (
        <div key={yearGroup.year} style={{ marginBottom: 32 }}>
          <h2 style={styles.yearTitle}>{yearGroup.year}</h2>
          <div style={styles.grid}>
            {yearGroup.stages.map((stage) => {
              const color = STAGE_COLORS[stage.stage] || "#50d890";
              const testKey = `${yearGroup.yearPath}/${stage.stage}`;
              const bestPct = dashboard?.bestByCompetition?.[testKey];
              const badgeColor =
                bestPct === undefined ? null :
                bestPct >= 70 ? "#50d890" :
                bestPct >= 40 ? "#f5a623" : "#e05050";
              return (
                <Link
                  key={stage.stage}
                  to={`/${yearGroup.yearPath}/${stage.stage}`}
                  style={{ ...styles.card, textDecoration: "none", color: "inherit", position: "relative" }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = color + "66";
                    e.currentTarget.style.transform = "translateY(-2px)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = "#1e1e2e";
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12, gap: 8 }}>
                    <div style={{ ...styles.stageBadge, background: color + "20", color, marginBottom: 0 }}>
                      {STAGE_LABELS[stage.stage]}
                    </div>
                    {badgeColor && (
                      <span style={{
                        fontSize: 12, fontWeight: 800,
                        color: badgeColor,
                        background: badgeColor + "1f",
                        border: `1px solid ${badgeColor}40`,
                        borderRadius: 999,
                        padding: "3px 8px",
                        whiteSpace: "nowrap",
                      }} title="Twoj najlepszy wynik">
                        {bestPct}%
                      </span>
                    )}
                  </div>
                  <div style={styles.cardInfo}>
                    <span style={{ color: "#7a7a90", fontSize: 13 }}>{stage.date}</span>
                    <span style={{ color: "#c8c8d8", fontSize: 14 }}>{stage.maxPoints} pkt</span>
                  </div>
                  {badgeColor && (
                    <div style={{
                      marginTop: 8,
                      height: 3, background: "#1e1e2e", borderRadius: 2, overflow: "hidden",
                    }}>
                      <div style={{
                        height: "100%",
                        width: `${bestPct}%`,
                        background: badgeColor,
                        transition: "width 0.5s",
                      }} />
                    </div>
                  )}
                </Link>
              );
            })}
          </div>
        </div>
      ))}
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
  title: {
    fontFamily: "'Playfair Display', Georgia, serif",
    fontSize: 32,
    fontWeight: 900,
    marginBottom: 8,
    background: "linear-gradient(135deg, #50d890, #42b4f5, #a78bfa)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: {
    color: "#7a7a90",
    fontSize: 15,
    lineHeight: 1.6,
    marginBottom: 32,
  },
  yearTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: "#c8c8d8",
    marginBottom: 12,
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
    gap: 12,
  },
  card: {
    display: "block",
    background: "#13131a",
    border: "1px solid #1e1e2e",
    borderRadius: 12,
    padding: "20px",
    transition: "border-color 0.2s, transform 0.2s",
  },
  stageBadge: {
    display: "inline-block",
    padding: "4px 12px",
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 700,
    marginBottom: 12,
  },
  cardInfo: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
};
