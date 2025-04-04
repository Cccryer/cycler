from pipeline_state import PipelineRunState

class PipelineRunResult:
    workflow: str
    
    result: any

    state: PipelineRunState

    error: list[Exception] | None

