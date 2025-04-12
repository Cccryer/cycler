from collections.abc import Iterable
from dataclasses import dataclass
import nltk
from transformers import AutoTokenizer
from config.model.chunk_config import ChunkingConfig
from graph.chunk.typing import TextChunk
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast

import logging
'''
分块策略
'''

logger = logging.getLogger(__name__)


def run_tokens(
    input: list[str],
    config: ChunkingConfig,
) -> Iterable[TextChunk]:
    """Chunks text into chunks based on encoding tokens."""
    tokens_per_chunk = config.size
    chunk_overlap = config.overlap
    encoding_name = config.encoding_model

    tokenizer = AutoTokenizer.from_pretrained(encoding_name, use_fast=True)

    return split_multiple_texts_on_tokens(
        input,
        Tokenizer(
            chunk_overlap=chunk_overlap,
            tokens_per_chunk=tokens_per_chunk,
            tokening=tokenizer,
        ),
    )


def run_sentences(
    input: list[str], _config: ChunkingConfig
) -> Iterable[TextChunk]:
    """Chunks text into multiple parts by sentence."""
    for doc_idx, text in enumerate(input):
        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            yield TextChunk(
                text_chunk=sentence,
                source_doc_indices=[doc_idx],
            )


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
