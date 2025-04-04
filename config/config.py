from pydantic import BaseModel

class GraphRagConfig(BaseModel):
    """Configuration for the pipeline."""
    def __init__(self):
        super().__init__()

