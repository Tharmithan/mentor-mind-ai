"""Request latency tracking middleware (Week 8 · Day 4)."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_lock = Lock()
_totals: dict[str, float] = defaultdict(float)
_counts: dict[str, int] = defaultdict(int)


def record_latency(path: str, duration_ms: float) -> None:
    with _lock:
        _totals[path] += duration_ms
        _counts[path] += 1


def latency_summary() -> dict[str, dict[str, float | int]]:
    with _lock:
        rows: dict[str, dict[str, float | int]] = {}
        for path, total in _totals.items():
            count = _counts[path]
            rows[path] = {
                "count": count,
                "avg_ms": round(total / count, 2) if count else 0.0,
                "total_ms": round(total, 2),
            }
        return dict(sorted(rows.items(), key=lambda x: -float(x[1]["total_ms"])))


class LatencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        path = request.url.path
        record_latency(path, duration_ms)
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
        return response
