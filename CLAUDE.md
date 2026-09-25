# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

CDC is a Portuguese association/club management application built with FastAPI. It manages members, dues payments, donations, items, sellers, categories, and expense accounts. The UI is in Portuguese.

## Running the Application

### Local development (no SSL)
```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-config app/log.ini --reload --header App:CDC
```

### Local with SSL
```sh
uvicorn app.main:app --host 0.0.0.0 --port 5443 --log-config app/log.ini --reload \
  --ssl-keyfile data/privkey.pem --ssl-certfile data/fullchain.pem
```

### Docker
```sh
./build_run_docker.sh          # build base + app images, run container
./build_run_docker.sh update   # rebuild after code changes
./build_run_docker.sh stop     # stop running instance
```

Two-stage Docker build: `Dockerfile.base` (python:3.12-slim + pip deps) produces `gqcv-base`, then `Dockerfile` copies app code on top. The `data/` directory is mounted as a volume at `/gqcv/data`.

## Branching Strategy

- **`main`** — stable/release branch for the default CDC application
- **`develop`** — integration branch, features are developed here first
- **`release/*`** — customer-specific branches (e.g., `release/cecc`). These differ only in naming/config (app name, env var prefixes, page titles), not in business logic. New features should be cherry-picked between `develop` and `release/*` branches to keep them in sync.

## Architecture

**Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 (SQLite at `data/data.spsql`), Pydantic v2, Jinja2 templates, JWT auth (python-jose).

### Layer structure (all under `app/`)

- **`main.py`** — FastAPI app, lifespan (DB init + `recalculate_all_members_totals()` on startup), middleware (session + request logging + IP filtering), exception handlers, router registration. Static files served from `app/web/static/`.
- **`api/`** — JSON REST endpoints under `/api/`. Each file is a router for one domain entity. Auth via `GET_CURRENT_API_CLIENT` (OAuth2 bearer token).
- **`web/`** — Server-rendered HTML endpoints under `/web/`. Same CRUD ops as API but return Jinja2 templates. Auth via `GET_CURRENT_WEB_CLIENT` (cookie-based token). Flash messages via session.
- **`db/models/`** — SQLAlchemy ORM models. `MemberAbs` is abstract base for `Member` and `MemberHistory`.
- **`db/schemas/`** — Pydantic schemas (Create/Update/View variants per entity). Re-exported from `db/schemas/__init__.py`.
- **`db/crud_*.py`** — Database operations. Pattern: query → mutate → commit/rollback → refresh.
- **`db/database.py`** — Engine, session, `Base`. Single module-level `SessionLocal()` instance.
- **`sec/`** — OAuth2 token auth (`security.py`), credential management from `data/credentials.json`, IP-based rate limiting/blocking (`block_traffic.py` using `data/access_list.json`).
- **`utils/`** — Date helpers (Europe/Lisbon timezone), JSON file I/O, base64, Excel export via pandas/openpyxl, custom exceptions.

### Auth & scopes

Clients are defined in `data/credentials.json` with scoped permissions (e.g., `app:read`, `app:create`, `member:update`). Every endpoint calls `are_valid_scopes()` to check authorization. Two auth paths: API (bearer token via `oauth2_scheme`) and Web (cookie `access_token`).

### IP filtering

`block_traffic.py` tracks error-status thresholds per client IP. Too many 4xx/5xx responses auto-block the IP. Config and blocked list persist to `data/access_list.json`. Successful (2xx/3xx) requests reset the counter.

### Request flow

All requests pass through `LogHTTPSMiddleware` which: validates IP isn't blocked → forwards request → updates IP counters → logs traffic → adds HSTS header via `unified_response()`.

## Key Patterns

- **Adding a new entity:** Create model in `db/models/`, schema in `db/schemas/` (with Create/Update/View variants), CRUD functions in `db/crud_*.py`, API router in `api/`, web router in `web/`, templates in `web/templates/<entity>/`. Register routers in `main.py`. Export schemas/models from their `__init__.py`.
- **Scope checks:** Always call `are_valid_scopes(["app:<action>", "<entity>:<action>"], current_client)` at the start of every endpoint.
- **Error handling:** Raise `CustomException` subclasses (`NotFound404`, `Conflict409`, `TooManyRequests429`). The middleware routes errors to JSON or HTML based on whether the path starts with `/web/`.
- **DB transactions:** Wrap mutations in try/except with `db.rollback()` on failure. Nested transactions use `db.begin(nested=db.in_transaction())` for savepoints.
- **Batch web endpoints:** Some web POST endpoints accept JSON (via `fetch`) instead of form data for batch operations (e.g., selling multiple items at once). These return `JSONResponse` with a redirect URL instead of `RedirectResponse`.

## Data Files (in `data/`, gitignored)

- `credentials.json` — client auth config (use `data/template_credentials.json` as reference)
- `access_list.json` — IP blocking config (use `data/template_access_list.json` as reference)
- `data.spsql` — SQLite database (auto-created on first run)
- `privkey.pem` / `fullchain.pem` — SSL certs (only needed for HTTPS mode)

## Environment Variables

- `CDC_SECRET_KEY` — App/JWT secret key (fallback: `_def#app_secret_key`)
- `CDC_SALT` — Password hashing salt (fallback from credentials.json)
- `CDC_MODE=TEST` — Enables `clear_db()` function for test cleanup
- `NAME` — Application name (default: `CDC`, or `CECC` on customer branches)

## Git Configuration

This repo uses SSH commit signing with a local override: `user.signingkey = ~/.ssh/id_rsa.pub` (the global config uses `id_ed25519`, but this repo's remote uses the `github-pjn` SSH host alias which requires `id_rsa`).
