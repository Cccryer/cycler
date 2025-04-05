from workflows.opera.chunk_text.typing import TextChunk
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Tokenizer:
    """Tokenizer data class."""

    chunk_overlap: int
    """Overlap in tokens between chunks"""
    tokens_per_chunk: int
    """Maximum number of tokens per chunk"""
    tokening: PreTrainedTokenizer | PreTrainedTokenizerFast
    """Tokenizer"""

def split_multiple_texts_on_tokens(
    texts: list[str], tokenizer: Tokenizer
) -> list[TextChunk]:
    """Split multiple texts and return chunks with metadata using the tokenizer."""
    result = []
    mapped_ids = []
    for source_doc_idx, text in enumerate(texts):
        encoded = tokenizer.tokening.encode(text)

        mapped_ids.append((source_doc_idx, encoded))

    input_ids = [
        (source_doc_idx, id) for source_doc_idx, ids in mapped_ids for id in ids
    ]

    start_idx = 0
    cur_idx = min(start_idx + tokenizer.tokens_per_chunk, len(input_ids))
    chunk_ids = input_ids[start_idx:cur_idx]

    while start_idx < len(input_ids):
        chunk_text = tokenizer.tokening.decode([id for _, id in chunk_ids])
        doc_indices = list({doc_idx for doc_idx, _ in chunk_ids})
        result.append(TextChunk(chunk_text, doc_indices, len(chunk_ids)))
        start_idx += tokenizer.tokens_per_chunk - tokenizer.chunk_overlap
        cur_idx = min(start_idx + tokenizer.tokens_per_chunk, len(input_ids))
        chunk_ids = input_ids[start_idx:cur_idx]

    return result
