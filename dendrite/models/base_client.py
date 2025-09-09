from pydantic import BaseModel
from abc import ABC
from dendrite.utils.file import read_file

class ModelConfig(BaseModel):
    model: str
    api_key: str
    system_prompt_path: str

class BaseClient(ABC): 
    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config
        self.system_prompt = read_file(model_config.system_prompt_path)