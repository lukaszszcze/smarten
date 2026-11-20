// Screenshot one part of a study page for a close look.
// Run: node tools/study/shot_part.mjs <page> <css-selector> <out.png> [nth] [open]   (vite preview on 5191)
// With "open" as the fifth argument, every "Advanced" box is opened first.
import { chromium } from "/home/lukasz/workspace/smartfc/node_modules/playwright/index.mjs";

const [pageName, selector, out, nth = "0", open = ""] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1000, height: 900 } });
await page.goto(`http://localhost:5191/ojaj_study/${pageName}`);
if (open === "open") await page.evaluate(() => document.querySelectorAll("details.more").forEach((d) => { d.open = true; }));
await page.locator(selector).nth(Number(nth)).screenshot({ path: out });
await browser.close();
