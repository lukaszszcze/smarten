import * as s from "./taskStyles";

function getItemResult(taskResult, itemId) {
  return taskResult?.items?.find((r) => r.id === itemId);
}

export default function WordSpelling({ task, answers, onChange, showResults, taskResult }) {
  const items = task.items || [];

  return (
    <div style={s.card}>
      <p style={s.instruction}>{task.instruction}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {items.map((item) => {
          const ir = getItemResult(taskResult, item.id);
          const inputStyle = showResults && ir
            ? (ir.nearMiss ? s.inputNearMiss : ir.correct ? s.inputCorrect : s.inputWrong)
            : s.input;
          return (
            <div key={item.id}>
              <p style={{ color: "#c8c8d8", fontSize: 14, lineHeight: 1.7, marginBottom: 6 }}>
                <span style={{ color: "#7a7a90", marginRight: 8 }}>{item.id}</span>
                {/* The papers name this field three ways; all three hold the
                    sentence with the letter pattern already inside it. Without
                    the fallbacks the row is a bare number and a blank box. */}
                {item.stem || item.clue || item.sentence}
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 10, paddingLeft: 8 }}>
                <input
                  style={{ ...inputStyle, width: 180 }}
                  value={answers[item.id] || ""}
                  onChange={(e) => onChange(item.id, e.target.value)}
                  disabled={showResults}
                  placeholder="wpisz slowo..."
                />
                {showResults && ir && !ir.correct && (
                  <span style={s.correctAnswer}>{ir.correctAnswer}</span>
                )}
                {showResults && ir?.nearMiss && (
                  <span style={{ ...s.correctAnswer, color: "#f0a020" }}>
                    nearly — it is spelt {ir.correctAnswer}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
