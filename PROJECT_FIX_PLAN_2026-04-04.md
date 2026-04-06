# SmartEn Fix Plan

Status: Complete

Date: 2026-04-04

Source review:

- [PROJECT_REVIEW_2026-04-04.md](PROJECT_REVIEW_2026-04-04.md)

Context:

- The app serves a handful of family and friends. There is no public user base.
- Anthropic API usage is bounded by a pre-paid fixed amount, so runaway cost is not a risk.
- Given the above, heavyweight auth infrastructure (server sessions, Cloudflare Access) is not warranted. The current client-side auth is sufficient.

Primary goals:

- Separate competition and practice history so metrics and links are correct.
- Make results sync work reliably across devices.
- Light API cleanup where the current behavior is pointless or sloppy.

Planning assumptions:

- Functional correctness (broken progress, leaked practice data) is the real user-facing problem and should ship first.
- Security hardening is deferred — the threat model does not justify the complexity for a family app with pre-paid API credits.
- The app has no automated test runner today; validation will be build + manual checks unless a test harness is introduced.

## Recommended Order

1. Normalize attempt records and fix Progress/Home consumers.
2. Add real remote-results hydration and merge behavior.
3. Light API cleanup.
4. Validate and deploy.

## Phase 1 - Normalize Attempt Records And Fix Progress Semantics

Target: 1 day

Files likely involved:

- `site/src/pages/KonkursTest.jsx`
- `site/src/pages/Practice.jsx`
- `site/src/pages/Progress.jsx`
- `site/src/pages/Home.jsx`
- `site/src/lib/resultsModel.js` (recommended new helper)

Problem to fix at the root:

- The code currently encodes different activity types into a single `testId` string and then re-parses that string in multiple places.
- That is why practice attempts leak into competition summaries and why the current history route logic breaks for practice entries.

Recommended record shape for new attempts:

```json
{
  "attemptId": "uuid",
  "kind": "competition | practice",
  "date": "ISO string",
  "score": 12,
  "maxScore": 20,
  "percentage": 60,
  "taskBreakdown": [],
  "year": "2024-2025",
  "stage": "rejonowy",
  "exerciseId": "cloze_005",
  "exerciseType": "open_cloze"
}
```

Actions:

- Add `attemptId` to all newly written results.
- Write explicit `kind` and route fields instead of relying on `testId` prefixes.
- Add a normalization helper that can still read legacy entries:
  - `practice/{id}` becomes a practice attempt.
  - `{year}/{stage}` becomes a competition attempt.
- Update `Progress.jsx` so summary cards, chart, and competition history are competition-only.
- If practice history should stay visible, render it in a separate section with correct `/cwiczenia/:type/:id` links.
- Update `Home.jsx` to consume the same normalized model instead of duplicating string-prefix logic.

Acceptance criteria:

- No practice attempt appears in competition averages, best-score cards, stage chart, or test history.
- Competition links always resolve to `/:year/:stage`.
- Practice links, if shown, always resolve to `/cwiczenia/:type/:id`.

## Phase 2 - Make Remote Results A Real Source Of Truth

Target: 1-2 days

Files likely involved:

- `site/src/pages/Home.jsx`
- `site/src/pages/Progress.jsx`
- `site/src/pages/KonkursTest.jsx`
- `site/src/pages/Practice.jsx`
- `site/src/lib/resultsSync.js` (recommended new helper)
- `site/functions/api/results.js`

Actions:

- Create local/remote load and merge helpers modeled after the existing quest sync flow.
- On load, fetch remote results for the signed-in user, merge them with local results by `attemptId`, and persist the merged copy locally.
- Backfill missing `attemptId` values on legacy local entries and save them back so they remain stable.
- Normalize legacy remote entries on read so sync does not duplicate older attempts.
- Decide clear-history semantics:
  - If synced history is user-facing, add a clear/delete API that removes both local and remote history.
  - If remote history is only backup/admin storage, stop writing user results from the client and remove the partial feature.

Acceptance criteria:

- The same user sees the same history on a second device after sign-in.
- Reloading after localStorage removal restores synced history from the server.
- Repeated sync cycles do not create duplicate attempts.

## Phase 3 - Light API Cleanup

Target: 0.5 day

Files likely involved:

- `site/functions/api/results.js`
- `site/functions/api/check.js`

Actions:

- Remove the `GET /api/results` branch that returns all users' results in one response. There is no use case for it.
- Add basic request validation on `/api/check`: reject malformed or oversized payloads early.
- Make unsupported methods return 405 instead of being silently accepted.

Acceptance criteria:

- `/api/results` only returns data for the requesting user.
- `/api/check` rejects obviously invalid requests.

## Validation Plan

Current constraint:

- `site/package.json` has no test runner today, so the default validation path is `npm run build` plus manual smoke tests.

Manual checks:

- Submit one competition test and one practice exercise; verify Progress shows correct separation and valid links.
- Sign in from a second browser/profile and confirm results hydrate correctly.
- Verify clear-history behavior matches the chosen product decision.
- Confirm `/api/results` no longer dumps all users' data.

Recommended small automated coverage if a test runner is added:

- Attempt normalization for legacy vs new result shapes.
- Results merge and dedupe behavior.

## Open Decisions

1. Results source of truth: synced user feature, or local-only history with no server write.
2. Progress scope: competition-only, or competition plus a separate practice section.
