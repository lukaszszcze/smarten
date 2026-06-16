import * as s from "./taskStyles";
import { parseGapText, splitSentenceGap } from "../../lib/gapText";

export default function WordFormation({ task, answers, onChange, showResults, taskResult }) {
  const items = task.items || [];
  const wordBank = task.wordBank || [];
  // Per-sentence shape: no shared text, each item carries its own sentence.
  const perSentence = !task.text && items.some((it) => it.sentence);

  return (
    <div style={s.card}>
      <p style={s.instruction}>{task.instruction}</p>

      {wordBank.length > 0 && (
        <div style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 8,
          marginBottom: 16,
          padding: 12,
          background: "#0d0d14",
          borderRadius: 8,
          border: "1px solid #1e1e2e",
        }}>
          {wordBank.map((word) => (
            <span key={word} style={{
              padding: "4px 10px",
              borderRadius: 6,
              background: "#1e1e2e",
              color: "#c8c8d8",
              fontSize: 13,
              fontWeight: 600,
            }}>{word}</span>
          ))}
        </div>
      )}

      {task.title && <p style={{ color: "#e8e8f0", fontWeight: 700, fontSize: 15, marginBottom: 12 }}>{task.title}</p>}

      {perSentence
        ? <SentenceList items={items} answers={answers} onChange={onChange} showResults={showResults} taskResult={taskResult} />
        : task.text && <div style={s.text}>{renderWordFormationText(task.text, items, answers, onChange, showResults, taskResult)}</div>}
    </div>
  );
}

function GapInput({ id, answers, onChange, showResults, taskResult }) {
  const ir = taskResult?.items?.find((r) => r.id === id);
  const inputStyle = showResults && ir ? (ir.correct ? s.inputCorrect : s.inputWrong) : s.input;
  return (
    <span style={{ display: "inline-flex", alignItems: "center", margin: "0 2px" }}>
      <span style={{ color: "#7a7a90", fontSize: 11, marginRight: 2 }}>{id}</span>
      <input
        style={{ ...inputStyle, width: 120 }}
        value={answers[id] || ""}
        onChange={(e) => onChange(id, e.target.value)}
        disabled={showResults}
      />
      {showResults && ir && !ir.correct && <span style={{ ...s.correctAnswer, marginLeft: 4 }}>{ir.correctAnswer}</span>}
    </span>
  );
}

// Flowing-text shape: one task.text with inline gaps.
function renderWordFormationText(text, items, answers, onChange, showResults, taskResult) {
  const parts = parseGapText(text, items);
  return parts.map((part, i) => {
    if (part.type === "text") return <span key={i}>{part.value}</span>;
    if (!part.item) return <span key={i}>[{part.id}]</span>;
    return (
      <GapInput key={i} id={part.id} answers={answers} onChange={onChange} showResults={showResults} taskResult={taskResult} />
    );
  });
}

// Per-sentence shape: each item is an independent sentence with its own base
// word and a single blank.
function SentenceList({ items, answers, onChange, showResults, taskResult }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {items.map((item) => {
        const id = String(item.id);
        const base = item.wordBase || item.baseWord;
        const { before, after } = splitSentenceGap(item.sentence);
        return (
          <div key={id} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {base && (
              <span style={{
                alignSelf: "flex-start",
                padding: "2px 10px",
                borderRadius: 6,
                background: "#1e1e2e",
                color: "#c8c8d8",
                fontSize: 12,
                fontWeight: 700,
                letterSpacing: 0.5,
              }}>{base}</span>
            )}
            <div style={{ ...s.text, lineHeight: 2.2 }}>
              <span>{before}</span>
              <GapInput id={id} answers={answers} onChange={onChange} showResults={showResults} taskResult={taskResult} />
              <span>{after}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
