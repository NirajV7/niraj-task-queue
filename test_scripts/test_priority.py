import requests
import json
import time

API_URL = "http://localhost:8000/jobs/"

def submit_job(payload):
    """Helper function to submit a job and print the response."""
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print(f"SUCCESS: Submitted job with priority '{payload['priority']}'.")
        print(f"Response: {response.json()}\n")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not submit job. Is the server running? Details: {e}")
        exit()

# 1. Define a LOW priority job
low_priority_job = {
    "type": "generate_report",
    "priority": "low",
    "payload": {"report_name": "weekly_metrics"}
}

# 2. Define a CRITICAL priority job
critical_priority_job = {
    "type": "send_alert",
    "priority": "critical",
    "payload": {"message": "System overload detected!"}
}

print("--- Starting Priority Test ---")
print("Submitting jobs out of order (low first, then critical)...\n")

# 3. Submit the jobs
submit_job(low_priority_job)
time.sleep(1) # Small delay to make the submission order clear
submit_job(critical_priority_job)

print("--- Test Complete ---")
print("Check the 'docker-compose up' logs to see which job the worker picks up first.")