from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agent import run_task_safe
from app.queue import enqueue, fetch

app = FastAPI(title="AI Agent Workflow")


class JobRequest(BaseModel):
    task: str = Field(min_length=5, max_length=4000)


class JobCreated(BaseModel):
    job_id: str
    status: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jobs", response_model=JobCreated)
def create_job(body: JobRequest):
    job_id = enqueue(body.task)
    return JobCreated(job_id=job_id, status="queued")


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = fetch(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@app.post("/run")
def run_sync(body: JobRequest):
    return run_task_safe(body.task)
