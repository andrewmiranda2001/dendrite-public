from typing import Self
from abc import abstractmethod
from .base_client import ModelConfig, BaseClient
from dendrite.utils.file import read_file

class ResponseClient(BaseClient):
    def __init__(self: Self, model_config: ModelConfig):
        super().__init__(model_config)

    @abstractmethod
    async def get_response(self, conversation: any) -> str:
        """
        Implemented provider specific processing of a conversation. For example, this could be as simple as summarizing a session. 
        """
        pass