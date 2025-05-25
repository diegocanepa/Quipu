import redis
import logging
from typing import Optional, Any
from core.interfaces.cache_service import CacheService
from config import Config

logger = logging.getLogger(__name__)

class RedisCacheClient(CacheService):
    """
    Implementation of the cache service using Valkey (replacing Redis).
    """
    def __init__(self, host: Optional[str] = None, port: int = 6379, password: Optional[str] = None, db: int = 0) -> None:
        """
        Initializes the Redis client.

        Args:
            host (Optional[str]): The address of the Redis server. Defaults to the REDIS_HOST environment variable.
            port (int): The port of the Redis server. Defaults to 6379.
            password (Optional[str]): The password for authenticating with Redis. Defaults to the REDIS_PASSWORD environment variable.
            db (int): The number of the Redis database to use. Defaults to 0.
        """
        self.host = host or Config.REDIS_HOST
        self.port = Config.REDIS_PORT
        self.password = Config.REDIS_PASSWORD
        self.db = Config.REDIS_DB
        self.redis_client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self) -> None:
        """
        Establishes the connection with the Redis server.
        """
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True  # To get strings instead of bytes
            )
            self.redis_client.ping()
            logger.info(f"Successfully connected to Redis (or Valkey) at {self.host}:{self.port}, DB: {self.db}")
        except redis.exceptions.ConnectionError as e:
            logger.info(f"Error connecting to Redis (or Valkey): {e}")
            self.redis_client = None # :TODO Raise an error when this happen otherwise it's a silence error. 


    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves a value from the Redis cache based on the prefix, key, and version.

        Args:
            prefix (str): The key prefix.
            key (str): The unique key.
            version (int): The version.

        Returns:
            Optional[Any]: The retrieved value if it exists, None otherwise.
        """
        if self.redis_client:
            return self.redis_client.get(key)
        return None

    def set(self,  key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """
        Stores a value in the Redis cache under the specified versioned key.

        Args:
            prefix (str): The key prefix.
            key (str): The unique key.
            value (Any): The value to store.
            version (int): The version.
            expiry (Optional[int]): Time-to-live in seconds.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if self.redis_client:
            return self.redis_client.set(key, value, ex=expiry)
        return False

    def delete(self, key: str) -> bool:
        """
        Deletes a value from the Redis cache based on the prefix, key, and version.

        Args:
            prefix (str): The key prefix.
            key (str): The unique key.
            version (int): The version.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if self.redis_client:
            return self.redis_client.delete(key) > 0
        return False

# Create a global instance of the cache client when importing the module
cache_client: Optional[CacheService] = RedisCacheClient()