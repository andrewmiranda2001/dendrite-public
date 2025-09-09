import os
from .constants import DIARRHEA_ROOT
from ..databases.io import DatabaseType
from dendrite.interface.types import Note
import json
from pydantic import BaseModel
from typing import cast
from dendrite.models.interface_client import InterfaceClient
from dendrite.models.response_client import ResponseClient
from dendrite.models.base_client import ModelConfig
from functools import cache
from dendrite.stages.write.full_pass import TemporalPass

config_path = os.getenv("CONFIG_PATH", os.path.join(DIARRHEA_ROOT, 'config.json'))
set_config = os.getenv("CONFIG", "")
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found at {config_path}")
if not set_config:
    raise ValueError("CONFIG needs to be set.")

class TemporalPassConfig(BaseModel):
    summarizer: ModelConfig
    tagger: ModelConfig

class Config(BaseModel):
    id: str
    write: TemporalPassConfig
    read: ModelConfig | None
    converse: ModelConfig | None

@cache
def get_config() -> Config:
    with open(config_path, 'r') as file:
        config_data = cast(list[dict], json.load(file))
    configs = [config for item in config_data if (config := Config.model_validate(item)) and config.id == set_config]
    if not len(configs) == 1:
        raise ValueError(f"Expected exactly one configuration, found {len(configs)}")
    return configs[0]

WritePass = dict[DatabaseType, InterfaceClient | TemporalPass]
class ClientSet(BaseModel):
    write_pass: WritePass
    read_client: InterfaceClient
    converse_client: None = None

    class Config:
        arbitrary_types_allowed = True

def get_client_set() -> ClientSet:
    from dendrite.mcp.write.mcp import WriteMCP
    from dendrite.mcp.read.mcp import ReadMCP
    from dendrite.models.client_implementations.interface.openai import OpenAIInterfaceClient
    
    if (config := get_config()).id == 'openai_write':
        # Create the actual OpenAI client with WriteMCP
        write_pass: dict[DatabaseType, InterfaceClient] = {}
        for type_ in DatabaseType:
            if type_ == DatabaseType.CONCEPTUAL:
                tie = None
            elif type_ == DatabaseType.CONCRETE:
                if DatabaseType.CONCEPTUAL not in write_pass:
                    raise ValueError("Conceptual interface not instantiated before concrete.")
                tie = write_pass[DatabaseType.CONCEPTUAL].mcp_instance.interface
            elif type_ == DatabaseType.TEMPORAL:
                if DatabaseType.CONCRETE not in write_pass:
                    raise ValueError("Concrete interface not instantiated before temporal.")
                tie = write_pass[DatabaseType.CONCRETE].mcp_instance.interface
            else:
                raise ValueError(f"Unexpected database type: {type_}")
            client = OpenAIInterfaceClient(
                mcp=WriteMCP(
                    type_,
                    tie
                ),
                system_prompt_path=f'C:\\Users\\Main\\Dendrite\\dendrite\\models\\system_prompts\\{type_.value}.txt'
            )
            if type_ == DatabaseType.TEMPORAL:
                write_pass[type_] = TemporalPass(
                    summarizer=ResponseClient(),
                    consolidator=client
                )
            else:
                write_pass[type_] = client
        return ClientSet(
            write_pass=write_pass,
            read_client=OpenAIInterfaceClient(
                mcp=ReadMCP(),
                system_prompt_path='C:\\Users\\Main\\Dendrite\\dendrite\\models\\stage_implementations\\read\\system.txt'
            )
        )
    elif config.id == 'anthropic_write':
        raise NotImplementedError("Anthropic client not implemented yet.")