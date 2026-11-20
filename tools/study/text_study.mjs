// Print the study pages as plain text for review, with every hidden answer shown.
// Run: node tools/study/text_study.mjs [page ...] > <file>   (vite preview on port 5191)
// With no pages named it prints the index, the checklist and base-change.
import { chromium } from "/home/lukasz/workspace/smartfc/node_modules/playwright/index.mjs";

const pages = process.argv.length > 2 ? process.argv.slice(2) : ["", "transformations", "base-change"];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1000, height: 900 } });
for (const p of pages) {
  await page.goto(`http://localhost:5191/ojaj_study/${p}`);
  const text = await page.evaluate(() => {
    document.querySelectorAll("details").forEach((d) => { d.open = true; });
    document.querySelectorAll("li.tq").forEach((li) => {
      li.querySelector("input.gapin").replaceWith("______");
      li.querySelector(".tq-actions")?.remove();
      const key = document.createElement("p");
      key.textContent = `[answer: ${li.dataset.answer} | shown after: ${li.dataset.why}]`;
      li.append(key);
    });
    document.querySelectorAll(".gap").forEach((g) => { g.textContent = "______"; });
    return document.body.innerText;
  });
  console.log(`${"=".repeat(72)}\n/ojaj_study/${p}\n${"=".repeat(72)}\n${text}\n`);
}
await browser.close();
