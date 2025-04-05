import asyncio
import logging.config
from llm.manager import ModelManager
from config.model.llm_config import LanguageModelConfig
from config.model.log_config import LOGGING_CONFIG
import logging
from storage.input.factory import create_input
from config.model.input_config import InputConfig
from utils.api import create_storage_from_config
from config.model.output_config import OutputConfig
from pipeline.factory import PipelineFactory
from type.pipeline import Pipeline
import pandas as pd
import time
import json
from storage.pipeline_storage import PipelineStorage
from type.context import PipelineRunResult
from type.context import PipelineRunStats
from typing import AsyncIterable
from config.model.workflow_config import WorkflowConfig
from type.context import PipelineRunContext
from dataclasses import asdict
from utils.storage import write_table_to_storage

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

async def _dump_json(context: PipelineRunContext) -> None:
    """Dump the stats and context state to the storage."""
    await context.storage.set(
        "stats.json", json.dumps(asdict(context.stats), indent=4, ensure_ascii=False)
    )
    await context.storage.set(
        "context.json", json.dumps(context.state, indent=4, ensure_ascii=False)
    )


async def _run_pipeline(
    pipeline: Pipeline,
    dataset: pd.DataFrame,
    storage: PipelineStorage,
    config: WorkflowConfig,
    logger: logging.Logger,
) -> AsyncIterable[PipelineRunResult]:
    # load existing state in case any workflows are stateful
    state_json = await storage.get("context.json")
    state = json.loads(state_json) if state_json else {}

    context = PipelineRunContext(
        storage=storage,
        state=state,
        stats=PipelineRunStats()
    )

    logger.info("Final # of rows loaded: %s", len(dataset))
    # context.state.num_documents = len(dataset)
    last_workflow = "starting documents"

    try:
        await _dump_json(context)
        await write_table_to_storage(dataset, "documents", context.storage)

        for name, workflow_function in pipeline.run():
            last_workflow = name
            work_time = time.time()
            result = await workflow_function(config, context)
            yield PipelineRunResult(
                workflow=name, result=result.result, state=context.state, errors=None
            )

            context.stats.workflows[name] = {"overall": time.time() - work_time}

        await _dump_json(context)

    except Exception as e:
        logger.exception("error running workflow %s", last_workflow)
        yield PipelineRunResult(
            workflow=last_workflow, result=None, state=context.state, errors=[e]
        )

async def run_pipeline():


    pipeline = PipelineFactory.create_pipeline()

    output_config = OutputConfig(
        type="file",
        base_dir="output"
    )
    storage = create_storage_from_config(output_config)
    dataset = await create_input(InputConfig(), "input")
    logger.info("Running standard indexing.")
    config = WorkflowConfig(
        name="test"

    )
    async for table in _run_pipeline(
        pipeline=pipeline,
        dataset=dataset,
        storage=storage,
        logger=logger,
        config=config,
    ):
        yield table

async def test_chunk_text():
    from workflows.create_base_text_unit import run_workflow as create_base_text_unit
    from pipeline.factory import PipelineFactory
    
    PipelineFactory.register("create_base_text_unit", create_base_text_unit)

    async for table in run_pipeline():
        logger.info(table)

if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_CONFIG)
    asyncio.run(test_chunk_text())