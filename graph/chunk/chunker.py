import json
from typing import Any, cast
import pandas as pd
from transformers import AutoTokenizer
from config.enums import ChunkStrategyType
from config.model.chunk_config import ChunkingConfig
from graph.chunk.typing import ChunkInput, ChunkStrategy
from utils.hashing import gen_sha512_hash

class Chunker:
    """文本分块器"""
    
    def __init__(
        self,
        group_by_columns: list[str],
        size: int,
        overlap: int,
        encoding_model: str,
        strategy: ChunkStrategyType,
        prepend_metadata: bool = False,
        chunk_size_includes_metadata: bool = False,
    ):
        self.group_by_columns = group_by_columns
        self.size = size
        self.overlap = overlap
        self.encoding_model = encoding_model
        self.strategy = strategy
        self.prepend_metadata = prepend_metadata
        self.chunk_size_includes_metadata = chunk_size_includes_metadata
        self.tokenizer = AutoTokenizer.from_pretrained(encoding_model, use_fast=True)
        self.strategy_exec = self._load_strategy(strategy)
        self.config = ChunkingConfig(size=size, overlap=overlap, encoding_model=encoding_model)
    
    def _load_strategy(self, strategy: ChunkStrategyType) -> ChunkStrategy:
        """加载分块策略"""
        match strategy:
            case ChunkStrategyType.tokens:
                from graph.chunk.strategies import run_tokens
                return run_tokens
            case ChunkStrategyType.sentence:
                from graph.chunk.bootstrap import bootstrap
                from graph.chunk.strategies import run_sentences
                bootstrap()
                return run_sentences
            case _:
                msg = f"Unknown strategy: {strategy}"
                raise ValueError(msg)
    
    def _run_strategy(
        self,
        input: ChunkInput,
    ) -> list[str | tuple[list[str] | None, str, int]]:
        """执行分块策略"""
        if isinstance(input, str):
            return [item.text_chunk for item in self.strategy_exec([input], self.config)]

        texts = [item if isinstance(item, str) else item[1] for item in input]
        strategy_results = self.strategy_exec(texts, self.config)

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
    
    def _prepare_metadata(self, row: dict[str, Any]) -> tuple[str, int]:
        """准备元数据字符串并计算token数量"""
        line_delimiter = ".\n"
        metadata_str = ""
        metadata_tokens = 0

        if self.prepend_metadata and "metadata" in row:
            metadata = row["metadata"]
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            if isinstance(metadata, dict):
                metadata_str = (
                    line_delimiter.join(f"{k}: {v}" for k, v in metadata.items())
                    + line_delimiter
                )

            if self.chunk_size_includes_metadata:
                metadata_tokens = len(self.tokenizer.encode(metadata_str))
                if metadata_tokens >= self.size:
                    message = "Metadata tokens exceeds the maximum tokens per chunk. Please increase the tokens per chunk."
                    raise ValueError(message)

        return metadata_str, metadata_tokens
    
    def _process_chunks(self, row: dict[str, Any]) -> dict[str, Any]:
        """处理单个文档的分块"""
        metadata_str, metadata_tokens = self._prepare_metadata(row)
        
        # 分块
        chunked = self._run_strategy(row["texts"])

        # 添加元数据
        if self.prepend_metadata:
            for index, chunk in enumerate(chunked):
                if isinstance(chunk, str):
                    chunked[index] = metadata_str + chunk
                else:
                    chunked[index] = (
                        (chunk[0], metadata_str + chunk[1], chunk[2]) if chunk else None
                    )

        row["chunks"] = chunked
        return row
    
    def chunk(self, documents: pd.DataFrame) -> pd.DataFrame:
        """对文档进行分块处理"""
        # 排序并准备数据
        sort = documents.sort_values(by=["id"], ascending=[True])
        sort["text_with_ids"] = list(
            zip(*[sort[col] for col in ["id", "text"]], strict=True)
        )

        # 聚合
        agg_dict = {"text_with_ids": list}
        if "metadata" in documents:
            agg_dict["metadata"] = "first"  # type: ignore

        aggregated = (
            (
                sort.groupby(self.group_by_columns, sort=False)
                if len(self.group_by_columns) > 0
                else sort.groupby(lambda _x: True)
            )
            .agg(agg_dict)
            .reset_index()
        )
        aggregated.rename(columns={"text_with_ids": "texts"}, inplace=True)

        # 分块处理
        aggregated = aggregated.apply(lambda row: self._process_chunks(row), axis=1)
        aggregated = cast("pd.DataFrame", aggregated[[*self.group_by_columns, "chunks"]])
        
        # 展开分块
        aggregated = aggregated.explode("chunks")
        aggregated.rename(columns={"chunks": "chunk"}, inplace=True)
        
        # 生成ID
        aggregated["id"] = aggregated.apply(
            lambda row: gen_sha512_hash(row, ["chunk"]), axis=1
        )
        
        # 提取分块信息
        aggregated[["document_ids", "chunk", "n_tokens"]] = pd.DataFrame(
            aggregated["chunk"].tolist(), index=aggregated.index
        )
        
        # 重命名
        aggregated.rename(columns={"chunk": "text"}, inplace=True)

        # 返回结果
        return cast(
            "pd.DataFrame", aggregated[aggregated["text"].notna()].reset_index(drop=True)
        )