from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class FileStorage(ABC):
    """
    Storage abstraction for knowledge document content.
    """

    @abstractmethod
    async def save(
        self,
        *,
        storage_key: str,
        content: AsyncIterator[bytes],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def read(
        self,
        *,
        storage_key: str,
    ) -> AsyncIterator[bytes]:
        """
        Streams stored file content.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        *,
        storage_key: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(
        self,
        *,
        storage_key: str,
    ) -> bool:
        raise NotImplementedError