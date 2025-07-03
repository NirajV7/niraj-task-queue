# Niraj's Smart Task Queue

This is a production-ready task queue system built with FastAPI, as per the Backend Engineer Case Study. It handles job scheduling, prioritization, dependencies, resource allocation, and real-time updates.

---

## Features

* **REST API:** A full-featured API to submit, view, list, and cancel jobs.
* **Smart Scheduling:** A background worker processes jobs based on:
    * **Priority:** Critical, High, Normal, and Low levels.
    * **Dependencies:** Jobs can depend on the successful completion of other jobs.
    * **Resource Management:** The system tracks CPU and memory usage to prevent overload.
* **Resiliency:**
    * **Retries with Exponential Backoff:** Failed jobs are automatically retried with increasing delays.
    * **Timeouts:** Jobs that run for too long are automatically cancelled.
* **Real-time Updates:** A WebSocket endpoint streams job status changes to connected clients.
* **Persistent Storage:** Uses PostgreSQL to store all job, dependency, and log data.
* **Containerized:** Fully containerized with Docker and Docker Compose for easy setup and consistent environments.

---

## Setup and Running the Project

### Prerequisites

* Docker
* Docker Compose

### Instructions

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/NirajV7/niraj-task-queue.git](https://github.com/NirajV7/niraj-task-queue.git)
    ```

2.  **Navigate to the project directory:**
    ```bash
    cd niraj-task-queue
    ```

3.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```

The application will be available at `http://localhost:8000`.

---

## API Endpoints

The full interactive API documentation (provided by Swagger UI) is available at:

* **`http://localhost:8000/docs`**

The core endpoints include:
* `POST /jobs/`: Submit a new job.
* `GET /jobs/`: List and filter all jobs.
* `GET /jobs/{job_id}`: Get details for a specific job.
* `GET /jobs/{job_id}/logs`: Get logs for a specific job.
* `PATCH /jobs/{job_id}/cancel`: Cancel a pending job.
* `WS /jobs/stream`: Connect to the real-time update stream.

---

## Testing

The project includes two forms of tests: an automated test suite and manual test scripts.

### Automated Tests

The `tests/` directory contains a formal test suite using `pytest`. These tests validate the core API paths by using an in-memory SQLite database, ensuring a clean testing environment.

With the services running, you can execute the automated tests with the following command:

```bash
docker-compose exec web pytest

Manual Test Scripts

The /test_scripts directory contains scripts to demonstrate the more complex features of the worker and scheduler. With the services running, you can execute any of these scripts from a separate terminal to see the system in action. For example:

python test_scripts/test_dependency.py

Development Journey
1. Implementation Approach
My approach was to build the system incrementally, ensuring each component was working before adding the next layer of complexity.

Foundation: Set up the initial FastAPI application, Docker configuration, and database connection.

Database & Migrations: Defined the core SQLAlchemy models and established a robust, automated migration workflow using Alembic and an entrypoint.sh script.

Core API: Built and tested the essential REST API endpoints for creating and retrieving jobs.

Worker Implementation: Developed the background worker, progressively adding logic for priority, dependencies, resource allocation, and finally, failure handling with retries and timeouts.

Real-time Features: Implemented the WebSocket endpoint for real-time communication.

Testing & Documentation: Wrote automated tests with Pytest and created documentation to explain the system's architecture and setup.

2. Challenges Encountered & Solutions
I collaborated extensively with an AI assistant to navigate several realistic development challenges. The AI provided guidance and helped debug complex issues.

Initial Migration Failures: The most significant challenge was a persistent relation "jobs" does not exist error. After extensive debugging with the AI, we discovered a combination of issues related to Docker volume persistence and the Alembic/SQLAlchemy import order. The final solution was to implement a foolproof manual volume deletion and an entrypoint.sh script to ensure migrations run correctly after the database is ready.

Testing Configuration: Setting up the automated test suite with pytest for an async application presented several challenges. With the AI's help, we resolved ModuleNotFound errors and library incompatibilities by pinning specific dependency versions in requirements.txt and correctly configuring pytest.ini to handle the anyio backend.

3. Future Improvements
With more time, I would address the trade-offs documented in ARCHITECTURE.md:

Implement a Redis Pub/Sub System: To enable the worker to broadcast real-time status updates (RUNNING, SUCCESS, FAILED) to all connected WebSocket clients, decoupling the worker and web services.

Centralize Resource Management: Move the resource manager's state from in-memory to Redis to support scaling the system with multiple worker containers.

Expand the Test Suite: Add more granular unit tests for the service and worker logic, in addition to the current API integration tests.
