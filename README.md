<div align="center">

# lmk — backend

### from *let me know,* to *let's go.*

The API behind **lmk**, the group decision-making app. It runs sessions, collects
everyone's answers, and uses AI to turn the group's input into a clear outcome —
a top pick, where you agree, where you split, and a recommendation to act on.

<sub>Built with FastAPI · SQLAlchemy · Supabase (PostgreSQL) · OpenAI · SSE</sub>

<br />

[![Live Site](https://img.shields.io/badge/Live_Site-letmeknow.quest-2ea44f?style=for-the-badge)](https://www.letmeknow.quest)
[![Devpost Submission](https://img.shields.io/badge/Devpost-Submission-blue?style=for-the-badge&logo=devpost&logoColor=white)](https://devpost.com/software/letmeknow-from-let-me-know-to-let-s-go)
[![YouTube Demo](https://img.shields.io/badge/YouTube-Demo-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=iX3x_TzALr8)

🏆 **Winner** — *Product Bundle by Mind the Product* at [World Product Day: Everyone Ships Now](https://devpost.com/software/letmeknow-from-let-me-know-to-let-s-go) hackathon.

---

### 📺 Watch the Demo

[![lmk Demo Video](https://img.youtube.com/vi/iX3x_TzALr8/hqdefault.jpg)](https://www.youtube.com/watch?v=iX3x_TzALr8)

</div>

---

## Overview

lmk (short for *LetMeKnow*) helps a group go from "where should we eat?" to an
actual plan. A host starts a session on a topic, shares a join link, and everyone
answers a few quick questions. The backend generates the questions, gathers the
answers, and asks an LLM to distill them into results that are streamed back to
every participant in real time.

This repository is the **backend API**. The React frontend lives in
[EJD222/lmk-frontend](https://github.com/EJD222/lmk-frontend).

## How it works

```
  Client (frontend)            Backend (this repo)              OpenAI
  ─────────────────            ───────────────────              ──────
  1. POST /sessions/      ──▶  create session + AI questions ──▶  generate Qs
  2. join + submit answers ─▶  persist participants & answers
  3. host advances        ──▶  build prompt from answers     ──▶  generate results
  4. subscribe to stream  ◀──  SSE state_change events
  5. GET /results         ◀──  top pick, agreement, split, recommendation
```

1. **Create** — a session is created for a topic; the AI service generates the
   question set (multi-select, slider, swipe, text, number).
2. **Join & answer** — participants join via the link and submit answers, which
   are persisted against the session.
3. **Generate** — when the host advances the session, the AI service composes the
   group's answers into a prompt and produces structured results.
4. **Stream** — session state changes are pushed to all clients over
   Server-Sent Events, so results appear live.

## Tech stack

| Area            | Choice                                                       |
| --------------- | ------------------------------------------------------------ |
| Framework       | [FastAPI](https://fastapi.tiangolo.com/)                     |
| Language        | Python 3.13                                                  |
| ORM             | [SQLAlchemy 2](https://www.sqlalchemy.org/)                  |
| Migrations      | [Alembic](https://alembic.sqlalchemy.org/)                   |
| Database        | [Supabase](https://supabase.com/) ([PostgreSQL](https://www.postgresql.org/)) (`psycopg2`) |
| AI              | [OpenAI](https://platform.openai.com/) (`gpt-4o` by default) |
| Validation      | [Pydantic v2](https://docs.pydantic.dev/)                    |
| Realtime        | Server-Sent Events ([`sse-starlette`](https://github.com/sysid/sse-starlette)) |
| Rate limiting   | [SlowAPI](https://github.com/laurentS/slowapi)               |
| Server          | [Uvicorn](https://www.uvicorn.org/) / [Gunicorn](https://gunicorn.org/) |
| Packaging       | [Poetry](https://python-poetry.org/)                         |
| Analytics       | [Pendo](https://www.pendo.io/)                               |

## Project structure

```
app/
├─ main.py          # FastAPI app: middleware, routers, static mount
├─ config.py        # settings / environment loading
├─ constants.py     # shared constants
├─ db.py            # SQLAlchemy engine & session
├─ routers/         # HTTP routes (sessions, participants, answers)
├─ models/          # SQLAlchemy models (session, participant, question, answer, result)
├─ schemas/         # Pydantic request/response schemas
├─ services/        # business logic (ai, session, question, answer, result, event_manager, …)
├─ middleware/      # CORS, rate limiting
└─ utils/           # helpers (HTTP status codes, etc.)
alembic/            # database migrations
bruno/              # Bruno API client collection
```

## API surface

All responses are wrapped in a `{ success, data, error }` envelope.

| Method | Endpoint                                               | Description                       |
| ------ | ------------------------------------------------------ | --------------------------------- |
| `POST` | `/sessions/`                                           | Create a session (returns join link) |
| `GET`  | `/sessions/{id}`                                       | Session info                      |
| `GET`  | `/sessions/{id}/state`                                 | Current state + results readiness |
| `POST` | `/sessions/{id}/advance`                               | Advance the session (host)        |
| `GET`  | `/sessions/{id}/questions`                             | Generated questions               |
| `GET`  | `/sessions/{id}/stream`                                | SSE stream of state changes       |
| `GET`  | `/sessions/{id}/results`                               | Final results                     |
| `GET`  | `/sessions/{id}/participants/answered`                 | Participants who have answered    |
| `GET`  | `/sessions/{id}/participants/{pid}/answered`           | Whether a participant has answered |
| `POST` | `/sessions/{linkId}/participants/`                     | Join a session                    |
| `POST` | `/answers/…`                                            | Submit answers                    |

> Interactive docs are available at `/docs` (Swagger) and `/redoc` when the server is running.

## Getting started

### Prerequisites

- **Python 3.13+**
- **PostgreSQL** database
- **Poetry** (`pipx install poetry`)
- An **OpenAI API key**

### Install & run

```bash
git clone https://github.com/Kent-Danielle/lmk-backend.git
cd lmk-backend
poetry install

cp .env.example .env        # fill in DATABASE_URL, OPENAI_API_KEY, etc.
poetry run alembic upgrade head        # apply migrations

poetry run uvicorn app.main:app --reload    # http://localhost:8000
```

> Prefer pip? `pip install -r requirements.txt`, then run the same `alembic` / `uvicorn` commands.

### Environment

Configuration lives in `.env` (see `.env.example`):

| Variable         | Description                                  | Example                                        |
| ---------------- | -------------------------------------------- | ---------------------------------------------- |
| `DATABASE_URL`   | PostgreSQL connection string                 | `postgresql://user:password@host:5432/lmk`     |
| `OPENAI_API_KEY` | OpenAI API key                               | `sk-...`                                        |
| `OPENAI_MODEL`   | Model used for generation                    | `gpt-4o`                                         |
| `FRONTEND_URL`   | Allowed CORS origin (the frontend)           | `http://localhost:5173`                         |

## Database migrations

```bash
poetry run alembic upgrade head                       # apply latest
poetry run alembic revision --autogenerate -m "msg"   # create a new migration
```

## Contributors

| | Contributor | GitHub |
| --- | --- | --- |
| 👨‍💻 | **Kent-Danielle Concengco** | [@Kent-Danielle](https://github.com/Kent-Danielle) |
| 👩‍💻 | **Elmalia Jane Diaz** | [@EJD222](https://github.com/EJD222) |

## License

Released under the [MIT License](./LICENSE).
</content>
