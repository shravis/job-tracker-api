from time import time
from os import getenv
from fastapi import HTTPException, Request

MAX_FAILED_ATTEMPTS = 5
MAX_REGISTER_ATTEMPTS = 5
BLOCK_TIME = 60
MAX_TRACKED_KEYS = 10_000

_buckets: dict[str, list[float]] = {}


def get_client_ip(request: Request) -> str:
    trust_proxy = getenv("TRUST_PROXY", "false").lower() in (
        "1",
        "true",
        "yes"
    )

    if trust_proxy:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

    if request.client is None:
        return "unknown"

    return request.client.host


def _prune() -> None:
    current_time = time()
    stale = [
        key for key, stamps in _buckets.items()
        if not stamps or current_time - stamps[-1] >= BLOCK_TIME
    ]
    for key in stale:
        _buckets.pop(key, None)

    if len(_buckets) > MAX_TRACKED_KEYS:
        ordered = sorted(
            _buckets.items(),
            key=lambda item: item[1][-1] if item[1] else 0
        )
        for key, _ in ordered[: len(_buckets) - MAX_TRACKED_KEYS]:
            _buckets.pop(key, None)


def _bucket_key(request: Request, action: str) -> str:
    return f"{action}:{get_client_ip(request)}"


def is_rate_limited(
    request: Request,
    action: str = "login",
    max_attempts: int = MAX_FAILED_ATTEMPTS,
    detail: str | None = None
) -> None:
    _prune()
    key = _bucket_key(request, action)
    current_time = time()
    timestamps = [
        t for t in _buckets.get(key, [])
        if current_time - t < BLOCK_TIME
    ]
    _buckets[key] = timestamps

    if len(timestamps) >= max_attempts:
        raise HTTPException(
            status_code=429,
            detail=detail or (
                "Too many failed login attempts. Please try again in one minute."
            )
        )


def record_failed_attempt(request: Request, action: str = "login") -> None:
    _prune()
    key = _bucket_key(request, action)
    _buckets.setdefault(key, []).append(time())


def reset_attempts(request: Request, action: str = "login") -> None:
    _buckets.pop(_bucket_key(request, action), None)
