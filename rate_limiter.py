from time import time
from os import getenv
import logging
from fastapi import HTTPException, Request

MAX_FAILED_ATTEMPTS = 5
MAX_REGISTER_ATTEMPTS = 5
BLOCK_TIME = 60
MAX_TRACKED_KEYS = 10_000

_buckets: dict[str, list[float]] = {}
_logged_untrusted_xff = False
logger = logging.getLogger("jobtracker")


def reset_limiter_state() -> None:
    _buckets.clear()


def get_client_ip(request: Request) -> str:
    trust_proxy = getenv("TRUST_PROXY", "false").lower() in (
        "1",
        "true",
        "yes"
    )
    forwarded = request.headers.get("x-forwarded-for")

    if trust_proxy and forwarded:
        return forwarded.split(",")[0].strip()

    # uvicorn --proxy-headers rewrites request.client.host from
    # X-Forwarded-For when the TCP peer is 127.0.0.1. If we do not
    # trust proxies, ignore that rewritten address so rotating headers
    # cannot bypass the limit.
    if not trust_proxy and forwarded:
        global _logged_untrusted_xff
        if not _logged_untrusted_xff:
            logger.warning(
                "X-Forwarded-For was present but TRUST_PROXY is false. "
                "Those clients share one rate-limit bucket. Set "
                "TRUST_PROXY=true and start Uvicorn with "
                "--forwarded-allow-ips set to your proxy, or omit XFF "
                "and use --no-proxy-headers for local development."
            )
            _logged_untrusted_xff = True
        return "untrusted-forwarded"

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
        oldest = timestamps[0]
        retry_after = max(1, int(BLOCK_TIME - (current_time - oldest)))
        raise HTTPException(
            status_code=429,
            detail=detail or (
                "Too many failed login attempts. Please try again in one minute."
            ),
            headers={"Retry-After": str(retry_after)}
        )


def record_failed_attempt(request: Request, action: str = "login") -> None:
    _prune()
    key = _bucket_key(request, action)
    _buckets.setdefault(key, []).append(time())


def reset_attempts(request: Request, action: str = "login") -> None:
    _buckets.pop(_bucket_key(request, action), None)
