import requests
import json
import time

API_URL = "http://localhost:8000/jobs/"

def submit_job(payload):
    """Helper function to submit a job and return its ID."""
    print(f"Submitting job: {payload.get('type')} with priority '{payload.get('priority')}'")
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        job_id = response.json()["job_id"]
        print(f" -> SUCCESS: Created job_id: {job_id}\n")
        return job_id
    except requests.exceptions.RequestException as e:
        print(f" -> ERROR: Could not submit job. Is the server running? Details: {e}")
        exit()

# --- Test Scenario 2: Simple Dependencies ---
print("--- Starting Dependency Test ---")

# 1. Create the first job in the chain. It has no dependencies.
job_a_payload = {
    "type": "fetch_data",
    "priority": "high",
    "payload": {"source": "market_api"}
}
job_a_id = submit_job(job_a_payload)

# 2. Create the second job, which depends on the first one.
job_b_payload = {
    "type": "process_data",
    "priority": "high",
    "payload": {"operation": "calculate_indicators"},
    "depends_on": [job_a_id]  # <-- Dependency on Job A
}
job_b_id = submit_job(job_b_payload)

# 3. Create the third job, which depends on the second one.
job_c_payload = {
    "type": "generate_report",
    "priority": "normal",
    "payload": {"format": "pdf"},
    "depends_on": [job_b_id]  # <-- Dependency on Job B
}
job_c_id = submit_job(job_c_payload)


print("\n--- Test Complete ---")
print(f"Created job chain: {job_c_id} -> {job_b_id} -> {job_a_id}")
print("Check the 'docker-compose up' logs to see the worker's execution order.")