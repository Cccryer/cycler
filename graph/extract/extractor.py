import logging
import re
import html
import asyncio
from typing import Any, List, Optional, TypeVar
import pandas as pd
import networkx as nx
from transformers import AutoTokenizer
from llm.protocol.base import ChatModel
from config.model.extract_config import ExtractGraphConfig
from graphrag.prompts.index.extract_graph import (
    CONTINUE_PROMPT,
    LOOP_PROMPT,
)
from .typing import Document, ExtractionResult

log = logging.getLogger(__name__)
T = TypeVar('T')

class GraphExtractor:
    """图实体关系提取器"""

    def __init__(
        self,
        model: ChatModel,
        entity_types: List[str] = ["organization", "person", "geo", "event"],
        join_descriptions: bool = True,
        encoding_model: Optional[str] = None,
        max_gleanings: Optional[int] = None,
        batch_size: int = 10,
    ):
        """初始化图实体关系提取器
        
        Args:
            model: 语言模型
            prompt: 提示词模板
            entity_types: 实体类型列表
            join_descriptions: 是否合并描述
            encoding_model: 编码模型名称
            max_gleanings: 最大提取次数
            batch_size: 批处理大小
        """
        self.model = model
        self.entity_types = entity_types
        self.join_descriptions = join_descriptions
        self.config = ExtractGraphConfig()
        self.max_gleanings = max_gleanings or self.config.max_gleanings
        self.batch_size = batch_size

        # 构建循环参数
        tokenizer = AutoTokenizer.from_pretrained(encoding_model or self.config.encoding_model)
        yes = f"{tokenizer.encode('Y')[0]}"
        no = f"{tokenizer.encode('N')[0]}"
        self.loop_args = {"logit_bias": {yes: 100, no: 100}, "max_tokens": 1}

    async def extract_from_dataframe(
        self,
        chunks: pd.DataFrame,
        text_column: str,
        id_column: str,
        prompt: str,
        prompt_variables: dict
    ) -> ExtractionResult:
        """从DataFrame中提取实体关系"""
        # 将DataFrame转换为Document列表
        documents = [
            Document(text=row[text_column], id=str(row[id_column]))
            for _, row in chunks.iterrows()
        ]
        return await self.extract_from_documents(documents, prompt, prompt_variables)

    async def extract_from_documents(
        self,
        documents: List[Document],
        prompt: str,
        prompt_variables: dict
    ) -> ExtractionResult:
        """从文档列表中提取实体关系"""
        # 分批处理文档，每个document是一个chunk
        batches = [
            documents[i:i + self.batch_size]
            for i in range(0, len(documents), self.batch_size)
        ]
        
        # 并发处理每个批次
        all_entities = []
        all_relationships = []
        # 每个batch有多个Document(chunk)
        for batch in batches:
            tasks = [self._process_document(chunkDoc, prompt, prompt_variables) for chunkDoc in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤出成功的结果
            for result in batch_results:
                if isinstance(result, tuple) and result is not None:
                    entities, relationships = result
                    all_entities.extend(entities)
                    all_relationships.extend(relationships)

        if not all_entities and not all_relationships:
            return ExtractionResult(
                entities=pd.DataFrame(),
                relationships=pd.DataFrame(),
                graph=nx.Graph()
            )

        # 转换为DataFrame并合并
        entities_df = pd.DataFrame(all_entities)
        relationships_df = pd.DataFrame(all_relationships)
        
        # 合并实体和关系
        entities = self._merge_entities([entities_df])
        relationships = self._merge_relationships([relationships_df])
        
        # 构建最终图
        final_graph = self._build_graph_from_dataframes(entities, relationships)

        return ExtractionResult(
            entities=entities,
            relationships=relationships,
            graph=final_graph
        )

    async def _process_document(
        self, 
        chunkDoc: Document,
        prompt: str,
        prompt_variables: dict
    ) -> tuple[list[dict], list[dict]] | None:
        """处理单个文档，提取实体和关系
        
        Args:
            doc: 文档对象
            
        Returns:
            tuple: (实体列表, 关系列表) 或 None（处理失败时）
        """
        try:
            # 提取实体和关系
            response = await self.model.achat(
                prompt.format(**{
                    **prompt_variables,
                    "input_text": chunkDoc.text
                })
            )
            results = response.content or ""
            log.info(f"results: {results}")
            # 重复提取以最大化实体数量
            for i in range(self.max_gleanings):
                response = await self.model.achat(
                    CONTINUE_PROMPT,
                    history=response.history,
                )
                results += response.content or ""

                if i >= self.max_gleanings - 1:
                    break

                response = await self.model.achat(
                    LOOP_PROMPT,
                    history=response.history,
                    model_parameters=self.loop_args,
                )

                if response.content != "Y":
                    break

            # 解析结果
            entities = []
            relationships = []
            
            for record in results.split("##"):
                '''
                ("entity"<|>何家<|>ORGANIZATION<|>何家 is a family that is referenced as having an incident involving the theft of their books by 孔乙己.)
                ("relationship"<|>孔乙己<|>酒<|>孔乙己 orders alcohol in the shop, indicating his attempts to enjoy life despite his poverty<|>3)
                '''
                record = record.strip()
                if not record:
                    continue
                    
                record = re.sub(r"^\(|\)$", "", record)
                attrs = record.split("<|>")
                
                if len(attrs) < 4:
                    continue
                    
                record_type = clean_str(attrs[0])
                
                if record_type == '"entity"':
                    entities.append({
                        "title": clean_str(attrs[1].upper()),
                        "type": clean_str(attrs[2].upper()),
                        "description": clean_str(attrs[3]),
                        "source_id": chunkDoc.id
                    })
                elif record_type == '"relationship"' and len(attrs) >= 5:
                    try:
                        weight = float(attrs[-1])
                    except (ValueError, IndexError):
                        weight = 1.0
                        
                    relationships.append({
                        "source": clean_str(attrs[1].upper()),
                        "target": clean_str(attrs[2].upper()),
                        "description": clean_str(attrs[3]),
                        "source_id": chunkDoc.id,
                        "weight": weight
                    })

            return entities, relationships

        except Exception as e:
            log.error(f"处理文档时出错: {e}, 文档ID: {chunkDoc.id}")
            return None

    def _merge_entities(self, entity_dfs: List[pd.DataFrame]) -> pd.DataFrame:
        """合并实体DataFrame"""
        if not entity_dfs:
            return pd.DataFrame()
            
        return pd.concat(entity_dfs, ignore_index=True).groupby(
            ["title", "type"], sort=False
        ).agg(
            description=("description", list),
            chunk_ids=("source_id", list),
            frequency=("source_id", "count")
        ).reset_index()

    def _merge_relationships(self, relationship_dfs: List[pd.DataFrame]) -> pd.DataFrame:
        """合并关系DataFrame"""
        if not relationship_dfs:
            return pd.DataFrame()
            
        return pd.concat(relationship_dfs, ignore_index=True).groupby(
            ["source", "target"], sort=False
        ).agg(
            description=("description", list),
            chunk_ids=("source_id", list),
            weight=("weight", "sum")
        ).reset_index()

    def _build_graph_from_dataframes(self, entities: pd.DataFrame, relationships: pd.DataFrame) -> nx.Graph:
        """从实体和关系DataFrame构建图"""
        graph = nx.Graph()
        
        for _, row in entities.iterrows():
            graph.add_node(
                row["title"],
                type=row["type"],
                description=row["description"],
                source_id=row["chunk_ids"]
            )

        for _, row in relationships.iterrows():
            graph.add_edge(
                row["source"],
                row["target"],
                weight=row["weight"],
                description=row["description"],
                source_id=row["chunk_ids"]
            )

        return graph


def clean_str(text: Any) -> str:
    """清理字符串"""
    if not isinstance(text, str):
        return text
    result = html.unescape(text.strip())
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", result)