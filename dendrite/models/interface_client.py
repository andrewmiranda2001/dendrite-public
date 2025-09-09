from typing import Self
from abc import ABC, abstractmethod
from dendrite.utils.file import read_file
from dendrite.mcp.base_mcp import InterfaceMCP

# client class specifically for both read and write models.
# They should not need any interaction, just tool calls.
# Likely will have the converse client have its own DBClient for reading and give it the same interface and everything else should work out.
class InterfaceClient(ABC):
    def __init__(self: Self, system_prompt_path: str, mcp_instance: InterfaceMCP):
        self.system_prompt = read_file(system_prompt_path)
        self.mcp_instance = mcp_instance

    @abstractmethod
    async def process_convo(self, conversation: any) -> str:
        """
        Handles the state of the interface, caching, context configuration, and other things that need to be done before getting a response.
        """
        pass
    
    @abstractmethod
    def _format_tools(self: Self, mcp: InterfaceMCP) -> any:
        """
        Format tools given to use by the mcp instance into a list of that the client API expects.
        """
        pass