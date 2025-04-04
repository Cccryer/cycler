from typing import Any, Generic, TypeVar, Optional
from abc import abstractmethod

from pydantic import BaseModel, Field

T = TypeVar("T")

class Usage(BaseModel):
    input_tokens: int = Field(..., description="The number of input tokens.")
    output_tokens: int = Field(..., description="The number of output tokens.")
    total_tokens: int = Field(..., description="The total number of tokens.")

class ModelResponse(BaseModel, Generic[T]):
    success: bool = Field(..., description="Whether the response was successful.")
    error_message: Optional[str] = Field(None, description="The error message if the response was not successful.")
    content: str = Field(..., description="The content of the response.")
    model: str = Field(..., description="The model used to generate the response.")

    usage: Usage = Field(..., description="The usage of the response.")

    raw_response: T = Field(..., description="The raw response from the model.")


