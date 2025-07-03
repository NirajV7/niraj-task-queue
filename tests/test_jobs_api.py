# In tests/test_jobs_api.py

import pytest
from httpx import AsyncClient
from app.main import app
from app.database import get_db
from .test_database import override_get_db

# Tell our app to use the test database for this test file
app.dependency_overrides[get_db] = override_get_db

@pytest.mark.anyio
async def test_submit_job_success():
    """
    Tests successful job submission.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        job_payload = {
            "type": "test_job",
            "priority": "high",
            "payload": {"data": "sample"}
        }
        response = await client.post("/jobs/", json=job_payload)

        # Assert that the response is what we expect
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["type"] == "test_job"
        assert response_data["status"] == "pending"
        assert "job_id" in response_data
        
@pytest.mark.anyio
async def test_get_job_details_success():
    """
    Tests successfully retrieving a job after creating it.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, create a job to ensure one exists
        job_payload = {"type": "retrieval_test"}
        create_response = await client.post("/jobs/", json=job_payload)
        assert create_response.status_code == 201
        job_id = create_response.json()["job_id"]

        # Now, try to get the job we just created
        get_response = await client.get(f"/jobs/{job_id}")
        assert get_response.status_code == 200
        response_data = get_response.json()
        assert response_data["job_id"] == job_id
        assert response_data["type"] == "retrieval_test"

@pytest.mark.anyio
async def test_get_nonexistent_job():
    """
    Tests that fetching a job that does not exist returns a 404 error.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/jobs/job_that_does_not_exist")
        assert response.status_code == 404
        
@pytest.mark.anyio
async def test_cancel_job_success():
    """
    Tests successfully cancelling a pending job.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a job to cancel
        job_payload = {"type": "cancellation_test"}
        create_response = await client.post("/jobs/", json=job_payload)
        job_id = create_response.json()["job_id"]

        # Immediately cancel the job
        cancel_response = await client.patch(f"/jobs/{job_id}/cancel")
        assert cancel_response.status_code == 200
        assert cancel_response.json()["status"] == "cancelled"