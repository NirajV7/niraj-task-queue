# Architecture and Design Decisions

This document outlines the key architectural decisions made during the development of the Smart Task Queue system.

---

## 1. System Architecture

The system is designed as a multi-container application orchestrated by Docker Compose, consisting of three main services:

* **`web`**: A FastAPI application server that exposes the REST API for job management and handles WebSocket connections for real-time updates.
* **`worker`**: A standalone Python process responsible for the core logic of the task queue. It continuously polls the database for pending jobs and executes them based on a set of rules.
* **`db`**: A PostgreSQL database container that provides persistent storage for all jobs, dependencies, and logs.

This separation of concerns ensures that the API's performance is not affected by the execution of long-running jobs.

### Startup and Migrations

A custom `entrypoint.sh` script is used for the `web` and `worker` services. This script solves a critical race condition by:
1.  Waiting until the `db` service is fully available before proceeding.
2.  Automatically running `alembic upgrade head` to apply any pending database migrations.

This makes the startup process robust and fully automated, ensuring the application and database schemas are always in sync.

---

## 2. API Design

* **Framework**: FastAPI was chosen for its high performance, automatic data validation with Pydantic, and automatic generation of interactive API documentation (Swagger UI).
* **Data Validation**: Pydantic schemas (`app/schemas.py`) are used to define the shape of API requests and responses, ensuring data integrity and providing clear contracts for API clients.
* **Service Layer**: A service layer (`app/services/`) was created to separate the core business logic (e.g., creating a job, managing resources) from the API routing layer (`app/routes/`). This improves code organization and maintainability.

---

## 3. Core Feature Implementation

### Priority, Dependencies, and Resources

The scheduling logic is implemented within the worker's main processing loop. To select the next job to run, a single database query is performed in `job_service.get_candidate_jobs` that:
1.  Filters for jobs with a `PENDING` status.
2.  Filters for jobs scheduled to run now (where `run_at` is null or in the past).
3.  Orders the results by `priority` (descending) and then by `created_at` (ascending) to ensure fairness (FIFO within the same priority level).

The worker then iterates through this candidate list, checking for met dependencies and available resources in memory before executing a job.

### Failure Handling and Retries

* **Error Catching**: The execution of each job within the worker is wrapped in a `try...except` block to catch any exceptions, including `TimeoutError` from `asyncio.wait_for`.
* **Retry Logic**: When a job fails, the `handle_job_failure` function is called. It increments a `current_attempt` counter and checks it against the job's `max_attempts` from its `retry_config`.
* **Exponential Backoff**: If a retry is warranted, the next run time (`run_at`) is calculated using an exponential backoff formula to avoid overwhelming a potentially failing downstream service.

### Idempotency

* To prevent duplicate jobs from network retries, the `POST /jobs` endpoint supports an optional `idempotency_key`.
* When a key is provided, the `create_job` service first queries the database to see if a job with that key already exists. If it does, the existing job is returned. If not, a new job is created with the key. A unique constraint on the `idempotency_key` column in the database provides a final layer of protection.

---

## 4. Documented Trade-offs and Future Improvements

* **Worker-to-API Communication**: The current implementation does not broadcast real-time updates from the worker (e.g., when a job status changes to `RUNNING` or `SUCCESS`). The `ConnectionManager` lives only in the `web` service's memory. In a full production system, this would be solved by implementing a message broker like **Redis Pub/Sub** or **RabbitMQ**. The worker would publish events to the broker, and the web server would subscribe to these events and broadcast them to connected WebSocket clients.
* **Resource Manager State**: The `ResourceManager` currently holds the state of used CPU and memory in memory. This is sufficient for a single-worker system but would not work if we scaled to multiple worker containers. To support multiple workers, this state should be moved to a shared, fast-access data store like **Redis**.