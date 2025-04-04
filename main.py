import asyncio
from llm.manager import ModelManager
from config.model.llmconfig import LanguageModelConfig

async def main():
    llm = ModelManager().register_chat(
        name="test",
        model_type="openai_completion",
        config=LanguageModelConfig(
            base_url="https://api.agicto.cn/v1",
            model="gpt-4o-mini",
            api_key="sk-BG7BGtHCOFyrx7btnF3gh8ylBeUzVa1AgAewRzcYKYc6QPYS"
        )
    )
    async for chunk in llm.achat_stream("给我讲个笑话"):
        print(chunk)

if __name__ == "__main__":
    asyncio.run(main())