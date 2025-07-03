import requests
import json
import time

API_URL = "http://localhost:8000/jobs/"

def submit_job(payload):
    """Helper function to submit a job and print the response."""
    job_type = payload.get('type')
    print(f"Submitting {job_type} job...")
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        job_id = response.json()["job_id"]
        print(f" -> SUCCESS: Created job_id: {job_id}\n")
        return job_id
    except requests.exceptions.RequestException as e:
        print(f" -> ERROR: Could not submit job. Is the server running? Details: {e}")
        exit()

# --- Test Scenario 4: Resource Contention ---
# System capacity is 8 CPU and 4096 MB Memory.
print("--- Starting Resource Contention Test ---")

# 1. Define three "heavy" jobs. Each requires half the system's resources.
# Only two should be able to run at the same time.
for i in range(3):
    heavy_job_payload = {
        "type": "heavy_processing",
        "priority": "high",
        "payload": {"batch_number": i + 1},
        "resource_requirements": {"cpu_units": 4, "memory_mb": 2048}
    }
    submit_job(heavy_job_payload)
    time.sleep(0.1)

# 2. Define two "light" jobs that could potentially fill gaps.
for i in range(2):
    light_job_payload = {
        "type": "quick_task",
        "priority": "normal",
        "payload": {"task_id": i + 1},
        "resource_requirements": {"cpu_units": 1, "memory_mb": 256}
    }
    submit_job(light_job_payload)
    time.sleep(0.1)


print("\n--- Test Complete ---")
print("Check the 'docker-compose up' logs to see how the worker allocates resources.")