import asyncio
import logging.config
from llm.manager import ModelManager
from config.model.llm_config import LanguageModelConfig
from config.model.log_config import LOGGING_CONFIG
import logging
from run.run import run

logger = logging.getLogger(__name__)

async def llm_chat():
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
        logger.info(chunk)


if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_CONFIG)
    asyncio.run(run())