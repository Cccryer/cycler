from pydantic import BaseModel
from dataclasses import field
from config.enums import ChunkStrategyType

from config.default import ChunksDefaults

chunk_defaults = ChunksDefaults()

class ChunkingConfig(BaseModel):
    """Configuration section for chunking."""

    size: int = field(
        default=chunk_defaults.size,
    )
    overlap: int = field(
        default=chunk_defaults.overlap,
    )
    group_by_columns: list[str] = field(
        default=chunk_defaults.group_by_columns,
    )
    strategy: ChunkStrategyType = field(
        default=chunk_defaults.strategy,
    )
    encoding_model: str = field(
        default=chunk_defaults.encoding_model,
    )
    prepend_metadata: bool = field(
        default=chunk_defaults.prepend_metadata,
    )
    chunk_size_includes_metadata: bool = field(
        default=chunk_defaults.chunk_size_includes_metadata,
    )
