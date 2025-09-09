from pydantic import BaseModel, Field
from typing import Any

class AnthropicToolSchema(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory = dict)

class AnthropicEasyInputMessageParam(BaseModel):
    role: str
    content: str