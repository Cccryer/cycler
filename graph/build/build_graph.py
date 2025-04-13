import pandas as pd
from graph.extract.typing import ExtractionResult
from storage.neo4jdb.neo4jdb import get_db_manager
'''
    将extractor提取的实体和关系写入到图数据库中

    入参                                                                     neo4j
    documents:                                                             DOCUMENT
        id: 文档id                                                          id
        title: 文档标题                                                     title
        text: 文档内容                                                      # text
        creation_data: 文档创建时间                                         creation_data

    chunk_result:                                                            CHUNK
        id: 文本块id                                                        id
        text: 文本块内容                                                    text
        document_ids: 所属文档id list                                       document_ids
        n_tokens: 文本块token数量                                           #n_tokens
                                                                           embedding
                                                                           next_id 
                                                                           prev_id   
    
    extraction_result:                                                     ENTITY
        entities: 实体列表                                                  id
            title: 实体名称                                                 name
            type: 实体类型                                                  type
            description: 实体描述                                           description
            chunk_ids: 所属chunk id list                                    chunk_ids
            frequency: 实体在文本中出现的次数                                frequency
        relationships: 关系列表
            source_id: 关系源实体id
            target_id: 关系目标实体id
            description: 关系描述
            chunk_ids: 所属chunk id list
            weight: 关系权重
        graph: 图 nx.Graph
'''


class GraphBuilder:
    def __init__(
            self,
            documents: pd.DataFrame,
            chunk_result: pd.DataFrame,
            extraction_result: ExtractionResult,
        ):
        self.extraction_result = extraction_result
        self.chunk_result = chunk_result
        self.graph = self.extraction_result.graph
        self.entities = self.extraction_result.entities
        self.relationships = self.extraction_result.relationships
        self.db_manager = get_db_manager()

    def build(self):
        pass


    def create_document_node(self):
        # 创建文档节点

        pass

    def create_chunk_node(self):
        pass

    def create_entity_node(self):
        pass