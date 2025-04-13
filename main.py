import asyncio
import logging.config
from llm.manager import ModelManager
from config.model.llm_config import LanguageModelConfig
from config.model.log_config import LOGGING_CONFIG
import logging
from storage.input.create_input import create_input
from config.model.input_config import InputConfig, InputType
from graph.chunk.chunker import Chunker
from config.enums import ChunkStrategyType
from graph.extract.extractor import GraphExtractor
from pyvis.network import Network

from graphrag.prompts.index.extract_graph import GRAPH_EXTRACTION_PROMPT

DEFAULT_TUPLE_DELIMITER = "<|>"
DEFAULT_RECORD_DELIMITER = "##"
DEFAULT_COMPLETION_DELIMITER = "<|COMPLETE|>"
DEFAULT_ENTITY_TYPES = ["organization", "person", "geo", "event"]

prompt_variables = {
    "tuple_delimiter": DEFAULT_TUPLE_DELIMITER,
    "record_delimiter": DEFAULT_RECORD_DELIMITER,
    "completion_delimiter": DEFAULT_COMPLETION_DELIMITER,
    "entity_types": DEFAULT_ENTITY_TYPES
}

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


async def test_chunk():
    input_text = await create_input(InputConfig(type=InputType.file, base_dir="input"), root_dir="test")
    input_text.to_csv('input.csv', index=False, encoding='utf-8')
    chunker = Chunker(
        group_by_columns=["id"],
        size=200,
        overlap=100,
        encoding_model="deepseek-ai/DeepSeek-V3-0324",
        strategy=ChunkStrategyType.tokens
    )
    chunks = chunker.chunk(input_text)
    chunks.to_csv('data.csv', index=False, encoding='utf-8')

    chat = ModelManager.get_instance().get_or_create_chat_model(
        name="test",
        model_type="openai_completion",
        config=LanguageModelConfig(
            base_url="https://api.agicto.cn/v1",
            model="gpt-4o-mini",
            api_key="sk-BG7BGtHCOFyrx7btnF3gh8ylBeUzVa1AgAewRzcYKYc6QPYS"
        )
    )

    extractor = GraphExtractor(
        model=chat,
        join_descriptions=True
    )
    result = await extractor.extract_from_dataframe(chunks, "text", "id", prompt=GRAPH_EXTRACTION_PROMPT, prompt_variables=prompt_variables)
    result.entities.to_csv('entities.csv', index=False, encoding='utf-8')
    result.relationships.to_csv('relationships.csv', index=False, encoding='utf-8')
    net = Network(notebook=True)
    net.from_nx(result.graph)
    net.show("graph.html")
    
if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_CONFIG)
    asyncio.run(test_chunk())