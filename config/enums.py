from enum import Enum

class ChunkStrategyType(Enum):
    """ChunkStrategy class definition."""

    tokens = "tokens"
    sentence = "sentence"

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'


class OutputType(str, Enum):
    """The output type for the pipeline."""

    file = "file"
    """The file output type."""
    memory = "memory"
    """The memory output type."""
    blob = "blob"
    """The blob output type."""
    cosmosdb = "cosmosdb"
    """The cosmosdb output type"""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'

class InputFileType(str, Enum):
    """The input file type for the pipeline."""

    csv = "csv"
    """The CSV input type."""
    txt = "txt"
    """The txt input type."""
    json = "json"
    """The JSON input type."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'

class InputType(str, Enum):
    """The input type for the pipeline."""

    file = "file"
    """The file storage type."""
    blob = "blob"
    """The blob storage type."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'


class AsyncType(str, Enum):
    """Enum for the type of async to use."""

    AsyncIO = "asyncio"
    Threaded = "threaded"