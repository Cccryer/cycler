from __future__ import annotations

from typing import  ClassVar

from config.enums import OutputType
from storage.file_pipeline_storage import FilePipelineStorage
from storage.pipeline_storage import PipelineStorage
class StorageFactory:
    """A factory class for storage implementations.

    Includes a method for users to register a custom storage implementation.

    Configuration arguments are passed to each storage implementation as kwargs
    for individual enforcement of required/optional arguments.
    """

    storage_types: ClassVar[dict[str, type]] = {}

    @classmethod
    def register(cls, storage_type: str, storage: type):
        """Register a custom storage implementation."""
        cls.storage_types[storage_type] = storage

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
            

