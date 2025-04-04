import asyncio
from pipeline import Pipeline
from config.config import GraphRagConfig
from type.context import PipelineRunContext
from type.pipeline_result import PipelineRunResult  
from typing import AsyncIterable
from pipeline.factory import PipelineFactory
async def run(
    pipeline: Pipeline,
    config: GraphRagConfig,
    context: PipelineRunContext,
)->AsyncIterable[PipelineRunResult]:
    """Run the pipeline."""
    
    for name, workflow in pipeline.run():
        result = await workflow(config, context)
        yield result



if __name__ == "__main__":
    # 读取配置
    config = GraphRagConfig()

    PipelineFactory.register_all()
    pipeline = PipelineFactory.create_pipeline()
    asyncio.run(run(pipeline, config, PipelineRunContext()))
