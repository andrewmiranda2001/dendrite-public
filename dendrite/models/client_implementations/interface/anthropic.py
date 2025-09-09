import anthropic
from typing import Self
import httpx
from mcp.server.fastmcp import FastMCP
import mcp.server.fastmcp.tools as mcp_types
import dendrite.models.client_implementations.provider_utils.anthropic as types
import anthropic.types as anthropic_types
import dendrite.utils as utils
from dendrite.models.interface_client import InterfaceClient

class AnthropicInterfaceClient(InterfaceClient):
    def __init__(self: Self, mcp: FastMCP, system_prompt_path: str = './system.txt'):
        super().__init__(system_prompt_path)
        self.mcp_instance = mcp
        self.conversation_history: list[types.AnthropicMessage] = []
        self.cache = False
        self.anthropic_client = anthropic.AsyncAnthropic(
            api_key=utils.get_config().write,
            http_client=httpx.AsyncClient(verify=False)
        )

    async def process_convo(self):
        # optional query for write model. we just literally want one pass ideally, so no conversing, just tool calls.
        response, err = await self._get_response()
        if err is not None:
            return None, err
            
        while not model_stop:
            # move this to the top so we always process the last tool call.
            model_stop = response.stop_reason == 'end_turn'
            # tool results are always None, and tool calls will always be presented in the notifications section of the interface.
            # therefore, simply call the tool and move on.
            tool_calls: list[anthropic_types.ToolUseBlock] = [content for content in response.content if isinstance(content, anthropic_types.ToolUseBlock)]
            if len(tool_calls) != len(response.content):
                raise ValueError(f"Expected all content to be tool calls, got {len(tool_calls)} tool calls and {len(response.content) - len(tool_calls)} other content blocks.")
    
    async def _get_response(self) -> tuple[anthropic_types.Message, Exception | None]:
        try:
            response: anthropic_types.Message = await self.anthropic_client.messages.create(
                model='claude-3-haiku-20240307',
                system=self.system_prompt,
                tools=self._format_tools,
                tool_choice={'type': 'auto'}, # give model the option to run a tool. might need to change this later. 
                messages=self.conversation_history,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"Error from Anthropic API: {e.response.status_code} - {e.response.text}")
        if response.usage.cache_creation_input_tokens > 2000:
            self.cache_on_next_message = True
        return response, None
    
    # Formats tools into a list of ToolSchema objects.
    def _format_tools(self: Self, mcp: FastMCP) -> list[types.AnthropicToolSchema]:
        tools: list[mcp_types.Tool] = list(mcp._tool_manager._tools.values())
        return [types.AnthropicToolSchema.model_validate({ "name": tool.name, "description": tool.description, "input_schema": tool.parameters }) for tool in tools]