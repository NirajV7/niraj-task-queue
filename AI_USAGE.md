# AI Usage History

This document contains a condensed history of my collaboration with an AI assistant, focusing on the key technical challenges encountered and how they were resolved during the development of the Smart Task Queue project.

---

### Challenge 1: Persistent Database Migration Failures

**Initial Problem:** After setting up the project and creating the first Alembic migration, the application consistently failed with a `sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) relation "jobs" does not exist`.

**Debugging Process:**

1.  **Initial Hypothesis:** The first assumption was that the Alembic migration command was not being run correctly. The AI suggested running the command inside the Docker container using `docker-compose exec web alembic upgrade head`.
2.  **Problem Persists:** Even after running the command manually, the error continued. This indicated a more complex issue.
3.  **Deeper Dive:** The AI guided me through a process to connect directly to the database container (`docker-compose exec db psql ...`) and inspect the tables with `\dt`. This proved that the `jobs` table was, in fact, not being created, even though the migration logs claimed it was running.
4.  **Race Condition Hypothesis:** The AI proposed that a race condition was occurring: the application container was starting and trying to access the database *before* the migrations had a chance to run.
5.  **Solution:** To solve this permanently, the AI provided a custom `entrypoint.sh` script. This script ensures that before the main application starts, it first waits for the PostgreSQL server to be fully available and then automatically runs `python -m alembic upgrade head`. This made the startup process robust and solved the recurring migration issue.

---

### Challenge 2: Handling Schema Changes on an Existing Table

**Problem:** When adding new, non-nullable columns (`current_attempt`, `run_at`) to the `jobs` table, the Alembic migration failed with a `NotNullViolation`.

**Debugging Process:**

1.  **Analysis:** I provided the error log to the AI. It correctly identified that PostgreSQL cannot add a `NOT NULL` column to a table that already contains data, because it doesn't know what default value to use for the existing rows.
2.  **Solution:** The AI instructed me to add `server_default='0'` to the `current_attempt` column definition in the `app/models/job.py` file. This provided a default value for the database to use when altering the table, allowing the migration to succeed without data loss.

---

### Challenge 3: Silent Failure of Alembic `autogenerate`

**Problem:** A very confusing issue arose where Alembic would generate new migration files, but they would be empty, containing only a `pass` statement in the `upgrade` and `downgrade` functions.

**Debugging Process:**

1.  **Investigation:** We used `alembic upgrade head --sql` to inspect the raw SQL that Alembic was trying to run, which confirmed that no `CREATE TABLE` statements were being generated.
2.  **Root Cause Analysis:** The AI deduced that the `env.py` script, which Alembic uses to discover the database models, was not importing the `app/models/job.py` file. Because the `Job` model was never loaded into Python's memory when the script ran, Alembic couldn't see it and therefore generated an empty migration.
3.  **Solution:** The fix was to add `from app import models` to the top of `migrations/env.py`. This ensured the models were registered with SQLAlchemy's metadata before Alembic's autogeneration process began, leading to correct migration scripts.

---

### Challenge 4: Configuring the Automated Test Suite

**Problem:** Setting up `pytest` to work with an `async` FastAPI application and a separate test database produced a series of errors, including `no such table: jobs`, `ModuleNotFoundError: No module named 'trio'`, and `AttributeError: module 'trio' has no attribute 'MultiError'`.

**Debugging Process:**

1.  **`no such table`:** The AI identified this as the same import-order issue from the Alembic problem. The solution was to import the models (`from app import models`) in `tests/test_database.py` before `Base.metadata.create_all()` was called.
2.  **`trio` Errors:** The AI explained that `pytest-anyio` was trying to run tests on multiple backends. We resolved this by pinning specific, compatible versions of `httpx` and `trio` in `requirements.txt` and creating a `pytest.ini` file to explicitly set the test backend to `asyncio`. This created a stable and predictable testing environment.

---