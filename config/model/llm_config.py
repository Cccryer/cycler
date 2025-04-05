
from pydantic import BaseModel, Field

class LanguageModelConfig(BaseModel):
    """
        Language model configuration.
        这里有待拓展，我目前还不清楚这些字段得种类, 以及其他模型的config
    """

    api_key: str | None = Field(
        default= "",
        description="The API key to use for the LLM service."
    )


    auth_type: str = Field(
        default= "api_key",
        description="The authentication type."
    )

    model: str = Field(
        default="",
        description="The model to use."
    )

    base_url: str = Field(
        default= "",
        description="The base URL to use for the LLM service.",
    )

    timeout: int = Field(
        default= 10,
        description="The timeout to use for the LLM service."
    )

    max_retries: int = Field(
        default= 3,
        description="The maximum number of retries to use for the LLM service."
    )

        