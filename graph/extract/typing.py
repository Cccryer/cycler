from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import networkx as nx
import pandas as pd


ExtractedEntity = dict[str, Any]
ExtractedRelationship = dict[str, Any]
StrategyConfig = dict[str, Any]
EntityTypes = list[str]


@dataclass
class Document:
    """文档类型定义"""
    text: str
    id: str


@dataclass
class EntityExtractionResult:
    """Entity extraction result class definition."""

    entities: list[ExtractedEntity]
    relationships: list[ExtractedRelationship]
    graph: nx.Graph | None


EntityExtractStrategy = Callable[
    [
        list[Document],
        EntityTypes,
        StrategyConfig,
    ],
    Awaitable[EntityExtractionResult],
]


class ExtractEntityStrategyType(str, Enum):
    """ExtractEntityStrategyType class definition."""

    graph_intelligence = "graph_intelligence"
    nltk = "nltk"

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'


@dataclass
class ExtractionResult:
    """提取结果类型定义"""
    entities: pd.DataFrame
    relationships: pd.DataFrame
    graph: nx.Graph
