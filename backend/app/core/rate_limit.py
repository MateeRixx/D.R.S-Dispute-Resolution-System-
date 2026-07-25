import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

_requests: dict[str, list[float]] = defaultdict(list)


async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/auth/login":
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60
        max_requests = 10

        timestamps = _requests[client_ip]
        _requests[client_ip] = [t for t in timestamps if now - t < window]

        if len(_requests[client_ip]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Try again later.",
            )

        _requests[client_ip].append(now)

    return await call_next(request)
