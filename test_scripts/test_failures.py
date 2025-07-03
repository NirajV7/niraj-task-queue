# In test_failures.py

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
        print(f" -> ERROR: Could not submit job. Details: {e}")
        exit()

print("--- Starting Failure and Retry Test ---")

# 1. A job that will fail, but should be retried 3 times
failing_job_payload = {
    "type": "unreliable_api_call",
    "priority": "high",
    "payload": {"should_fail": True},
    "retry_config": {"max_attempts": 3, "backoff_multiplier": 2}
}
submit_job(failing_job_payload)

# 2. A job that will run for too long and time out
timeout_job_payload = {
    "type": "long_running_task",
    "priority": "normal",
    "payload": {"duration_seconds": 20}, # It will run for 20s
    "timeout_seconds": 10 # But it has a 10s timeout
}
submit_job(timeout_job_payload)

print("\n--- Test Complete ---")
print("Check the 'docker-compose up' logs to see the worker handle failures.")