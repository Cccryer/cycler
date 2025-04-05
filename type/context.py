from storage.pipeline_storage import PipelineStorage
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PipelineRunStats:
    """Pipeline running stats."""

    total_runtime: float = field(default=0)
    """Float representing the total runtime."""

    num_documents: int = field(default=0)
    """Number of documents."""

    input_load_time: float = field(default=0)
    """Float representing the input load time."""

    workflows: dict[str, dict[str, float]] = field(default_factory=dict)
    """A dictionary of workflows."""


PipelineState = dict[Any, Any]


@dataclass
class PipelineRunResult:
    workflow: str
    
    result: Any | None

    state: PipelineState

    errors: list[Exception] | None



@dataclass
class PipelineRunContext:
    stats: PipelineRunStats
    storage: PipelineStorage
    state: PipelineState

