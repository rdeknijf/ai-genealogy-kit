# Ancestors (ancesto.rs) — MVP Design

## Problem

Millions of people are interested in their family history but lack the skills
or time to systematically research and verify their family tree. AI-powered
genealogy research is powerful but currently requires technical expertise
(Claude Code, archive skills, GEDCOM parsing). There's a market — especially
among older generations — for a service that does this for them.

## Product

A web application where users upload a GEDCOM (or enter a few generations
manually), buy credits, and get back a researched and verified family tree
with source citations. The system discovers new ancestors and hardens
existing data against official archive records.

## MVP Scope

### What it does

- Google OAuth sign-up
- Upload a GEDCOM or enter 3 generations manually
- Buy credits via Stripe (prepaid bundles, no subscription)
- Automated research engine: discover new ancestors + verify existing data
- Dashboard: read-only tree viewer, live findings feed, credit balance
- Pause/resume: credits run out → research pauses, add more → continues
- Export: enriched GEDCOM + scorecard report

### What it doesn't do (v2)

- Tree editing in the UI
- User-managed research queue
- Notes/annotations on persons
- Subscription billing
- Multi-language UI
- Mobile optimization
- Per-customer archive auto-discovery
- PDF story/narrative generation
- Family collaboration/sharing

## Architecture

```
┌─────────────────────────────────┐
│  HTMX Frontend (Jinja2 + CSS)  │
├─────────────────────────────────┤
│  FastAPI Backend                │
├─────────────────────────────────┤
│  Research Engine                │
├─────────────────────────────────┤
│  PostgreSQL                     │
└─────────────────────────────────┘
         ↕                    ↕
   Stripe (credits)    Archive Skills (HTTP/Playwright)
```

Single Python app with a background worker for research jobs. One repo,
one Docker Compose deploy.

## Data Model

### users

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| email | text | unique |
| name | text | |
| google_id | text | unique |
| created_at | timestamp | |

### credits

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| user_id | uuid | FK → users |
| amount | int | credits purchased |
| stripe_payment_id | text | |
| created_at | timestamp | |

### credit_ledger

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| user_id | uuid | FK → users |
| delta | int | positive = topup, negative = spend |
| reason | text | e.g. "purchase", "research_cycle" |
| research_job_id | uuid | FK → research_jobs, nullable |
| balance_after | int | running balance |
| created_at | timestamp | |

### trees

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| user_id | uuid | FK → users |
| gedcom_blob | bytea | raw GEDCOM for export |
| person_count | int | |
| uploaded_at | timestamp | |

### persons

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| tree_id | uuid | FK → trees |
| gedcom_id | text | original GEDCOM INDI id |
| name | text | |
| birth_date | text | GEDCOM date format |
| birth_place | text | |
| death_date | text | |
| death_place | text | |
| father_id | uuid | FK → persons, nullable |
| mother_id | uuid | FK → persons, nullable |

### research_jobs

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| tree_id | uuid | FK → trees |
| status | enum | queued/running/paused/done |
| credits_spent | int | |
| started_at | timestamp | |
| finished_at | timestamp | nullable |

### findings

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| research_job_id | uuid | FK → research_jobs |
| person_id | uuid | FK → persons |
| tier | enum | A/B/C/D |
| finding_type | text | birth/marriage/death/other |
| summary | text | |
| source_citation | text | |
| source_url | text | nullable |
| scan_url | text | nullable |
| applied_to_gedcom | bool | |
| created_at | timestamp | |

## User Flow

1. **Land** — marketing page
2. **Sign up** — Google OAuth
3. **Onboard** — upload GEDCOM or enter 3 generations via form (yourself: name + birth date/place; parents: names + birth dates/places; grandparents: names + any known dates/places)
4. **Buy credits** — Stripe Checkout (e.g. €10/100 credits, €25/300)
5. **Start research** — system estimates cost, user confirms
6. **Dashboard** — tree viewer (fan chart or pedigree), live findings feed, credit balance
7. **Pause/resume** — credits exhausted → pauses → add more → continues
8. **Export** — download enriched GEDCOM + report

## Research Engine

The engine runs two interleaved operations per person:

### Discovery

Extend the tree by finding unknown ancestors, siblings, and marriages.
Search archives broadly based on known names, dates, and locations.
Work outward from the known leaves of the tree.

### Verification

Verify and cite existing data against official records. Cross-validate
ages across records (age at marriage + marriage year = birth year, etc.).
Apply Tier A/B evidence directly to the GEDCOM.

### Cycle

1. Parse GEDCOM into persons table
2. Score each person: verification level + discovery potential
3. Sort by priority: closest generations first, least-verified first
4. For each person:
   - Determine relevant archives (time period + location)
   - Call archive modules (HTTP API first, Playwright fallback)
   - Cross-validate findings
   - Write findings to DB with tier and source citation
   - If Tier A/B: apply to internal GEDCOM
   - If new persons discovered: add to persons table, queue for next cycle
5. Debit credits: ~1 credit per verify cycle, ~2-3 per discovery cycle
6. If credits = 0: pause job, notify user
7. If unknown archive needed: create GitHub issue for datasource onboarding

### Confidence Tiers

| Tier | Source | Action |
|------|--------|--------|
| A | Primary source scan, user verified | Apply to GEDCOM |
| B | Indexed civil record with archive reference | Apply with citation |
| C | Multiple secondary sources agree | Flag in findings |
| D | Single secondary source or AI inference | Note only |

## Tech Stack

- **Python 3.13** / uv
- **FastAPI** — web framework
- **Jinja2 + HTMX** — templates with interactivity, minimal JS
- **PostgreSQL** — primary database (asyncpg)
- **Redis + ARQ** — async job queue for research workers
- **Stripe** — credit purchases via Checkout Sessions
- **authlib** — Google OAuth
- **Playwright** — browser automation for archives without APIs
- **Docker Compose** — app + postgres + redis + playwright

### Repo Structure

```
src/
  app.py              ← FastAPI entry point
  auth.py             ← Google OAuth
  billing.py          ← Stripe + credit ledger
  models.py           ← SQLAlchemy/DB models
  research/
    engine.py         ← orchestrator (discover + harden loop)
    archives/         ← one module per archive
    gedcom.py         ← parse/export GEDCOM
  templates/          ← Jinja2 + HTMX
  static/             ← CSS, minimal JS
tests/
docker-compose.yml
pyproject.toml
```

### Deploy

- Docker Compose on a single VPS (€10/month to start)
- Traefik for TLS (Let's Encrypt)
- Scale by adding more research workers

## Credit Model

- 1 credit ≈ 1 person verification cycle (birth + marriage + death lookup)
- 2-3 credits ≈ 1 person discovery cycle (broader search)
- 500-person tree, 60% unverified ≈ 300 credits to fully process
- Pricing: €10 = 100 credits, €25 = 300 credits, €50 = 750 credits

Credits map to actual API/compute costs (LLM tokens + archive lookups).
Exact pricing requires measuring real costs during development.

## Paperclip AI Company

The product is built and operated by a Paperclip-managed agent team:

### Org Chart

- **CEO** — Rutger (human). Approves PRs, sets priorities, product decisions.
- **CTO agent** — breaks features into issues, assigns to engineers, reviews architecture
- **Frontend engineer** — templates, HTMX, CSS, user flows
- **Backend engineer** — FastAPI routes, models, billing logic
- **Research engineer** — ports archive skills to Python, builds engine
- **QA agent** — writes tests, runs on PRs, flags regressions
- **DevOps agent** — Dockerfile, CI/CD, deploy scripts
- **Datasource agent** — picks up "missing archive" issues, onboards new archive modules

### Worker Assignment

- **Claude Code** — complex research/skill work, architecture decisions
- **Codex** — straightforward backend tasks, bug fixes
- **Gemini** — frontend, docs, simpler features

### Workflow

1. Issue created in GitHub
2. CTO agent triages, assigns to appropriate engineer
3. Engineer agent picks up, writes code, opens PR
4. QA agent runs tests
5. Rutger reviews and merges

### Budget Controls

Per-agent token limits in Paperclip to prevent runaway costs.

## V2 Roadmap

After MVP validates:

1. Tree editor + research queue management
2. Subscription billing with auto-research
3. PDF story/narrative generation per family line
4. Archive self-expansion per customer request
5. Family collaboration (invite members)
6. Mobile-optimized UI
