from enum import Enum
from pydantic import BaseModel
from typing import Any

class EasyInputMessageParamType(str, Enum):
    USER = 'user'
    ASSISTANT = 'assistant'

class EasyInputMessageParam(BaseModel):
    type: EasyInputMessageParamType
    content: str

    def __dict__(self, cache: bool = False) -> dict[str, Any]:
        output = {
            "content": [{
                "text": self.content,
                "type": "text",
            }],
            "role": self.type.value,
        }
        if cache:
            output["content"][0]["cache_control"] = {"type": "ephemeral"}
        return output

class ToolSchema(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]