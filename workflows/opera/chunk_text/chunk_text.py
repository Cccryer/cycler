import pandas as pd
from typing import Any, cast
from config.enums import ChunkStrategyType
from config.model.chunk_config import ChunkingConfig
from workflows.opera.chunk_text.typing import ChunkInput, ChunkStrategy
def chunk_text(
    input: pd.DataFrame,
    column: str,
    size: int,
    overlap: int,
    encoding_model: str,
    strategy: ChunkStrategyType,
) -> pd.Series:
    """
    Chunk a piece of text into smaller pieces.

    ## Usage
    ```yaml
    args:
        column: <column name> # The name of the column containing the text to chunk, this can either be a column with text, or a column with a list[tuple[doc_id, str]]
        strategy: <strategy config> # The strategy to use to chunk the text, see below for more details
    ```

    ## Strategies
    The text chunk verb uses a strategy to chunk the text. The strategy is an object which defines the strategy to use. The following strategies are available:

    ### tokens
    This strategy uses the [tokens] library to chunk a piece of text. The strategy config is as follows:

    ```yaml
    strategy: tokens
    size: 1200 # Optional, The chunk size to use, default: 1200
    overlap: 100 # Optional, The chunk overlap to use, default: 100
    ```

    ### sentence
    This strategy uses the nltk library to chunk a piece of text into sentences. The strategy config is as follows:

    ```yaml
    strategy: sentence
    ```
    """
    strategy_exec = load_strategy(strategy)

    # collapse the config back to a single object to support "polymorphic" function call
    config = ChunkingConfig(size=size, overlap=overlap, encoding_model=encoding_model)

    return cast(
        "pd.Series",
        input.apply(
            cast(
                "Any",
                lambda x: run_strategy(
                    strategy_exec,
                    x[column],
                    config,
                ),
            ),
            axis=1,
        ),
    )

def run_strategy(
    strategy_exec: ChunkStrategy,
    input: ChunkInput,
    config: ChunkingConfig,
) -> list[str | tuple[list[str] | None, str, int]]:
    """Run strategy method definition."""
    if isinstance(input, str):
        return [item.text_chunk for item in strategy_exec([input], config)]

    # We can work with both just a list of text content
    # or a list of tuples of (document_id, text content)
    # text_to_chunk = '''
    texts = [item if isinstance(item, str) else item[1] for item in input]

    strategy_results = strategy_exec(texts, config)

    results = []
    for strategy_result in strategy_results:
        doc_indices = strategy_result.source_doc_indices
        if isinstance(input[doc_indices[0]], str):
            results.append(strategy_result.text_chunk)
        else:
            doc_ids = [input[doc_idx][0] for doc_idx in doc_indices]
            results.append((
                doc_ids,
                strategy_result.text_chunk,
                strategy_result.n_tokens,
            ))
    return results


def load_strategy(strategy: ChunkStrategyType) -> ChunkStrategy:
    """Load strategy method definition."""
    match strategy:
        case ChunkStrategyType.tokens:
            from workflows.opera.chunk_text.strategies import run_tokens

            return run_tokens
        case ChunkStrategyType.sentence:
            # NLTK
            from workflows.opera.chunk_text.bootstrap import bootstrap
            from workflows.opera.chunk_text.strategies import run_sentences
            bootstrap()
            return run_sentences
        case _:
            msg = f"Unknown strategy: {strategy}"
            raise ValueError(msg)


def _get_num_total(output: pd.DataFrame, column: str) -> int:
    num_total = 0
    for row in output[column]:
        if isinstance(row, str):
            num_total += 1
        else:
            num_total += len(row)
    return num_total
