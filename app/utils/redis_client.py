import logging

import redis.asyncio as aioredis
from redis.exceptions import ConnectionError as RedisConnectionError

from app.config import config

logger = logging.getLogger("uvicorn")

_redis: aioredis.Redis | None = None
_connection_failed: bool = False


async def get_redis() -> aioredis.Redis | None:
    global _redis, _connection_failed
    if _connection_failed:
        return None
    if _redis is None:
        try:
            _redis = aioredis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=3,
                retry_on_timeout=False,
            )
            await _redis.ping()
        except RedisConnectionError:
            logger.warning(
                "Redis 连接失败 (%s:%s)，缓存功能已禁用，程序仍可正常运行",
                config.REDIS_HOST,
                config.REDIS_PORT,
            )
            _connection_failed = True
            _redis = None
            return None
    return _redis


async def close_redis() -> None:
    global _redis, _connection_failed
    if _redis is not None:
        await _redis.close()
        _redis = None
    _connection_failed = False
