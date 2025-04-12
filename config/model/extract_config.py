from pathlib import Path

from pydantic import BaseModel, Field

from config.default import ExtractGraphDefaults
from config.model.llm_config import LanguageModelConfig

extract_graph_defaults = ExtractGraphDefaults()

class ExtractGraphConfig(BaseModel):
    """Configuration section for entity extraction."""

    model_id: str = Field(
        description="The model ID to use for text embeddings.",
        default=extract_graph_defaults.model_id,
    )
    prompt: str | None = Field(
        description="The entity extraction prompt to use.",
        default=extract_graph_defaults.prompt,
    )
    entity_types: list[str] = Field(
        description="The entity extraction entity types to use.",
        default=extract_graph_defaults.entity_types,
    )
    max_gleanings: int = Field(
        description="The maximum number of entity gleanings to use.",
        default=extract_graph_defaults.max_gleanings,
    )
    strategy: dict | None = Field(
        description="Override the default entity extraction strategy",
        default=extract_graph_defaults.strategy,
    )
    encoding_model: str | None = Field(
        default=extract_graph_defaults.encoding_model,
        description="The encoding model to use.",
    )

    def resolved_strategy(
        self, root_dir: str, model_config: LanguageModelConfig
    ) -> dict:
        """Get the resolved entity extraction strategy."""
        from graph.extract.typing import (
            ExtractEntityStrategyType,
        )

        return self.strategy or {
            "type": ExtractEntityStrategyType.graph_intelligence,
            "llm": model_config.model_dump(),
            "num_threads": model_config.concurrent_requests,
            "extraction_prompt": (Path(root_dir) / self.prompt).read_text(
                encoding="utf-8"
            )
            if self.prompt
            else None,
            "max_gleanings": self.max_gleanings,
            "encoding_name": model_config.encoding_model,
        }
