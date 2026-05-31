"""In-process TTL response cache (Week 8 · Day 4)."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

T = TypeVar("T")

_store: dict[str, tuple[float, Any]] = {}


def _cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    payload = json.dumps({"a": args, "k": kwargs}, sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return f"{prefix}:{digest}"


def get_cached(key: str) -> Any | None:
    entry = _store.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if time.monotonic() >= expires_at:
        _store.pop(key, None)
        return None
    return value


def set_cached(key: str, value: Any, ttl_seconds: float) -> None:
    _store[key] = (time.monotonic() + ttl_seconds, value)


def invalidate_prefix(prefix: str) -> None:
    to_drop = [k for k in _store if k.startswith(f"{prefix}:")]
    for k in to_drop:
        _store.pop(k, None)


def ttl_cache(ttl_seconds: float = 60, *, prefix: str | None = None):
    """Decorator for async route handlers — caches JSON-serializable responses."""

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        name = prefix or fn.__name__

        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            key = _cache_key(name, *args, **kwargs)
            cached = get_cached(key)
            if cached is not None:
                return cached
            result = await fn(*args, **kwargs)
            set_cached(key, result, ttl_seconds)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def cache_stats() -> dict[str, int]:
    now = time.monotonic()
    active = sum(1 for exp, _ in _store.values() if exp > now)
    return {"entries": len(_store), "active": active}
