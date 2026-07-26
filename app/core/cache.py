import time
from typing import Dict, Any, Optional
from app.core.logging import logger

class SimpleTTLCache:
    """
    High-performance in-memory TTL cache for competitor search results & repeated LLM queries.
    """
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                logger.info(f"Cache HIT for key: {key}")
                return entry["data"]
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        self.cache[key] = {
            "timestamp": time.time(),
            "data": value
        }

ttl_cache = SimpleTTLCache(ttl_seconds=3600)
