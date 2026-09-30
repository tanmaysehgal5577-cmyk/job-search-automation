# Job Search Automation (Playwright + Python)

A production-style browser automation that scrapes a job board, filters and ranks the results, and exports them
to **CSV, Excel and PDF**. It also demonstrates **form automation** (fill → submit → verify).

Built with Python 3.10+, **async Playwright**, a CLI, Docker and GitHub Actions CI.

> The default target is [Real Python's Fake Jobs board](https://realpython.github.io/fake-jobs/) - a static site
> made for scraping practice, so it is safe and legal to automate. Only automate sites whose terms allow it.

## Features

| Area | What you get |
|---|---|
| Mandatory | `.env` config, rotating-file + console logging, exception hierarchy, screenshots (on failure **and** on success), README |
| Browser | Chromium / Firefox / WebKit, headless or headed, slow-mo, timeouts, guaranteed cleanup in `finally` |
| Reliability | Explicit waits (no `sleep`), retry with exponential backoff, result validation (fails loudly if the site layout changes) |
| Data | De-duplication, keyword / exclude / location / date filters, sorting, limit, optional detail-page enrichment (concurrent) |
| Export | CSV (Excel-safe UTF-8), styled Excel (frozen header, filters, hyperlinks), PDF report with summary |
| Forms | `apply` command fills a form, submits it and verifies the server's echo |
| Tooling | Argparse CLI, Dockerfile (non-root), GitHub Actions (lint, tests on 3.10/3.12, Docker build, manual scrape), 37 pytest tests, ruff |

## Project structure

```
src/job_automation/
├── cli.py         argparse commands: search, apply
├── pipeline.py    workflows that wire everything together
├── browser.py     browser lifecycle + screenshot-on-failure
├── scraper.py     navigate → wait → extract → validate
├── forms.py       fill / submit / verify a form
├── filters.py     dedupe, filter, sort, limit (pure functions)
├── models.py      Job dataclass + parsing rules
├── exporters.py   CSV / Excel / PDF
├── config.py      typed settings from .env
├── logger.py      logging setup
├── utils.py       retry_async, slugify, timestamp
└── exceptions.py  AutomationError hierarchy
tests/             pytest suite (no browser needed)
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
playwright install chromium
cp .env.example .env                 # Windows: copy .env.example .env
export PYTHONPATH=src                # Windows PowerShell: $env:PYTHONPATH="src"   (or: pip install -e .)
```

## Usage

```bash
# All Python-related jobs, newest first, exported to three formats
python -m job_automation search -k python -k developer --sort posted -f csv excel pdf

# Filters: exclude words, locations, date, limit; visit detail pages for descriptions
python -m job_automation search -k engineer -x senior -l "AP" --since 2021-04-01 --limit 25 --details

# Watch the browser work (debugging)
python -m job_automation search --headed -k python

# Form automation (needs APPLICANT_* in .env)
python -m job_automation apply --title "Python Developer" --company "Acme"
```

Results go to `output/`, screenshots to `screenshots/`, logs to `logs/automation.log`.
Exit codes: `0` ok, `1` automation failure, `2` configuration/usage error, `130` interrupted.

## Docker

```bash
docker build -t job-automation .
docker run --rm -v "$PWD/data:/data" job-automation                                   # default: 20 jobs → CSV
docker run --rm -v "$PWD/data:/data" job-automation search -k python -f csv excel pdf
docker run --rm --env-file .env -v "$PWD/data:/data" job-automation apply --title "Dev" --company "Acme"
```

## Tests and quality

```bash
pytest -q          # unit tests (config, models, filters, exporters, forms, CLI, retry/screenshot helpers)
ruff check .
```

CI (`.github/workflows/ci.yml`) runs lint + tests on Python 3.10 and 3.12, builds the Docker image, and lets you
trigger a real scrape manually (*Actions → CI → Run workflow*) with results uploaded as artifacts.

## Design decisions

- **One `eval_on_selector_all` call** extracts all cards in the browser instead of hundreds of round-trips.
- **Validation over silence:** zero cards or >50% malformed cards raises `ValidationError` rather than exporting junk.
- **Screenshots never hide the real error:** `capture_screenshot` swallows its own failures.
- **Pure functions** (`filters`, `parse_jobs`, `parse_form_response`) keep the logic unit-testable without a browser.
- **The `apply` form** is httpbin's sandbox form (it echoes input as JSON, so success can be verified). To target
  another form, change `FORM_URL` and `FIELD_SELECTORS` in `forms.py`.

## Extending

Add a new site by changing `BASE_URL` and the selectors/JS at the top of `scraper.py`. Add a new export format by
writing one function in `exporters.py` and registering it in `EXPORTERS`.
