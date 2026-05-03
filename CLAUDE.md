# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All workflow commands run through `just` (see `justfile`):

- `just dev` — runs Uvicorn with reload **and** the Tailwind v4 watcher concurrently. The dev server expects `PYTHONPATH=src` and listens on port 8000.
- `just stop` — kills the running uvicorn process (`pkill -f uvicorn`).
- `just format` — `ruff format` + `ruff check --fix` for Python, `djlint --reformat` for HTML/Jinja.
- `just lint` — `ruff check` + `djlint --lint` (non-mutating; CI-style).
- `just seed` — runs `scripts/seed.py` to populate `database.db` with admin/resident users, hospitals, master schedule, and bookings. Skips if any User already exists.
- `just reset-db` — deletes `database.db` and re-seeds from scratch.
- `just inspect` — runs `scripts/inspect_db.py` to dump current DB contents.

Running things directly (any command that imports app code needs `PYTHONPATH=src`):

- Tests: `PYTHONPATH=src uv run pytest` — single test: `PYTHONPATH=src uv run pytest src/tests/features/residents/test_custom_slot.py::test_create_custom_slot_success`.
- Migrations: `uv run alembic upgrade head`, `uv run alembic revision --autogenerate -m "msg"`. `migrations/env.py` auto-imports every `models.py` under `src/` via `rglob`, so new feature models are picked up automatically — no manual import needed.
- Default seeded credentials: `admin@example.com` / `resident@example.com`, password `password123`.

Note: `main.py` calls `SQLModel.metadata.create_all(engine)` on startup as a temporary shortcut alongside Alembic; both paths exist intentionally.

## Architecture

### Vertical slices with CQRS-style handlers

Code is organized by feature, not by layer. Each slice lives in `src/features/<feature>/` and contains:

- `router.py` — FastAPI routes, the only place that talks to HTTP.
- `models.py` — `SQLModel` table classes for the feature.
- `commands/<verb>.py` — write operations. Each file exports a `<Verb>Command` dataclass and a `<Verb>Handler` class with `__init__(self, db: Session)` and `execute(self, command) -> ...`.
- `queries/<verb>.py` — read operations, same `Query` + `Handler.execute(query)` shape.
- `templates/` and `templates/partials/` — feature-local Jinja templates.

Routers stay thin: parse the form/query, build a `Command`/`Query` dataclass, instantiate `Handler(db).execute(...)`, render a template. Business logic, validation that touches the DB, and password hashing live in handlers. The README says "use_cases/" — the actual code uses **`commands/` and `queries/`**; follow the existing pattern when adding code.

Current slices: `home` (root + dashboard link-tree + admin user CRUD), `users` (login/register/logout), `hospitals` (master schedules, public grid view, admin-only edit), `residents` (the resident's `/my-calendar` and personal `BookedSlot` records), `info` (hard-coded Key Information and Contacts pages — content lives in templates, no DB tables yet).

### Shared infrastructure (`src/core/`)

- `database.py` — single SQLite engine at `database.db`; `get_session()` is the FastAPI session dependency.
- `auth.py` — `get_current_user` reads the `user_session` cookie (just the user id, HTTP-only) and returns the `User` or `None`. There is no JWT, no middleware — every protected route must `Depends(get_current_user)` and check for `None` itself, returning a 302 to `/login` (full page) or `HTMLResponse("Unauthorized", 401/403)` (HTMX). Admin checks compare `current_user.role` to `"admin"`.
- `logger.py` — `setup_logging()` (called once in `main.py`) hijacks Uvicorn/FastAPI logs into Loguru. Use `from loguru import logger` everywhere.

### HTMX partial-rendering pattern

This is pervasive — match it in every new route. Each page route checks `request.headers.get("hx-request") == "true"` and returns either:

- the full page template (`templates/foo.html`, which extends `base.html`), or
- the partial fragment (`templates/partials/foo_content.html`) when HTMX is swapping into `#main-content`.

`Jinja2Templates` is constructed with a **list** of directories, e.g. `["src/features/residents", "src/templates"]`, so templates reference the feature folder as `templates/...` and shared templates by name. The shared `src/templates/base.html` provides the sidebar shell and a `#main-content` swap target; `hx-boost="true"` is set on `<body>`.

HTMX-specific response headers used in this codebase:

- `HX-Redirect: <url>` — full client-side redirect after a successful POST/DELETE; routes return both this (for HTMX) and a 302 `Location` (for non-HTMX) where applicable.
- `HX-Trigger: hospitalSelected` (or JSON `{"hospitalSelected": {"short_name": ...}}`) — re-renders the sidebar hospital list, which polls `/hospitals/nav` on this trigger. Every page route should set this header so the sidebar stays in sync after an HTMX swap.

### Dashboard & navigation as a link tree

`/dashboard` is a launcher of compact `<a class="card">` tiles in four sections (Workspace, My work, Hospitals, Admin) — not a content page. The sidebar (`src/templates/components/_nav_links.html`, included by both the desktop sidebar in `base.html` and the mobile dialog) mirrors the same sections, so adding a new top-level surface means editing both files. Inner pages start with a `← Back to dashboard` button (`btn btn-secondary btn-sm mb-10`) using HTMX swap into `#main-content`.

**Auth-gated tiles** stay visible to logged-out users — they swap their right-side affordance for a lock icon + "Login required" via the shared `indicator(lock=True)` macro in `src/templates/components/_indicators.html`, and link to `/login?next=<destination>` (full nav, not HTMX) so login redirects back. Same convention for sidebar items. The indicator macro also renders status dots (`accent` / `success` / `warning` / `danger`) and short text badges; reuse it for any new card or nav row instead of inventing new visual treatments.

The dashboard handler loads a single `GetDashboardSummaryQuery` (per-hospital slot counts, my-bookings flag, upcoming-shift count + worst status) — one round-trip, do not add per-card queries.

### Data model essentials

- `User` has a `UserRole` enum (`admin`, `resident`); `is_active`/`is_superuser` exist but most authorization is via `role`.
- `Hospital` has both `name` (display) and `short_name` (URL slug, no spaces, enforced in `CreateHospitalHandler` and the router).
- `MasterSlot` is the admin-defined recurring schedule, keyed by `day_of_week`. Two fields drive separate concerns:
  - `time_block` — what residents claim (`AM`, `PM`, or `AM/PM`); the per-day claim list shows AM/PM buttons based on this.
  - `session` — which row of the Service × Day grid the slot renders in (`AM` or `PM` only). An "AM/PM" clinic is seeded as **two rows** (one per session) both with `time_block="AM/PM"` so it appears in both grid rows while the claim flow still offers AM/PM/both buttons.
  - `qualifier` — short suffix (e.g. `wk 1&3`, `9–12`, `once a month`, `Telemed only`) rendered in muted text next to the physician name in the grid.
- `BookedSlot` is the resident's personal tracked shift, with a `SlotStatus` workflow (`To Contact` → `Emailed` → `Confirmed`). `BookedSlot` denormalizes hospital/physician/specialty fields from the master slot rather than holding a foreign key, so editing a `MasterSlot` does not retroactively change bookings.

### Hospital page layout

`/hospitals/{short_name}` renders three things in order: back-to-dashboard button, the **Service × Day grid** (`partials/schedule_grid.html`, fed by `GetScheduleGridHandler`), and the **per-day claim list** (the original `public_calendar_content.html` content, with AM/PM claim buttons for logged-in residents). The grid has a "Download as image" button that calls a global `downloadGrid(id, filename)` JS helper using `html2canvas` (loaded from CDN in `base.html`); the table is wrapped in `overflow-x-auto` so on-screen scroll stays usable while the captured node renders at full unscrolled width — do not collapse columns to fit mobile.

### Testing

`src/tests/` mirrors `src/features/`. Tests use FastAPI's `TestClient` and override `get_session` and `get_current_user` via `app.dependency_overrides` against an in-memory SQLite (`StaticPool`). The test imports look like `from main import app` and `from features.users.models import User` — they rely on `PYTHONPATH=src`.

## Conventions

- Python 3.13, formatted with `ruff` (line length 88, double quotes). Lint rules enabled: `E, F, I, UP, B, C4`. Pyright runs in `basic` mode and ignores `migrations/` and `.venv/`.
- Imports from app code use the `features.x.y` / `core.x` form (no `src.` prefix) because `PYTHONPATH=src`.
- Passwords are hashed with `pwdlib`'s `PasswordHash.recommended()` (Argon2). Never store or compare raw passwords.
- Inline error HTML is returned with `status_code=200` for HTMX form submissions so HTMX swaps the error markup in place — don't change those to 4xx without also updating the front-end swap target.
- Deployment is Render (`render.yaml`): `uv sync --frozen` + Tailwind build at build time; `alembic upgrade head` + `uvicorn main:app` at start time, with `PYTHONPATH=src`.
