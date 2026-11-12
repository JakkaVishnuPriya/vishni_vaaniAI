import asyncio
import time
from collections import deque

class SlidingWindowLimiter:
    """In-process RPM/TPM guard for a single app process; not distributed."""
    def __init__(self, rpm: int, tpm: int):
        self.rpm, self.tpm = rpm, tpm
        self.requests = deque()
        self.tokens = deque()
        self.lock = asyncio.Lock()

    async def acquire(self, estimated_tokens: int = 1):
        async with self.lock:
            now = time.monotonic()
            while self.requests and now - self.requests[0] >= 60:
                self.requests.popleft()
            while self.tokens and now - self.tokens[0][0] >= 60:
                self.tokens.popleft()
            used_tokens = sum(n for _, n in self.tokens)
            if len(self.requests) >= self.rpm or used_tokens + estimated_tokens > self.tpm:
                raise RuntimeError("Local rate guard reached; request not sent.")
            self.requests.append(now)
            self.tokens.append((now, estimated_tokens))
