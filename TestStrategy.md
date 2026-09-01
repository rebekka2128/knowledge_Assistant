## TEST STRATEGY
Knowledge Assistant

## 1. Objective

Define and justify the automated test approach for the Knowledge Assistant — a
document Q&A system that returns an answer, citations, and a list of visible source
documents based on a user's question, region, and role context — so that access
control, document lifecycle rules, and citation correctness are verified reliably and
regressions are caught automatically going forward.

## 2. Scope

- API automation (`/query` endpoint, `requests`)
- UI automation (Playwright)
- Access control: region × role scoping of answers, citations, and visible documents
- Document lifecycle enforcement: Draft, In Review, Approved, Retired
- Citation correctness: right document, not just a present document
- Input robustness: malformed, missing, oversized, and adversarial input
- Guardrail/prompt-injection resistance
- Shared, data-driven golden-question dataset driving both layers

## 3. Out of Scope

- Performance / load testing
- Systematic penetration testing (beyond targeted injection smoke checks)
- Accessibility (a11y)
- Mobile / responsive UI
- Long-term output-drift monitoring
- Free-form NLU/paraphrase robustness as a fixed regression target

These need a fundamentally different testing approach (sustained load, dedicated
security tooling, longitudinal comparison) than the functional/access-control focus
here, and are better treated as separate follow-on work than folded into this suite.

## 4. Test Approach

- **Layering by cost and flakiness.** Access, lifecycle, and citation rules are
  verified primarily at the API layer — cheap, deterministic, driven from the full
  relevant matrix. The UI layer is reserved for what only exists there: that
  region/role selectors, the answer, citations, and the documents panel actually
  render and scope correctly for the logged-in context. UI tests do not re-check
  business logic already proven at the API layer.
- **Risk-based, not combinatorial.** Coverage is concentrated where the content
  library creates real risk (see Section 7), not spread evenly across every possible
  input combination.
- **Design patterns:** Page Object Model for UI (`pages/base_page.py`,
  `pages/knowledge_Assistant.py`); a Service Object equivalent for API
  (`utils/api_client.py`), with response-parsing helpers tolerant of minor schema
  variation; shared-intent validators (`validators_api.py`,
  `validators_knowledgeAssistant.py`) so a "pass" means the same thing at both layers.
- **Independence.** Each test is self-contained — fresh browser context or session per
  test, no shared mutable state, no dependency on execution order.

## 5. Test Coverage

| Area | Status |
|---|---|
| Lifecycle exclusion (D-003 In Review, D-005 Retired, D-009 Draft) | Partially covered — D-009's combined region+role gating needs its own dedicated case |
| Access boundaries at narrowly-scoped docs (D-006/007/008/009) | Covered via golden set |
| Access boundaries at wide-open (Global/All Staff) docs | Spot-checked, not exhaustive |
| Citation correctness, positive path | Covered for single-fact cases; multi-document grounding has only one case |
| Guardrail / prompt injection | Covered generically (3 cases); not yet targeted at the specific trap docs |
| Header-level negative input (missing/invalid region or role) | Covered |
| Body-level negative input (invalid JSON, wrong method/content-type, empty/oversized question) | Not yet implemented |
| Security smoke | One SQL-injection-style case; XSS and payloads targeting trap docs not yet added |
| Cross-layer consistency (same question, UI result diffed against API result) | Not implemented — each layer is independently validated, not diffed against the other |

## 6. Test Data Strategy

All functional cases are driven by a single shared fixture,
`test_data/golden_questions.json`. Each entry defines the question, region, role,
`test_type` (which layer(s) it runs against — `ui`, `api`, or both), expected
behavior (`answer` or `refusal`), expected facts/citations, and forbidden citations.

This keeps UI and API suites aligned to one source of truth and means adding a new
business scenario — e.g. a new lifecycle or role restriction — requires a new JSON
entry, not new test code. Ground truth for the dataset is the content library and data
export provided with the assignment, not assumptions about intended behavior.

## 7. Test Prioritization

The 9-document library is deliberately booby-trapped: an **In Review** APAC travel doc
(D-003), a **Retired** remote-work doc (D-005) next to its live replacement (D-004),
and a **Draft** EMEA-only, Manager-only vendor checklist (D-009). Lifecycle leakage is
the cheapest bug to trigger and the most damaging to ship — a Draft or Retired fact
reaching a user looks identical to a correct answer unless the ground truth is known.

Priority order:

1. **Lifecycle exclusion** for every role/region that could otherwise see the
   approved sibling of D-003/D-005/D-009 — binary pass/fail against known ground
   truth, highest signal-to-effort ratio.
2. **Access boundaries at the seams** — exhaustive at the narrowly-scoped docs,
   spot-checked at the wide-open ones, rather than the full region×role grid.
3. **Citation correctness on positive-path questions** before adversarial cases — a
   system that cites wrong on easy questions won't hold up under pressure.
4. **Guardrail/prompt-injection attempts** aimed specifically at the three trap docs,
   not generic jailbreak phrasing.
5. **The spec's own open questions** (which region a travel question resolves to,
   multi-role handling) — pinned down as explicit testable rules rather than left
   ambiguous.
6. **Input robustness** (malformed bodies, wrong content-type/method, empty/oversized
   questions) — necessary, but ordered after business-logic risk: a malformed
   request failing loudly is a cheaper bug than a lifecycle leak succeeding silently.

## 8. Defect Management

- **Severity mapping, tied to risk category, not just symptom:**
  - *Critical* — any Draft/In Review/Retired content, or any cross-region/cross-role
    content, surfaces in an answer or citation.
  - *High* — correct document set but wrong citation attribution; refusal expected
    but an answer is given (or vice versa); guardrail bypass on a trap-doc target.
  - *Medium* — malformed/negative input handled ungracefully (5xx instead of a clean
    4xx, or a leaked stack trace) without an actual data leak.
  - *Low* — cosmetic UI issues, non-blocking rendering glitches.
- **Logging.** Each failure is traceable to a golden-question `id` (e.g. `GQ-014`) or
  a named negative/security case, with the request, expected vs. actual, and region/
  role context attached — no defect logged without a reproducible case in the suite.
- **Triage.** Critical/High block sign-off (see Exit Criteria); Medium/Low may be
  deferred with an explicit owner and reason, tracked in Section 5's coverage table
  rather than left implicit.
- **Regression.** Every fixed defect gets a permanent golden-question or negative-case
  entry so the suite guards against recurrence, not just the original report.

## 9. Automation Framework

- **UI:** Playwright (Python, sync API), Page Object Model.
- **API:** `requests`, Service Object pattern (`utils/api_client.py`).
- **Test runner:** pytest, with `test_data/golden_questions.json` parametrizing both
  suites via `test_type`.
- **Validation:** shared-intent validators so pass/fail criteria are identical in
  meaning across layers, even though implemented separately.
- **Reporting:** Allure (`reports/allure-results` → `reports/allure-report`).

## 10. Environment & Tools

| Component | Detail |
|---|---|
| UI automation | Playwright (Python, sync API), Chromium |
| API automation | `requests` |
| Test runner | pytest |
| Config | `config.py` + `.env` (base URLs, headless flag, timeouts) |
| Test data | `test_data/golden_questions.json` |
| Reporting | Allure |

## 11. Entry Criteria

- Application deployed and reachable at the configured base URL(s).
- Golden-question dataset reviewed and reconciled against `content-library.md` /
  `data-export.csv` as ground truth.
- Test environment configuration (`.env`, `config.py`) validated.

## 12. Exit Criteria

- All golden questions pass at both UI and API layers.
- Every item marked "not yet implemented" in Section 5 is either closed or explicitly
  deferred with a stated owner and reason — not silently dropped.
- No open Critical or High severity defect per Section 8.
- Allure report generated and reviewed.

## 13. Risks & Limitations

| Risk | Mitigation |
|---|---|
| API response schema changes silently break tests | `extract_*` helpers accept multiple key names and fail with a specific, actionable error rather than a raw `KeyError` |
| Flaky UI waits on async answer loading | Explicit wait on `"Thinking..."` removal + `networkidle` |
| Negative/malformed-input suite is thin | Tracked in Section 5; prioritized per Section 7, item 6 |
| "UI and API agree" is assumed, not verified | Each layer is validated independently against the same criteria; a true cross-layer diff (same question, UI-extracted vs. API-extracted result compared directly) is not yet implemented — should not be claimed as covered until it exists |
| Small content library (9 docs) limits statistical confidence | Compensated by exhaustive coverage at every scoped/trap document rather than sampling |