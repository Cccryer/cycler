from pydantic import BaseModel, Field
from config.enums import InputType, InputFileType
from config.default import InputDefaults

input_defaults = InputDefaults()
class InputConfig(BaseModel):
    """The default configuration section for Input."""

    type: InputType = Field(
        description="The input type to use.",
        default=input_defaults.type,
    )
    file_type: InputFileType = Field(
        description="The input file type to use.",
        default=input_defaults.file_type,
    )
    base_dir: str = Field(
        description="The input base directory to use.",
        default=input_defaults.base_dir,
    )
    connection_string: str | None = Field(
        description="The azure blob storage connection string to use.",
        default=input_defaults.connection_string,
    )
    storage_account_blob_url: str | None = Field(
        description="The storage account blob url to use.",
        default=input_defaults.storage_account_blob_url,
    )
    container_name: str | None = Field(
        description="The azure blob storage container name to use.",
        default=input_defaults.container_name,
    )
    encoding: str = Field(
        description="The input file encoding to use.",
        default=input_defaults.encoding,
    )
    file_pattern: str = Field(
        description="The input file pattern to use.",
        default=input_defaults.file_pattern,
    )
    file_filter: dict[str, str] | None = Field(
        description="The optional file filter for the input files.",
        default=input_defaults.file_filter,
    )
    text_column: str = Field(
        description="The input text column to use.",
        default=input_defaults.text_column,
    )
    title_column: str | None = Field(
        description="The input title column to use.",
        default=input_defaults.title_column,
    )
    metadata: list[str] | None = Field(
        description="The document attribute columns to use.",
        default=input_defaults.metadata,
    )
