from typing import Callable, Awaitable

from config.config import config
from type.context import PipelineRunContext
from type.pipeline_result import PipelineRunResult

WorkflowFunction = Callable[
    [config, PipelineRunContext],
    Awaitable[PipelineRunResult],
]
Workflow = tuple[str, WorkflowFunction]
