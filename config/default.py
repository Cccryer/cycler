from dataclasses import dataclass, field
from config.enums import ChunkStrategyType, OutputType, InputFileType, InputType
DEFAULT_OUTPUT_BASE_DIR = "output"
DEFAULT_CHAT_MODEL_ID = "gpt-4o-mini"
DEFAULT_ENCODING_MODEL = "Alibaba-NLP/gte-Qwen2-7B-instruct"
@dataclass
class ChunksDefaults:

    size: int = 1200
    overlap: int = 100
    group_by_columns: list[str] = field(default_factory=lambda: ["id"])
    strategy = ChunkStrategyType.tokens
    encoding_model: str = "deepseek-ai/DeepSeek-V3-0324"
    prepend_metadata: bool = False
    chunk_size_includes_metadata: bool = False

@dataclass
class OutputDefaults:

    type = OutputType.file
    base_dir: str = DEFAULT_OUTPUT_BASE_DIR
    connection_string: None = None
    container_name: None = None
    storage_account_blob_url: None = None
    cosmosdb_account_url: None = None

@dataclass
class InputDefaults:
    """Default values for input."""

    type = InputType.file
    file_type = InputFileType.txt
    base_dir: str = "input"
    connection_string: None = None
    storage_account_blob_url: None = None
    container_name: None = None
    encoding: str = "utf-8"
    file_pattern: str = ""
    file_filter: None = None
    text_column: str = "text"
    title_column: None = None
    metadata: None = None


@dataclass
class ExtractGraphDefaults:
    """Default values for extracting graph."""

    prompt: None = None
    entity_types: list[str] = field(
        default_factory=lambda: ["organization", "person", "geo", "event"]
    )
    max_gleanings: int = 1
    strategy: None = None
    encoding_model: str = DEFAULT_ENCODING_MODEL
    model_id: str = DEFAULT_CHAT_MODEL_ID