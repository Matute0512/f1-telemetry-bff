from abc import ABC, abstractmethod
from typing import Any


class Cache(ABC):
    """Port for application caching."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Return the cached value for a key."""
        raise NotImplementedError

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int,
    ) -> None:
        """Store a value with a time-to-live."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a cached value."""
        raise NotImplementedError
