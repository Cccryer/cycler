from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from llm.response.base import ModelResponse


class EmbeddingModel(Protocol):

    async def aembed_batch(
        self, text_list: list[str], **kwargs: Any
    ) -> list[list[float]]:
        ...

    async def aembed(self, text: str, **kwargs: Any) -> list[float]:
        ...

    def embed_batch(self, text_list: list[str], **kwargs: Any) -> list[list[float]]:

        ...

    def embed(self, text: str, **kwargs: Any) -> list[float]:
        ...


class ChatModel(Protocol):

    async def achat(
        self, prompt: str, history: list | None = None, **kwargs: Any
    ) -> ModelResponse:
        ...

    async def achat_stream(
        self, prompt: str, history: list | None = None, **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        
        yield ""  # Yield an empty string so that the function is recognized as a generator
        ...

    def chat(
        self, prompt: str, history: list | None = None, **kwargs: Any
    ) -> ModelResponse:
        ...

    def chat_stream(
        self, prompt: str, history: list | None = None, **kwargs: Any
    ) -> Generator[str, None]:
        ...
