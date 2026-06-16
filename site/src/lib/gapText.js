// Shared gap-fill text parsing for the text-with-inline-inputs task renderers
// (open_cloze, word_formation).
//
// Competition data uses three gap-marker conventions:
//   1. "1.1. _________"  — sub-numbered gaps whose label equals the item id
//   2. "1. _________"    — single-number gaps in reading order; item ids are
//                          "{taskId}.{n}" so the label does NOT equal the id
//   3. bare "_________"  — no number at all
//
// parseGapText turns the text into an ordered list of parts. Each gap is mapped
// to an item by preferring an exact id match, then an id-suffix match
// (label "7" -> item "4.7"), then position. Suffix matching means a missing or
// reordered gap does not shift every later answer onto the wrong item.

// Optional "N." or "N.M." prefix immediately before a run of underscores.
const GAP_RE = /(?:(\d+(?:\.\d+)?)\.\s*)?_{2,}/g;

export function parseGapText(text, items = []) {
  const parts = [];
  if (!text) return parts;

  let last = 0;
  let match;
  let gapIndex = 0;
  GAP_RE.lastIndex = 0;
  while ((match = GAP_RE.exec(text)) !== null) {
    if (match.index > last) {
      parts.push({ type: "text", value: text.slice(last, match.index) });
    }
    const label = match[1];
    // Map the gap to its item by, in order of preference:
    //   1. exact id match      ("1.1" -> item "1.1")            [sub-numbered]
    //   2. id-suffix match     ("7"   -> item "4.7")            [single-number]
    //   3. positional fallback (bare "___" with no number)
    let item = null;
    if (label) {
      item = items.find((it) => String(it.id) === label)
        || items.find((it) => String(it.id).endsWith("." + label));
    }
    if (!item) item = items[gapIndex];
    parts.push({
      type: "gap",
      item,
      id: item ? String(item.id) : label || String(gapIndex),
    });
    gapIndex++;
    last = GAP_RE.lastIndex;
  }
  if (last < text.length) {
    parts.push({ type: "text", value: text.slice(last) });
  }
  return parts;
}

// Split a single sentence on its gap marker into { before, after } around one
// blank. Used by the per-sentence word_formation shape (each item carries its
// own sentence rather than sharing one task.text).
export function splitSentenceGap(sentence) {
  const text = String(sentence || "");
  const m = text.match(/_{2,}/);
  if (!m) return { before: text, after: "" };
  return { before: text.slice(0, m.index), after: text.slice(m.index + m[0].length) };
}
