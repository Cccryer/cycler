from __future__ import annotations

from config.enums import OutputType
from storage.file_pipeline_storage import FilePipelineStorage
from storage.base.pipeline_storage import PipelineStorage
class StorageFactory:

    @classmethod
    def create_storage(
        cls, storage_type: OutputType | str, kwargs: dict
    ) -> PipelineStorage:
        """Create or get a storage object from the provided type."""
        match storage_type:
            case OutputType.file:
                base_dir = kwargs["base_dir"]
                return FilePipelineStorage(root_dir=base_dir)
            case _:
                raise ValueError(f"Unknown storage type: {storage_type}")
            

