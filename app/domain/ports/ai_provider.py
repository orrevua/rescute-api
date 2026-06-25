from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class AIProvider(ABC):

    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    async def reply(
        self, system_prompt: str, messages: Sequence[ChatMessage]
    ) -> str: ...

    @abstractmethod
    async def generate_response(
        self, prompt: str, context: str | None = None
    ) -> str: ...
