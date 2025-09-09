from dendrite.utils.config import get_config, get_client_set, TemporalPass
from dendrite.db.io import DatabaseType
from dendrite.interface.types import Note, Content, ContentStatus
from dendrite.models.client_implementations.interface.openai import OpenAIInterfaceClient
from dendrite.models.client_implementations.response.openai import OpenAIResponseClient
from dendrite.models.client_implementations.provider_utils.openai.utils import read_convo_from_file
from dendrite.models.interface_client import InterfaceClient
from dendrite.models.response_client import ResponseClient

from openai.types.responses.response_input_param import EasyInputMessageParam
from pydantic import BaseModel
from datetime import datetime

class TemporalPass(BaseModel):
    summarizer: ResponseClient
    tagger: InterfaceClient

# No need for WritePass class, just use the dict

async def run_temporal_pass(conversation: list[EasyInputMessageParam], temporal: TemporalPass, previous_notes: list[Note]):
    summarizer, tagger = temporal.summarizer, temporal.tagger
    interface = tagger.mcp_instance.interface

    summary = await summarizer.get_response(conversation=conversation)

    now = datetime.now()
    year = str(now.year)
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"
    temporal_path = f"{DatabaseType.TEMPORAL.value}/{year}/{month}/{day}"
    interface.open_node(temporal_path)
    temporal_node = interface.explorer.node

    session_note = Note(
        db_type=DatabaseType.TEMPORAL,
        id=hash(summary),
        read_only=True,
        name=f"Session",
        content=[
            Content(text=summary, status=ContentStatus.ADDED)
        ],
        node_references=[temporal_node],
        note_references=previous_notes,
        status=ContentStatus.STAGED
    )
    tagger.mcp_instance.interface.explorer.create_note_direct(session_note)
    tagger.process_convo(conversation=conversation)

async def run_write_pass(conversation_path: str):
    write_clients = get_client_set().write_pass
    if get_config().id != 'openai_write':
        raise ValueError("run_write_pass only works with OpenAI write configuration.")
    conversation = read_convo_from_file(conversation_path)
    # just to type everything correctly in the actual passes
    if not isinstance((temporal := write_clients[DatabaseType.TEMPORAL]), TemporalPass) or not isinstance(temporal.summarizer, OpenAIResponseClient) or not isinstance(temporal.tagger, OpenAIInterfaceClient) or not isinstance(write_clients[DatabaseType.CONCEPTUAL], OpenAIInterfaceClient) or not isinstance(write_clients[DatabaseType.CONCRETE], OpenAIInterfaceClient):
        raise ValueError("run_write_pass requires specific client types for Temporal, Concrete, and Conceptual passes.")


    for db_type in [DatabaseType.CONCRETE, DatabaseType.CONCEPTUAL, DatabaseType.TEMPORAL]:
        client = write_clients[db_type]
        print(f'Running {db_type.name} pass ...')
        if db_type == DatabaseType.CONCEPTUAL:
            await client.process_convo(conversation=conversation)
        elif db_type == DatabaseType.CONCRETE:
            await client.process_convo(conversation=conversation)
        elif db_type == DatabaseType.TEMPORAL:
            await run_temporal_pass(conversation=conversation, temporal=temporal, previous_notes=write_clients[DatabaseType.CONCRETE].mcp_instance.interface.opened.open_notes)
