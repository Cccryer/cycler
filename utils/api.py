from config.model.output_config import OutputConfig
from storage.base.pipeline_storage import PipelineStorage
from storage.storage_factory import StorageFactory

def create_storage_from_config(output: OutputConfig) -> PipelineStorage:
    """Create a storage object from the config."""
    storage_config = output.model_dump()
    return StorageFactory().create_storage(
        storage_type=storage_config["type"],
        kwargs=storage_config,
    )
