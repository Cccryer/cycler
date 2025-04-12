from config.model.workflow_config import WorkflowConfig
from type.context import PipelineRunContext
from type.workflow import WorkflowFunctionOutput
from utils.storage import load_table_from_storage, write_table_to_storage

from graph.chunk.chunker import Chunker


async def run_workflow(
    config: WorkflowConfig,
    context: PipelineRunContext,
) -> WorkflowFunctionOutput:
    """All the steps to transform base text_units."""
    documents = await load_table_from_storage("documents", context.storage)

    chunks = config.chunks
    chunker = Chunker(
        group_by_columns=chunks.group_by_columns,
        size=chunks.size,
        overlap=chunks.overlap,
        encoding_model=chunks.encoding_model,
        strategy=chunks.strategy,
        prepend_metadata=chunks.prepend_metadata,
        chunk_size_includes_metadata=chunks.chunk_size_includes_metadata,
    )

    output = chunker.chunk(documents)
    await write_table_to_storage(output, "text_units", context.storage)

    return WorkflowFunctionOutput(result=output)

