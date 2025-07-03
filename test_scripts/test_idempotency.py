import requests
import uuid
import time

API_URL = "http://localhost:8000/jobs/"

def submit_job_with_key(payload):
    """Helper function to submit a job and return the response JSON."""
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f" -> ERROR: Could not submit job. Details: {e}")
        exit()

# --- Test Scenario: Idempotency ---
print("--- Starting Idempotency Test ---")

# 1. Generate a single, unique key for this test run
idempotency_key = f"test-key-{uuid.uuid4()}"
print(f"Using idempotency key: {idempotency_key}\n")

# 2. Define the job payload
job_payload = {
    "type": "idempotent_test",
    "priority": "normal",
    "idempotency_key": idempotency_key,
    "payload": {"test_run_id": str(uuid.uuid4())}
}

# 3. Submit the job for the first time
print("Submitting request 1...")
response1 = submit_job_with_key(job_payload)
job_id1 = response1.get("job_id")
print(f" -> SUCCESS: Received job_id: {job_id1}\n")

time.sleep(1)

# 4. Submit the exact same job with the same key for the second time
print("Submitting request 2 with the SAME idempotency key...")
response2 = submit_job_with_key(job_payload)
job_id2 = response2.get("job_id")
print(f" -> SUCCESS: Received job_id: {job_id2}\n")

# 5. Verify the result
print("--- Verification ---")
if job_id1 and job_id1 == job_id2:
    print(f"✅ TEST PASSED: Both requests returned the same job ID ({job_id1}).")
    print("A new job was NOT created on the second request, as expected.")
else:
    print(f"❌ TEST FAILED: The job IDs do not match! ({job_id1} vs {job_id2})")