from dataclasses import dataclass
from callback import WorkflowCallbacks
from pipeline_state import PipelineState
from storage.pipeline_storage import PipelineStorage

@dataclass
class PipelineRunContext:
    storage: PipelineStorage

    callbacks: WorkflowCallbacks
    
    state: PipelineState

