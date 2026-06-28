"""
General utility helpers.
"""

import hashlib
import time
from functools import wraps
from typing import Callable, Any


def make_cache_key(*args) -> str:
    raw = "_".join(str(a) for a in args)
    return hashlib.md5(raw.encode()).hexdigest()


def timeit(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[timeit] {fn.__name__} took {elapsed:.1f}ms")
        return result
    return wrapper


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def score_label(score: float) -> str:
    if score >= 0.8:
        return "Excellent"
    if score >= 0.6:
        return "Good"
    if score >= 0.4:
        return "Fair"
    return "Poor"
