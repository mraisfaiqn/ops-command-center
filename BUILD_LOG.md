# Build Log — Ops Command Center

A record of how this project was actually built: the prompting process, decisions made along the way, and the real troubleshooting that came up. Written for anyone (including an interviewer) who wants to see how I work with an AI coding agent, not just the finished output.

## Scoping the idea

I started with a broader job description for an "AI Engineer" role and generated a handful of technically deep project ideas (RAG pipelines, evaluation harnesses, AI gateways). Partway through, I realized I had the wrong JD — the actual role I was targeting was a **Forward Deployed Engineer** position, which explicitly values rapid, AI-agent-driven prototyping ("vibe coding") and business communication over deep infrastructure engineering.

That changed the shape of the project entirely. I discarded the infra-heavy ideas and reframed around: pick a plausible internal pain point, build a working tool fast using an AI coding agent, and be able to talk about the business value — not just the tech stack. I also proposed several domain-flavored ideas (RFI triage, site inspection reports, water treatment monitoring) tied to the target company's actual business lines, since generic SaaS demos are less convincing than something that shows I understood who I was building for.

**Decision:** Data Center Asset & Network Outage Tracker — it maps cleanly onto standard CRUD + relational data (a good fit for the requested stack), doesn't require any real company data to build convincingly, and has a very quantifiable business case (incident write-up time saved, MTTR).

## Stack and scope decisions

- **FastAPI + Postgres + React + Tailwind**, per the role's listed stack, with Node handling frontend tooling (Vite).
- Chose to **merge two related project ideas into one platform with a single working module** rather than half-build two separate apps — reduced risk of finishing nothing well within a single day.
- Deliberately **did not build**: real-time WebSocket streaming, authentication, historical trend charts. All three would have added engineering time without adding much interview signal for this specific role, which explicitly deprioritizes deep infrastructure work. They're documented in the README roadmap instead of built badly under time pressure.
- Synthetic data only — no access to the target company's real systems, so the seed script generates a plausible multi-site asset inventory and simulated incidents rather than requiring real inputs.

## Troubleshooting log

Real issues hit during the build, in order:

**1. Empty repo on first push**
```
git push -u origin master
error: src refspec master does not match any
```
Turned out no commit had been made yet — there was nothing for Git to push. Fixed by running `git add .`, `git commit`, then `git branch -M main` (to match GitHub's current default branch name) before pushing.

**2. `useState is not defined`**
`App.jsx` called `useState(0)` without importing it from React. Easy fix (`import { useState } from 'react'`), but a good reminder that hooks aren't ambient — every file needs its own import. Ended up removing the unused hook entirely rather than importing something not yet in use.

**3. Gemini auth failure: `ACCESS_TOKEN_SCOPE_INSUFFICIENT`**
The AI report generation endpoint returned a 403 the first time it ran. Root cause turned out to be twofold:
- `ChatGoogleGenerativeAI` expects the parameter `google_api_key`, not `api_key` — I'd used the wrong kwarg name, so the client silently fell back to ambient Google credentials with the wrong OAuth scopes instead of erroring immediately.
- Separately, the actual `.env` variable name didn't match what `os.getenv()` was reading (a naming mismatch between `GEMINI_API_KEY` in the file and in the code).

Both had to be fixed together. This was the single most instructive bug in the build — a wrong parameter name failed *silently* by falling back to a different (broken) auth path instead of raising a clear error, which made it look like a Gemini-side problem rather than a one-line typo.

## How I validated AI output before shipping it

- Ran the `/generate-report` endpoint against real seeded incidents and read every field before trusting it, not just checking that the API call succeeded.
- Specifically checked that the **root cause hypothesis was appropriately hedged** ("likely resulted from," not stated as fact) — an LLM confidently asserting a root cause it can't actually know would be a real production risk in a tool like this, so the prompt explicitly instructs the model to phrase it as a hypothesis for engineers to validate.
- Checked that the **stakeholder email tone actually shifted** for a non-technical audience — no jargon, focused on impact and resolution, not technical detail. This mattered because the JD explicitly calls out communicating with non-technical stakeholders as a core skill, not just generating any text.

## What I'd do differently with more time

- Add a small "bulk generate" script to pre-populate a few reports as a demo safety net, in case a live API call is slow or fails during an actual interview walkthrough.
- Get real discovery input instead of hypothetical stakeholder assumptions — the README's "Discovery approach" section is honest about this being simulated, not real.
- Add basic tests around the AI output parsing, since a malformed JSON response from the model is the most likely failure mode in production use.
