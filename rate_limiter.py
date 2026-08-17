from time import time
from fastapi import HTTPException, Request

MAX_FAILED_ATTEMPTS = 5
BLOCK_TIME = 60

failed_attempts = {}


def get_client_ip(request: Request):
    return request.client.host


def is_rate_limited(request: Request):
    ip = get_client_ip(request)
    current_time = time()

    if ip not in failed_attempts:
        return

    timestamps = [
        t for t in failed_attempts[ip]
        if current_time - t < BLOCK_TIME
    ]

    failed_attempts[ip] = timestamps

    if len(timestamps) >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please try again in one minute."
        )


def record_failed_attempt(request: Request):
    ip = get_client_ip(request)

    if ip not in failed_attempts:
        failed_attempts[ip] = []

    failed_attempts[ip].append(time())


def reset_attempts(request: Request):
    ip = get_client_ip(request)

    if ip in failed_attempts:
        failed_attempts.pop(ip)