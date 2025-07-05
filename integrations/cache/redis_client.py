import redis
from logging_config import get_logger
from typing import Optional, Any
from core.interfaces.cache_service import CacheService
from config import Config

logger = get_logger(__name__)

class RedisCacheClient(CacheService):
    """
    Implementation of the cache service using Redis.
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
        self.ssl = Config.REDIS_SSL
        self.username = Config.REDIS_USERNAME
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
                username=self.username,
                db=self.db,
                decode_responses=False,
                socket_timeout=5,  # 5 seconds timeout
                socket_connect_timeout=5,  # 5 seconds connection timeout
                health_check_interval=30,  # Check connection every 30 seconds
                ssl=self.ssl,  # Enable SSL for encryption in transit
                ssl_cert_reqs=None  # Don't verify SSL certificate
            )
            # Try to ping with a short timeout
            self.redis_client.ping()
            logger.info(f"Successfully connected to Redis at {self.host}:{self.port}, DB: {self.db}")
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.warning(f"Could not connect to Redis: {e}. Cache will be disabled.")
            self.redis_client = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            self.redis_client = None

    def get(self, key: str) -> Any:
        """
        Retrieves a value from the cache.

        Args:
            key (str): The key to retrieve.

        Returns:
            Optional[Any]: The value if found, None otherwise.
        """
        if not self.redis_client:
            logger.warning("Redis client not available. Cache disabled.")
            return None
            
        try:
            return self.redis_client.get(key)
        except redis.RedisError as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None

    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """
        Sets a value in the cache.

        Args:
            key (str): The key to set.
            value (Any): The value to store.
            expiry (Optional[int]): The expiry time in seconds.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.redis_client:
            logger.warning("Redis client not available. Cache disabled.")
            return False
            
        try:
            return self.redis_client.set(key, value, ex=expiry)
        except redis.RedisError as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Deletes a value from the cache.

        Args:
            key (str): The key to delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.redis_client:
            logger.warning("Redis client not available. Cache disabled.")
            return False
            
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False

# Create a global instance
cache_client = RedisCacheClient()