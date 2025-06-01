"""Key-value cache with expiration."""

import redis
from typing import Any
import json
from functools import wraps

from src.utils.configuration import conf
from src.utils.logger import logger


def redis_connection_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in Redis operation: {e}")
            raise
    return wrapper


class RedisClient:
    def __init__(self):
        self.host = conf.get("cache.host", "localhost")
        self.port = conf.get("cache.port", 6379)
        self.db = conf.get("cache.db", 0)
        self.client = self._create_client()
        logger.info(f"Redis client initialized with host={self.host}, port={self.port}")

    def _create_client(self) -> redis.Redis:
        return redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)

    @redis_connection_error_handler
    def ping(self) -> bool:
        return self.client.ping()

    @redis_connection_error_handler
    def set(self, key: str, value: Any, expire: int | None = None) -> bool:
        if not isinstance(value, str):
            value = json.dumps(value)

        result = self.client.set(key, value)
        if expire is not None:
            self.client.expire(key, expire)
        return result

    @redis_connection_error_handler
    def get(self, key: str, deserialize: bool = True) -> Any:
        value = self.client.get(key)
        if value is not None and deserialize:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    @redis_connection_error_handler
    def delete(self, *keys) -> int:
        return self.client.delete(*keys)

    @redis_connection_error_handler
    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    @redis_connection_error_handler
    def ttl(self, key: str) -> int:
        return self.client.ttl(key)

    @redis_connection_error_handler
    def keys(self, pattern: str = "*") -> list[str]:
        return self.client.keys(pattern)

    @redis_connection_error_handler
    def flush_db(self) -> bool:
        return self.client.flushdb()


client = RedisClient()


def cache(ttl: int | None = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            value = client.get(key)
            if value is not None:
                return value
            value = func(*args, **kwargs)
            client.set(key, value, expire=ttl)
            return value
        return wrapper
    return decorator
