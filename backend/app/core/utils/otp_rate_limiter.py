import time
from collections import defaultdict
from threading import Lock


class OTPRateLimiter:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._records: dict[str, list[float]] = defaultdict(list)
                    inst._max_requests = 3
                    inst._window_seconds = 600
                    cls._instance = inst
        return cls._instance

    def is_allowed(self, email: str, purpose: str) -> tuple[bool, int]:
        key = f"{email}:{purpose}"
        now = time.time()

        self._records[key] = [
            t for t in self._records[key] if now - t < self._window_seconds
        ]

        current_count = len(self._records[key])

        if current_count >= self._max_requests:
            oldest = self._records[key][0]
            retry_after = int(self._window_seconds - (now - oldest))
            return False, max(retry_after, 1)

        self._records[key].append(now)
        return True, 0
