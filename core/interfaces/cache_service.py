from abc import ABC, abstractmethod
from typing import Optional, Any

class CacheService(ABC):
    """
    Abstract interface for a generic cache service.
    Defines the basic operations for interacting with a cache.
    """
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves a value from the cache based on the prefix, key, and version.

        Args:
            prefix (str): The prefix of the key to segment the cache.
            key (str): The unique key of the data within the prefix.
            version (int): The version of the stored data.

        Returns:
            Optional[Any]: The value retrieved from the cache if it exists, None otherwise.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """
        Stores a value in the cache under the specified versioned key.

        Args:
            prefix (str): The prefix of the key to segment the cache.
            key (str): The unique key of the data within the prefix.
            value (Any): The value to store in the cache.
            version (int): The version of the data to store.
            expiry (Optional[int]): Time-to-live in seconds for the element in the cache.
                                    If None, the element does not expire.

        Returns:
            bool: True if the storage operation was successful, False otherwise.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Deletes a value from the cache based on the prefix, key, and version.

        Args:
            prefix (str): The prefix of the key to segment the cache.
            key (str): The unique key of the data within the prefix.
            version (int): The version of the data to delete.

        Returns:
            bool: True if the deletion operation was successful, False otherwise.
        """
        pass