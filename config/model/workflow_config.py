from pydantic import BaseModel, Field
from config.model.chunk_config import ChunkingConfig
from config.default import ChunksDefaults

class WorkflowConfig(BaseModel):
    """Workflow config."""

    name: str
    """The name of the workflow."""
    
    chunks: ChunkingConfig = Field(default=ChunksDefaults())