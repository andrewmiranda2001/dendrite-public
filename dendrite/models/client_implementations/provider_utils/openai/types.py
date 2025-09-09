from pydantic import BaseModel, Field
from typing import Any


class OpenAIToolSchema(BaseModel):
    type: str = Field(default = "function")
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory = dict)