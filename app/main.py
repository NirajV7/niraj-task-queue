from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI(
    title="Niraj's Smart Task Queue",
    description="A production-ready task queue system using FastAPI that handles job scheduling, prioritization, and execution.",
    version="0.1.0",
)

@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm that the API is up and running.
    """
    return {"message": "Welcome to the Smart Task Queue API!"}