from typing import Callable, Awaitable, Any

from config.model.workflow_config import WorkflowConfig
from type.context import PipelineRunContext
from type.context import PipelineRunResult
from dataclasses import dataclass

@dataclass
class WorkflowFunctionOutput:
    """Data container for Workflow function results."""

    result: Any | None
    """The result of the workflow function. This can be anything - we use it only for logging downstream, and expect each workflow function to write official outputs to the provided storage."""


WorkflowFunction = Callable[
    [WorkflowConfig, PipelineRunContext],
    Awaitable[PipelineRunResult],
]

Workflow = tuple[str, WorkflowFunction]
