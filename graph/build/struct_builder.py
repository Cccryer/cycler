from graph.extract.typing import ExtractionResult
from storage.neo4jdb.neo4jdb import DBConnectionManager
import pandas as pd
'''
    根据extractor提取的实体和关系，构建图数据库的结构
    设置三种节点:
    1. 文档节点
    2. chunk节点
    3. 实体节点

    关系：
    1. 文档和chunk之间”从属关系“
    2. chunk和和节点间的“提及关系”
    3. 实体之间的“抽象或相似关系” 该关系由模型描述
    4. 文本块之间的”顺序关系“
'''

class StructBuilder:
    def __init__(
            self,
            extraction_result: ExtractionResult,
            chunk_result: pd.DataFrame,
            db_manager: DBConnectionManager
        ):
        self.extraction_result = extraction_result
        self.db_manager = db_manager

    def create_document_node(self):
        pass

    def create_chunk_node(self):
        pass

    def create_entity_node(self):
        pass