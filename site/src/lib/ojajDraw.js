// The draw: an online test put together from the vault of own items, aimed at
// the user's mistakes (CONTEXT.md: vault, draw, repeat).
//
// Each task is filled in three steps:
//   1. same item: items whose latest answer was a miss come back word for
//      word, likelier the more often they were missed;
//   2. same type: unseen items of the types he misses, likelier the weaker the
//      type (typeShare), until the task has its repeats;
//   3. the rest: unseen items, and once those run out, the least seen.
// Every step keeps the task's level profile and idiom count reachable, and a
// repeat that would break them is skipped. Answer words are unique across the
// vault (tmp/_ojaj_online.py checks it), so no test holds one twice.

import { typeShare } from "./ojajRecord.js";

// Repeats per task: at most `total`, of which at most `sameItem` are items
// missed before. 3 and 2 in tasks 1-4; culture has one slot, so 13 of 45 at most.
const DEFAULT_REPEATS = { total: 3, sameItem: 2 };
const REPEATS = { knowledge_questions: { total: 1, sameItem: 1 } };

function shuffle(xs) {
  const out = [...xs];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

// One of `options` ({item, weight}, every weight above 0), with chance
// proportional to its weight.
function pickWeighted(options) {
  let r = Math.random() * options.reduce((s, o) => s + o.weight, 0);
  for (const option of options.slice(0, -1)) {
    r -= option.weight;
    if (r < 0) return option.item;
  }
  return options[options.length - 1].item;
}

/**
 * Whether `chosen` can still grow into a task that meets its profile, using
 * items from `pool`: the task's count, each level within its range (`levels`,
 * e.g. {C1: [4, 5]}) and the idiom, collocation and phrasal verb items within
 * `focus`. A task with neither range only needs the count.
 */
function completable(task, chosen, pool) {
  const left = task.count - chosen.length;
  if (left < 0 || pool.length < left) return false;
  if (task.levels) {
    if (chosen.some((it) => !(it.level in task.levels))) return false;
    let need = 0;
    let room = 0;
    for (const [level, [min, max]] of Object.entries(task.levels)) {
      const have = chosen.filter((it) => it.level === level).length;
      const avail = pool.filter((it) => it.level === level).length;
      if (have > max || min - have > avail) return false;
      need += Math.max(0, min - have);
      room += Math.min(max - have, avail);
    }
    if (need > left || room < left) return false;
  }
  if (task.focus) {
    const [min, max] = task.focus;
    const have = chosen.filter((it) => it.focus).length;
    const withFocus = pool.filter((it) => it.focus).length;
    // How many of the remaining picks can be focus items.
    const fewest = Math.max(0, min - have, left - (pool.length - withFocus));
    const most = Math.min(withFocus, max - have, left);
    if (fewest > most) return false;
  }
  return true;
}

// The first way, in `order`, to complete `chosen`; null when there is none.
function fill(task, chosen, order) {
  if (chosen.length === task.count) return chosen;
  for (let i = 0; i < order.length; i++) {
    const next = [...chosen, order[i]];
    const rest = order.slice(i + 1);
    if (!completable(task, next, rest)) continue;
    const done = fill(task, next, rest);
    if (done) return done;
  }
  return null;
}

function drawTask(task, record) {
  const caps = REPEATS[task.type] || DEFAULT_REPEATS;
  const seen = (it) => record.items[it.id];
  const chosen = [];
  const left = () => task.items.filter((it) => !chosen.includes(it));

  const repeat = (candidates, weight, slots) => {
    for (let n = 0; n < slots; n++) {
      const options = candidates
        .filter((it) => !chosen.includes(it) && weight(it) > 0)
        .filter((it) => completable(task, [...chosen, it], left().filter((x) => x !== it)))
        .map((it) => ({ item: it, weight: weight(it) }));
      if (options.length === 0) return;
      chosen.push(pickWeighted(options));
    }
  };

  repeat(task.items.filter((it) => seen(it)?.lastCorrect === false),
    (it) => seen(it).misses, caps.sameItem);
  repeat(task.items.filter((it) => !seen(it)),
    (it) => (record.types[it.mistakeType] ? typeShare(record.types[it.mistakeType]) : 0),
    caps.total - chosen.length);

  // Unseen first, in random order; a seen item only when the unseen ones cannot
  // complete the task, the least seen first. Tier by tier, since one search
  // over everything would take the first completion it finds, which can hold
  // a seen item where an all-unseen one exists.
  const rest = left();
  const bySeen = new Map();
  for (const it of rest.filter(seen)) {
    const n = seen(it).seen;
    bySeen.set(n, [...(bySeen.get(n) || []), it]);
  }
  const tiers = [
    shuffle(rest.filter((it) => !seen(it))),
    ...[...bySeen.keys()].sort((a, b) => a - b).map((n) => shuffle(bySeen.get(n))),
  ];
  let order = [];
  let done = null;
  for (const tier of tiers) {
    order = [...order, ...tier];
    done = fill(task, chosen, order);
    if (done) break;
  }
  if (!done) {
    throw new Error(`cannot put task ${task.id} together: the vault has too few items `
      + "of the levels or kinds its profile needs");
  }
  // Mixed, so a repeat's place does not give it away.
  return shuffle(done);
}

/**
 * An online test from items already chosen, in the shape the player and
 * scoreTest read: the vault's tasks in order, the questions numbered 1 up
 * through the test (the renderers print the id as the number), each item
 * keeping its vault id and whether it was in an earlier test.
 *
 * @param {object} vault the vault of own items (online/vault.json)
 * @param {object[][]} chosen the items of each vault task, in order
 * @param {object} record the user's mistake record (mistakeRecord)
 */
export function assembleTest(vault, chosen, record) {
  let number = 0;
  const tasks = vault.tasks.map((task, i) => ({
    id: task.id,
    type: task.type,
    points: chosen[i].length,
    instruction: task.instruction,
    items: chosen[i].map((item) => {
      number += 1;
      return { ...item, id: String(number), vaultId: item.id, seenBefore: !!record.items[item.id] };
    }),
  }));
  return {
    competition: "ojaj",
    kind: "online",
    label: vault.label,
    maxPoints: number,
    timeMinutes: vault.timeMinutes,
    tasks,
  };
}

/**
 * Draw an online test for one user.
 *
 * @param {object} vault the vault of own items
 * @param {object} record the user's mistake record, from synced attempts
 * @returns {object} the test, as assembleTest builds it
 * @throws when the vault cannot fill a task to its profile
 *
 * @example
 * const test = drawTest(vault, mistakeRecord(vault, attempts));
 */
export function drawTest(vault, record) {
  return assembleTest(vault, vault.tasks.map((task) => drawTask(task, record)), record);
}
