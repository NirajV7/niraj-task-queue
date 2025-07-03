# Evaluation Results

This document confirms that the system successfully passes all the test scenarios outlined in the case study.

---

### Scenario 1: Priority Scheduling

* **Objective:** Verify that jobs with higher priority are executed before jobs with lower priority.
* **Test Procedure:** Ran the `test_priority.py` script, which submits a `low` priority job followed by a `critical` priority job.
* **Expected Outcome:** The worker logs should show that the `critical` job is picked up and executed first, despite being submitted second.
* **Result:** ✅ PASS

---

### Scenario 2 & 3: Dependency Management

* **Objective:** Verify that a job is not executed until the jobs it depends on have a `SUCCESS` status.
* **Test Procedure:** Ran the `test_dependency.py` script, which creates a chain of jobs where Job C depends on Job B, and Job B depends on Job A.
* **Expected Outcome:** The worker logs should show that it processes Job A first. Only after A is successful does it process B. Only after B is successful does it process C.
* **Result:** ✅ PASS

---

### Scenario 4: Resource Contention

* **Objective:** Verify that the system does not run jobs if it would exceed the predefined resource capacity (8 CPU, 4096 MB).
* **Test Procedure:** Ran the `test_resources.py` script, which submits three "heavy" jobs that each require half the system's resources.
* **Expected Outcome:** The resource manager logs show that it allocates resources for the first two heavy jobs, bringing usage to 100%. The worker logs then show that it is skipping the third heavy job due to "Not enough resources". Only after one of the first jobs completes and releases its resources is the third job executed.
* **Result:** ✅ PASS

---

### Scenario 5: Failure and Recovery

* **Objective:** Verify that the system correctly handles job timeouts and execution failures, including retries with exponential backoff.
* **Test Procedure:** Ran the `test_failures.py` script, which submits one job designed to fail repeatedly and another designed to time out.
* **Expected Outcome:**
    * **Failing Job:** The worker logs show the job failing, being rescheduled with increasing delays (e.g., 'Rescheduling to run in 10 seconds', '...in 20 seconds'), and finally being marked as `FAILED` after reaching its `max_attempts`.
    * **Timeout Job:** The worker logs show an `asyncio.TimeoutError`, and the job is subsequently marked as `FAILED`.
* **Result:** ✅ PASS