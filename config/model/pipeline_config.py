from pydantic import BaseModel, Field

class PipelineConfig(BaseModel):
    """Pipeline configuration."""

    name: str = Field(
        ...,
        description="The name of the pipeline.",
    )