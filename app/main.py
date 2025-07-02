from fastapi import FastAPI
from .routes import jobs


# Create an instance of the FastAPI class
app = FastAPI(
    title="Niraj's Smart Task Queue",
    description="A production-ready task queue system using FastAPI that handles job scheduling, prioritization, and execution.",
    version="0.1.0",
)

# Include the jobs router in your main application
app.include_router(jobs.router)

@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm that the API is up and running.
    """
    return {"message": "Welcome to the Smart Task Queue API!"}