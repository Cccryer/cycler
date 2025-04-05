from collections.abc import Callable
from typing import Any, ClassVar

from llm.protocol.base import ChatModel, EmbeddingModel
from llm.openai.model import OpenAIChatModel, OpenAIEmbeddingModel, OpenAICompletionModel
class ModelFactory:

    _chat_registry: ClassVar[dict[str, Callable[..., ChatModel]]] = {}
    _embedding_registry: ClassVar[dict[str, Callable[..., EmbeddingModel]]] = {}

    @classmethod
    def register_chat(cls, model_type: str, creator: Callable[..., ChatModel]) -> None:
        cls._chat_registry[model_type] = creator

    @classmethod
    def register_embedding(
        cls, model_type: str, creator: Callable[..., EmbeddingModel]
    ) -> None:
        cls._embedding_registry[model_type] = creator

    @classmethod
    def create_chat_model(cls, model_type: str, **kwargs: Any) -> ChatModel:
        if model_type not in cls._chat_registry:
            msg = f"ChatMOdel implementation '{model_type}' is not registered."
            raise ValueError(msg)
        return cls._chat_registry[model_type](**kwargs)

    @classmethod
    def create_embedding_model(cls, model_type: str, **kwargs: Any) -> EmbeddingModel:

        if model_type not in cls._embedding_registry:
            msg = f"EmbeddingModel implementation '{model_type}' is not registered."
            raise ValueError(msg)
        return cls._embedding_registry[model_type](**kwargs)

    @classmethod
    def get_chat_models(cls) -> list[str]:
        return list(cls._chat_registry.keys())

    @classmethod
    def get_embedding_models(cls) -> list[str]:
        return list(cls._embedding_registry.keys())

    @classmethod
    def is_supported_chat_model(cls, model_type: str) -> bool:
        return model_type in cls._chat_registry

    @classmethod
    def is_supported_embedding_model(cls, model_type: str) -> bool:
        return model_type in cls._embedding_registry

    @classmethod
    def is_supported_model(cls, model_type: str) -> bool:
        return cls.is_supported_chat_model(
            model_type
        ) or cls.is_supported_embedding_model(model_type)


ModelFactory.register_chat(
    "openai_completion", lambda **kwargs: OpenAICompletionModel(**kwargs)
)

ModelFactory.register_embedding(
    "openai_embedding", lambda **kwargs: OpenAIEmbeddingModel(**kwargs)
)

ModelFactory.register_chat(
    "openai_chat", lambda **kwargs: OpenAIChatModel(**kwargs)
)


