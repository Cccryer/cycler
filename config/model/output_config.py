from pydantic import BaseModel, Field

from config.enums import OutputType
from config.default import OutputDefaults

output_defaults = OutputDefaults()

class OutputConfig(BaseModel):
    """The default configuration section for Output."""

    type: OutputType = Field(
        description="The output type to use.",
        default=output_defaults.type,
    )
    base_dir: str = Field(
        description="The base directory for the output.",
        default=output_defaults.base_dir,
    )
    connection_string: str | None = Field(
        description="The storage connection string to use.",
        default=output_defaults.connection_string,
    )
    container_name: str | None = Field(
        description="The storage container name to use.",
        default=output_defaults.container_name,
    )
    storage_account_blob_url: str | None = Field(
        description="The storage account blob url to use.",
        default=output_defaults.storage_account_blob_url,
    )
    cosmosdb_account_url: str | None = Field(
        description="The cosmosdb account url to use.",
        default=output_defaults.cosmosdb_account_url,
    )
