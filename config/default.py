from dataclasses import dataclass, field
from config.enums import ChunkStrategyType, OutputType, InputFileType, InputType
DEFAULT_OUTPUT_BASE_DIR = "output"


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
    file_type = InputFileType.text
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