// Open the USA & Canada notebook in a real browser and check its pictures: every photo loads,
// every figure has a size, nothing is wider than the screen at phone width (except inside the
// figures' own scroll boxes), no console errors, in light and dark. Saves screenshots when given
// a directory.
//
// Run from the checkout root, with site/public served on port 5192:
//   (cd site/public && python3 -m http.server 5192) &
//   node tools/usa_canada/e2e_usa_canada.mjs [screenshot-dir]
// Playwright is borrowed, read-only, from another project's install.
import { chromium } from "/home/lukasz/workspace/smartfc/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";

const URL = "http://localhost:5192/usa_kanada.html";
const SHOTS = process.argv[2] || "";
let failures = 0;
const fail = (msg) => { failures++; console.log("FAIL", msg); };

const browser = await chromium.launch();
for (const [label, viewport] of [["desktop", { width: 1100, height: 900 }],
                                 ["phone", { width: 390, height: 844 }]]) {
  for (const scheme of ["light", "dark"]) {
    const page = await browser.newPage({ viewport, colorScheme: scheme });
    const errors = [];
    page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
    page.on("pageerror", (e) => errors.push(String(e)));
    await page.goto(URL, { waitUntil: "networkidle" });
    // lazy images: scroll through the page so every one is requested
    const height = await page.evaluate(() => document.body.scrollHeight);
    for (let y = 0; y < height; y += 700) {
      await page.evaluate((yy) => window.scrollTo(0, yy), y);
      await page.waitForTimeout(40);
    }
    await page.waitForLoadState("networkidle");
    const imgs = await page.$$eval("img", (els) => els.map((e) => ({
      src: e.getAttribute("src"), ok: e.complete && e.naturalWidth > 0, alt: e.alt })));
    imgs.filter((i) => !i.ok).forEach((i) => fail(`${label}/${scheme}: image did not load ${i.src}`));
    const figs = await page.$$eval("figure.viz svg", (els) => els.map((e) => {
      const r = e.getBoundingClientRect(); return [r.width, r.height]; }));
    figs.filter(([w, h]) => w < 100 || h < 50).forEach(() => fail(`${label}/${scheme}: a figure has no size`));
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (overflow > 1) fail(`${label}/${scheme}: page is ${overflow}px wider than the screen`);
    errors.forEach((e) => fail(`${label}/${scheme}: console: ${e}`));
    console.log(`${label}/${scheme}: ${imgs.length} images, ${figs.length} figures, height ${height}px`);
    if (SHOTS) {
      fs.mkdirSync(SHOTS, { recursive: true });
      await page.evaluate(() => window.scrollTo(0, 0));
      for (const id of ["where", "states", "land", "wildlife", "parks"]) {
        const sec = page.locator(`#${id}`);
        await sec.scrollIntoViewIfNeeded();
        await page.screenshot({ path: path.join(SHOTS, `${label}_${scheme}_${id}.png`) });
      }
    }
    await page.close();
  }
}
await browser.close();
console.log(failures ? `${failures} failures` : "all browser checks pass");
process.exit(failures ? 1 : 0);
