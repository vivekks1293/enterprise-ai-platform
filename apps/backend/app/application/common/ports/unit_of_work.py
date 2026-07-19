from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """
    Coordinates transactional work across one or more repositories.

    The Application layer depends only on this contract.
    Infrastructure decides how transactions are implemented.
    """

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError