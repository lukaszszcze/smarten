import TrueFalseNI from "./TrueFalseNI";
import GapFillSentences from "./GapFillSentences";
import MultipleChoice from "./MultipleChoice";
import OpenCloze from "./OpenCloze";
import WordSpelling from "./WordSpelling";
import WordFormation from "./WordFormation";
import Matching from "./Matching";
import MatchingColumns from "./MatchingColumns";
import KnowledgeQuestions from "./KnowledgeQuestions";
import SentenceTransformation from "./SentenceTransformation";
import GrammarGaps from "./GrammarGaps";
import Writing from "./Writing";
import SkippedTask from "./SkippedTask";

const COMPONENTS = {
  true_false_ni: TrueFalseNI,
  gap_fill_sentences: GapFillSentences,
  multiple_choice: MultipleChoice,
  dialogue_choice: MultipleChoice,
  open_cloze: OpenCloze,
  word_spelling: WordSpelling,
  word_formation: WordFormation,
  matching: Matching,
  matching_columns: MatchingColumns,
  knowledge_questions: KnowledgeQuestions,
  sentence_transformation: SentenceTransformation,
  grammar_gaps: GrammarGaps,
  writing: Writing,
};

const SKIPPED_TYPES = [
  "listening_true_false_ni",
  "listening_open",
];

// These types have items but need AI to grade
// (open_cloze + word_formation are AI-graded so synonyms / spelling variants
// beyond the official answer key can be accepted.)
export const AI_CHECKED_TYPES = [
  "sentence_transformation",
  "grammar_gaps",
  "writing",
  "open_cloze",
  "word_formation",
];

export default function TaskRenderer({ task, answers, onChange, showResults, taskResult }) {
  // Only skip if type is truly unrenderable (listening) or has no items and is marked skipped
  const isListening = SKIPPED_TYPES.includes(task.type);
  const isAIType = AI_CHECKED_TYPES.includes(task.type);
  const hasNoItems = !task.items || task.items.length === 0;

  if (isListening || (task.skipped && !isAIType) || (isAIType && hasNoItems)) {
    return <SkippedTask task={task} />;
  }

  const Comp = COMPONENTS[task.type];
  if (!Comp) {
    return (
      <div style={styles.unknown}>
        <p>Nieobsługiwany typ zadania: <code>{task.type}</code></p>
      </div>
    );
  }

  return <Comp task={task} answers={answers} onChange={onChange} showResults={showResults} taskResult={taskResult} />;
}

const styles = {
  unknown: {
    padding: 20,
    background: "#1a1a2e",
    borderRadius: 10,
    border: "1px solid #2a2a3e",
    color: "#7a7a90",
  },
};
