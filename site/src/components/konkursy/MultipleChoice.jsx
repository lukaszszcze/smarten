import { useMemo } from "react";
import * as s from "./taskStyles";

const LETTERS = ["A", "B", "C", "D"];

function getItemResult(taskResult, itemId) {
  return taskResult?.items?.find((r) => r.id === itemId);
}

function shuffleItemOptions(item) {
  const rawOpts = item.options.map((opt) => opt.replace(/^[A-D]\)\s*/, ""));
  const order = rawOpts.map((_, i) => i);
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  const correctOrigIdx = LETTERS.indexOf(item.answer);
  const newCorrectIdx = order.indexOf(correctOrigIdx);
  return {
    ...item,
    options: order.map((i) => rawOpts[i]),
    answer: LETTERS[newCorrectIdx],
    _toOriginalLetter: order.map((i) => LETTERS[i]),
  };
}

export default function MultipleChoice({ task, answers, onChange, showResults, taskResult }) {
  const shuffledItems = useMemo(
    () => (task.items || []).map(shuffleItemOptions),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [task.id]
  );

  return (
    <div style={s.card}>
      <p style={s.instruction}>{task.instruction}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        {shuffledItems.map((item) => {
          const ir = getItemResult(taskResult, item.id);
          return (
            <div key={item.id}>
              <p style={{ color: "#c8c8d8", fontSize: 14, lineHeight: 1.7, marginBottom: 8, whiteSpace: "pre-wrap" }}>
                <span style={{ color: "#7a7a90", marginRight: 8 }}>{item.id}</span>
                {item.stem || item.prompt}
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: 4, paddingLeft: 8 }}>
                {item.options.map((opt, i) => {
                  const letter = LETTERS[i];
                  const origLetter = item._toOriginalLetter[i];
                  const selected = answers[item.id] === origLetter;
                  const isCorrect = letter === item.answer;
                  let style = selected ? s.radioSelected : s.radioLabel;
                  if (showResults && ir) {
                    if (selected && ir.correct) style = s.radioCorrect;
                    else if (selected && !ir.correct) style = s.radioWrong;
                    else if (isCorrect) style = s.radioCorrect;
                  }
                  return (
                    <div
                      key={letter}
                      style={style}
                      onClick={() => !showResults && onChange(item.id, origLetter)}
                    >
                      <span style={{
                        width: 18,
                        height: 18,
                        borderRadius: "50%",
                        border: `2px solid ${selected ? "#42b4f5" : "#3a3a5e"}`,
                        background: selected ? "#42b4f5" : "transparent",
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        flexShrink: 0,
                        transition: "all 0.15s",
                      }}>
                        {selected && <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#0d0d14" }} />}
                      </span>
                      <span style={{ fontWeight: 600, color: "#7a7a90", minWidth: 20 }}>{letter}.</span>
                      {opt}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
