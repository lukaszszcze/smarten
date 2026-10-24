import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDocumentHead } from "../../hooks";
import { useUser } from "../../App";
import StarDisplay from "../../components/StarDisplay";
import { loadRewards, OJAJ_POOL } from "../../lib/practiceRewards";
import { loadAttempts } from "../../lib/resultsModel";
import { syncAttempts } from "../../lib/resultsSync";
import {
  doneCounts,
  drawOnlineTest,
  isOnlineAttempt,
  onlineAttemptLabel,
} from "../../lib/ojajOnline";
import { percentageToStars } from "../../lib/questStars";
import { aoeUnitForPercentage, usesAoeMarks } from "../../lib/aoeRanks";
import {
  OJAJ_ACCENT,
  OJAJ_INDEX_PATH,
  OJAJ_STAGE_COLORS,
  ojajStageTitle,
} from "../../lib/ojaj";

const UK_NOTEBOOK_PATH = "/ojaj_uk";

const TYPE_LABELS = {
  word_formation: "Slowotworstwo",
  word_spelling: "Wisielec",
  sentence_transformation: "Transformacje zdan",
  multiple_choice: "Test jednokrotnego wyboru",
  grammar_gaps: "Luki gramatyczne",
  knowledge_questions: "Wiedza o krajach",
  matching: "Dopasowywanie",
  true_false_ni: "Prawda / falsz",
};

const TYPE_COLORS = {
  word_formation: "#e05080",
  word_spelling: "#f5a623",
  sentence_transformation: "#50d890",
  multiple_choice: "#42b4f5",
  grammar_gaps: "#a78bfa",
  knowledge_questions: "#a78bfa",
  matching: "#50d890",
  true_false_ni: "#f5a623",
};

/**
 * The exercise list under one heading per source paper, in index order.
 *
 * The four sample-test exercises carry no group and stay together at the top;
 * everything the compendium papers contributed is long enough that an
 * ungrouped list of it reads as one undifferentiated column.
 */
function groupExercises(exercises) {
  const out = [];
  for (const ex of exercises) {
    const group = ex.group || "";
    if (!out.length || out[out.length - 1].group !== group) {
      out.push({ group, rows: [] });
    }
    out[out.length - 1].rows.push(ex);
  }
  return out;
}

function scoreColor(pct) {
  if (pct >= 70) return "#50d890";
  if (pct >= 40) return "#f5a623";
  return "#e05050";
}

function useOjajIndex() {
  const [index, setIndex] = useState(null);
  useEffect(() => {
    fetch(OJAJ_INDEX_PATH)
      .then((r) => r.json())
      .then(setIndex)
      .catch(console.error);
  }, []);
  return index;
}

function useOjajProgress() {
  const user = useUser();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const [progress, setProgress] = useState({ bestByTest: {}, bestScores: {} });

  useEffect(() => {
    try {
      const bestByTest = {};
      for (const a of loadAttempts(storageKey)) {
        if (a.kind !== "competition" || !a.testId?.startsWith("ojaj/")) continue;
        const key = a.testId.slice("ojaj/".length);
        if (!(key in bestByTest) || a.percentage > bestByTest[key]) {
          bestByTest[key] = a.percentage;
        }
      }
      setProgress({ bestByTest, bestScores: loadRewards(storageKey, OJAJ_POOL) });
    } catch {
      setProgress({ bestByTest: {}, bestScores: {} });
    }
  }, [storageKey]);

  return progress;
}

function TestCard({ edition, stage, bestPct }) {
  const color = OJAJ_STAGE_COLORS[stage.stage] || OJAJ_ACCENT;
  const badge = bestPct === undefined ? null : scoreColor(bestPct);

  return (
    <Link
      to={`/ojaj/${edition.yearPath}/${stage.stage}`}
      style={{ ...styles.card, textDecoration: "none", color: "inherit" }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = color + "66";
        e.currentTarget.style.transform = "translateY(-2px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "#1e1e2e";
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8, marginBottom: 12 }}>
        <span style={{ ...styles.stageBadge, background: color + "20", color }}>
          {ojajStageTitle(stage)}
        </span>
        {badge && (
          <span
            style={{
              fontSize: 12, fontWeight: 800, color: badge,
              background: badge + "1f", border: `1px solid ${badge}40`,
              borderRadius: 999, padding: "3px 8px", whiteSpace: "nowrap",
            }}
            title="Twoj najlepszy wynik"
          >
            {bestPct}%
          </span>
        )}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ color: "#7a7a90", fontSize: 13 }}>
          {stage.timeMinutes} min{stage.variant ? ` · wersja ${stage.variant}` : ""}
        </span>
        <span style={{ color: "#c8c8d8", fontSize: 14 }}>{stage.maxPoints} pkt</span>
      </div>
      {badge && (
        <div style={{ marginTop: 8, height: 3, background: "#1e1e2e", borderRadius: 2, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${bestPct}%`, background: badge, transition: "width 0.5s" }} />
        </div>
      )}
    </Link>
  );
}

/**
 * Etap I, czesc II: the draw and the user's online results.
 *
 * The tests are not listed for direct choice; the button draws one, unseen
 * ones first. Attempts are synced before the draw, or a test done on another
 * device would count as unseen.
 */
function OnlineSection({ vault }) {
  const user = useUser();
  const navigate = useNavigate();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const [attempts, setAttempts] = useState(() => loadAttempts(storageKey));
  const [drawing, setDrawing] = useState(false);

  useEffect(() => {
    setAttempts(loadAttempts(storageKey));
  }, [storageKey]);

  const ids = vault.map((t) => t.id);
  const counts = doneCounts(ids, attempts);
  const done = ids.filter((id) => counts[id] > 0).length;
  const results = attempts.filter(isOnlineAttempt).reverse();

  // A failed sync (offline) does not stop the draw: it then counts this
  // device's attempts only, so a test done elsewhere may come up again, which
  // beats having no test to write.
  const draw = async () => {
    setDrawing(true);
    const synced = user?.name
      ? await syncAttempts(user.name, storageKey).catch(() => loadAttempts(storageKey))
      : loadAttempts(storageKey);
    navigate(`/ojaj/online/${drawOnlineTest(ids, synced)}`);
  };

  return (
    <div style={{ marginBottom: 40 }}>
      <h2 style={styles.sectionTitle}>Etap I, czesc II - test online</h2>
      <div style={styles.card}>
        <p style={{ color: "#9a9ab0", fontSize: 14, lineHeight: 1.6, margin: "0 0 14px" }}>
          45 pytan w 45 minut, jedno pytanie na ekranie, jak na platformie OJAJ.
          Zadania wlasne aplikacji. Test jest losowany, najpierw sposrod jeszcze
          nierozwiazanych.
        </p>
        <div style={styles.drawRow}>
          <span style={{ color: "#c8c8d8", fontSize: 14 }}>
            Rozwiazane: <strong>{done}</strong> z {ids.length}
          </span>
          <button
            onClick={draw}
            disabled={drawing}
            style={{ ...styles.drawBtn, opacity: drawing ? 0.6 : 1 }}
          >
            {drawing ? "Losowanie..." : "Losuj test"}
          </button>
        </div>
        {results.length > 0 && (
          <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 6 }}>
            {results.map((a) => (
              <div key={a.attemptId} style={styles.resultRow}>
                <span style={{ color: "#c8c8d8", fontWeight: 600 }}>{onlineAttemptLabel(a)}</span>
                <span style={{ color: "#5a5a6a", fontSize: 12, flex: 1 }}>
                  {new Date(a.date).toLocaleDateString("pl-PL", {
                    day: "numeric", month: "long", hour: "2-digit", minute: "2-digit",
                  })}
                </span>
                <span style={{ color: scoreColor(a.percentage), fontWeight: 700 }}>
                  {a.score}/{a.maxScore}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ExerciseRow({ exercise, bestPct }) {
  const color = TYPE_COLORS[exercise.taskType] || OJAJ_ACCENT;
  const stars = bestPct !== undefined ? percentageToStars(bestPct) : -1;

  return (
    <Link
      to={`/ojaj/cwiczenia/${exercise.id}`}
      style={{ ...styles.card, textDecoration: "none", color: "inherit" }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = color + "66";
        e.currentTarget.style.transform = "translateY(-2px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "#1e1e2e";
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ color: "#e8e8f0", fontSize: 15, fontWeight: 600 }}>
              {TYPE_LABELS[exercise.taskType] || exercise.taskType}
            </span>
            {stars >= 0 && (usesAoeMarks(exercise.id) ? (
              <span style={{ color: "#f5a623", fontSize: 13, fontWeight: 700 }}>
                {aoeUnitForPercentage(bestPct).icon} {aoeUnitForPercentage(bestPct).name}
              </span>
            ) : (
              <StarDisplay count={stars} size={14} color="#f5a623" letterSpacing={1} />
            ))}
          </div>
          <div style={{ color: "#5a5a6a", fontSize: 12, marginTop: 2 }}>{exercise.title}</div>
        </div>
        <span
          style={{
            fontSize: 14, fontWeight: 700, whiteSpace: "nowrap",
            color: bestPct === undefined ? "#7a7a90" : scoreColor(bestPct),
          }}
        >
          {bestPct === undefined ? `${exercise.points} pkt` : `${bestPct}%`}
        </span>
      </div>
    </Link>
  );
}

export default function OjajHome() {
  useDocumentHead(
    "OJAJ",
    "Olimpiada Jezyka Angielskiego dla Juniorow - testy i cwiczenia"
  );
  const index = useOjajIndex();
  const { bestByTest, bestScores } = useOjajProgress();

  const exercises = index?.exercises || [];
  const earnedStars = exercises.reduce(
    (sum, ex) => sum + (bestScores[ex.id] === undefined ? 0 : percentageToStars(bestScores[ex.id])),
    0
  );
  const maxStars = exercises.length * 5;

  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
        rel="stylesheet"
      />

      <Link to="/" style={styles.back}>&larr; Powrot do strony glownej</Link>
      <h1 style={styles.title}>OJAJ</h1>
      <p style={styles.subtitle}>
        Olimpiada Jezyka Angielskiego dla Juniorow - ogolnopolska olimpiada dla szkol
        podstawowych, trudniejsza od konkursu kuratoryjnego (poziom B2-C1+).
      </p>

      <div style={styles.infoCard}>
        <span style={{ fontWeight: 700, color: "#e8e8f0" }}>Czym rozni sie od konkursu:</span>{" "}
        zaawansowana gramatyka i slownictwo, teksty autentyczne, wiecej form pisemnych.
        Sluchanie jest obowiazkowe od II etapu, a w finale dochodzi rozmowa z komisja -
        tych dwoch czesci nie da sie tu cwiczyc.
      </div>

      {/* A static page in site/public, so a plain link rather than a router Link. */}
      <a
        href={UK_NOTEBOOK_PATH}
        style={{ ...styles.card, textDecoration: "none", color: "inherit", marginBottom: 40 }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = "#50d89066";
          e.currentTarget.style.transform = "translateY(-2px)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = "#1e1e2e";
          e.currentTarget.style.transform = "translateY(0)";
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
          <div style={{ flex: 1 }}>
            <span style={{ color: "#e8e8f0", fontSize: 15, fontWeight: 600 }}>
              Wielka Brytania - notatki do nauki
            </span>
            <div style={{ color: "#5a5a6a", fontSize: 12, marginTop: 2 }}>
              Wszystkie tematy z mapy mysli OJAJ 2026/27: symbole, parlament, historia,
              slynni Brytyjczycy, Londyn i parki krolewskie
            </div>
          </div>
          <span style={{ color: "#50d890", fontSize: 14, fontWeight: 700, whiteSpace: "nowrap" }}>
            Czytaj &rarr;
          </span>
        </div>
      </a>

      {!index && <p style={{ color: "#7a7a90" }}>Ladowanie...</p>}

      {index?.online?.length > 0 && <OnlineSection vault={index.online} />}

      {index?.editions?.map((edition) => (
        <div key={edition.yearPath} style={{ marginBottom: 32 }}>
          <h2 style={styles.sectionTitle}>{edition.label || `Testy ${edition.year}`}</h2>
          <div style={styles.grid}>
            {edition.stages.map((stage) => (
              <TestCard
                key={`${edition.yearPath}/${stage.stage}`}
                edition={edition}
                stage={stage}
                bestPct={bestByTest[`${edition.yearPath}/${stage.stage}`]}
              />
            ))}
          </div>
        </div>
      ))}

      {exercises.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 12 }}>
            <h2 style={{ ...styles.sectionTitle, marginBottom: 0 }}>Cwiczenia</h2>
            <span style={{ color: "#f5a623", fontSize: 13, fontWeight: 700 }}>
              &#9733; {earnedStars}/{maxStars}
            </span>
          </div>
          <p style={{ color: "#7a7a90", fontSize: 13, marginTop: 0, marginBottom: 12 }}>
            Zadania z testow przykladowych OJAJ. Zadne z nich nie powtarza sie w
            testach powyzej.
          </p>
          {groupExercises(exercises).map(({ group, rows }) => (
            <div key={group || "_"} style={{ marginBottom: 20 }}>
              {group && <p style={styles.groupTitle}>{group}</p>}
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {rows.map((ex) => (
                  <ExerciseRow key={ex.id} exercise={ex} bestPct={bestScores[ex.id]} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {index?.competition?.url && (
        <p style={{ color: "#4a4a5a", fontSize: 12 }}>
          Zrodlo zadan:{" "}
          <a href={index.competition.url} target="_blank" rel="noreferrer" style={{ color: "#5a5a6a" }}>
            {index.competition.url}
          </a>
        </p>
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
    fontSize: 32,
    fontWeight: 900,
    marginBottom: 8,
    background: `linear-gradient(135deg, ${OJAJ_ACCENT}, #f5a623, #a78bfa)`,
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: {
    color: "#7a7a90",
    fontSize: 15,
    lineHeight: 1.6,
    marginBottom: 24,
  },
  infoCard: {
    background: "#13131a",
    border: "1px solid #1e1e2e",
    borderRadius: 10,
    padding: "16px 20px",
    marginBottom: 16,
    fontSize: 14,
    lineHeight: 1.7,
    color: "#7a7a90",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: "#c8c8d8",
    marginBottom: 12,
  },
  groupTitle: {
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: 0.6,
    textTransform: "uppercase",
    color: "#5a5a6a",
    margin: "0 0 8px",
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
    padding: "16px 20px",
    transition: "border-color 0.2s, transform 0.2s",
  },
  stageBadge: {
    display: "inline-block",
    padding: "4px 12px",
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 700,
  },
  drawRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
    flexWrap: "wrap",
  },
  drawBtn: {
    background: `linear-gradient(135deg, ${OJAJ_ACCENT}, #f5a623)`,
    color: "#0d0d14",
    border: "none",
    borderRadius: 10,
    padding: "10px 28px",
    fontSize: 15,
    fontWeight: 700,
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
  },
  resultRow: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    fontSize: 14,
    padding: "6px 0",
    borderTop: "1px solid #1e1e2e",
  },
};
