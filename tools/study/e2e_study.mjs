// Click through the OJAJ study pages in a real browser: the index, every page's
// checks (typed answers accepted from the key, answers that open on a click), the
// typed-check behaviour and the "I've learnt this" tick in detail on one page, the
// card on the OJAJ page, every link, phone width in light and dark, and the console.
// Saves screenshots when given a directory.
//
// Run, from the checkout root, against a build (vite preview serves
// /ojaj_study/<key> the way Cloudflare Pages does; the dev server does not):
//   (cd site && ./node_modules/.bin/vite build && ./node_modules/.bin/vite preview --port 5191)
//   node tools/study/e2e_study.mjs [screenshot-dir]
//
// Playwright is borrowed, read-only, from another project's install.
import { chromium } from "/home/lukasz/workspace/smartfc/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "../..");
const BASE = "http://localhost:5191";
const SHOTS = process.argv[2] || "";
// In the order the index lists them: the grammar page first, then the word pages.
const GRAMMAR = ["inversion"];
const WORD_PAGES = [
  "negative-prefix", "ance-ence", "base-change", "suffix-spelling", "double-letters",
  "silent-letters", "vowels",
];
const PAGES = [...GRAMMAR, ...WORD_PAGES];
// Off the site for now (Lukasz, 2026-10-25): word formation and wisielec first.
const HIDDEN = ["transformations", "conditionals", "relative-clauses", "comparison"];

let failures = 0;
function check(ok, what) {
  console.log(`${ok ? "ok  " : "FAIL"} ${what}`);
  if (!ok) failures += 1;
}

async function shot(page, name) {
  if (!SHOTS) return;
  fs.mkdirSync(SHOTS, { recursive: true });
  await page.screenshot({ path: path.join(SHOTS, `${name}.png`), fullPage: true });
}

const browser = await chromium.launch();

async function newPage(opts = {}) {
  const context = await browser.newContext({ viewport: { width: 1100, height: 900 }, ...opts });
  await context.addInitScript(() => localStorage.setItem("smarten_user", "Tadzio"));
  const page = await context.newPage();
  const errors = [];
  // vite preview has no Cloudflare Functions, so /api/ requests fail here and only here.
  page.on("console", (m) => {
    if (m.type() === "error" && !m.text().startsWith("Failed to load resource")) errors.push(m.text());
  });
  page.on("response", (r) => {
    if (r.status() >= 400 && !new URL(r.url()).pathname.startsWith("/api/")) errors.push(`${r.status()} ${r.url()}`);
  });
  page.on("pageerror", (e) => errors.push(String(e)));
  return { context, page, errors };
}

// --- Index -------------------------------------------------------------
{
  const { context, page, errors } = await newPage();
  await page.goto(`${BASE}/ojaj_study/`);
  check(await page.title() === "OJAJ Study Pages", "index title");
  const links = await page.$$eval("a.card", (as) => as.map((a) => a.getAttribute("href")));
  const want = [...PAGES.map((p) => `/ojaj_study/${p}`), "/ojaj_uk"];
  check(JSON.stringify(links) === JSON.stringify(want), `index links inversion, the word pages and the notebook, not the hidden grammar pages`);
  const grammarCards = await page.$$eval("section.group.grammar a.card", (as) => as.map((a) => a.getAttribute("href")));
  check(JSON.stringify(grammarCards) === '["/ojaj_study/inversion"]', "the grammar group shows inversion only");
  check(await page.locator(".card.later").count() === 0, "no page left as not written yet");
  check((await page.locator("[data-done]").allTextContents()).every((t) => t === ""), "no learnt marks at first");
  await shot(page, "index_light");
  check(errors.length === 0, `index: no console errors ${errors.join(" | ")}`);
  await context.close();
}

// --- Every page: its checks work, its title is right, no errors ----------
for (const key of PAGES) {
  const { context, page, errors } = await newPage();
  await page.goto(`${BASE}/ojaj_study/${key}`);
  check((await page.locator("h1").count()) === 1 && !(await page.title()).includes("SmartEn"), `${key}: its own page`);
  check(await page.locator(`input[data-learnt="${key}"]`).count() === 1, `${key}: tick has the page's key`);
  const typed = page.locator("li.tq");
  const nTyped = await typed.count();
  const details = page.locator(".check details");
  const nDetails = await details.count();
  check(nTyped + nDetails >= 5 && nTyped + nDetails <= 8, `${key}: 5-8 check questions (${nTyped + nDetails})`);
  for (let i = 0; i < nTyped; i += 1) {
    const li = typed.nth(i);
    const answer = (await li.getAttribute("data-answer")).split("|")[0];
    await li.locator("input.gapin").fill(answer);
    await li.locator("button.tq-check").click();
  }
  if (nTyped) {
    check(await page.locator(".tally").textContent() === `Right so far: ${nTyped} of ${nTyped}`, `${key}: every key accepted`);
  }
  for (let i = 0; i < nDetails; i += 1) {
    const d = details.nth(i);
    if (await d.locator(".ans").isVisible()) check(false, `${key}: answer ${i + 1} shown before the click`);
    await d.locator("summary").click();
    if (!(await d.locator(".ans").isVisible())) check(false, `${key}: answer ${i + 1} does not open`);
  }
  if (nDetails) check(true, `${key}: ${nDetails} answers open on a click`);
  if (WORD_PAGES.includes(key)) {
    const lists = await page.locator("ul.pairs").count();
    const boxes = page.locator("details.more");
    const nBoxes = await boxes.count();
    check(lists > 0 && (key === "ance-ence") === (nBoxes === 0), `${key}: word lists (${lists}), Advanced boxes (${nBoxes}), none on ance-ence`);
    const openBoxes = await boxes.evaluateAll((ds) => ds.filter((d) => d.open).length);
    check(openBoxes === 0, `${key}: Advanced boxes closed at first`);
    const cols = await page.locator("ul.pairs").first().evaluate((ul) => getComputedStyle(ul).columnCount);
    check(cols === "3" || Number(cols) > 1, `${key}: lists in columns (${cols})`);
  } else {
    check(await page.locator("table.grid").count() > 0, `${key}: has its rule tables`);
  }
  await shot(page, `${key}_light`);
  check(errors.length === 0, `${key}: no console errors ${errors.join(" | ")}`);
  await context.close();
}

// --- The hidden pages are not served -------------------------------------
{
  const { context, page } = await newPage();
  for (const key of HIDDEN) {
    const res = await page.request.get(`${BASE}/ojaj_study/${key}`, { headers: { Accept: "text/html" } });
    const body = await res.text();
    check(!body.includes("data-learnt"), `${key}: not served`);
  }
  await context.close();
}

// --- Typed checks and the tick, in detail, on base-change ----------------
{
  const { context, page } = await newPage();
  await page.goto(`${BASE}/ojaj_study/base-change`);
  const first = page.locator("li.tq").nth(0);
  const input = first.locator("input.gapin");
  check(await input.getAttribute("spellcheck") === "false", "browser spellcheck off (it would give the answer away)");
  await first.locator("button.tq-check").click();
  check((await first.locator(".tq-out").textContent()) === "Type a word first.", "empty answer asks for a word");
  await input.fill("explaination");
  await first.locator("button.tq-check").click();
  check(await input.evaluate((el) => el.classList.contains("bad")), "a wrong spelling is marked wrong");
  check(await first.locator("button", { hasText: "Show the answer" }).isVisible(), "a wrong answer offers the answer");
  await input.fill("explanatio");
  await input.press("Enter");
  check(await input.evaluate((el) => el.classList.contains("bad")), "one letter short is wrong too (no allowance)");
  await first.locator("button", { hasText: "Show the answer" }).click();
  check((await first.locator(".tq-out").textContent()).startsWith("The answer is: explanation."), "Show the answer reveals it");
  await input.fill("  Explanation ");
  await input.press("Enter");
  check(await input.evaluate((el) => el.classList.contains("ok")), "right answer, capitals and outer spaces ignored");
  check(await page.locator(".tally").textContent() === "Right so far: 1 of 8", "tally counts it");

  await page.locator("input[data-learnt]").check();
  await page.reload();
  check(await page.locator("input[data-learnt]").isChecked(), "tick survives a reload");
  check(await page.locator(".tally").textContent() === "Right so far: 0 of 8", "typed answers are not saved");
  const stored = await page.evaluate(() => [localStorage.getItem("ojaj-study-learnt"), localStorage.getItem("uk-notebook-learnt")]);
  check(stored[0] === '{"base-change":true}', `tick stored under its own key: ${stored[0]}`);
  check(stored[1] === null, "the notebook's ticks are untouched");
  await page.goto(`${BASE}/ojaj_study/`);
  const marks = await page.$$eval("[data-done]", (els) => Object.fromEntries(els.map((e) => [e.dataset.done, e.textContent])));
  check(marks["base-change"] === "✓ learnt" && Object.entries(marks).every(([k, v]) => k === "base-change" || v === ""),
    "index marks the ticked page only");
  await context.close();
}

// --- A wisielec hint: the letters shown fit the answer --------------------
{
  const { context, page } = await newPage();
  await page.goto(`${BASE}/ojaj_study/silent-letters`);
  const hint = await page.locator("li.tq .hint").first().textContent();
  check(hint.split(" ").length === (await page.locator("li.tq").first().getAttribute("data-answer")).length, `wisielec hint has one place per letter: ${hint}`);
  await context.close();
}

// --- Every link on every page --------------------------------------------
{
  const { context, page } = await newPage();
  const ex = JSON.parse(fs.readFileSync(path.join(ROOT, "pub/konkursy/angielski/data/ojaj/index.json"), "utf8"));
  const exerciseIds = new Set(ex.exercises.map((e) => e.id));
  const kurat = JSON.parse(fs.readFileSync(path.join(ROOT, "pub/konkursy/angielski/data/practice/index.json"), "utf8"));
  const kuratRoutes = new Set(kurat.exercises.map((e) => `/cwiczenia/${e.taskType}/${e.id}`));
  const hrefs = new Set();
  for (const p of ["", ...PAGES]) {
    await page.goto(`${BASE}/ojaj_study/${p}`);
    for (const h of await page.$$eval("a[href]", (as) => as.map((a) => a.getAttribute("href")))) hrefs.add(h);
  }
  for (const h of hrefs) {
    if (h.startsWith("/ojaj/cwiczenia/")) {
      check(exerciseIds.has(h.split("/").pop()), `practice link names a real exercise: ${h}`);
      continue;
    }
    if (h.startsWith("/cwiczenia/")) {
      check(kuratRoutes.has(h), `practice link names a real exercise of its type: ${h}`);
      continue;
    }
    const res = await page.request.get(`${BASE}${h}`, { headers: { Accept: "text/html" } });
    const body = await res.text();
    const own = h === "/ojaj" || !body.includes("SmartEn — Konkurs angielski");
    check(res.status() === 200 && own, `link resolves: ${h}`);
  }
  await context.close();
}

// --- Phone width and dark mode -------------------------------------------
for (const scheme of ["light", "dark"]) {
  const { context, page } = await newPage({ viewport: { width: 375, height: 800 }, colorScheme: scheme });
  const over = [];
  for (const p of ["", ...PAGES]) {
    await page.goto(`${BASE}/ojaj_study/${p}`);
    const px = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (px > 0) over.push(`${p || "index"} ${px}px`);
    if (scheme === "dark") await shot(page, `${p || "index"}_phone_dark`);
  }
  check(over.length === 0, `${scheme}, 375px: no sideways scroll on any page ${over.join(", ")}`);
  await context.close();
}

// --- The card on the OJAJ page -------------------------------------------
{
  const { context, page, errors } = await newPage();
  await page.goto(`${BASE}/ojaj`);
  const card = page.locator('a[href="/ojaj_study/"]');
  await card.waitFor();
  check((await card.textContent()).includes("Strony do nauki"), "OJAJ page has the study pages card");
  const order = await page.$$eval('a[href="/ojaj_uk"], a[href="/ojaj_study/"]', (as) => as.map((a) => a.getAttribute("href")));
  check(JSON.stringify(order) === '["/ojaj_uk","/ojaj_study/"]', "the card comes right after the notebook's");
  await card.click();
  await page.waitForURL(`${BASE}/ojaj_study/`);
  check(await page.title() === "OJAJ Study Pages", "the card opens the index");
  check(errors.length === 0, `OJAJ page: no console errors ${errors.join(" | ")}`);
  await context.close();
}

await browser.close();
console.log(failures ? `\n${failures} FAILED` : "\nall passed");
process.exit(failures ? 1 : 0);
