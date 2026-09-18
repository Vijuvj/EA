# arch-compliance

A CLI agent that scores a solution architecture document against your
organization's architecture standards, using an LLM to grade each requirement
and deterministic code to aggregate the final compliance percentage.

Talks to any OpenAI-compatible chat-completions endpoint (OpenAI, Azure
OpenAI, Core42/G42 Compass, self-hosted gateways, etc.).

## How it works

1. **`normalize-standards`** — reads one or more standards documents (PDF,
   Word, or Excel) and asks the model to normalize them into a canonical
   rubric: a JSON list of atomic, checkable requirements, each with a
   category, mandatory flag, and weight (1-5).
2. **`evaluate`** — reads a solution architecture document (PDF or Word,
   including diagrams on PDF pages, sent to the model as images) and grades
   it against every rubric item, producing a verdict
   (`pass`/`partial`/`fail`/`not_applicable`) with evidence and rationale for
   each.
3. Scoring is aggregated in code (not by the LLM): `pass` = full weight,
   `partial` = half weight, `fail` = zero, `not_applicable` items are excluded
   from the denominator. This keeps the final percentage deterministic and
   auditable — the LLM only grades individual, evidence-backed items.

## Install

```bash
pip install -e .

# Point at your OpenAI-compatible endpoint, e.g. Core42/G42 Compass:
export COMPASS_API_KEY=...
export COMPASS_BASE_URL=https://<your-compass-endpoint>/v1
export ARCH_COMPLIANCE_MODEL=<model name available on your Compass account>

# Or, to use OpenAI directly instead:
# export OPENAI_API_KEY=sk-...
```

## Usage

```bash
# One-time: turn your standards docs into a rubric
arch-compliance normalize-standards \
  --input standards/security.pdf standards/patterns.docx standards/checklist.xlsx \
  --output rubric.json

# Evaluate an architecture doc against the rubric
arch-compliance evaluate \
  --architecture solutions/payments-platform-sad.pdf \
  --rubric rubric.json \
  --format md \
  --output report.md
```

Re-run `evaluate` against the same `rubric.json` for as many architecture
documents as you like — the rubric only needs to be regenerated when the
standards documents change.

## Notes / limitations

- `ARCH_COMPLIANCE_MODEL` env var selects the model (must be a model available
  on your endpoint/account, and must support image input to grade diagrams).
- `COMPASS_API_KEY`/`COMPASS_BASE_URL` (or `OPENAI_API_KEY`/`OPENAI_BASE_URL`)
  configure which OpenAI-compatible endpoint is used.
- Architecture text is truncated to ~60k characters and diagrams to the first
  20 PDF pages per call; very large documents may need to be split.
- Review the generated `rubric.json` before relying on it — spot-check that
  requirements were split atomically and weighted sensibly, since it's the
  basis for every future score.

# prr-readiness

A CLI for the change team to assess a change/service against SRE Production
Readiness Review (PRR) criteria before the `02 Production Readiness Review`
step of the release flow, and get a Ready / Conditional / Not Ready gate
decision to bring into TAB/CAB.

It's built on the same engine as `arch-compliance` (LLM grades each
criterion against the change docs, code aggregates the score), plus:

- A **built-in default rubric** (`prr_readiness/default_rubric.py`) grounded
  in Google's *The Site Reliability Workbook* (O'Reilly, 2018) — principally
  Ch.18 "SRE Engagement Model" (which defines the PRR itself), plus Ch.2
  Implementing SLOs, Ch.4 Monitoring, Ch.5 Alerting on SLOs, Ch.6 Eliminating
  Toil, Ch.8 On-Call, Ch.9 Incident Response, Ch.11 Managing Load, and Ch.16
  Canarying Releases. It's organization-agnostic — no internal policy or
  contract is referenced — covering SLOs/error budget, monitoring, alerting,
  toil, on-call, incident response, capacity/load, rollout safety,
  dependencies, and documentation.
- A **gate decision**: any mandatory criterion that fails blocks go-live
  (`NOT READY`); a partially-met mandatory criterion is `CONDITIONAL`;
  otherwise `READY`. Non-mandatory criteria only move the readiness
  percentage, not the gate.

## Usage

```bash
# Assess a change against the built-in SRE Workbook PRR rubric
prr-readiness assess --change release-notes/payments-v2.docx --format md --output prr-report.md

# Or bring your own SRE readiness checklist instead of the default rubric
prr-readiness normalize-criteria --input standards/sre-readiness-checklist.pdf --output criteria.json
prr-readiness assess --change release-notes/payments-v2.docx --rubric criteria.json
```

The `assess` command exits non-zero when the gate decision is `NOT READY`,
so it can be wired into a CI/CD gate ahead of the staged/canary go-live step.
Same environment variables and limitations as `arch-compliance` apply
(`ARCH_COMPLIANCE_MODEL`, `COMPASS_API_KEY`/`COMPASS_BASE_URL` or
`OPENAI_API_KEY`/`OPENAI_BASE_URL`, ~60k char / 20 page truncation).

## Web application

The change team can also run PRR assessments from a browser instead of the CLI:
upload a change doc, get back the gate decision, category scores, and findings,
without touching a terminal.

```bash
pip install -e ".[web]"
prr-readiness-web
# then open http://localhost:8000
```

- **`POST /api/assess`** — upload a change document (+ optional custom rubric
  JSON) and get back a `job_id`.
- **`POST /api/normalize-criteria`** — upload standards document(s) and get
  back a `job_id` for building a custom rubric.
- **`GET /api/jobs/{job_id}`** — poll for `pending` → `running` → `done`/`error`.

Both endpoints run as background jobs rather than blocking the request,
since grading a document against a rubric is an LLM call that can take
10-30+ seconds. The static frontend (`prr_readiness/static/`) is plain
HTML/CSS/JS with no build step or external dependencies — it submits a job
and polls the status endpoint until it resolves.

The server-side `OPENAI_API_KEY`/`COMPASS_API_KEY` etc. are read from the
environment the server runs in — they are never exposed to the browser.
Configure host/port via `PRR_WEB_HOST` / `PRR_WEB_PORT` (default
`0.0.0.0:8000`). This is a single-process server (in-memory job store —
keep replicas at 1, or swap `_jobs` for Redis if you need more).

**Authentication:** set `PRR_WEB_USERNAME` / `PRR_WEB_PASSWORD` to turn on
HTTP Basic Auth for every route. If either is unset, the server starts with
no authentication and prints a warning — fine for `localhost`, never for a
public URL, since an unauthenticated deployment lets anyone with the link
submit jobs against your LLM API key.

## Deploying it as a public web tool

The app is a standard FastAPI service (`Dockerfile` at the repo root), so
any container host works. Steps for a permanent public URL:

1. **Push this repo (or just this branch) to your own git remote** if you
   haven't already — most hosts deploy straight from a connected repo.

2. **Set the required environment variables on the host** (never commit
   these):
   - `OPENAI_API_KEY` (or `COMPASS_API_KEY` + `COMPASS_BASE_URL`)
   - `ARCH_COMPLIANCE_MODEL` — a model available on your endpoint that
     supports image input
   - `PRR_WEB_USERNAME` / `PRR_WEB_PASSWORD` — required for any public
     deployment (see Authentication above)

3. **Deploy the `Dockerfile`** on whichever host you prefer:
   - **Render**: New → Web Service → connect the repo → it auto-detects
     the `Dockerfile` → add the env vars above → Deploy. You get
     `https://<your-app>.onrender.com`.
   - **Railway**: `railway init` in the repo, then `railway up` (or connect
     the repo in the dashboard) → add the env vars → you get
     `https://<your-app>.up.railway.app`.
   - **Fly.io**: `fly launch` (detects the `Dockerfile` and asks a few
     questions) → `fly secrets set OPENAI_API_KEY=... PRR_WEB_USERNAME=...
     PRR_WEB_PASSWORD=...` → `fly deploy` → you get
     `https://<your-app>.fly.dev`.
   - **Any other Docker host** (Cloud Run, ECS, a VM, etc.): `docker build
     -t prr-readiness . && docker run -p 8000:8000 -e OPENAI_API_KEY=...
     -e PRR_WEB_USERNAME=... -e PRR_WEB_PASSWORD=... prr-readiness`, then
     point that host's load balancer/ingress at container port `8000`
     (the container also honors a `PORT` env var if the host sets one,
     e.g. Cloud Run).

4. **Verify:** open the URL, confirm the browser prompts for the basic-auth
   credentials, log in, and run a small assessment end-to-end before
   sharing the link.

5. **Share the link** — anyone with the URL and credentials can now use the
   tool from a browser with no local setup.
