import requests
import json
import time

API_URL = "http://localhost:8000/jobs/"

def submit_job(payload):
    """Submits a job and returns its ID."""
    print(f"Submitting job to be cancelled...")
    try:
        # The line below has been corrected
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        job_id = response.json()["job_id"]
        print(f" -> SUCCESS: Created job with ID: {job_id}")
        return job_id
    except requests.exceptions.RequestException as e:
        print(f" -> ERROR: Could not submit job. Details: {e}")
        exit()

def cancel_job(job_id):
    """Attempts to cancel the job with the given ID."""
    print(f"Attempting to cancel job {job_id}...")
    try:
        response = requests.patch(f"{API_URL}{job_id}/cancel")
        response.raise_for_status()
        print(f" -> SUCCESS: Cancel request sent.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f" -> ERROR: Could not cancel job. Details: {e}")
        exit()

def get_job_status(job_id):
    """Gets the status of a specific job."""
    try:
        response = requests.get(f"{API_URL}{job_id}")
        response.raise_for_status()
        return response.json()["status"]
    except requests.exceptions.RequestException as e:
        print(f" -> ERROR: Could not get job status. Details: {e}")
        exit()


# --- Test Scenario: Job Cancellation ---
print("--- Starting Job Cancellation Test ---")

# To make sure the worker is busy, we submit a blocker job first
blocker_job_payload = {
    "type": "blocker_task",
    "priority": "normal",
    "payload": {"duration_seconds": 10}
}
print("Submitting a blocker job to keep the worker busy...")
submit_job(blocker_job_payload)
time.sleep(1) # Give the worker a second to pick it up

# Now submit the job we actually want to cancel
job_to_cancel_payload = {
    "type": "cancellable_task",
    "priority": "low",
}

# 1. Submit the target job
job_id = submit_job(job_to_cancel_payload)

# 2. Immediately try to cancel it while the worker is busy
cancel_job(job_id)

# 3. Wait a moment and verify its status
time.sleep(1)
final_status = get_job_status(job_id)

print(f"\nFinal status of job {job_id} is: '{final_status.upper()}'")

if final_status == "cancelled":
    print("✅ TEST PASSED: Job was successfully cancelled.")
else:
    print(f"❌ TEST FAILED: Job status is '{final_status}', not 'cancelled'.")