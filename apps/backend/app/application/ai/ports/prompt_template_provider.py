
from abc import ABC, abstractmethod


class PromptTemplateProvider(ABC):
    """
    Provides prompt templates used by PromptBuilder.
    """

    @abstractmethod
    async def get_system_prompt(self) -> str:
        raise NotImplementedError