import hashlib
import json

from app.utils.redis_client import get_redis

CACHE_TTL = 3600


def file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


async def get_cached(key: str) -> dict | None:
    r = await get_redis()
    data = await r.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cache(key: str, value: dict, ttl: int = CACHE_TTL) -> None:
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value, ensure_ascii=False))
