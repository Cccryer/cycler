"""Encapsulates pipeline construction and selection."""
from typing import ClassVar

from type.workflow import WorkflowFunction
from type.pipeline import Pipeline


class PipelineFactory:
    """A factory class for workflow pipelines."""

    workflows: ClassVar[dict[str, WorkflowFunction]] = {} # 类变量

    @classmethod
    def register(cls, name: str, workflow: WorkflowFunction):
        """Register a custom workflow function."""
        cls.workflows[name] = workflow

    @classmethod
    def register_all(cls, workflows: dict[str, WorkflowFunction]):
        """Register a dict of custom workflow functions."""
        for name, workflow in workflows.items():
            cls.register(name, workflow)

    @classmethod
    def create_pipeline(
        cls
    ) -> Pipeline:
        """Create a pipeline generator."""
        return Pipeline([(name, cls.workflows[name]) for name in cls.workflows])

