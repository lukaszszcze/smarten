# SmartEn Project Review

Status: Request changes

Date: 2026-04-04

Scope reviewed:

- Core client flows: `App.jsx`, `Home.jsx`, `Progress.jsx`, `Practice.jsx`, `KonkursTest.jsx`, Quest pages
- Serverless APIs: `results.js`, `quest-progress.js`, `check.js`
- Shared scoring/progress logic: `scoring.js`, `questProgress.js`, `practiceRewards.js`, `questStars.js`

Verification performed:

- Reviewed the current application and API code paths directly
- Checked workspace diagnostics: no current compile/lint errors reported under `site/`
- Confirmed `npm run build` had already passed in `site/`

## Findings

### 1. High — All server APIs trust caller-controlled identity; any visitor can read or overwrite user data

Files:

- [site/src/App.jsx#L13](site/src/App.jsx#L13)
- [site/src/App.jsx#L36](site/src/App.jsx#L36)
- [site/functions/api/results.js#L5](site/functions/api/results.js#L5)
- [site/functions/api/results.js#L24](site/functions/api/results.js#L24)
- [site/functions/api/quest-progress.js#L7](site/functions/api/quest-progress.js#L7)
- [site/functions/api/quest-progress.js#L9](site/functions/api/quest-progress.js#L9)
- [site/functions/api/quest-progress.js#L22](site/functions/api/quest-progress.js#L22)

Why this matters:

- The only "authentication" is a client-side password list embedded in the bundle.
- The server endpoints do not verify any session, token, or signature. They accept a user name from the request and operate on KV immediately.
- `results.js` exposes both per-user reads and a full-dataset read path.
- `quest-progress.js` limits names to an allowlist, but that is not authorization. Anyone who knows the three names can fetch or overwrite those users' quest progress.

Impact:

- Cross-user data exposure: results and quest progress are readable by anyone who can hit the API.
- Cross-user data corruption: results/progress can be overwritten or spammed for any allowed user.
- The UI password gate gives a false sense of isolation because it is never enforced server-side.

Suggested fix:

- Move identity verification to the server.
- At minimum, require a server-validated token/session tied to the authenticated user and reject requests where requested user does not match that identity.
- Remove the public "all users" results read path unless it is intentionally admin-only.
- If this stays family-only, protect the whole site/API behind Cloudflare Access or another edge auth layer instead of relying on client-side secrets.

### 2. High — `/api/check` is an unauthenticated Anthropic proxy with direct cost-abuse exposure

Files:

- [site/functions/api/check.js#L9](site/functions/api/check.js#L9)
- [site/functions/api/check.js#L15](site/functions/api/check.js#L15)
- [site/functions/api/check.js#L36](site/functions/api/check.js#L36)
- [site/functions/api/check.js#L44](site/functions/api/check.js#L44)

Why this matters:

- The endpoint accepts arbitrary caller-supplied `task` and `answers` payloads and forwards them to Anthropic using the production API key.
- There is no authentication, rate limiting, body-size constraint, or requirement that the task correspond to real published content.
- For writing tasks in particular, student text is interpolated directly into the prompt, so grading behavior depends on model robustness rather than validated server-side structure.

Impact:

- Any internet user can spend Anthropic quota without logging in.
- A caller can send oversized or adversarial prompts unrelated to the real exercise set.
- Grading integrity is weaker than it looks because the server trusts caller-provided task definitions.

Suggested fix:

- Require authenticated access before the endpoint can call Anthropic.
- Stop accepting arbitrary task objects from the client; send only a stable task ID, then load canonical task content server-side.
- Add request size limits and rate limiting.
- Consider rejecting unsupported or unexpectedly large answer payloads before building prompts.

### 3. Medium — The Progress page mixes practice attempts into competition stats and history, producing broken links and misleading numbers

Files:

- [site/src/pages/Practice.jsx#L372](site/src/pages/Practice.jsx#L372)
- [site/src/pages/Practice.jsx#L394](site/src/pages/Practice.jsx#L394)
- [site/src/pages/Progress.jsx#L204](site/src/pages/Progress.jsx#L204)
- [site/src/pages/Progress.jsx#L205](site/src/pages/Progress.jsx#L205)
- [site/src/pages/Progress.jsx#L206](site/src/pages/Progress.jsx#L206)
- [site/src/pages/Progress.jsx#L295](site/src/pages/Progress.jsx#L295)
- [site/src/pages/Progress.jsx#L298](site/src/pages/Progress.jsx#L298)
- [site/src/pages/Progress.jsx#L71](site/src/pages/Progress.jsx#L71)
- [site/src/pages/Home.jsx#L85](site/src/pages/Home.jsx#L85)
- [site/src/pages/Home.jsx#L86](site/src/pages/Home.jsx#L86)

Why this matters:

- Practice attempts are stored in the same `attempts` array as competition attempts, using `testId: practice/{exerciseId}`.
- `Progress.jsx` then treats every attempt as a competition record: totals, averages, best score, chart stage labels, and the history links all consume the combined array.
- The history renderer derives `yearPath` and `stage` by splitting `testId` on `/`, which makes a practice record link to `/practice/{exerciseId}` — not a valid route in this app.
- `Home.jsx` already separates competitions from practice, so the current Progress behavior is inconsistent with the rest of the product.

Impact:

- The "Historia testow" section can render links that do not open the original attempt.
- Competition summary numbers are inflated or distorted by practice exercises.
- The score-over-time chart mixes two different activity types into one timeline.

Suggested fix:

- Split competition and practice attempts at read time in `Progress.jsx`, as `Home.jsx` already does.
- Keep competition summary/history/chart competition-only.
- If practice history is desired, render it as a separate section with correct links back to `/cwiczenia/{type}/{id}`.

### 4. Medium — Server-backed results are never read back into the UI, so stored data and visible user state diverge

Files:

- [site/src/pages/KonkursTest.jsx#L96](site/src/pages/KonkursTest.jsx#L96)
- [site/src/pages/Practice.jsx#L425](site/src/pages/Practice.jsx#L425)
- [site/src/pages/Home.jsx#L81](site/src/pages/Home.jsx#L81)
- [site/src/pages/Progress.jsx#L26](site/src/pages/Progress.jsx#L26)
- [site/src/pages/Progress.jsx#L174](site/src/pages/Progress.jsx#L174)
- [site/functions/api/results.js#L5](site/functions/api/results.js#L5)

Why this matters:

- Competition tests and practice exercises both POST results to `/api/results`.
- The user-facing dashboard and progress pages only read localStorage. They do not hydrate from the server copy at all.
- Quest correctly implements a local-plus-remote merge model, but the main results flow does not.

Impact:

- Clearing localStorage or switching devices loses visible history even though the backend still has a copy.
- Two devices can show different dashboards for the same user indefinitely.
- `/api/results` behaves like a write-only sink from the user's perspective.

Suggested fix:

- Decide on a real source of truth for competition/practice history.
- If server persistence is intended to matter, fetch and merge remote results on load the same way Quest does.
- If local-only history is the intended product behavior, stop writing these records to the server or explicitly mark the API as backup/admin-only.

## Open Questions / Assumptions

1. Is the deployment intentionally private enough that the lack of server-side auth is considered acceptable? If yes, `/api/check` is still the endpoint I would lock down first because it has direct billing exposure.
2. Should the Progress page represent only competition tests, or both competition and practice? The current labels and routes imply competition-only, but the storage model currently mixes both.
3. Is `/api/results` meant to support user-facing restore/cross-device continuity, or is it only an operator/debugging archive? The current implementation sits awkwardly between those two roles.

## Brief Positives

- Quest sync is substantially more coherent than the older local-only pattern: normalization, merge-on-write, and derived star recomputation are in the right direction.
- Shared star/reward helpers are small and readable.
- The current workspace diagnostics are clean, and the project builds successfully.