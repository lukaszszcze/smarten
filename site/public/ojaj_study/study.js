// Shared by every page in /ojaj_study/.
//
// - The "I've learnt this" tick: <input type="checkbox" data-learnt="<key>">.
//   Ticks are kept in this browser only (localStorage "ojaj-study-learnt",
//   one entry per page key). Nothing else is saved.
// - The index's marks: <span data-done="<key>"> shows "✓ learnt" for a ticked
//   page.
// - Typed checks: <li class="tq" data-answer="word|other" data-why="..."> with
//   one <input class="gapin"> in it. The answer is checked letter for letter,
//   ignoring only capitals and spaces at the ends: on the real test one wrong
//   letter loses the point, so it does here too.
//
// Plain script, no build step. Test it in a browser: open a page, type a right
// and a wrong answer, tick the page, reload, and look at the index.
(function () {
  const KEY = "ojaj-study-learnt";

  function loadTicks() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "{}") || {};
    } catch (e) {
      return {};
    }
  }

  const ticks = loadTicks();

  function paintMarks() {
    document.querySelectorAll("[data-done]").forEach((el) => {
      el.textContent = ticks[el.getAttribute("data-done")] ? "✓ learnt" : "";
    });
  }

  document.querySelectorAll("input[data-learnt]").forEach((box) => {
    const page = box.getAttribute("data-learnt");
    box.checked = !!ticks[page];
    box.addEventListener("change", () => {
      ticks[page] = box.checked;
      try {
        localStorage.setItem(KEY, JSON.stringify(ticks));
      } catch (e) {
        // Private window or blocked storage: the tick works until the page closes.
      }
      paintMarks();
    });
  });
  paintMarks();

  // Typed checks
  function norm(text) {
    return text.trim().replace(/\s+/g, " ").replace(/[‘’]/g, "'").toLowerCase();
  }

  const items = Array.from(document.querySelectorAll("li.tq"));
  const tally = document.querySelector(".tally");

  function paintTally() {
    if (!tally) return;
    const right = items.filter((li) => li.dataset.state === "ok").length;
    tally.textContent = `Right so far: ${right} of ${items.length}`;
  }

  items.forEach((li, i) => {
    const input = li.querySelector("input.gapin");
    const accepted = li.dataset.answer.split("|").map(norm);
    const why = li.dataset.why || "";

    input.setAttribute("aria-label", `Answer ${i + 1}`);
    input.setAttribute("autocomplete", "off");
    input.setAttribute("autocapitalize", "off");
    input.setAttribute("autocorrect", "off");
    input.setAttribute("spellcheck", "false");

    const actions = document.createElement("div");
    actions.className = "tq-actions";
    const check = document.createElement("button");
    check.type = "button";
    check.className = "tq-check";
    check.textContent = "Check";
    const show = document.createElement("button");
    show.type = "button";
    show.textContent = "Show the answer";
    show.hidden = true;
    actions.append(check, show);
    const out = document.createElement("p");
    out.className = "tq-out";
    out.setAttribute("role", "status");
    li.append(actions, out);

    function say(cls, text, note) {
      out.className = `tq-out ${cls}`;
      out.textContent = text;
      if (note) {
        const span = document.createElement("span");
        span.className = "note";
        span.textContent = ` ${note}`;
        out.append(span);
      }
    }

    function run() {
      const typed = norm(input.value);
      if (!typed) {
        say("", "Type a word first.");
        return;
      }
      const ok = accepted.includes(typed);
      li.dataset.state = ok ? "ok" : "bad";
      input.classList.toggle("ok", ok);
      input.classList.toggle("bad", !ok);
      if (ok) {
        show.hidden = true;
        say("ok", "✓ Right.", why);
      } else {
        show.hidden = false;
        say("bad", "✗ Not yet. Go through it letter by letter and try again.");
      }
      paintTally();
    }

    check.addEventListener("click", run);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        run();
      }
    });
    input.addEventListener("input", () => {
      input.classList.remove("ok", "bad");
    });
    show.addEventListener("click", () => {
      show.hidden = true;
      say("bad", `The answer is: ${li.dataset.answer.split("|")[0]}.`, why);
      input.focus();
    });
  });
  paintTally();
})();
