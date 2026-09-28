import * as s from "./taskStyles";

const DEFAULT_OPTIONS = ["T", "F", "NI"];

function getItemResult(taskResult, itemId) {
  return taskResult?.items?.find((r) => r.id === itemId);
}

export default function TrueFalseNI({ task, answers, onChange, showResults, taskResult }) {
  const items = task.items || [];
  const vocabItems = task.vocabItems || [];
  // Most papers offer T, F and "not in the text"; some offer only T and F, and
  // showing a column that is never the answer changes what the task asks.
  const OPTIONS = task.options || DEFAULT_OPTIONS;

  return (
    <div style={s.card}>
      <p style={s.instruction}>{task.instruction}</p>
      {task.title && <p style={s.passageTitle}>{task.title}</p>}
      {task.text && <div style={s.text}>{task.text}</div>}

      <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: vocabItems.length ? 20 : 0 }}>
        <thead>
          <tr>
            <th style={thStyle}></th>
            {OPTIONS.map((o) => (
              <th key={o} style={{ ...thStyle, textAlign: "center", width: 60 }}>{o}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const ir = getItemResult(taskResult, item.id);
            return (
              <tr key={item.id} style={rowStyle(showResults, ir)}>
                <td style={tdStyle}>
                  <span style={{ color: "#7a7a90", marginRight: 8 }}>{item.id}</span>
                  {item.statement}
                </td>
                {OPTIONS.map((o) => (
                  <td key={o} style={{ ...tdStyle, textAlign: "center" }}>
                    <input
                      type="radio"
                      name={`tfni-${item.id}`}
                      checked={answers[item.id] === o}
                      onChange={() => onChange(item.id, o)}
                      disabled={showResults}
                      style={{ accentColor: showResults && ir ? (ir.correct ? "#50d890" : "#e05050") : "#42b4f5" }}
                    />
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>

      {showResults && items.map((item) => {
        const ir = getItemResult(taskResult, item.id);
        if (!ir) return null;
        return (
          <div key={item.id} style={{ marginBottom: 10, padding: "8px 12px", borderRadius: 6, background: ir.correct ? "#50d89010" : "#e0505010" }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: ir.correct ? "#50d890" : "#e05050", marginBottom: 4 }}>
              {item.id}: {ir.correct ? "Correct" : `Correct answer: ${ir.correctAnswer}`}
            </div>
            {item.explanation && (
              <div style={{ fontSize: 13, color: "#a0a0b8", lineHeight: 1.5 }}>{item.explanation}</div>
            )}
          </div>
        );
      })}

      {vocabItems.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <p style={{ ...s.instruction, fontSize: 13, marginBottom: 12 }}>
            Znajdz w tekscie wyrazy odpowiadajace definicjom:
          </p>
          {vocabItems.map((item) => {
            const ir = getItemResult(taskResult, item.id);
            const inputStyle = showResults && ir
              ? (ir.correct ? s.inputCorrect : s.inputWrong)
              : s.input;
            return (
              <div key={item.id} style={{ marginBottom: 10, display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                <span style={{ color: "#7a7a90", fontSize: 13, minWidth: 32 }}>{item.id}</span>
                <span style={{ color: "#c8c8d8", fontSize: 13, flex: 1, minWidth: 200 }}>{item.definition}</span>
                <input
                  style={{ ...inputStyle, width: 180 }}
                  value={answers[item.id] || ""}
                  onChange={(e) => onChange(item.id, e.target.value)}
                  disabled={showResults}
                  placeholder="..."
                />
                {showResults && ir && !ir.correct && (
                  <span style={s.correctAnswer}>{ir.correctAnswer}</span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

const thStyle = { padding: "8px 12px", borderBottom: "1px solid #1e1e2e", color: "#7a7a90", fontSize: 13, fontWeight: 600, textAlign: "left" };
const tdStyle = { padding: "10px 12px", borderBottom: "1px solid #1e1e2e", fontSize: 14, color: "#c8c8d8" };
function rowStyle(show, ir) {
  if (!show || !ir) return {};
  return { background: ir.correct ? "#50d89008" : "#e0505008" };
}
