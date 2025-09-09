import openai
from typing import Self
import openai.types.responses as api_types
from openai.types.responses.response_input_param import EasyInputMessageParam
from dendrite.models.client_implementations.provider_utils.openai.types import OpenAIToolSchema
from dendrite.models.response_client import ResponseClient
from dendrite.models.base_client import ModelConfig
from dendrite.utils.config import get_config

from pprint import pprint
import json

class OpenAIResponseClient(ResponseClient):
    def __init__(
            self: Self, 
            model_config: ModelConfig
        ):
        super().__init__(model_config)
        self.conversation_history: list[EasyInputMessageParam] = []
        self.client = openai.AsyncOpenAI(
            api_key=get_config().write
        )

    async def process_convo(self: Self, conversation: list[EasyInputMessageParam]) -> str:

        response = await self.client.responses.create(
            model="gpt-5",
            instructions=self.system_prompt,
            input=conversation,
        )
        outputs = response.output
        pprint(response.model_dump())
        

        return response