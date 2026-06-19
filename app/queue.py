import json
import uuid
from datetime import datetime, timezone

import redis

from app.config import settings

QUEUE_KEY = "agent:jobs"
JOB_PREFIX = "agent:job:"


def _client() -> redis.Redis:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue(task: str) -> str:
    job_id = str(uuid.uuid4())
    client = _client()
    payload = {
        "id": job_id,
        "task": task,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "result": None,
        "error": None,
    }
    client.set(f"{JOB_PREFIX}{job_id}", json.dumps(payload))
    client.rpush(QUEUE_KEY, job_id)
    return job_id


def fetch(job_id: str) -> dict | None:
    raw = _client().get(f"{JOB_PREFIX}{job_id}")
    if not raw:
        return None
    return json.loads(raw)


def save(job: dict) -> None:
    job["updated_at"] = datetime.now(timezone.utc).isoformat()
    _client().set(f"{JOB_PREFIX}{job['id']}", json.dumps(job))


def pop_job_id(block_seconds: int = 2) -> str | None:
    item = _client().blpop(QUEUE_KEY, timeout=block_seconds)
    if not item:
        return None
    return item[1]
