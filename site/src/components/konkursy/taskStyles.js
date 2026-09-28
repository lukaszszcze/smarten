export const card = {
  background: "#13131a",
  border: "1px solid #1e1e2e",
  borderRadius: 12,
  padding: "20px 24px",
  marginBottom: 0,
};

export const instruction = {
  fontSize: 14,
  color: "#9a9ab0",
  lineHeight: 1.7,
  marginBottom: 16,
};

// Headline printed above a reading passage. The papers put it in task.title.
export const passageTitle = {
  color: "#e8e8f0",
  fontWeight: 700,
  fontSize: 15,
  marginBottom: 12,
};

export const text = {
  fontSize: 14,
  color: "#c8c8d8",
  lineHeight: 1.8,
  whiteSpace: "pre-wrap",
  marginBottom: 16,
  padding: "16px",
  background: "#0d0d14",
  borderRadius: 8,
  border: "1px solid #1e1e2e",
};

export const input = {
  background: "#0d0d14",
  border: "1px solid #2a2a3e",
  borderRadius: 6,
  padding: "6px 10px",
  color: "#e8e8f0",
  fontSize: 14,
  fontFamily: "'DM Sans', sans-serif",
  outline: "none",
  width: 120,
};

export const inputCorrect = {
  ...input,
  borderColor: "#50d890",
  background: "#50d89015",
};

export const inputWrong = {
  ...input,
  borderColor: "#e05050",
  background: "#e0505015",
};

// A typed word that was one letter out. Quest practice counts it right and shows
// the spelling next to it; the competition players never produce this state.
export const inputNearMiss = {
  ...input,
  borderColor: "#f0a020",
  background: "#f0a02018",
};

export const radioLabel = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  padding: "8px 12px",
  borderRadius: 8,
  cursor: "pointer",
  fontSize: 14,
  color: "#c8c8d8",
  border: "1px solid transparent",
  transition: "all 0.15s",
};

export const radioSelected = {
  ...radioLabel,
  background: "#1e1e2e",
  borderColor: "#3a3a5e",
};

export const radioCorrect = {
  ...radioLabel,
  background: "#50d89015",
  borderColor: "#50d890",
};

export const radioWrong = {
  ...radioLabel,
  background: "#e0505015",
  borderColor: "#e05050",
};

export const correctAnswer = {
  fontSize: 12,
  color: "#50d890",
  marginTop: 2,
};
