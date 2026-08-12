# Ops Command Center — Data Center Asset & Network Outage Tracker

A lightweight internal tool that turns raw infrastructure events into human-readable incident reports, root-cause hypotheses, and stakeholder communications — built in a single day to demonstrate rapid, AI-assisted prototyping for operational efficiency.

## Why this exists

Internal IT/network teams typically spend significant time manually writing up incidents after the fact: what broke, why, who needs to know, and what it cost. This tool automates that translation layer — from a raw outage event to a polished, ready-to-send incident report — so engineers can focus on the fix, not the paperwork.

**The business case:**
- Manual incident write-ups typically take 20–40 minutes each
- A mid-size org can see 10–20+ minor/major incidents per month
- Automating the first draft of the report + stakeholder email could save several hours per month per team, while producing more consistent, complete documentation than ad-hoc write-ups

## What it does

- **Asset inventory** — tracks servers, network devices, and their relationships/dependencies
- **Incident logging** — records outage/downtime events against assets, with severity and duration
- **AI-generated incident reports** — turns raw event data into a structured, readable incident summary
- **Root-cause hypothesis drafting** — AI suggests likely causes based on the asset type, event pattern, and historical incidents on record
- **Stakeholder communication drafts** — auto-generates a plain-English update email for non-technical stakeholders
- **Downtime cost & MTTR dashboard** — visualizes trends: incident frequency, mean time to resolution, and estimated downtime cost avoided over time

## Tech stack

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI |
| Database | PostgreSQL |
| Frontend | React, Tailwind CSS |
| Tooling | Node.js (Vite dev server / build) |
| AI layer | LLM-based report/RCA/email generation via prompt-engineered API calls |

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React UI   │◄────►│  FastAPI     │◄────►│  PostgreSQL  │
│  (Tailwind)  │      │  REST API    │      │              │
└─────────────┘      └──────┬───────┘      └─────────────┘
                             │
                             ▼
                     ┌───────────────┐
                     │  AI Report/RCA │
                     │  Generation     │
                     └───────────────┘
```

## Data model (simplified)

- **assets** — id, name, type (server/network device), location, status
- **incidents** — id, asset_id (FK), severity, start_time, end_time, description
- **incident_reports** — id, incident_id (FK), ai_summary, root_cause_hypothesis, stakeholder_email_draft, generated_at

## Getting started

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Environment variables needed (see `.env.example`):
- `DATABASE_URL` — Postgres connection string
- `LLM_API_KEY` — API key for the AI report generation layer

## Demo data

This build uses a synthetic asset inventory and simulated outage events (no real company data) to demonstrate the workflow end-to-end. See `seed_data.py` for the generator.

## How this was built

This project was built in a single day using an AI coding agent (Claude) for rapid prototyping — from initial scaffolding through iteration. A companion build log documenting the prompting process, decisions, and troubleshooting is included in [`BUILD_LOG.md`](./BUILD_LOG.md).

## Roadmap / what's next

- **Smart Site IoT Telemetry module** — extend the same architecture (assets → events → AI narration → dashboard) to live sensor data from construction sites (vibration, temperature, dust levels), enabling real-time anomaly alerts
- Real-time WebSocket updates instead of polling
- Historical trend-based root-cause suggestions (pattern matching across past incidents)
- Role-based access for different stakeholder views (engineering vs. leadership)
- Packaging as a modular, reusable internal platform ("Ops Command Center") that could extend to other operational domains (site inspection, safety incidents, material delivery tracking)

## Discovery approach (hypothetical)

Since this was built without access to a real internal team, here's how I'd validate and scope this with actual stakeholders before building further:
- Interview IT/network ops staff: how long does incident write-up currently take? What's missing from current reports?
- Confirm what "good enough" AI-generated RCA looks like to an experienced engineer — where would they trust it vs. want to override it?
- Identify the actual stakeholder audience for incident emails, and what tone/detail level they expect
