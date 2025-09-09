import openai
from typing import Self
import openai.types.responses as api_types
from openai.types.responses.response_input_param import EasyInputMessageParam
from dendrite.models.client_implementations.provider_utils.openai.types import OpenAIToolSchema
import dendrite.utils.config as config
from dendrite.models.interface_client import InterfaceClient
from dendrite.mcp.write.mcp import WriteMCP
from dendrite.mcp.base_mcp import InterfaceMCP
from dendrite.db.io import save_session_changes

from pprint import pprint
import json

class OpenAIInterfaceClient(InterfaceClient):
    def __init__(
            self: Self, 
            mcp: InterfaceMCP,
            system_prompt_path: str
        ):
        super().__init__(system_prompt_path, mcp_instance=mcp)
        self.client = openai.AsyncOpenAI(
            api_key=config.get_config().write
        )
        self.tools = self._format_tools(mcp)

    async def process_convo(self, conversation: list[EasyInputMessageParam]):
        response = await self._get_response(conversation=conversation)
        outputs = response.output

        while (function_calls := [o for o in outputs if o.type == 'function_call']):
            for fc in function_calls:
                pprint(fc.model_dump())
                print(f"Processing function call:")
                print(fc)
                if fc.type != 'function_call':
                    continue
                args = json.loads(fc.arguments)
                try:
                    await self.mcp_instance.call_tool(fc.name, args)
                except Exception as e:
                    print(f"Error calling tool {fc.name}: {e}")
                    conversation.append(
                        EasyInputMessageParam(
                            role='developer',
                            content=f'<error>{str(e)}</error>'
                        )
                    )
            response = await self._get_response(conversation=conversation)
            outputs = response.output
            pprint(response.model_dump())

    async def _get_response(self, conversation: list[EasyInputMessageParam]) -> api_types.Response:
        interface_state = str(self.mcp_instance.interface)
        pprint(f"Interface state:\n{interface_state}")
        
        messages = [
            EasyInputMessageParam(
                role='user',
                content=f"Current Interface State:\n{interface_state}"
            )
        ]
        if isinstance(self.mcp_instance, WriteMCP) and self.mcp_instance.tie_interface:
            messages.append(
                EasyInputMessageParam(
                    role='user',
                    content=f"Current {self.mcp_instance.tie_interface.db_type.value} Interface State:\n{self.mcp_instance.tie_interface}"
                )
            )
        messages.extend(conversation)

        print(f"Total messages being sent: {len(messages)}")
        print("Last few messages:")
        for i, msg in enumerate(messages):
            print(f"  {i}: {msg['role']} - {msg['content']}...")
    
        response = await self.client.responses.create(
            model="gpt-5",
            instructions=self.system_prompt,
            tools=self.tools,
            parallel_tool_calls=False,
            tool_choice='auto',
            input=messages,
        )
        return response


    def _format_tools(self: Self, mcp: InterfaceMCP) -> list[api_types.FunctionToolParam]:
        tools: list[OpenAIToolSchema] = list(mcp._tool_manager._tools.values())
        return [
            api_types.FunctionToolParam(
                type='function',
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters,
                strict=False,
            ) for tool in tools
        ]