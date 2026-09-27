# Notes — Sanctum Sanctorum

## 1. Deployment & Live Verification

- **Live Application:** https://sanctum-sanctorum-main-0soj.onrender.com
- **Interactive OpenAPI Docs:** https://sanctum-sanctorum-main-0soj.onrender.com/docs
- **Health Check Endpoint:** https://sanctum-sanctorum-main-0soj.onrender.com/health

### Quick-Test Seed Personas
The database auto-seeds on first launch with members representing each tier:
- **Supreme (ID 1 — `wong@example.com`):** 15% discount, 10 active loan capacity, unrestricted catalogue access.
- **Master (ID 2 — `christine@example.com`):** 10% discount, 5 active loan capacity, unrestricted catalogue access.
- **Adept (ID 3 — `jonathan@example.com`):** 5% discount, 3 loan capacity.
- **Apprentice (ID 4 — `sara@example.com`):** Baseline tier (0% discount, 1 loan capacity, restricted book access denied).

---

## 2. Completed Scope & Extras

- **Core System (202 / 202 tests passing):** Implemented all domain logic across Books, Members, Orders, Loans, and Reports in strict accordance with `SPEC.md`.
  - *Note on Test Warnings:* The 2 deprecation warnings in `pytest` originate entirely inside upstream third-party dependencies (`starlette.testclient` and `anyio` imports), not application code. Per the assignment ground rules ("Don't add new dependencies"), `pyproject.toml` was left unmodified, making these upstream library notices expected and benign.
- **Targeted Extensions:**
  - **Deadlock-Free Atomic Stock Reservation:** Addressed the optional concurrent ordering challenge by acquiring inventory via atomic conditional SQL statements ordered by primary key.
  - **Member Pagination:** Extended `GET /members` with consistent `limit`/`offset` pagination and query validation matching `GET /books`.

---

## 3. Architecture & Technical Decisions

- **Domain-Driven Service Layer:** Kept routers purely as thin HTTP translation layers (parameter extraction, status code mapping, schema validation). All business invariants, state transitions (e.g. pending → paid/cancelled, active → returned), and fee calculations reside entirely within `app/services/`.
- **Concurrency & Transaction Integrity:**
  - Standard ORM attribute mutation (`book.stock -= qty`) is prone to race conditions and overselling when concurrent checkouts hit low inventory.
  - Resolved this by issuing atomic conditional updates (`UPDATE books SET stock = stock - :qty WHERE id = :id AND stock >= :qty`). If `rowcount == 0`, the transaction rolls back immediately and returns `409 Conflict`.
  - Sorted multi-item book IDs prior to locking/updating to prevent circular wait deadlocks when concurrent carts contain overlapping book sets.
- **Database & Hosting Trade-offs:**
  - The assignment ground rules strictly required avoiding new dependencies. Connecting to an external database like PostgreSQL would have required adding a database driver (such as `psycopg2` or `psycopg`). Given this constraint, SQLite was the ideal fit—it relies entirely on Python's built-in `sqlite3` driver, introduces zero external dependencies, and maintains 100% parity with the local test suite.
  - Deployed on **Render** (free tier). Render's free tier lacks persistent disk storage, meaning local SQLite files reset if the container restarts or redeploys; this architecture is obviously not suitable for real production. However, because our startup lifecycle automatically re-seeds the demo data whenever the database is empty, it is perfectly suited for evaluation and development.
  - Configured an **autopinger** targeting `/health` to keep the container warm and prevent Render from spinning down during review.
  - If adding new dependencies were permitted, the preferred production setup would be managed serverless PostgreSQL via **Neon** (using `psycopg` with connection pooling) to handle concurrent write serialization across multiple workers.
- **Code Style & Quality:** Used Ruff (configured via `ruff.toml`) to enforce strict formatting, linting, and Python 3.10 conventions across the entire codebase.

---

## 4. Spec Ambiguities
- The spec was thorough, consistent, and unambiguous. No assumptions or workarounds outside the spec were required.

---

## 5. AI Usage

- **Tools:** Antigravity / Gemini coding assistant.
- **Workflow:** Used for rapid initial scaffolding of Pydantic v2 validation models, standard CRUD endpoints, and test harness execution.
- **Critical Override:** The AI's initial implementation for order placement relied on in-memory stock validation followed by a standard ORM decrement and commit. This created a classic check-then-act race condition vulnerable to overselling under load. I overrode this approach by restructuring the reservation loop to use database-level atomic conditional updates (`WHERE stock >= quantity`) sorted by ID to guarantee linearizable inventory management.
