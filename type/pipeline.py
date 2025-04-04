from collections.abc import Generator

from workflow import Workflow


class Pipeline:
    """Encapsulates running workflows."""

    def __init__(self, workflows: list[Workflow]):
        self.workflows = workflows

    def run(self) -> Generator[Workflow]:
        """Return a Generator over the pipeline workflows."""
        yield from self.workflows

    def names(self) -> list[str]:
        """Return the names of the workflows in the pipeline."""
        return [name for name, _ in self.workflows]
