import { useEffect, useMemo, useReducer, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useDocumentHead } from "../../hooks";
import { useUser } from "../../App";
import TaskRenderer from "../../components/konkursy/TaskRenderer";
import { saveAttempt } from "../../lib/resultsSync";
import { OJAJ_ACCENT } from "../../lib/ojaj";
import {
  initialPlayerState,
  isAnswered,
  markOnlineTest,
  onlineAttempt,
  onlineQuestions,
  onlineTestPath,
  playerReducer,
  secondsLeft,
} from "../../lib/ojajOnline";

// The player for online tests, copying the OJAJ platform (a Moodle quiz): one
// question per screen, "Nastepne" to go on, a numbered panel that jumps to any
// question, the clock top left, and "Zatwierdz wszystkie i zakoncz" with a
// confirmation. The test submits itself when the clock reaches 0:00.
//
// The rules (what can change when) are playerReducer's, tested in
// src/lib/ojajOnline.test.js; this page connects them to the clock, the
// marking and the renderers.

const TASK_NAMES = {
  word_formation: "Slowotworstwo",
  word_spelling: "Wisielec",
  sentence_transformation: "Transformacje zdan",
  multiple_choice: "Gramatyka i slownictwo",
  knowledge_questions: "Kultura Wielkiej Brytanii",
};

// Leaving the page while these are on screen loses the attempt.
const UNSAVED_PHASES = ["running", "marking", "failed"];

function formatClock(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function clockColor(seconds) {
  if (seconds < 300) return "#e05050";
  if (seconds < 600) return "#f5a623";
  return "#50d890";
}

function scoreColor(pct) {
  if (pct >= 70) return "#50d890";
  if (pct >= 40) return "#f5a623";
  return "#e05050";
}

export default function OjajOnlineTest() {
  const { id } = useParams();
  const user = useUser();
  const storageKey = `smarten_konkursy_${user?.name || "default"}`;
  const [test, setTest] = useState(null);
  const [loadFailed, setLoadFailed] = useState(false);
  const [state, dispatch] = useReducer(playerReducer, initialPlayerState);
  const [now, setNow] = useState(() => Date.now());
  const [confirming, setConfirming] = useState(false);

  useDocumentHead("Test online OJAJ", "OJAJ etap I, czesc II - test online");

  useEffect(() => {
    fetch(onlineTestPath(id))
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setTest)
      .catch(() => setLoadFailed(true));
  }, [id]);

  const questions = useMemo(() => (test ? onlineQuestions(test) : []), [test]);
  const { phase, current, answers, startedAt, result } = state;

  // The clock. It reads the wall clock on each tick, so a slowed background
  // tab still loses the time it was away.
  useEffect(() => {
    if (phase !== "running") return undefined;
    const tick = () => setNow(Date.now());
    tick();
    const timer = setInterval(tick, 500);
    return () => clearInterval(timer);
  }, [phase]);

  const limit = test ? test.timeMinutes : 0;
  const left = startedAt === null
    ? limit * 60
    : secondsLeft(startedAt, Math.max(now, startedAt), limit);

  useEffect(() => {
    if (phase === "running" && left === 0) {
      setConfirming(false);
      dispatch({ type: "submit" });
    }
  }, [phase, left]);

  // The marking, re-run on a retry. Nothing is saved until every task has a
  // mark: a transformation task the AI did not answer would be saved as 0.
  useEffect(() => {
    if (phase !== "marking") return undefined;
    let cancelled = false;
    markOnlineTest(test, answers)
      .then(({ result: marked, unmarkedTaskIds }) => {
        if (cancelled) return;
        if (unmarkedTaskIds.length > 0) {
          dispatch({ type: "markingFailed" });
          return;
        }
        saveAttempt(storageKey, user?.name, onlineAttempt(test, answers, marked));
        dispatch({ type: "marked", result: marked });
      })
      .catch(() => {
        if (!cancelled) dispatch({ type: "markingFailed" });
      });
    // Development mode runs every effect twice; the first run's answer is
    // dropped, so one submit saves one attempt.
    return () => {
      cancelled = true;
    };
    // The answers are locked from the submit on, so the phase alone decides.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase]);

  useEffect(() => {
    if (!UNSAVED_PHASES.includes(phase)) return undefined;
    const warn = (e) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [phase]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [current, phase]);

  if (loadFailed) {
    return (
      <div style={styles.page}>
        <Link to="/ojaj" style={styles.back}>&larr; Powrot do OJAJ</Link>
        <p style={{ color: "#7a7a90" }}>Nie ma takiego testu online.</p>
      </div>
    );
  }

  if (!test) {
    return (
      <div style={styles.page}>
        <p style={{ color: "#7a7a90" }}>Ladowanie testu...</p>
      </div>
    );
  }

  if (phase === "intro") {
    return <Intro test={test} onStart={() => dispatch({ type: "start", now: Date.now() })} />;
  }

  const running = phase === "running";
  const done = phase === "done";
  const unanswered = questions.filter((q) => !isAnswered(answers, q.item));
  const onChange = (itemId, value) => dispatch({ type: "answer", id: itemId, value });
  const question = questions[current];
  const isLast = current === questions.length - 1;

  // Every question's renderer stays mounted from the start to the review, so
  // a multiple choice keeps the option order it was first shown in. Inactive
  // ones are only hidden, and nothing above them changes shape.
  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
        rel="stylesheet"
      />

      <div style={styles.header}>
        {done ? (
          <Link to="/ojaj" style={{ ...styles.back, margin: 0 }}>&larr; OJAJ</Link>
        ) : (
          <span style={{ ...styles.clock, color: running ? clockColor(left) : "#7a7a90" }}>
            Pozostaly czas {formatClock(left)}
          </span>
        )}
        <span style={{ color: "#c8c8d8", fontWeight: 700, fontSize: 15 }}>{test.label}</span>
        {done && (
          <span style={{ color: scoreColor(result.percentage), fontWeight: 700, fontSize: 15 }}>
            {result.earned}/{result.max}
          </span>
        )}
      </div>

      {done && <ResultSummary test={test} result={result} />}
      {phase === "marking" && (
        <div style={styles.statusCard}>
          <p style={{ color: "#a78bfa", fontSize: 15, margin: 0 }}>
            Sprawdzanie odpowiedzi... Zadanie 3 (transformacje zdan) sprawdza AI,
            to moze potrwac do minuty.
          </p>
        </div>
      )}
      {phase === "failed" && (
        <div style={{ ...styles.statusCard, borderColor: "#f8717166" }}>
          <p style={{ color: "#f87171", fontSize: 15, lineHeight: 1.6, margin: "0 0 16px" }}>
            Nie udalo sie sprawdzic zadania 3 (transformacje zdan). Odpowiedzi sa
            zatwierdzone i nie mozna ich juz zmienic, a wynik nie jest jeszcze zapisany.
            Nie zamykaj tej strony.
          </p>
          <button style={styles.primaryBtn} onClick={() => dispatch({ type: "retry" })}>
            Sprawdz ponownie
          </button>
        </div>
      )}

      <div style={styles.layout}>
        <div style={styles.main}>
          {running && (
            <div style={styles.questionMeta}>
              <span style={{ color: "#e8e8f0", fontWeight: 700 }}>
                Pytanie {question.number} z {questions.length}
              </span>
              <span style={{ color: "#7a7a90" }}>
                Zadanie {question.task.id}: {TASK_NAMES[question.task.type]}
              </span>
            </div>
          )}
          {done && <h2 style={styles.sectionTitle}>Przeglad pytan</h2>}

          <div>
            {questions.map((q, i) => {
              const visible = running ? i === current : done;
              const taskResult = done
                ? result.tasks.find((r) => r.taskId === q.task.id)
                : undefined;
              // In the review the instruction is printed once per task.
              const task = done && !q.firstOfTask ? { ...q.task, instruction: "" } : q.task;
              return (
                <div
                  key={q.number}
                  style={{ display: visible ? "block" : "none", marginBottom: done ? 12 : 0 }}
                >
                  {done && q.firstOfTask && (
                    <TaskHeading task={q.task} taskResult={taskResult} />
                  )}
                  <TaskRenderer
                    task={task}
                    answers={answers}
                    onChange={onChange}
                    showResults={done}
                    taskResult={taskResult}
                  />
                </div>
              );
            })}
          </div>

          {running && (
            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 16 }}>
              {isLast ? (
                <button style={styles.primaryBtn} onClick={() => setConfirming(true)}>
                  Zatwierdz wszystkie i zakoncz
                </button>
              ) : (
                <button
                  style={styles.primaryBtn}
                  onClick={() => dispatch({ type: "go", index: current + 1 })}
                >
                  Nastepne
                </button>
              )}
            </div>
          )}
          {done && (
            <div style={{ textAlign: "center", marginTop: 32 }}>
              <Link to="/ojaj" style={styles.primaryBtn}>Powrot do OJAJ</Link>
            </div>
          )}
        </div>

        {running && (
          <aside style={styles.panel}>
            <div style={{ color: "#c8c8d8", fontSize: 13, fontWeight: 700, marginBottom: 10 }}>
              Nawigacja
            </div>
            <div style={styles.panelGrid}>
              {questions.map((q, i) => (
                <button
                  key={q.number}
                  onClick={() => dispatch({ type: "go", index: i })}
                  title={isAnswered(answers, q.item) ? "Odpowiedz zapisana" : "Brak odpowiedzi"}
                  style={{
                    ...styles.panelBtn,
                    ...(isAnswered(answers, q.item) ? styles.panelBtnAnswered : {}),
                    ...(i === current ? styles.panelBtnCurrent : {}),
                  }}
                >
                  {q.number}
                </button>
              ))}
            </div>
            <button
              style={{ ...styles.secondaryBtn, width: "100%", marginTop: 14 }}
              onClick={() => setConfirming(true)}
            >
              Zatwierdz wszystkie i zakoncz
            </button>
          </aside>
        )}
      </div>

      {running && confirming && (
        <div style={styles.overlay}>
          <div style={styles.dialog}>
            <h2 style={{ ...styles.sectionTitle, marginTop: 0 }}>Zatwierdz wszystkie i zakoncz</h2>
            <p style={{ color: "#c8c8d8", fontSize: 14, lineHeight: 1.6 }}>
              Po zatwierdzeniu odpowiedzi nie da sie juz zmienic.
            </p>
            {unanswered.length > 0 && (
              <p style={{ color: "#f5a623", fontSize: 14, lineHeight: 1.6 }}>
                Bez odpowiedzi: {unanswered.length} z {questions.length} (
                {unanswered.map((q) => q.number).join(", ")}).
              </p>
            )}
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 16 }}>
              <button
                style={styles.primaryBtn}
                onClick={() => {
                  setConfirming(false);
                  dispatch({ type: "submit" });
                }}
              >
                Zatwierdz wszystkie i zakoncz
              </button>
              <button style={styles.secondaryBtn} onClick={() => setConfirming(false)}>
                Wroc do testu
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Intro({ test, onStart }) {
  const count = test.tasks.reduce((n, t) => n + t.items.length, 0);
  return (
    <div style={styles.page}>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Playfair+Display:wght@700;900&display=swap"
        rel="stylesheet"
      />
      <Link to="/ojaj" style={styles.back}>&larr; Powrot do OJAJ</Link>
      <h1 style={styles.title}>Etap I, czesc II - test online</h1>
      <p style={styles.subtitle}>{test.label}</p>
      <div style={styles.infoCard}>
        <div style={styles.infoRow}><span>Pytania</span><strong>{count}</strong></div>
        <div style={styles.infoRow}><span>Czas</span><strong>{test.timeMinutes} minut</strong></div>
        <div style={{ ...styles.infoRow, borderBottom: "none" }}>
          <span>Punktacja</span><strong>1 pkt za pytanie</strong>
        </div>
      </div>
      <ul style={styles.rules}>
        <li>Zadania wlasne aplikacji, w formacie testu online OJAJ.</li>
        <li>
          Na ekranie jest jedno pytanie. &quot;Nastepne&quot; przechodzi dalej, a panel
          z numerami pozwala wrocic do kazdego pytania.
        </li>
        <li>Po {test.timeMinutes} minutach test zatwierdzi sie sam.</li>
        <li>Zadanie 3 sprawdza AI, wiec wynik pojawi sie chwile po zatwierdzeniu.</li>
      </ul>
      <button onClick={onStart} style={styles.primaryBtn}>Rozpocznij test</button>
    </div>
  );
}

function ResultSummary({ test, result }) {
  return (
    <div style={{
      ...styles.statusCard,
      borderColor: scoreColor(result.percentage),
      textAlign: "center",
    }}>
      <div style={styles.resultScore}>{result.earned}/{result.max}</div>
      <div style={{ color: "#c8c8d8", fontSize: 18, fontWeight: 700, marginBottom: 16 }}>
        {result.percentage}%
      </div>
      <div style={{
        display: "flex", flexDirection: "column", gap: 6, maxWidth: 360, margin: "0 auto",
      }}>
        {test.tasks.map((task) => {
          const r = result.tasks.find((t) => t.taskId === task.id);
          return (
            <div key={task.id} style={styles.summaryRow}>
              <span>{task.id}. {TASK_NAMES[task.type]}</span>
              <strong style={{ color: scoreColor(r.max > 0 ? (100 * r.earned) / r.max : 0) }}>
                {r.earned}/{r.max}
              </strong>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function TaskHeading({ task, taskResult }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", margin: "20px 0 8px" }}>
      <span style={{ color: "#e8e8f0", fontSize: 16, fontWeight: 700 }}>
        Zadanie {task.id}: {TASK_NAMES[task.type]}
      </span>
      <span style={{ color: "#7a7a90", fontSize: 13, fontWeight: 600 }}>
        {taskResult.earned}/{taskResult.max} pkt
      </span>
    </div>
  );
}

const button = {
  display: "inline-block",
  border: "none",
  borderRadius: 10,
  padding: "12px 28px",
  fontSize: 15,
  fontWeight: 700,
  cursor: "pointer",
  fontFamily: "'DM Sans', sans-serif",
  textDecoration: "none",
};

const styles = {
  page: {
    maxWidth: 960,
    margin: "0 auto",
    padding: "20px 16px 60px",
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
    padding: "8px 20px",
    marginBottom: 16,
    maxWidth: 480,
  },
  infoRow: {
    display: "flex",
    justifyContent: "space-between",
    padding: "10px 0",
    borderBottom: "1px solid #1e1e2e",
    color: "#c8c8d8",
    fontSize: 15,
  },
  rules: {
    color: "#9a9ab0",
    fontSize: 14,
    lineHeight: 1.7,
    paddingLeft: 20,
    marginBottom: 24,
    maxWidth: 560,
  },
  header: {
    position: "sticky",
    top: 0,
    zIndex: 100,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    flexWrap: "wrap",
    background: "#0d0d14ee",
    backdropFilter: "blur(10px)",
    padding: "10px 16px",
    borderRadius: 10,
    marginBottom: 20,
    border: "1px solid #1e1e2e",
  },
  clock: { fontFamily: "monospace", fontSize: 16, fontWeight: 700 },
  statusCard: {
    background: "#13131a",
    border: "2px solid #1e1e2e",
    borderRadius: 16,
    padding: 24,
    marginBottom: 24,
  },
  resultScore: {
    fontSize: 36,
    fontWeight: 900,
    color: "#e8e8f0",
    fontFamily: "'Playfair Display', serif",
  },
  summaryRow: {
    display: "flex",
    justifyContent: "space-between",
    color: "#c8c8d8",
    fontSize: 14,
    padding: "4px 0",
    borderBottom: "1px solid #1e1e2e",
  },
  layout: {
    display: "flex",
    flexWrap: "wrap",
    gap: 20,
    alignItems: "flex-start",
  },
  main: { flex: "1 1 480px", minWidth: 0 },
  questionMeta: {
    display: "flex",
    justifyContent: "space-between",
    flexWrap: "wrap",
    gap: 8,
    fontSize: 14,
    marginBottom: 10,
  },
  sectionTitle: { fontSize: 18, fontWeight: 700, color: "#c8c8d8", marginBottom: 12 },
  panel: {
    flex: "0 1 230px",
    background: "#13131a",
    border: "1px solid #1e1e2e",
    borderRadius: 12,
    padding: 14,
  },
  panelGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gap: 6,
  },
  panelBtn: {
    padding: "6px 0",
    fontSize: 13,
    fontWeight: 600,
    borderRadius: 6,
    border: "1px solid #2a2a3e",
    background: "#0d0d14",
    color: "#7a7a90",
    cursor: "pointer",
    fontFamily: "'DM Sans', sans-serif",
  },
  panelBtnAnswered: { background: "#2a2a3e", color: "#e8e8f0" },
  panelBtnCurrent: { border: `2px solid ${OJAJ_ACCENT}` },
  primaryBtn: {
    ...button,
    background: "linear-gradient(135deg, #50d890, #42b4f5)",
    color: "#0d0d14",
  },
  secondaryBtn: {
    ...button,
    background: "#1e1e2e",
    color: "#c8c8d8",
    border: "1px solid #2a2a3e",
    padding: "10px 16px",
    fontSize: 14,
  },
  overlay: {
    position: "fixed",
    inset: 0,
    zIndex: 200,
    background: "#0a0a12cc",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
  },
  dialog: {
    background: "#13131a",
    border: "1px solid #2a2a3e",
    borderRadius: 14,
    padding: 24,
    maxWidth: 460,
    width: "100%",
  },
};
