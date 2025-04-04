from llm.protocol.base import ChatModel, EmbeddingModel
from typing import Any
from collections.abc import AsyncGenerator, Generator
from config.model.llmconfig import LanguageModelConfig
from openai import OpenAI, AsyncOpenAI
from openai.types.responses.response import Response as OpenAIResponse
from llm.response.base import ModelResponse, Usage
from llm.utils import run_coroutine_sync
from openai.types.create_embedding_response import CreateEmbeddingResponse
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

'''
1. openai response chat model
2. openai completion chat model
3. openai embedding model
'''

class OpenAIChatModel(ChatModel):
    def __init__(self, name: str, config: LanguageModelConfig):
        self.name = name #标识
        self.model = config.model #模型名称
        self.api_key = config.api_key #api key
        self.base_url = config.base_url #base url
        self.timeout = config.timeout #超时时间
        self.max_retries = config.max_retries #最大重试次数
        self.sync_client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
    async def achat(self, prompt: str, history: list | None = None, **kwargs: Any) -> ModelResponse:
        input = []
        if history:
            input.extend(history)
        input.append({
            "role": "user",
            "content": {
                "text": prompt,
                "type": "input_text"
            }
        })
        print(input)

        response: OpenAIResponse = await self.async_client.responses.create(
            model=self.model,
            input=input,
            **kwargs
        )

        return ModelResponse(
            success=response.status == "completed",
            error_message=response.error.message if response.error else None,
            content=response.output_text,
            model=response.model,
            usage=Usage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.total_tokens
            ),
            raw_response=response
        )

    async def achat_stream(self, prompt: str, history: list | None = None, **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        input = []
        if history:
            input.extend(history)
        input.append({
            "role": "user",
            "content": {
                "text": prompt,
                "type": "input_text"
            }
        })

        response: OpenAIResponse = await self.async_client.responses.create(
            model=self.model,
            input=input,
            **kwargs
        )
        async for chunk in response.output.content:
            if chunk is not None:
                yield chunk    

    def chat(self, prompt: str, history: list | None = None, **kwargs: Any) -> ModelResponse:
        return run_coroutine_sync(self.achat(prompt, history=history, **kwargs))


    def chat_stream(
        self, prompt: str, history: list | None = None, **kwargs: Any
    ) -> Generator[str, None]:
        msg = "chat_stream is not supported for synchronous execution"
        raise NotImplementedError(msg)


class OpenAICompletionModel(ChatModel):
    def __init__(self, name: str, config: LanguageModelConfig):
        self.name = name #标识
        self.model = config.model #模型名称
        self.api_key = config.api_key #api key
        self.base_url = config.base_url #base url
        self.timeout = config.timeout #超时时间
        self.max_retries = config.max_retries #最大重试次数

        self.sync_client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )

    async def achat(self, prompt: str, history: list | None = None, **kwargs: Any) -> ModelResponse:
        messages = []
        if history:
            messages.extend(history)
        messages.append({
            "role": "user",
            "content": prompt
        })
        response: ChatCompletion = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return ModelResponse(
            success=True,
            error_message=None,
            content=response.choices[0].message.content,
            model=response.model,
            usage=Usage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            ),
            raw_response=response
        )

    async def achat_stream(self, prompt: str, history: list | None = None, **kwargs: Any) -> AsyncGenerator[str, None]:
        messages = []
        if history:
            messages.extend(history)
        messages.append({
            "role": "user",
            "content": prompt
        })
        response: AsyncGenerator[ChatCompletionChunk, None] = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk is not None:
                yield chunk.choices[0].delta.content

    def chat(self, prompt: str, history: list | None = None, **kwargs: Any) -> ModelResponse:
        return run_coroutine_sync(self.achat(prompt, history=history, **kwargs))

    def chat_stream(self, prompt: str, history: list | None = None, **kwargs: Any) -> Generator[str, None]:
        msg = "chat_stream is not supported for synchronous execution"
        raise NotImplementedError(msg)




class OpenAIEmbeddingModel(EmbeddingModel):
    def __init__(self, name: str, config: LanguageModelConfig):
        self.name = name #标识
        self.model = config.model #模型名称
        self.api_key = config.api_key #api key
        self.base_url = config.base_url #base url
        self.timeout = config.timeout #超时时间
        self.max_retries = config.max_retries #最大重试次数
        
        self.sync_client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )

    async def aembed_batch(
        self, text_list: list[str], **kwargs: Any
    ) -> list[list[float]]:
        response: CreateEmbeddingResponse = await self.async_client.embeddings.create(
            model=self.model,
            input=text_list,
            **kwargs
        )
        return [embedding.embedding for embedding in response.data]

    async def aembed(self, text: str, **kwargs: Any) -> list[float]:
        response: CreateEmbeddingResponse = await self.async_client.embeddings.create(
            model=self.model,
            input=text,
            **kwargs
        )
        return response.data[0].embedding

    def embed_batch(self, text_list: list[str], **kwargs: Any) -> list[list[float]]:
        return run_coroutine_sync(self.aembed_batch(text_list, **kwargs))


    def embed(self, text: str, **kwargs: Any) -> list[float]:
        return run_coroutine_sync(self.aembed(text, **kwargs))
    