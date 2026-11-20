// Click through the online tests in a real browser: the OJAJ page, the draw,
// the player, the marking, the review, the weak points and the history. The API
// is mocked and the OJAJ data is served from this checkout's pub/ (site/public
// links to the main checkout's data, which a worktree's dev server would
// otherwise serve).
//
// Each test is drawn, so the script finds every question it is shown in the
// vault by its text, and answers it from the key or, where a miss is wanted,
// wrongly. Three tests in a row: all right; four misses; then the misses must
// come back, marked "powtorka" in the review.
//
// Run, from the checkout root:
//   (cd site && npx vite --port 5179 --strictPort)   # in another shell
//   node tools/ojaj/e2e_online.mjs
// SHOTS=1 also saves screenshots to tmp/_shots/, at the width in WIDTH
// (default 1280).
//
// Playwright is borrowed, read-only, from another project's install.
import { chromium } from "/home/lukasz/workspace/smartfc/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "../..");
const DATA = path.join(ROOT, "pub/konkursy/angielski/data");
const BASE = "http://localhost:5179";
const readData = (rel) => JSON.parse(fs.readFileSync(path.join(DATA, rel), "utf8"));
const VAULT = readData("ojaj/online/vault.json");
const ITEMS = VAULT.tasks.flatMap((task) => task.items.map((item) => ({ task, item })));
const TOTAL = ITEMS.length;
const KEY = "smarten_konkursy_Tadzio";

const SHOTS = process.env.SHOTS === "1";
const WIDTH = Number(process.env.WIDTH || 1280);
async function shot(page, name) {
  if (!SHOTS) return;
  fs.mkdirSync(path.join(ROOT, "tmp/_shots"), { recursive: true });
  await page.screenshot({ path: path.join(ROOT, `tmp/_shots/${WIDTH}_${name}.png`), fullPage: false });
}

let failures = 0;
function check(cond, msg) {
  console.log(`  ${cond ? "ok  " : "FAIL"} ${msg}`);
  if (!cond) failures++;
}

const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const squash = (s) => s.replace(/\s+/g, " ").trim();

// The stretches of an item's prompt between its blanks, which is how it reads
// on screen whatever stands in for a blank. All of them have to be there: one
// alone can open another item's sentence ("Our teacher asked us").
const promptOf = (item) => item.sentence || item.stem || item.original || item.question;
const parts = (text) => text.split(/_{2,}/).map(squash).filter((p) => p.length >= 4);

async function onScreen(page) {
  const text = squash(await page.evaluate(() => document.body.innerText));
  const found = ITEMS.filter(({ item }) => parts(promptOf(item)).every((p) => text.includes(p)));
  if (found.length !== 1) throw new Error(`the question on screen matches ${found.length} vault items`);
  return found[0];
}

async function open(browser, { checkStatus = 200, clock = false, vaultMissing = false } = {}) {
  const context = await browser.newContext({ viewport: { width: WIDTH, height: 860 } });
  await context.addInitScript(() => localStorage.setItem("smarten_user", "Tadzio"));
  const page = await context.newPage();
  page.on("pageerror", (e) => check(false, `page error: ${e.message}`));
  if (clock) await page.clock.install({ time: new Date("2026-11-02T09:00:00Z") });
  const api = { posts: [], checks: [], puts: 0, checkStatus };

  await page.route("**/konkursy/angielski/data/**", (route) => {
    const rel = new URL(route.request().url()).pathname.replace("/konkursy/angielski/data/", "");
    const file = path.join(DATA, rel);
    if (!fs.existsSync(file) || (vaultMissing && rel.endsWith("vault.json"))) {
      return route.fulfill({ status: 404, body: "not found" });
    }
    return route.fulfill({ status: 200, contentType: "application/json", body: fs.readFileSync(file) });
  });
  await page.route("**/api/results**", (route) => {
    const req = route.request();
    if (req.method() === "GET") return route.fulfill({ json: [] });
    if (req.method() === "PUT") {
      api.puts++;
      return route.fulfill({ json: { attempts: JSON.parse(req.postData()).attempts } });
    }
    api.posts.push(JSON.parse(req.postData()));
    return route.fulfill({ json: { ok: true } });
  });
  // Marks a listed phrasing correct and anything else wrong, as check.js does
  // before it asks the model.
  await page.route("**/api/check", (route) => {
    const body = JSON.parse(route.request().postData());
    api.checks.push(body.type);
    if (api.checkStatus !== 200) {
      return route.fulfill({ status: api.checkStatus, json: { error: "down" } });
    }
    const items = body.task.items.map((it) => {
      const accepted = it.answer.split(" / ").map((s) => s.trim().toLowerCase());
      const correct = accepted.includes(String(body.answers[it.id] || "").trim().toLowerCase());
      return { id: it.id, earned: correct ? 1 : 0, max: 1, correct, feedback: "", correctAnswer: it.answer };
    });
    return route.fulfill({ json: { items, earned: items.filter((i) => i.correct).length, max: items.length } });
  });
  return { page, context, api };
}

const keyText = ({ task, item }) => {
  if (task.type === "sentence_transformation") return item.answer.split(" / ")[0];
  if (Array.isArray(item.answer)) return item.answer[0];
  return item.options.find((o) => o.startsWith(item.answer)).replace(/^[A-D][.)]\s*/, "");
};
const wrongText = ({ task, item }) => {
  if (["multiple_choice", "knowledge_questions"].includes(task.type)) {
    return item.options.find((o) => !o.startsWith(item.answer)).replace(/^[A-D][.)]\s*/, "");
  }
  return `${keyText({ task, item })}x`;
};

// The option on screen whose whole text is "<letter>.<text>" or "<letter>. <text>".
const optionLocator = (page, text) =>
  page.locator("div:visible", { hasText: new RegExp(`^[A-D]\\.\\s*${escape(text)}$`) });

async function give(page, q, text) {
  if (["multiple_choice", "knowledge_questions"].includes(q.task.type)) {
    await optionLocator(page, text).click();
  } else {
    await page.locator("input:visible").fill(text);
  }
}

async function visibleOptions(page) {
  return page.locator("div:visible", { hasText: /^[A-D]\.\s*\S/ }).allTextContents();
}

async function storedOnline(page) {
  return page.evaluate((key) => {
    const stored = JSON.parse(localStorage.getItem(key) || "{}");
    return (stored.attempts || []).filter((a) => a.testId?.startsWith("ojaj/online/"));
  }, KEY);
}

const submitButton = (page) => page.locator("div").filter({ hasText: /^Zatwierdz wszystkie i zakoncz/ })
  .getByRole("button", { name: "Zatwierdz wszystkie i zakoncz" }).last();

// Plays one drawn test through the player. `miss(number, q)` says which
// questions to answer wrongly. Question 10 is left blank until the
// confirmation, which must name it. Returns the vault items shown, in order.
async function play(page, api, { miss = () => false, snap = async () => {} } = {}) {
  await page.getByText("Zadania wlasne aplikacji").waitFor();
  await snap(page, "02_intro");
  await page.getByRole("button", { name: "Rozpocznij test" }).click();
  await page.getByText("Pytanie 1 z 45").waitFor();
  await snap(page, "03_question_1");
  check(/Pozostaly czas 4[45]:\d\d/.test(await page.getByText(/Pozostaly czas/).textContent()),
    "the clock starts at 45 minutes");
  check(await page.getByRole("button", { name: "Poprzednie" }).count() === 0, "there is no Poprzednie button");
  check(await page.getByText("powtorka").count() === 0, "nothing is marked a repeat during the test");

  const shown = [];
  let choiceOrder = null;
  for (let n = 1; n <= 45; n++) {
    await page.getByText(`Pytanie ${n} z 45`).waitFor();
    const q = await onScreen(page);
    shown.push(q);
    if (n !== 10) await give(page, q, miss(n, q) ? wrongText(q) : keyText(q));
    if (n === 31) choiceOrder = await visibleOptions(page);
    if ([11, 21, 31, 41].includes(n)) await snap(page, `04_question_${n}`);
    if (n < 45) await page.getByRole("button", { name: "Nastepne" }).click();
  }
  check(await page.getByRole("button", { name: "Nastepne" }).count() === 0, "the last question has no Nastepne");
  check(new Set(shown.map((q) => q.item.id)).size === 45, "45 different vault items were shown");
  let start = 0;
  const inOrder = VAULT.tasks.every((task) => {
    const run = shown.slice(start, start + task.count);
    start += task.count;
    return run.every((q) => q.task === task);
  });
  check(inOrder, "the tasks come in order, each with its count of questions");

  // Back to an earlier question through the panel: the options keep their order.
  await page.locator("aside").getByRole("button", { name: "31", exact: true }).click();
  await page.getByText("Pytanie 31 z 45").waitFor();
  check(JSON.stringify(await visibleOptions(page)) === JSON.stringify(choiceOrder),
    "a multiple choice keeps its option order when revisited");
  check(await page.locator("aside").getByRole("button", { name: "10", exact: true })
    .getAttribute("title") === "Brak odpowiedzi", "the panel marks question 10 unanswered");

  await page.locator("aside").getByRole("button", { name: "Zatwierdz wszystkie i zakoncz" }).click();
  check(await page.getByText("Bez odpowiedzi: 1 z 45 (10).").isVisible(), "the confirmation names the blank question");
  await snap(page, "05_confirm");
  await page.getByRole("button", { name: "Wroc do testu" }).click();
  await page.locator("aside").getByRole("button", { name: "10", exact: true }).click();
  await give(page, shown[9], miss(10, shown[9]) ? wrongText(shown[9]) : keyText(shown[9]));
  await page.locator("aside").getByRole("button", { name: "Zatwierdz wszystkie i zakoncz" }).click();
  check(await page.getByText(/Bez odpowiedzi/).count() === 0, "with every answer given, no blank is listed");
  await submitButton(page).click();
  await page.getByText("Przeglad pytan").waitFor();
  check(JSON.stringify(api.checks.filter((t) => t !== "sentence_transformation")) === "[]",
    `only transformations went to the AI (${api.checks.join(", ")})`);
  return shown;
}

// The saved attempt: filed under the drawn testId, with every question's vault
// item and verdict, matching what was shown and given.
async function checkSaved(page, api, shown, missed, runs) {
  const saved = await storedOnline(page);
  check(saved.length === runs && api.posts.length === runs, `attempt ${runs} is stored and sent`);
  const last = saved[saved.length - 1];
  const sent = api.posts[api.posts.length - 1];
  check(last.testId === "ojaj/online/drawn", "filed under ojaj/online/drawn");
  check(JSON.stringify(sent.items) === JSON.stringify(last.items), "the results API got the verdicts too");
  check(JSON.stringify(last.items.map((i) => i.vaultId)) === JSON.stringify(shown.map((q) => q.item.id)),
    "each question's vault item is saved");
  check(last.items.every((i, k) => i.number === String(k + 1) && i.correct === !missed.has(i.vaultId)),
    `each question's verdict is saved (${missed.size} wrong)`);
}

async function threeRuns(browser) {
  const { page, context, api } = await open(browser);
  const seen = new Set();

  console.log("\nthe first test, every answer right");
  await page.goto(`${BASE}/ojaj`);
  await page.getByText("Etap I, czesc II - test online").waitFor();
  check(await page.getByText(`Nowe pytania w bazie: ${TOTAL} z ${TOTAL}`).isVisible(),
    `the OJAJ page shows all ${TOTAL} questions new`);
  check(await page.getByText("Twoje slabe punkty").count() === 0, "and no weak points yet");
  check(await page.locator('a[href^="/ojaj/online"]').count() === 0, "no online test is listed as a link");
  await shot(page, "01_ojaj_page");
  const putsBefore = api.puts;
  await page.getByRole("button", { name: "Losuj test" }).click();
  await page.waitForURL(/\/ojaj\/online$/);
  let shown = await play(page, api, { snap: shot });
  check(api.puts > putsBefore, "the attempts were synced before the draw");
  await shot(page, "06_result");
  check(await page.getByText("45/45", { exact: true }).first().isVisible(), "the key scores 45/45");
  for (const [n, name, max] of [[1, "Slowotworstwo", 10], [2, "Wisielec", 10],
    [3, "Transformacje zdan", 10], [4, "Gramatyka i slownictwo", 10], [5, "Kultura Wielkiej Brytanii", 5]]) {
    check(await page.getByText(`${n}. ${name}`).isVisible(), `the summary lists task ${n}`);
    check(await page.getByText(`${max}/${max} pkt`).count() >= 1, `task ${n} scores ${max}/${max}`);
  }
  check(await page.getByText("powtorka", { exact: true }).count() === 0, "a first test has no repeats");
  check(await page.getByText(/Nowe pytania:/).count() === 0, "and no separate score on new questions");
  check(await page.locator("input:visible").count() === 30, "the review shows all 30 typed answers");
  check(await page.locator("input:visible:not([disabled])").count() === 0, "the review's answers are locked");
  await checkSaved(page, api, shown, new Set(), 1);
  shown.forEach((q) => seen.add(q.item.id));

  console.log("\nthe second test, four misses");
  await page.goto(`${BASE}/ojaj`);
  await page.getByText(`Nowe pytania w bazie: ${TOTAL - 45} z ${TOTAL}`).waitFor();
  check(true, `the OJAJ page shows ${TOTAL - 45} questions new`);
  await page.getByRole("button", { name: "Losuj test" }).click();
  await page.waitForURL(/\/ojaj\/online$/);
  const missed = new Set();
  // Three typed misses in word formation and one culture question.
  const miss = (n, q) => {
    if (![1, 2, 3, 41].includes(n)) return false;
    missed.add(q.item.id);
    return true;
  };
  shown = await play(page, api, { miss });
  check(!shown.some((q) => seen.has(q.item.id)), "nothing from the first test comes back: it had no misses");
  check(await page.getByText("41/45", { exact: true }).first().isVisible(), "four misses score 41/45");
  await checkSaved(page, api, shown, missed, 2);
  shown.forEach((q) => seen.add(q.item.id));

  await page.goto(`${BASE}/ojaj`);
  await page.getByText("Twoje slabe punkty").waitFor();
  await page.getByText("Twoje slabe punkty").scrollIntoViewIfNeeded();
  await shot(page, "09_weak_points");
  check(await page.getByText("Pytania do powtorki: 4").isVisible(), "the weak points count 4 questions to come back");
  // A typed answer with an x on the end matches no rule, so each miss counts
  // for its item's own type.
  const types = new Set([...missed].map((id) => ITEMS.find((x) => x.item.id === id).item.mistakeType));
  for (const key of types) {
    const info = VAULT.mistakeTypes.find((t) => t.key === key);
    // Not exact: a label with a link shares its element with "Czytaj".
    check(await page.getByText(info.label).first().isVisible(), `the weak points list ${key}`);
    if (info.link) {
      check(await page.locator(`a[href="${info.link}"]`).count() >= 1, `with its link, ${info.link}`);
    }
  }
  // The typed words, which are distinctive; a culture answer can be an
  // ordinary word found elsewhere on the page.
  const words = [...missed].map((id) => ITEMS.find((x) => x.item.id === id))
    .filter((q) => q.task.type === "word_formation").map(keyText);
  const wordsShown = [];
  for (const w of words) if (await page.getByText(w).count() > 0) wordsShown.push(w);
  check(words.length === 3 && wordsShown.length === 0,
    `the missed words are not shown (${wordsShown.join(", ") || "none of " + words.join(", ")})`);

  console.log("\nthe third test, the misses come back");
  await page.getByRole("button", { name: "Losuj test" }).click();
  await page.waitForURL(/\/ojaj\/online$/);
  shown = await play(page, api);
  const back = shown.filter((q) => seen.has(q.item.id));
  const missedBack = shown.filter((q) => missed.has(q.item.id));
  const task1Back = missedBack.filter((q) => q.task.type === "word_formation").length;
  check(task1Back >= 2, `at least 2 of the 3 word-formation misses come back (${task1Back})`);
  check(missedBack.some((q) => q.task.type === "knowledge_questions"), "the culture miss comes back");
  await shot(page, "07_result_repeats");
  const marks = await page.getByText("powtorka", { exact: true }).count();
  check(marks === back.length, `the review marks every question seen before "powtorka" (${marks} of ${back.length})`);
  check(await page.getByText(`Nowe pytania: ${45 - back.length}/${45 - back.length}`).isVisible(),
    "the score on new questions leaves the repeats out");
  check(await page.getByText(`powtorki: ${back.length}/${back.length}`).isVisible(), "and gives the repeats' own");
  await page.getByText("powtorka", { exact: true }).first().scrollIntoViewIfNeeded();
  await shot(page, "08_review_repeat");
  await checkSaved(page, api, shown, new Set(), 3);

  await page.goto(`${BASE}/postepy`);
  await page.getByText("Historia testow konkursowych").waitFor();
  const rows = page.locator("span", { hasText: /^Test online$/ });
  check(await rows.count() === 3, `the history lists the three tests (${await rows.count()})`);
  check(await page.locator("a", { hasText: /Test online/ }).count() === 0, "their history rows are not links");
  await rows.first().scrollIntoViewIfNeeded();
  await shot(page, "10_history");
  await context.close();
}

async function timeUp(browser) {
  console.log("\nthe clock runs out");
  const { page, context, api } = await open(browser, { clock: true });
  await page.goto(`${BASE}/ojaj/online`);
  await page.getByRole("button", { name: "Rozpocznij test" }).click();
  const first = await onScreen(page);
  await give(page, first, keyText(first));
  await page.clock.fastForward("44:58");
  check(await page.getByText("Pytanie 1 z 45").isVisible(), "the test still runs at 44:58");
  await page.clock.fastForward("00:03");
  await page.getByText("Przeglad pytan").waitFor();
  check(await page.getByText("1/45", { exact: true }).first().isVisible(), "it submitted itself, 1/45");
  check(api.posts.length === 1 && api.posts[0].items.length === 45, "and saved one attempt with 45 verdicts");
  await context.close();
}

async function markingFails(browser) {
  console.log("\nthe AI marking fails, then a retry succeeds");
  const { page, context, api } = await open(browser, { checkStatus: 500 });
  await page.goto(`${BASE}/ojaj/online`);
  await page.getByRole("button", { name: "Rozpocznij test" }).click();
  const first = await onScreen(page);
  await give(page, first, keyText(first));
  await page.locator("aside").getByRole("button", { name: "Zatwierdz wszystkie i zakoncz" }).click();
  await submitButton(page).click();
  await page.getByText(/Nie udalo sie sprawdzic zadania 3/).waitFor();
  await shot(page, "11_marking_failed");
  check(api.posts.length === 0, "nothing is sent to the results API");
  check((await storedOnline(page)).length === 0, "nothing is stored locally");
  check(await page.locator("input:visible").count() === 0, "the answers cannot be reached to change");

  api.checkStatus = 200;
  await page.getByRole("button", { name: "Sprawdz ponownie" }).click();
  await page.getByText("Przeglad pytan").waitFor();
  check(api.posts.length === 1, "the retry saves one attempt");
  const saved = await storedOnline(page);
  check(saved.length === 1 && saved[0].answers["1"] === keyText(first)
    && saved[0].items[0].vaultId === first.item.id && saved[0].items[0].correct === true,
  "with the answer given before the failure, and its verdict");
  await context.close();
}

async function drawFails(browser) {
  console.log("\nthe vault does not load");
  const { page, context } = await open(browser, { vaultMissing: true });
  await page.goto(`${BASE}/ojaj/online`);
  await page.getByText(/Nie udalo sie wylosowac testu/).waitFor();
  check(true, "the player says so");
  await page.goto(`${BASE}/ojaj`);
  await page.getByText("Cwiczenia").waitFor();
  check(await page.getByText("Etap I, czesc II - test online").count() === 0,
    "the OJAJ page leaves the section out");
  await context.close();
}

async function oldAddress(browser) {
  console.log("\nan old fixed-test address");
  const { page, context } = await open(browser);
  await page.goto(`${BASE}/ojaj/online/02`);
  await page.waitForURL(/\/ojaj$/);
  check(true, "goes to the OJAJ page");
  await context.close();
}

const browser = await chromium.launch();
try {
  await threeRuns(browser);
  await timeUp(browser);
  await markingFails(browser);
  await drawFails(browser);
  await oldAddress(browser);
} catch (e) {
  check(false, `stopped: ${e.message.split("\n")[0]}`);
} finally {
  await browser.close();
}
console.log(failures === 0 ? "\nall checks passed" : `\n${failures} failure(s)`);
process.exit(failures === 0 ? 0 : 1);
