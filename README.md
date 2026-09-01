# Knowledge Assistant — Automated Test Suite

Automated regression suite for the Knowledge Assistant take-home assignment, covering
both the REST API (`pytest` + `requests`) and the UI (`pytest` + `Playwright`), driven
from a shared golden-question dataset.

Target under test: **https://main-knowledge-assistant.newpage.workers.dev/**

---

## Project structure

```
.
├── config.py                          # Loads .env; base URLs, timeouts, headless flag
├── conftest.py                        # Shared fixtures (browser/page, API client, golden-question params)
├── pytest.ini                         # Pytest config (Allure result output)
├── .env                                # Environment configuration (see below)
│
├── pages/
│   ├── base_page.py                   # Opens the app in the browser
│   └── knowledge_Assistant.py         # Page object: region/role selectors, ask, answer, citations, docs panel
│
├── utils/
│   ├── api_client.py                  # Thin requests wrapper for POST /query and GET /documents
│   ├── validators_api.py              # Shared pass-criteria checks for API responses
│   └── validators_knowledgeAssistant.py  # Shared pass-criteria checks for UI responses
│
├── tests/
│   ├── api/
│   │   └── test_query_api.py          # API-layer tests
│   └── ui/
│       └── test_KnowledgeAssistantPage.py  # UI-layer tests
│
├── test_data/
│   └── golden_questions.json          # The golden-question dataset (single source of truth for both layers)
│
└── reports/                           # Allure results/report output (generated, not source — see .gitignore note below)
```

## The golden-question dataset

`test_data/golden_questions.json` is the backbone of the suite: each entry defines a
question, the user context (`region`, `role`) to ask it under, and the pass criteria
that define correct behaviour — independent of *how* the assistant is implemented
underneath (no model, no prompt, no index details are baked into the assertions).

Each question has:

| Field | Meaning |
|---|---|
| `id` | Stable identifier (e.g. `GQ-007`), used as the pytest test ID |
| `category` | What it's testing: `positive`, `lifecycle`, `role_access`, `region_access`, `global_access`, `citation`, `hallucination`, `prompt_injection`, `boundary`, `unsupported`, `input_validation`, `missing_context`, `paraphrased_question`, `multi_document` |
| `test_type` | Which layer(s) run this question: `"ui"`, `"api"`, or both |
| `question`, `region`, `role` | The request to send |
| `expected_behavior` | `"answer"` or `"refusal"` |
| `expected_status` | Expected HTTP status (API layer) |
| `expected_facts` | Substrings that must appear in the answer (only checked for `"answer"`) or must **not** appear (checked for `"refusal"`, to catch leaked content) |
| `expected_citations` / `forbidden_citations` | Document IDs that must / must not appear in the citation list |
| `expected_visible_documents` | Document IDs that should appear in the scoped documents panel |

Both layers import the **same** dataset and the **same** pass-criteria logic
(`utils/validators_api.py` and `utils/validators_knowledgeAssistant.py` share the same
shape of checks), so a golden question means the same thing whether it's exercised
through the API or the UI.

`conftest.py` filters the dataset into two parametrized fixtures — `api_golden_question`
and `ui_golden_question` — based on each entry's `test_type`, so adding a new golden
question to the JSON file is enough to get it running at the right layer(s); no test
code changes needed.

---

## Setup

### Prerequisites

- Python 3.11+
- Network access to the target app (or a local instance, via `.env`)

### 1. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Playwright's browser binaries

```bash
playwright install chromium
```

### 3. Configure environment variables

Copy `.env` (already included) or create your own — it's read by `config.py` via
`python-dotenv`:

```dotenv
# Application url
WEB_BASE_URL=https://main-knowledge-assistant.newpage.workers.dev/

# Runner settings
HEADLESS=true
SLOW_MO=0

# API settings
API_BASE_URL=https://main-knowledge-assistant.newpage.workers.dev/
API_TIMEOUT_SECONDS=15
```

Set `HEADLESS=false` and a non-zero `SLOW_MO` (milliseconds) locally if you want to
watch the UI tests run.

---

## Running the tests

Run everything:

```bash
pytest
```

Run just the API layer:

```bash
pytest tests/api
```

Run just the UI layer:

```bash
pytest tests/ui
```

Run a single golden question by ID (works at either layer, since IDs are the pytest
test ID):

```bash
pytest -k GQ-007
```

Run the UI suite in parallel across workers (requires `pytest-xdist`, already in
`requirements.txt`):

```bash
pytest tests/ui -n auto
```

### Viewing the Allure report

`pytest.ini` is configured to write raw results to `reports/allure-results` on every
run (and clears them first via `--clean-alluredir`). To generate and view the HTML
report, you need the [Allure commandline](https://allurereport.org/docs/install/)
installed separately (`brew install allure`, or download the CLI release):

```bash
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

> `reports/` is generated output, not source — see the note below on adding it to
> `.gitignore`.

---

## Design notes

- **Layering.** Access-control, lifecycle, and citation-correctness rules are verified
  at the API layer, where they're cheapest to check across the full region×role
  matrix. The UI layer is reserved for what's genuinely UI-specific: that the answer,
  citations, and documents panel actually render and are scoped correctly for the
  selected region/role — not a re-check of every business rule already covered by the
  API tests.
- **Assertions are substring/contains-based, not exact-string matches**, so the suite
  should keep passing across a model swap, prompt change, or index rebuild, as long as
  the underlying facts and citations stay correct. `expected_facts` are checked with
  `in` against a lowercased, stripped answer; citations are checked as a set after
  uppercasing/stripping.
- **Data-driven, not copy-pasted.** Both `test_golden_question_api` and
  `test_golden_question_ui` are single parametrized test functions driven entirely by
  `test_data/golden_questions.json` — new coverage is added by extending the JSON file,
  not by writing new test functions.

## Known gaps (not yet covered)


- No tests yet for header casing (`"americas"` vs `"Americas"`), malformed request
  bodies, or unsupported HTTP methods on `/query`.
- No CI workflow file yet (see "Next steps" if you're setting one up — this suite is
  structured to be CI-ready: headless by default, JUnit/Allure output already wired
  in `pytest.ini`).