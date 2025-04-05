# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing chunk strategies."""

from collections.abc import Iterable

import nltk
from transformers import AutoTokenizer
from config.model.chunk_config import ChunkingConfig
from workflows.opera.chunk_text.typing import TextChunk
from workflows.opera.text_split.text_split import Tokenizer, split_multiple_texts_on_tokens

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