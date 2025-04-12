from dataclasses import dataclass
from typing import Callable, Iterable
from config.model.chunk_config import ChunkingConfig

@dataclass
class TextChunk:
    """Text chunk class definition."""

    text_chunk: str
    source_doc_indices: list[int]
    n_tokens: int | None = None

ChunkInput = str | list[str] | list[tuple[str, str]]
"""Input to a chunking strategy. Can be a string, a list of strings, or a list of tuples of (id, text)."""

ChunkStrategy = Callable[
    [list[str], ChunkingConfig], Iterable[TextChunk]
]
