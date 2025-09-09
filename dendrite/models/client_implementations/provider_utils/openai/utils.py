from openai.types.responses.response_input_param import EasyInputMessageParam
import json
from typing import cast

def read_convo_from_file(file_path: str) -> list[EasyInputMessageParam]:
        with open(file_path, 'r') as file:
            conversation_history = [EasyInputMessageParam(**msg) for msg in cast(list[dict], json.load(file))]
        return conversation_history