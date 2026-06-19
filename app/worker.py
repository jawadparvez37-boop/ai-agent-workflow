from app.agent import run_task_safe
from app.config import settings
from app.queue import fetch, pop_job_id, save


def process_once() -> bool:
    job_id = pop_job_id(block_seconds=settings.worker_poll_seconds)
    if not job_id:
        return False

    job = fetch(job_id)
    if not job:
        return True

    job["status"] = "running"
    save(job)

    outcome = run_task_safe(job["task"])
    if outcome["status"] == "completed":
        job["status"] = "completed"
        job["result"] = outcome
        job["error"] = None
    else:
        job["status"] = "failed"
        job["result"] = None
        job["error"] = outcome.get("error", "unknown error")

    save(job)
    return True


def main() -> None:
    print("worker started")
    while True:
        process_once()


if __name__ == "__main__":
    main()
